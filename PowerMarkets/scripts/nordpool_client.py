"""
Nord Pool Data Collection Script
---------------------------------
Fetches intraday market data from Nord Pool Exchange.
Supports continuous trading and auction data retrieval.

Usage:
    python nordpool_client.py --areas SE3,FI,NO1 --date 2026-07-21
"""

import os
import sys
import argparse
import asyncio
import httpx
import pandas as pd
from datetime import datetime, date
from typing import List, Dict, Any
import json

class NordPoolDataCollector:
    """
    Collects intraday market data from Nord Pool Exchange.
    Handles both continuous trading and auction data.
    """
    
    def __init__(self, api_key: str = None):
        """
        Initialize Nord Pool client.
        
        Args:
            api_key: Nord Pool API token (if None, reads from environment)
        """
        self.api_key = api_key or os.getenv("NORDPOOL_API_KEY", "")
        self.base_url = "https://nordpoolgroup.com"
        
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Accept": "application/json",
            "User-Agent": "NordPoolDataCollector/1.0"
        }
        
        print(f"✓ Nord Pool client initialized")
        if not self.api_key:
            print("⚠ Warning: No API key found. API requests may fail.")
            print("  Set NORDPOOL_API_KEY environment variable or use --api-key parameter")

    async def fetch_intraday_statistics(self, areas: List[str], delivery_date: date) -> List[Dict[str, Any]]:
        """
        Fetch intraday hourly statistics for specified areas.
        
        Args:
            areas: List of bidding zone codes (e.g., ['SE3', 'FI', 'NO1'])
            delivery_date: Delivery date for data
            
        Returns:
            List of dictionaries containing market data
        """
        endpoint = f"{self.base_url}/Intraday/ContractStatistics/ByAreas"
        
        params = {
            "date": delivery_date.isoformat(),
            "areas": ",".join(areas)
        }
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                print(f"Fetching Nord Pool data for {areas} on {delivery_date}...")
                response = await client.get(endpoint, headers=self.headers, params=params)
                
                if response.status_code == 401:
                    print("✗ Authentication failed. Check your Nord Pool API key.")
                    return []
                elif response.status_code == 429:
                    print("✗ Rate limit exceeded. Please wait before retrying.")
                    return []
                elif response.status_code != 200:
                    print(f"✗ API error: HTTP {response.status_code}")
                    print(f"  Response: {response.text[:200]}")
                    return []
                
                data = response.json()
                print(f"✓ Successfully retrieved Nord Pool data")
                return self._parse_statistics(data)
                
        except httpx.ConnectTimeout:
            print("✗ Connection timeout. Nord Pool API may be unreachable.")
            return []
        except httpx.RequestError as e:
            print(f"✗ Request error: {str(e)}")
            return []
        except Exception as e:
            print(f"✗ Unexpected error: {str(e)}")
            return []

    def _parse_statistics(self, raw_data: dict) -> List[Dict[str, Any]]:
        """
        Parse Nord Pool API response into structured records.
        
        Args:
            raw_data: Raw JSON response from API
            
        Returns:
            List of parsed records
        """
        records = []
        
        try:
            rows = raw_data.get("data", {}).get("rows", [])
            
            for row in rows:
                record = {
                    "start_time": row.get("startTime"),
                    "end_time": row.get("endTime"),
                    "area": row.get("areaName"),
                    "vwap_eur_mwh": float(row.get("vwap", 0.0)),
                    "high_price": float(row.get("high", 0.0)),
                    "low_price": float(row.get("low", 0.0)),
                    "volume_mwh": float(row.get("volume", 0.0)),
                    "first_trade_time": row.get("firstTradeTime"),
                    "last_trade_time": row.get("lastTradeTime"),
                }
                records.append(record)
            
            print(f"✓ Parsed {len(records)} market records")
            
        except (KeyError, AttributeError, ValueError) as e:
            print(f"⚠ Warning: Error parsing some records: {str(e)}")
        
        return records

    def save_to_csv(self, records: List[Dict[str, Any]], filename: str, output_dir: str = "data"):
        """
        Save records to CSV file.
        
        Args:
            records: List of record dictionaries
            filename: Output filename
            output_dir: Output directory path
        """
        if not records:
            print(f"⚠ No data to save for {filename}")
            return
        
        os.makedirs(output_dir, exist_ok=True)
        df = pd.DataFrame(records)
        
        filepath = os.path.join(output_dir, filename)
        df.to_csv(filepath, index=False)
        print(f"✓ Saved to {filepath} ({len(records)} records)")

    def save_to_json(self, records: List[Dict[str, Any]], filename: str, output_dir: str = "data"):
        """
        Save records to JSON file.
        
        Args:
            records: List of record dictionaries
            filename: Output filename
            output_dir: Output directory path
        """
        if not records:
            print(f"⚠ No data to save for {filename}")
            return
        
        os.makedirs(output_dir, exist_ok=True)
        filepath = os.path.join(output_dir, filename)
        
        with open(filepath, 'w') as f:
            json.dump(records, f, indent=2)
        
        print(f"✓ Saved to {filepath} ({len(records)} records)")


async def main_async(args):
    """Async main function for data collection."""
    # Parse areas
    areas = [a.strip().upper() for a in args.areas.split(',')]
    
    # Parse date
    try:
        delivery_date = datetime.strptime(args.date, '%Y-%m-%d').date()
    except ValueError:
        print(f"Error: Invalid date format '{args.date}'. Use YYYY-MM-DD")
        sys.exit(1)
    
    # Initialize collector
    collector = NordPoolDataCollector(api_key=args.api_key)
    
    # Fetch data
    records = await collector.fetch_intraday_statistics(areas, delivery_date)
    
    if not records:
        print("No data retrieved. Check API key and parameters.")
        sys.exit(1)
    
    # Save data
    filename_base = f"nordpool_{'_'.join(areas)}_{args.date}"
    
    if args.format in ['csv', 'both']:
        collector.save_to_csv(records, f"{filename_base}.csv", args.output)
    
    if args.format in ['json', 'both']:
        collector.save_to_json(records, f"{filename_base}.json", args.output)
    
    print("\n✓ Data collection completed successfully")


def main():
    """Command-line interface for Nord Pool data collection."""
    parser = argparse.ArgumentParser(
        description="Fetch intraday market data from Nord Pool Exchange",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Fetch data for Swedish and Finnish markets
  python nordpool_client.py --areas SE3,FI --date 2026-07-21

  # Fetch data for all Nordic areas
  python nordpool_client.py --areas SE1,SE2,SE3,SE4,FI,NO1,NO2,DK1,DK2 --date 2026-07-21

  # Save as JSON format
  python nordpool_client.py --areas FI --date 2026-07-21 --format json
        """
    )
    
    parser.add_argument('--areas', type=str, required=True,
                        help='Comma-separated list of bidding zones (e.g., SE3,FI,NO1)')
    parser.add_argument('--date', type=str, required=True,
                        help='Delivery date (YYYY-MM-DD)')
    parser.add_argument('--api-key', type=str, default=None,
                        help='Nord Pool API key (overrides NORDPOOL_API_KEY env var)')
    parser.add_argument('--format', type=str, choices=['csv', 'json', 'both'], default='csv',
                        help='Output format (default: csv)')
    parser.add_argument('--output', type=str, default='data',
                        help='Output directory for data files (default: data)')
    
    args = parser.parse_args()
    
    # Run async main
    asyncio.run(main_async(args))


if __name__ == "__main__":
    main()
