"""
Database ORM Models
-------------------
Defines SQLAlchemy models for storing intraday power market data.
Optimized for TimescaleDB hypertables for efficient time-series queries.
"""

from sqlalchemy import Column, String, Float, DateTime, UniqueConstraint, Index
from database import Base
import datetime

class IntradayPriceRecord(Base):
    """
    Nord Pool intraday continuous market price records.
    Stores 15-minute Market Time Unit (MTU) pricing data.
    """
    __tablename__ = "intraday_prices"

    id = Column(String, primary_key=True)  # Composite ID: area_timestamp
    start_time = Column(DateTime, nullable=False, index=True)
    end_time = Column(DateTime, nullable=False)
    area = Column(String(10), nullable=False, index=True)  # SE3, FI, NO1, DK1
    price_eur = Column(Float, nullable=False)  # EUR/MWh
    fetched_at = Column(DateTime, default=datetime.datetime.utcnow)

    # Prevent duplicate records for same time period and area
    __table_args__ = (
        UniqueConstraint('start_time', 'area', name='_start_time_area_uc'),
        Index('idx_area_time', 'area', 'start_time'),  # Composite index for fast queries
    )

    def __repr__(self):
        return f"<IntradayPrice(area={self.area}, time={self.start_time}, price={self.price_eur})>"


class EntsoeGridRecord(Base):
    """
    ENTSO-E Transparency Platform grid and market data.
    Stores actual load, generation, and intraday price metrics.
    """
    __tablename__ = "entsoe_grid_data"

    id = Column(String, primary_key=True)  # Composite ID: BZN_zone_metric_timestamp
    timestamp = Column(DateTime, nullable=False, index=True)
    bidding_zone = Column(String(10), nullable=False, index=True)  # FI, SE1, NO, etc.
    metric_name = Column(String(30), nullable=False)  # actual_load, intraday_price, generation
    metric_value = Column(Float, nullable=False)
    fetched_at = Column(DateTime, default=datetime.datetime.utcnow)

    # Prevent duplicate metrics for same timestamp and zone
    __table_args__ = (
        UniqueConstraint('timestamp', 'bidding_zone', 'metric_name', name='_entsoe_metric_uc'),
        Index('idx_entsoe_lookup', 'bidding_zone', 'metric_name', 'timestamp'),
    )

    def __repr__(self):
        return f"<EntsoeGrid(zone={self.bidding_zone}, metric={self.metric_name}, value={self.metric_value})>"
