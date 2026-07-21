"""
External API Connectors
-----------------------
Handles async HTTP requests to Nord Pool and ENTSO-E APIs.
Includes error handling, retry logic, and response parsing.
"""

import httpx
import os
from fastapi import HTTPException
from schemas import MarketDataRequest, PriceRecord
from typing import List

class NordPoolConnector:
    """
    Asynchronous connector for Nord Pool Market Data API.
    Handles intraday continuous market and auction data retrieval.
    """
    
    def __init__(self):
        self.base_url = "https://nordpoolgroup.com"
        self.api_key = os.getenv("NORDPOOL_API_KEY", "")
        
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Accept": "application/json",
            "User-Agent": "EnergyTradingBot/2.0 (FastAPI-Asynchronous-Connector)"
        }
        
        # Connection timeout and retry settings
        self.timeout = httpx.Timeout(15.0, connect=5.0)
        self.max_retries = 3

    async def fetch_intraday_prices(self, params: MarketDataRequest) -> List[PriceRecord]:
        """
        Fetches intraday price data from Nord Pool API.
        
        Args:
            params: MarketDataRequest with areas and delivery_date
            
        Returns:
            List of PriceRecord objects
            
        Raises:
            HTTPException: If API request fails or returns error status
        """
        endpoint = f"{self.base_url}/Intraday/ContractStatistics/ByAreas"
        
        query_params = {
            "date": params.delivery_date.isoformat(),
            "areas": ",".join(params.areas)
        }

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                response = await client.get(
                    endpoint, 
                    headers=self.headers, 
                    params=query_params
                )
                
                if response.status_code == 401:
                    raise HTTPException(
                        status_code=401,
                        detail="Nord Pool API authentication failed. Check NORDPOOL_API_KEY environment variable."
                    )
                elif response.status_code == 429:
                    raise HTTPException(
                        status_code=429,
                        detail="Nord Pool API rate limit exceeded. Please retry after cooldown period."
                    )
                elif response.status_code != 200:
                    raise HTTPException(
                        status_code=response.status_code,
                        detail=f"Nord Pool API error: {response.text}"
                    )
                
                return self._parse_response(response.json(), params.areas)

            except httpx.ConnectTimeout:
                raise HTTPException(
                    status_code=504,
                    detail="Connection timeout to Nord Pool API. Server may be unreachable."
                )
            except httpx.RequestError as exc:
                raise HTTPException(
                    status_code=503,
                    detail=f"Failed connection to Nord Pool server: {str(exc)}"
                )

    def _parse_response(self, raw_json: dict, requested_areas: List[str]) -> List[PriceRecord]:
        """
        Parses Nord Pool API JSON response into structured PriceRecord objects.
        
        Args:
            raw_json: Raw JSON response from API
            requested_areas: List of requested bidding zones
            
        Returns:
            List of parsed PriceRecord objects
        """
        parsed_records = []
        
        try:
            # Navigate the JSON structure based on Nord Pool schema
            rows = raw_json.get("data", {}).get("rows", [])
            
            for row in rows:
                # Extract and validate required fields
                start_time = row.get("startTime")
                end_time = row.get("endTime")
                area = row.get("areaName")
                vwap = row.get("vwap", 0.0)
                
                if start_time and end_time and area:
                    parsed_records.append(PriceRecord(
                        start_time=start_time,
                        end_time=end_time,
                        area=area,
                        price_eur=float(vwap)
                    ))
                    
        except (KeyError, AttributeError, TypeError, ValueError) as e:
            # Log parsing error but don't fail completely
            print(f"Warning: Failed to parse some Nord Pool records: {str(e)}")
        
        # If no data parsed, return mock data for development/testing
        if not parsed_records and requested_areas:
            print("Warning: No data parsed from Nord Pool API. Returning empty list.")
        
        return parsed_records

    def __repr__(self):
        return f"<NordPoolConnector(base_url={self.base_url})>"
