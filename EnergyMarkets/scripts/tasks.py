"""
Automated Background Tasks
---------------------------
Scheduled jobs for periodic data collection from Nord Pool and ENTSO-E.
Runs every 15 minutes to maintain up-to-date market data.
"""

import datetime
import os
import pandas as pd
from sqlalchemy.dialects.postgresql import insert
from entsoe import EntsoePandasClient
from database import AsyncSessionLocal
from connectors import NordPoolConnector
from schemas import MarketDataRequest
from models import IntradayPriceRecord, EntsoeGridRecord


async def auto_fetch_nordpool_job():
    """
    Automated task to fetch and save Nord Pool intraday prices.
    Executes every 15 minutes via APScheduler.
    """
    print(f"[{datetime.datetime.now()}] Starting Nord Pool 15-minute data scrape...")
    
    connector = NordPoolConnector()
    
    # Query today and tomorrow to capture newly opened trading sessions
    today = datetime.date.today()
    payload = MarketDataRequest(
        areas=["SE3", "FI", "NO1", "DK1"], 
        delivery_date=today
    )
    
    try:
        # Fetch data from Nord Pool API
        raw_records = await connector.fetch_intraday_prices(payload)
        
        if not raw_records:
            print("No records returned from Nord Pool API. Skipping database transaction.")
            return

        # Save to database with upsert logic
        async with AsyncSessionLocal() as session:
            async with session.begin():
                for record in raw_records:
                    # Parse ISO timestamp strings
                    start_dt = datetime.datetime.fromisoformat(record.start_time.replace("Z", ""))
                    end_dt = datetime.datetime.fromisoformat(record.end_time.replace("Z", ""))
                    
                    # PostgreSQL upsert: insert or update on conflict
                    stmt = insert(IntradayPriceRecord).values(
                        id=f"{record.area}_{start_dt.isoformat()}",
                        start_time=start_dt,
                        end_time=end_dt,
                        area=record.area,
                        price_eur=record.price_eur
                    )
                    
                    # Update if record already exists
                    update_stmt = stmt.on_conflict_do_update(
                        constraint='_start_time_area_uc',
                        set_=dict(
                            price_eur=stmt.excluded.price_eur, 
                            fetched_at=datetime.datetime.utcnow()
                        )
                    )
                    
                    await session.execute(update_stmt)
                
                await session.commit()
                print(f"✓ Nord Pool: Successfully processed {len(raw_records)} records in database.")

    except Exception as e:
        print(f"✗ Nord Pool Task Execution Failure: {str(e)}")


async def auto_fetch_entsoe_job():
    """
    Automated task to fetch and save ENTSO-E grid data.
    Retrieves actual load and intraday prices for specified bidding zones.
    """
    print(f"[{datetime.datetime.now()}] Pulling fundamental grid data from ENTSO-E...")
    
    api_key = os.getenv("ENTSOE_API_KEY")
    if not api_key:
        print("✗ ENTSOE_API_KEY environment variable is missing. Skipping task.")
        return

    # Initialize ENTSO-E client
    client = EntsoePandasClient(api_key=api_key)
    
    # Define sliding 24-hour evaluation window
    start_time = pd.Timestamp.utcnow() - pd.Timedelta(hours=12)
    end_time = pd.Timestamp.utcnow() + pd.Timedelta(hours=12)
    
    # Focus on specified bidding zones
    bidding_zones = ["FI", "SE3", "NO1"]
    
    for bidding_zone in bidding_zones:
        try:
            print(f"  Processing bidding zone: {bidding_zone}")
            
            # Query actual physical grid load
            try:
                df_load = client.query_load(bidding_zone, start=start_time, end=end_time)
            except Exception as e:
                print(f"  ⚠ Load data unavailable for {bidding_zone}: {str(e)}")
                df_load = pd.Series()
            
            # Query intraday market prices
            try:
                df_prices = client.query_day_ahead_prices(bidding_zone, start=start_time, end=end_time)
            except Exception as e:
                print(f"  ⚠ Price data unavailable for {bidding_zone}: {str(e)}")
                df_prices = pd.Series()
            
            # Container for cleaned data points
            records_to_upsert = []
            
            # Parse load time-series
            if isinstance(df_load, pd.Series) and not df_load.empty:
                for ts, value in df_load.items():
                    if pd.notna(value):
                        records_to_upsert.append({
                            "ts": ts.to_pydatetime().replace(tzinfo=None),
                            "metric": "actual_load",
                            "val": float(value)
                        })
            elif isinstance(df_load, pd.DataFrame) and not df_load.empty:
                for ts, row in df_load.iterrows():
                    val = row.iloc[0]
                    if pd.notna(val):
                        records_to_upsert.append({
                            "ts": ts.to_pydatetime().replace(tzinfo=None),
                            "metric": "actual_load",
                            "val": float(val)
                        })
            
            # Parse price time-series
            if isinstance(df_prices, pd.Series) and not df_prices.empty:
                for ts, value in df_prices.items():
                    if pd.notna(value):
                        records_to_upsert.append({
                            "ts": ts.to_pydatetime().replace(tzinfo=None),
                            "metric": "intraday_price",
                            "val": float(value)
                        })
            elif isinstance(df_prices, pd.DataFrame) and not df_prices.empty:
                for ts, row in df_prices.iterrows():
                    val = row.iloc[0]
                    if pd.notna(val):
                        records_to_upsert.append({
                            "ts": ts.to_pydatetime().replace(tzinfo=None),
                            "metric": "intraday_price",
                            "val": float(val)
                        })
            
            if not records_to_upsert:
                print(f"  No valid data points found for {bidding_zone}")
                continue
            
            # Synchronize to TimescaleDB
            async with AsyncSessionLocal() as session:
                async with session.begin():
                    for item in records_to_upsert:
                        stmt = insert(EntsoeGridRecord).values(
                            id=f"BZN_{bidding_zone}_{item['metric']}_{item['ts'].isoformat()}",
                            timestamp=item['ts'],
                            bidding_zone=bidding_zone,
                            metric_name=item['metric'],
                            metric_value=item['val']
                        )
                        
                        # Update existing records with latest values
                        upsert_stmt = stmt.on_conflict_do_update(
                            constraint='_entsoe_metric_uc',
                            set_=dict(
                                metric_value=stmt.excluded.metric_value,
                                fetched_at=datetime.datetime.utcnow()
                            )
                        )
                        
                        await session.execute(upsert_stmt)
                    
                    await session.commit()
                    print(f"  ✓ {bidding_zone}: Upserted {len(records_to_upsert)} data points")

        except Exception as e:
            print(f"  ✗ Error processing {bidding_zone}: {str(e)}")
    
    print(f"✓ ENTSO-E Integration completed")
