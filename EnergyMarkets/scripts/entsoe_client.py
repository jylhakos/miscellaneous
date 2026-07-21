"""
ENTSO-E Data Collection Script
-------------------------------
Fetches historical and real-time data from ENTSO-E Transparency Platform.
Supports load, generation, prices, and cross-border flow data.

Usage:
    python entsoe_client.py --zone FI --start 2026-01-01 --end 2026-01-31
"""

import os
import sys
import argparse
import pandas as pd
from datetime import datetime, timedelta
from entsoe import EntsoePandasClient

class EntsoeDataCollector:
    """
    Collects and processes data from ENTSO-E Transparency Platform.
    Handles multiple bidding zones and metric types.
    """
    
    def __init__(self, api_key: str = None):
        """
        Initialize ENTSO-E client.
        
        Args:
            api_key: ENTSO-E API token (if None, reads from environment)
        """
        self.api_key = api_key or os.getenv("ENTSOE_API_KEY")
        
        if not self.api_key:
            raise ValueError(
                "ENTSO-E API key not found. Set ENTSOE_API_KEY environment variable "
                "or pass api_key parameter. Request a token from: "
                "transparency@entsoe.eu"
            )
        
        self.client = EntsoePandasClient(api_key=self.api_key)
        print(f"✓ ENTSO-E client initialized successfully")

    def fetch_load_data(self, country_code: str, start: pd.Timestamp, end: pd.Timestamp) -> pd.DataFrame:
        """
        Fetch actual load (electricity demand) data.
        
        Args:
            country_code: Bidding zone code (e.g., 'FI', 'SE', 'NO')
            start: Start timestamp (UTC)
            end: End timestamp (UTC)
            
        Returns:
            DataFrame with timestamp index and load values
        """
        try:
            print(f"Fetching load data for {country_code} from {start} to {end}...")
            df = self.client.query_load(country_code, start=start, end=end)
            
            if isinstance(df, pd.Series):
                df = df.to_frame(name='actual_load_mw')
            
            print(f"✓ Retrieved {len(df)} load records")
            return df
            
        except Exception as e:
            print(f"✗ Error fetching load data: {str(e)}")
            return pd.DataFrame()

    def fetch_day_ahead_prices(self, country_code: str, start: pd.Timestamp, end: pd.Timestamp) -> pd.DataFrame:
        """
        Fetch day-ahead market prices.
        
        Args:
            country_code: Bidding zone code
            start: Start timestamp (UTC)
            end: End timestamp (UTC)
            
        Returns:
            DataFrame with timestamp index and price values
        """
        try:
            print(f"Fetching day-ahead prices for {country_code}...")
            df = self.client.query_day_ahead_prices(country_code, start=start, end=end)
            
            if isinstance(df, pd.Series):
                df = df.to_frame(name='day_ahead_price_eur_mwh')
            
            print(f"✓ Retrieved {len(df)} price records")
            return df
            
        except Exception as e:
            print(f"✗ Error fetching day-ahead prices: {str(e)}")
            return pd.DataFrame()

    def fetch_generation_data(self, country_code: str, start: pd.Timestamp, end: pd.Timestamp) -> pd.DataFrame:
        """
        Fetch actual generation by production type.
        
        Args:
            country_code: Bidding zone code
            start: Start timestamp (UTC)
            end: End timestamp (UTC)
            
        Returns:
            DataFrame with generation by fuel type
        """
        try:
            print(f"Fetching generation data for {country_code}...")
            df = self.client.query_generation(country_code, start=start, end=end)
            print(f"✓ Retrieved generation data with {len(df.columns)} production types")
            return df
            
        except Exception as e:
            print(f"✗ Error fetching generation data: {str(e)}")
            return pd.DataFrame()

    def fetch_cross_border_flows(self, country_from: str, country_to: str, 
                                  start: pd.Timestamp, end: pd.Timestamp) -> pd.DataFrame:
        """
        Fetch physical cross-border electricity flows.
        
        Args:
            country_from: Source bidding zone
            country_to: Destination bidding zone
            start: Start timestamp (UTC)
            end: End timestamp (UTC)
            
        Returns:
            DataFrame with flow data
        """
        try:
            print(f"Fetching cross-border flows {country_from} -> {country_to}...")
            df = self.client.query_crossborder_flows(country_from, country_to, start=start, end=end)
            
            if isinstance(df, pd.Series):
                df = df.to_frame(name='flow_mw')
            
            print(f"✓ Retrieved {len(df)} flow records")
            return df
            
        except Exception as e:
            print(f"✗ Error fetching cross-border flows: {str(e)}")
            return pd.DataFrame()

    def save_to_csv(self, df: pd.DataFrame, filename: str, output_dir: str = "data"):
        """
        Save DataFrame to CSV file.
        
        Args:
            df: DataFrame to save
            filename: Output filename
            output_dir: Output directory path
        """
        if df.empty:
            print(f"⚠ Skipping empty DataFrame for {filename}")
            return
        
        os.makedirs(output_dir, exist_ok=True)
        filepath = os.path.join(output_dir, filename)
        df.to_csv(filepath)
        print(f"✓ Saved to {filepath} ({len(df)} records)")


