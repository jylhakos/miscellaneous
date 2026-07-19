-- TimescaleDB Initialization Script for Energy Trading Platform

-- Create main grid consumption table
CREATE TABLE IF NOT EXISTS grid_consumption (
    timestamp TIMESTAMPTZ NOT NULL,
    region_id TEXT NOT NULL,
    actual_mw DOUBLE PRECISION,
    wind_speed_ms DOUBLE PRECISION,
    solar_irradiance DOUBLE PRECISION,
    clearing_price_eur DOUBLE PRECISION,
    CONSTRAINT grid_consumption_pkey PRIMARY KEY (timestamp, region_id)
);

-- Convert to hypertable for time-series optimization
SELECT create_hypertable('grid_consumption', 'timestamp', if_not_exists => TRUE);

-- Create index on region and timestamp for fast queries
CREATE INDEX IF NOT EXISTS idx_grid_consumption_region_time 
ON grid_consumption (region_id, timestamp DESC);

-- Create forecast predictions table
CREATE TABLE IF NOT EXISTS demand_forecasts (
    forecast_timestamp TIMESTAMPTZ NOT NULL,
    target_timestamp TIMESTAMPTZ NOT NULL,
    region_id TEXT NOT NULL,
    predicted_mw DOUBLE PRECISION,
    actual_mw DOUBLE PRECISION,
    error_mw DOUBLE PRECISION,
    CONSTRAINT demand_forecasts_pkey PRIMARY KEY (forecast_timestamp, target_timestamp, region_id)
);

-- Convert forecasts to hypertable
SELECT create_hypertable('demand_forecasts', 'forecast_timestamp', if_not_exists => TRUE);

-- Create trading signals table
CREATE TABLE IF NOT EXISTS trading_signals (
    signal_timestamp TIMESTAMPTZ NOT NULL,
    region_id TEXT NOT NULL,
    signal_type TEXT NOT NULL, -- 'BUY_LONG', 'SELL_SHORT', 'HOLD'
    imbalance_mw DOUBLE PRECISION,
    predicted_generation_mw DOUBLE PRECISION,
    committed_mw DOUBLE PRECISION,
    executed BOOLEAN DEFAULT FALSE,
    CONSTRAINT trading_signals_pkey PRIMARY KEY (signal_timestamp, region_id)
);

-- Convert trading signals to hypertable
SELECT create_hypertable('trading_signals', 'signal_timestamp', if_not_exists => TRUE);

-- Create materialized view for hourly aggregations
CREATE MATERIALIZED VIEW IF NOT EXISTS hourly_grid_stats AS
SELECT 
    time_bucket('1 hour', timestamp) AS hour,
    region_id,
    AVG(actual_mw) AS avg_mw,
    MAX(actual_mw) AS max_mw,
    MIN(actual_mw) AS min_mw,
    STDDEV(actual_mw) AS stddev_mw,
    AVG(wind_speed_ms) AS avg_wind_speed,
    AVG(solar_irradiance) AS avg_solar_irradiance
FROM grid_consumption
GROUP BY hour, region_id;

-- Create index on materialized view
CREATE INDEX IF NOT EXISTS idx_hourly_stats_hour_region 
ON hourly_grid_stats (hour DESC, region_id);

-- Create function to refresh materialized view
CREATE OR REPLACE FUNCTION refresh_hourly_stats()
RETURNS void AS $$
BEGIN
    REFRESH MATERIALIZED VIEW CONCURRENTLY hourly_grid_stats;
END;
$$ LANGUAGE plpgsql;

COMMIT;
