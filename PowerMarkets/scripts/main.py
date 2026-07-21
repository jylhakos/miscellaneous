"""
FastAPI Application Entry Point
--------------------------------
Main application with API routes, background schedulers, and lifecycle management.
Serves REST API for market data and manages automated data collection tasks.
"""

from fastapi import FastAPI, Depends, status, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
import datetime

from database import engine, Base, get_db
from schemas import (
    MarketDataRequest, MarketDataResponse,
    EntsoeDataRequest, EntsoeDataResponse,
    HealthCheckResponse
)
from connectors import NordPoolConnector
from tasks import auto_fetch_nordpool_job, auto_fetch_entsoe_job
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, text
from models import IntradayPriceRecord, EntsoeGridRecord


# Global scheduler instance
scheduler = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifecycle management.
    Handles startup and shutdown events for database and scheduler.
    """
    global scheduler
    
    # ========== STARTUP ==========
    print("=" * 60)
    print("🚀 Starting Power Trading Data Engine")
    print("=" * 60)
    
    # Create database tables if they don't exist
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("✓ Database tables initialized")
    
    # Configure and start background scheduler
    scheduler = AsyncIOScheduler()
    
    # Job 1: Nord Pool continuous trade tracker (every 15 minutes)
    scheduler.add_job(
        auto_fetch_nordpool_job,
        trigger=IntervalTrigger(minutes=15),
        id="nordpool_15min_scraper",
        replace_existing=True,
        max_instances=1  # Prevent overlapping executions
    )
    print("✓ Scheduled: Nord Pool scraper (every 15 minutes)")
    
    # Job 2: ENTSO-E grid data tracker (every 15 minutes, offset by 1 minute)
    scheduler.add_job(
        auto_fetch_entsoe_job,
        trigger=IntervalTrigger(minutes=15, start_date=datetime.datetime.now() + datetime.timedelta(seconds=10)),
        id="entsoe_15min_scraper",
        replace_existing=True,
        max_instances=1
    )
    print("✓ Scheduled: ENTSO-E scraper (every 15 minutes, offset +1min)")
    
    scheduler.start()
    print("✓ Background scheduler started")
    print("=" * 60)
    
    yield  # Application runs here
    
    # ========== SHUTDOWN ==========
    print("\n" + "=" * 60)
    print("🛑 Shutting down Power Trading Data Engine")
    print("=" * 60)
    
    if scheduler:
        scheduler.shutdown()
        print("✓ Background scheduler stopped")
    
    await engine.dispose()
    print("✓ Database connections closed")
    print("=" * 60)


# Initialize FastAPI application
app = FastAPI(
    title="Power Trading Data Engine",
    description="Automated data aggregator for Nordic intraday power markets",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS for web dashboard access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================================
# API Routes
# ============================================================================

@app.get("/", tags=["System"])
async def root():
    """Root endpoint with API information."""
    return {
        "service": "Power Trading Data Engine",
        "version": "1.0.0",
        "status": "operational",
        "documentation": "/docs",
        "health": "/api/v1/health"
    }


@app.get("/api/v1/health", response_model=HealthCheckResponse, tags=["System"])
async def health_check(db: AsyncSession = Depends(get_db)):
    """
    Health check endpoint.
    Verifies database connectivity and scheduler status.
    """
    # Test database connection
    db_connected = False
    try:
        await db.execute(text("SELECT 1"))
        db_connected = True
    except Exception as e:
        print(f"Database health check failed: {e}")
    
    # Check scheduler status
    scheduler_running = scheduler is not None and scheduler.running
    
    return HealthCheckResponse(
        status="healthy" if (db_connected and scheduler_running) else "degraded",
        timestamp=datetime.datetime.utcnow(),
        database_connected=db_connected,
        scheduler_running=scheduler_running
    )


@app.post(
    "/api/v1/market-data/fetch",
    response_model=MarketDataResponse,
    status_code=status.HTTP_200_OK,
    tags=["Market Data"]
)
async def fetch_nord_pool_data(
    payload: MarketDataRequest,
    connector: NordPoolConnector = Depends(lambda: NordPoolConnector())
):
    """
    Fetch Nord Pool intraday market data on-demand.
    Triggers real-time scraping of specified bidding zones.
    
    Args:
        payload: MarketDataRequest with areas and delivery_date
        
    Returns:
        MarketDataResponse with fetched price records
    """
    # Execute async scraping
    raw_records = await connector.fetch_intraday_prices(payload)
    
    return MarketDataResponse(
        status="success",
        records_count=len(raw_records),
        data=raw_records
    )


@app.get("/api/v1/prices/latest", tags=["Market Data"])
async def get_latest_prices(
    area: str = "SE3",
    limit: int = 96,
    db: AsyncSession = Depends(get_db)
):
    """
    Retrieve latest stored intraday prices from database.
    
    Args:
        area: Bidding zone code (default: SE3)
        limit: Number of records to return (default: 96 for 24 hours of 15-min data)
        
    Returns:
        List of price records
    """
    query = (
        select(IntradayPriceRecord)
        .where(IntradayPriceRecord.area == area)
        .order_by(IntradayPriceRecord.start_time.desc())
        .limit(limit)
    )
    
    result = await db.execute(query)
    records = result.scalars().all()
    
    return {
        "area": area,
        "count": len(records),
        "data": [
            {
                "start_time": r.start_time.isoformat(),
                "end_time": r.end_time.isoformat(),
                "price_eur_mwh": r.price_eur
            }
            for r in records
        ]
    }


@app.get("/api/v1/entsoe/latest", tags=["Grid Data"])
async def get_latest_entsoe_data(
    zone: str = "FI",
    metric: str = "actual_load",
    limit: int = 48,
    db: AsyncSession = Depends(get_db)
):
    """
    Retrieve latest ENTSO-E grid data from database.
    
    Args:
        zone: Bidding zone code (default: FI)
        metric: Metric name (default: actual_load)
        limit: Number of records (default: 48)
        
    Returns:
        List of grid metric records
    """
    query = (
        select(EntsoeGridRecord)
        .where(
            EntsoeGridRecord.bidding_zone == zone,
            EntsoeGridRecord.metric_name == metric
        )
        .order_by(EntsoeGridRecord.timestamp.desc())
        .limit(limit)
    )
    
    result = await db.execute(query)
    records = result.scalars().all()
    
    return {
        "bidding_zone": zone,
        "metric": metric,
        "count": len(records),
        "data": [
            {
                "timestamp": r.timestamp.isoformat(),
                "value": r.metric_value
            }
            for r in records
        ]
    }


@app.get("/api/v1/scheduler/status", tags=["System"])
async def scheduler_status():
    """
    Get status of background scheduler and scheduled jobs.
    
    Returns:
        Scheduler status and job information
    """
    if not scheduler:
        raise HTTPException(status_code=503, detail="Scheduler not initialized")
    
    jobs_info = []
    for job in scheduler.get_jobs():
        jobs_info.append({
            "id": job.id,
            "name": job.name,
            "next_run": job.next_run_time.isoformat() if job.next_run_time else None,
            "trigger": str(job.trigger)
        })
    
    return {
        "scheduler_running": scheduler.running,
        "active_jobs": len(jobs_info),
        "jobs": jobs_info
    }


if __name__ == "__main__":
    import uvicorn
    
    # Run development server
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,  # Auto-reload on code changes
        log_level="info"
    )