def main():
    """Command-line interface for ENTSO-E data collection."""
    parser = argparse.ArgumentParser(
        description="Fetch data from ENTSO-E Transparency Platform",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Fetch Finnish load data for January 2026
  python entsoe_client.py --zone FI --start 2026-01-01 --end 2026-01-31 --metrics load

  # Fetch multiple metrics for Sweden
  python entsoe_client.py --zone SE --start 2026-01-01 --end 2026-01-07 --metrics load,prices,generation

  # Fetch cross-border flows
  python entsoe_client.py --flow SE FI --start 2026-01-01 --end 2026-01-31
        """
    )
    
    parser.add_argument('--zone', type=str, help='Bidding zone code (e.g., FI, SE, NO, DK)')
    parser.add_argument('--start', type=str, required=True, help='Start date (YYYY-MM-DD)')
    parser.add_argument('--end', type=str, required=True, help='End date (YYYY-MM-DD)')
    parser.add_argument('--metrics', type=str, default='load,prices', 
                        help='Comma-separated metrics: load,prices,generation')
    parser.add_argument('--flow', nargs=2, metavar=('FROM', 'TO'), 
                        help='Fetch cross-border flow between two zones')
    parser.add_argument('--output', type=str, default='data', 
                        help='Output directory for CSV files')
    
    args = parser.parse_args()
    
    # Parse dates
    try:
        start = pd.Timestamp(args.start, tz='UTC')
        end = pd.Timestamp(args.end, tz='UTC')
    except Exception as e:
        print(f"Error parsing dates: {e}")
        sys.exit(1)
    
    # Initialize collector
    try:
        collector = EntsoeDataCollector()
    except ValueError as e:
        print(f"Error: {e}")
        sys.exit(1)
    
    # Fetch cross-border flows if specified
    if args.flow:
        country_from, country_to = args.flow
        df = collector.fetch_cross_border_flows(country_from, country_to, start, end)
        collector.save_to_csv(df, f"flows_{country_from}_{country_to}_{args.start}.csv", args.output)
        return
    
    # Validate zone
    if not args.zone:
        print("Error: --zone is required (unless using --flow)")
        sys.exit(1)
    
    # Fetch requested metrics
    metrics = [m.strip().lower() for m in args.metrics.split(',')]
    
    if 'load' in metrics:
        df = collector.fetch_load_data(args.zone, start, end)
        collector.save_to_csv(df, f"load_{args.zone}_{args.start}.csv", args.output)
    
    if 'prices' in metrics:
        df = collector.fetch_day_ahead_prices(args.zone, start, end)
        collector.save_to_csv(df, f"prices_{args.zone}_{args.start}.csv", args.output)
    
    if 'generation' in metrics:
        df = collector.fetch_generation_data(args.zone, start, end)
        collector.save_to_csv(df, f"generation_{args.zone}_{args.start}.csv", args.output)
    
    print("\n✓ Data collection completed successfully")


if __name__ == "__main__":
    main()
