"""
Pydantic Data Validation Schemas
---------------------------------
Defines request/response models for API endpoints with strict type validation.
"""

from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import date, datetime

# ============================================================================
# Nord Pool Schemas
# ============================================================================

class MarketDataRequest(BaseModel):
    """Request model for fetching Nord Pool market data"""
    areas: List[str] = Field(
        default=["SE3", "FI"], 
        description="Nordic price zones (SE1-SE4, FI, NO1-NO5, DK1-DK2)"
    )
    delivery_date: date = Field(
        default_factory=date.today, 
        description="Target delivery date for intraday data"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "areas": ["SE3", "FI", "NO1"],
                "delivery_date": "2026-07-21"
            }
        }


class PriceRecord(BaseModel):
    """Individual price record for a specific time slot and area"""
    start_time: str
    end_time: str
    area: str
    price_eur: float

    class Config:
        json_schema_extra = {
            "example": {
                "start_time": "2026-07-21T14:00:00",
                "end_time": "2026-07-21T14:15:00",
                "area": "SE3",
                "price_eur": 45.23
            }
        }


class MarketDataResponse(BaseModel):
    """Response model containing market data records"""
    status: str
    source: str = "NordPool_V2"
    records_count: int
    data: List[PriceRecord]

    class Config:
        json_schema_extra = {
            "example": {
                "status": "success",
                "source": "NordPool_V2",
                "records_count": 96,
                "data": [
                    {
                        "start_time": "2026-07-21T14:00:00",
                        "end_time": "2026-07-21T14:15:00",
                        "area": "SE3",
                        "price_eur": 45.23
                    }
                ]
            }
        }


# ============================================================================
# ENTSO-E Schemas
# ============================================================================

class EntsoeDataRequest(BaseModel):
    """Request model for fetching ENTSO-E grid data"""
    bidding_zones: List[str] = Field(
        default=["FI"], 
        description="ENTSO-E bidding zone codes"
    )
    start_date: datetime = Field(
        description="Start of data query period (UTC)"
    )
    end_date: datetime = Field(
        description="End of data query period (UTC)"
    )
    metrics: List[str] = Field(
        default=["actual_load", "intraday_price"],
        description="Metrics to retrieve"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "bidding_zones": ["FI", "SE3"],
                "start_date": "2026-07-21T00:00:00",
                "end_date": "2026-07-21T23:59:59",
                "metrics": ["actual_load", "intraday_price"]
            }
        }


class EntsoeGridMetric(BaseModel):
    """Individual ENTSO-E grid metric record"""
    timestamp: datetime
    bidding_zone: str
    metric_name: str
    metric_value: float


class EntsoeDataResponse(BaseModel):
    """Response model for ENTSO-E data"""
    status: str
    source: str = "ENTSO-E_Transparency"
    records_count: int
    data: List[EntsoeGridMetric]


# ============================================================================
# Health Check Schemas
# ============================================================================

class HealthCheckResponse(BaseModel):
    """API health check response"""
    status: str
    timestamp: datetime
    database_connected: bool
    scheduler_running: bool
    
    class Config:
        json_schema_extra = {
            "example": {
                "status": "healthy",
                "timestamp": "2026-07-21T12:00:00",
                "database_connected": True,
                "scheduler_running": True
            }
        }
