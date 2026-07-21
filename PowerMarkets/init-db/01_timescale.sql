-- ==============================================================================
-- TimescaleDB Initialization Script
-- ==============================================================================
-- Creates TimescaleDB extension and converts tables to hypertables
-- for optimized time-series data storage and querying
-- ==============================================================================

-- 1. Enable TimescaleDB extension
CREATE EXTENSION IF NOT EXISTS timescaledb CASCADE;

-- 2. Create Nord Pool intraday prices table
CREATE TABLE IF NOT EXISTS intraday_prices (
    id VARCHAR(100) NOT NULL PRIMARY KEY,
    start_time TIMESTAMP WITHOUT TIME ZONE NOT NULL,
    end_time TIMESTAMP WITHOUT TIME ZONE NOT NULL,
    area VARCHAR(10) NOT NULL,
    price_eur DOUBLE PRECISION NOT NULL,
    fetched_at TIMESTAMP WITHOUT TIME ZONE DEFAULT (NOW() AT TIME ZONE 'UTC')
);

-- 3. Convert to TimescaleDB Hypertable (partitioned by 7-day chunks)
SELECT create_hypertable(
    'intraday_prices', 
    'start_time', 
    chunk_time_interval => INTERVAL '7 days', 
    if_not_exists => TRUE
);

-- 4. Create optimized composite indexes
CREATE INDEX IF NOT EXISTS idx_area_start_time 
    ON intraday_prices (area, start_time DESC);

CREATE INDEX IF NOT EXISTS idx_start_time_only 
    ON intraday_prices (start_time DESC);

-- 5. Create unique constraint for preventing duplicates
ALTER TABLE intraday_prices 
    ADD CONSTRAINT _start_time_area_uc 
    UNIQUE (start_time, area);

-- 6. Create ENTSO-E grid data table
CREATE TABLE IF NOT EXISTS entsoe_grid_data (
    id VARCHAR(120) NOT NULL PRIMARY KEY,
    timestamp TIMESTAMP WITHOUT TIME ZONE NOT NULL,
    bidding_zone VARCHAR(10) NOT NULL,
    metric_name VARCHAR(30) NOT NULL,
    metric_value DOUBLE PRECISION NOT NULL,
    fetched_at TIMESTAMP WITHOUT TIME ZONE DEFAULT (NOW() AT TIME ZONE 'UTC')
);

-- 7. Convert ENTSO-E table to hypertable
SELECT create_hypertable(
    'entsoe_grid_data', 
    'timestamp', 
    chunk_time_interval => INTERVAL '7 days', 
    if_not_exists => TRUE
);

-- 8. Create specialized indexes for ENTSO-E queries
CREATE INDEX IF NOT EXISTS idx_entsoe_lookup 
    ON entsoe_grid_data (bidding_zone, metric_name, timestamp DESC);

CREATE INDEX IF NOT EXISTS idx_entsoe_timestamp 
    ON entsoe_grid_data (timestamp DESC);

-- 9. Create unique constraint for ENTSO-E data
ALTER TABLE entsoe_grid_data 
    ADD CONSTRAINT _entsoe_metric_uc 
    UNIQUE (timestamp, bidding_zone, metric_name);

-- 10. Create retention policy (optional: auto-delete data older than 90 days)
-- Uncomment the following lines to enable automatic data retention:
-- SELECT add_retention_policy('intraday_prices', INTERVAL '90 days');
-- SELECT add_retention_policy('entsoe_grid_data', INTERVAL '90 days');

-- 11. Grant permissions
GRANT ALL PRIVILEGES ON TABLE intraday_prices TO trader_admin;
GRANT ALL PRIVILEGES ON TABLE entsoe_grid_data TO trader_admin;

-- Success message
DO $$
BEGIN
    RAISE NOTICE 'TimescaleDB initialization completed successfully';
    RAISE NOTICE 'Created hypertables: intraday_prices, entsoe_grid_data';
    RAISE NOTICE 'Chunk interval: 7 days';
END $$;
