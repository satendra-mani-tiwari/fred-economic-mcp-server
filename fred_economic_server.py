#!/usr/bin/env python3

import asyncio
import json
import os
import sys
import traceback
from typing import Any, Dict
from datetime import datetime, timedelta

import httpx
from mcp.server import NotificationOptions, Server
from mcp.types import (
    CallToolRequest,
    CallToolResult,
    ListToolsRequest,
    ListToolsResult,
    Tool,
    TextContent,
)


class FredServer:
    """Enhanced FRED MCP Server with full historical data support"""

    def __init__(self):
        print("🏦 Starting Enhanced FRED Server...", file=sys.stderr)

        # Check API key
        self.api_key = os.getenv("FRED_API_KEY")
        if not self.api_key:
            print("❌ FRED_API_KEY not found!", file=sys.stderr)
            raise ValueError("FRED_API_KEY required")

        print(f"✅ API key: {self.api_key[:8]}...", file=sys.stderr)

        self.base_url = "https://api.stlouisfed.org/fred"
        self.server = Server("fred-server")

        # Set up handlers
        self._setup_handlers()
        print("✅ Handlers configured", file=sys.stderr)

    def _setup_handlers(self):
        """Setup MCP handlers"""

        @self.server.list_tools()
        async def list_tools() -> list[Tool]:
            """List available tools"""
            print("📋 Listing tools", file=sys.stderr)
            return [
                Tool(
                    name="get_fred_data",
                    description="Get FRED economic data by series ID with full historical support",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "series_id": {
                                "type": "string",
                                "description": "FRED series ID (e.g., GDP, UNRATE, FEDFUNDS)"
                            },
                            "limit": {
                                "type": "integer",
                                "description": "Number of observations (default: 50, max: 100000)",
                                "default": 50
                            },
                            "start_date": {
                                "type": "string",
                                "description": "Start date in YYYY-MM-DD format (optional)"
                            },
                            "end_date": {
                                "type": "string",
                                "description": "End date in YYYY-MM-DD format (optional)"
                            },
                            "frequency": {
                                "type": "string",
                                "description": "Data frequency: d, w, bw, m, q, sa, a (optional)",
                                "enum": ["d", "w", "bw", "m", "q", "sa", "a"]
                            },
                            "aggregation_method": {
                                "type": "string",
                                "description": "Aggregation method: avg, sum, eop (end of period)",
                                "enum": ["avg", "sum", "eop"]
                            }
                        },
                        "required": ["series_id"]
                    }
                ),
                Tool(
                    name="get_fred_historical",
                    description="Get extensive historical data for analysis (4+ years)",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "series_id": {
                                "type": "string",
                                "description": "FRED series ID"
                            },
                            "years": {
                                "type": "integer",
                                "description": "Number of years back (default: 4)",
                                "default": 4
                            },
                            "frequency": {
                                "type": "string",
                                "description": "q=quarterly, m=monthly, a=annual",
                                "default": "q"
                            }
                        },
                        "required": ["series_id"]
                    }
                ),
                Tool(
                    name="search_fred",
                    description="Search FRED database for series",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "Search query"
                            },
                            "limit": {
                                "type": "integer",
                                "description": "Number of results (default: 10)",
                                "default": 10
                            }
                        },
                        "required": ["query"]
                    }
                ),
                Tool(
                    name="fred_dashboard",
                    description="Get key economic indicators",
                    inputSchema={
                        "type": "object",
                        "properties": {}
                    }
                ),
                Tool(
                    name="get_multiple_series",
                    description="Get multiple FRED series at once for comparison",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "series_ids": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "List of FRED series IDs"
                            },
                            "start_date": {
                                "type": "string",
                                "description": "Start date in YYYY-MM-DD format"
                            },
                            "frequency": {
                                "type": "string",
                                "description": "Data frequency",
                                "default": "q"
                            }
                        },
                        "required": ["series_ids"]
                    }
                )
            ]

        @self.server.call_tool()
        async def call_tool(name: str, arguments: Dict[str, Any]) -> list[TextContent]:
            """Handle tool calls"""
            print(f"🔧 Tool: {name}", file=sys.stderr)

            try:
                if name == "get_fred_data":
                    result = await self._get_fred_data(arguments)
                elif name == "get_fred_historical":
                    result = await self._get_fred_historical(arguments)
                elif name == "search_fred":
                    result = await self._search_fred(arguments)
                elif name == "fred_dashboard":
                    result = await self._fred_dashboard(arguments)
                elif name == "get_multiple_series":
                    result = await self._get_multiple_series(arguments)
                else:
                    result = f"Unknown tool: {name}"

                return [TextContent(type="text", text=result)]

            except Exception as e:
                error_msg = f"Error in {name}: {str(e)}"
                print(f"❌ {error_msg}", file=sys.stderr)
                traceback.print_exc(file=sys.stderr)
                return [TextContent(type="text", text=error_msg)]

    async def _make_request(self, endpoint: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Make FRED API request"""
        params.update({
            'api_key': self.api_key,
            'file_type': 'json'
        })

        url = f"{self.base_url}/{endpoint}"

        print(f"🌐 API call: {endpoint} with params: {params}", file=sys.stderr)

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(url, params=params)

                if response.status_code != 200:
                    raise Exception(f"API error: {response.status_code} - {response.text}")

                data = response.json()

                if 'error_code' in data:
                    raise Exception(f"FRED error: {data.get('error_message')}")

                return data

        except Exception as e:
            raise Exception(f"Request failed: {str(e)}")

    async def _get_fred_data(self, args: Dict[str, Any]) -> str:
        """Get FRED series data with full historical support"""
        series_id = args.get("series_id", "").upper()
        limit = min(args.get("limit", 50), 100000)  # Allow up to 100k observations
        start_date = args.get("start_date")
        end_date = args.get("end_date")
        frequency = args.get("frequency")
        aggregation_method = args.get("aggregation_method")

        if not series_id:
            return "Error: series_id required"

        try:
            # Build parameters
            params = {
                "series_id": series_id,
                "limit": limit,
                "sort_order": "desc"  # Most recent first
            }

            # Add optional parameters
            if start_date:
                params["observation_start"] = start_date
            if end_date:
                params["observation_end"] = end_date
            if frequency:
                params["frequency"] = frequency
            if aggregation_method:
                params["aggregation_method"] = aggregation_method

            # Get data
            data = await self._make_request("series/observations", params)
            observations = data.get("observations", [])

            # Get series info
            info = await self._make_request("series", {"series_id": series_id})
            series_info = info.get("seriess", [{}])[0]

            # Filter out invalid values (FRED uses "." for missing data)
            valid_observations = [
                obs for obs in observations
                if obs.get("value") and obs.get("value") != "."
            ]

            result = {
                "series_id": series_id,
                "title": series_info.get("title", "Unknown"),
                "units": series_info.get("units", ""),
                "frequency": series_info.get("frequency", ""),
                "total_observations": len(valid_observations),
                "date_range": {
                    "start": valid_observations[-1]["date"] if valid_observations else None,
                    "end": valid_observations[0]["date"] if valid_observations else None
                },
                "latest_value": valid_observations[0] if valid_observations else None,
                "all_data": valid_observations  # Return ALL data, not just recent
            }

            print(f"✅ Got {len(valid_observations)} valid points for {series_id}", file=sys.stderr)
            return json.dumps(result, indent=2)

        except Exception as e:
            error_msg = f"Error getting {series_id}: {str(e)}"
            print(f"❌ {error_msg}", file=sys.stderr)
            return error_msg

    async def _get_fred_historical(self, args: Dict[str, Any]) -> str:
        """Get extensive historical data optimized for analysis"""
        series_id = args.get("series_id", "").upper()
        years = args.get("years", 4)
        frequency = args.get("frequency", "q")

        if not series_id:
            return "Error: series_id required"

        # Calculate start date
        end_date = datetime.now()
        start_date = end_date - timedelta(days=years * 365)

        start_date_str = start_date.strftime("%Y-%m-%d")
        end_date_str = end_date.strftime("%Y-%m-%d")

        try:
            params = {
                "series_id": series_id,
                "observation_start": start_date_str,
                "observation_end": end_date_str,
                "frequency": frequency,
                "aggregation_method": "avg",
                "limit": 100000  # Get all available data
            }

            # Get data
            data = await self._make_request("series/observations", params)
            observations = data.get("observations", [])

            # Get series info
            info = await self._make_request("series", {"series_id": series_id})
            series_info = info.get("seriess", [{}])[0]

            # Filter and sort data
            valid_observations = [
                obs for obs in observations
                if obs.get("value") and obs.get("value") != "."
            ]

            # Sort chronologically (oldest first)
            valid_observations.sort(key=lambda x: x["date"])

            result = {
                "series_id": series_id,
                "title": series_info.get("title", "Unknown"),
                "units": series_info.get("units", ""),
                "frequency": frequency.upper(),
                "years_requested": years,
                "total_points": len(valid_observations),
                "date_range": {
                    "start": valid_observations[0]["date"] if valid_observations else None,
                    "end": valid_observations[-1]["date"] if valid_observations else None
                },
                "historical_data": valid_observations
            }

            print(f"✅ Historical: {len(valid_observations)} points for {series_id} ({years} years)", file=sys.stderr)
            return json.dumps(result, indent=2)

        except Exception as e:
            error_msg = f"Error getting historical {series_id}: {str(e)}"
            print(f"❌ {error_msg}", file=sys.stderr)
            return error_msg

    async def _get_multiple_series(self, args: Dict[str, Any]) -> str:
        """Get multiple series for comparison"""
        series_ids = args.get("series_ids", [])
        start_date = args.get("start_date")
        frequency = args.get("frequency", "q")

        if not series_ids:
            return "Error: series_ids required"

        results = {}

        for series_id in series_ids:
            try:
                series_args = {
                    "series_id": series_id,
                    "frequency": frequency
                }
                if start_date:
                    series_args["start_date"] = start_date

                # Use the historical method for each series
                result_str = await self._get_fred_historical(series_args)
                result_data = json.loads(result_str)
                results[series_id] = result_data

            except Exception as e:
                results[series_id] = {"error": str(e)}

        combined_result = {
            "requested_series": series_ids,
            "frequency": frequency,
            "start_date": start_date,
            "series_data": results
        }

        print(f"✅ Multiple series: {len(series_ids)} series retrieved", file=sys.stderr)
        return json.dumps(combined_result, indent=2)

    async def _search_fred(self, args: Dict[str, Any]) -> str:
        """Search FRED series"""
        query = args.get("query", "")
        limit = args.get("limit", 10)

        if not query:
            return "Error: query required"

        try:
            data = await self._make_request(
                "series/search",
                {"search_text": query, "limit": limit, "order_by": "popularity"}
            )

            series = data.get("seriess", [])

            results = []
            for s in series:
                results.append({
                    "id": s.get("id"),
                    "title": s.get("title"),
                    "units": s.get("units"),
                    "frequency": s.get("frequency"),
                    "observation_start": s.get("observation_start"),
                    "observation_end": s.get("observation_end")
                })

            result = {
                "query": query,
                "found": len(series),
                "results": results
            }

            print(f"✅ Found {len(series)} series for '{query}'", file=sys.stderr)
            return json.dumps(result, indent=2)

        except Exception as e:
            return f"Search error: {str(e)}"

    async def _fred_dashboard(self, args: Dict[str, Any]) -> str:
        """Get economic dashboard"""
        indicators = {
            "GDP": "Gross Domestic Product",
            "UNRATE": "Unemployment Rate",
            "FEDFUNDS": "Fed Funds Rate",
            "CPIAUCSL": "Inflation (CPI)",
            "DGS10": "10-Year Treasury",
            "DTWEXBGS": "USD Index",
            "SP500": "S&P 500"
        }

        results = {}

        for series_id, name in indicators.items():
            try:
                data = await self._make_request(
                    "series/observations",
                    {"series_id": series_id, "limit": 1, "sort_order": "desc"}
                )

                obs = data.get("observations", [])
                latest = obs[0] if obs else {"date": "N/A", "value": "N/A"}

                results[series_id] = {
                    "name": name,
                    "date": latest.get("date"),
                    "value": latest.get("value")
                }

            except Exception as e:
                results[series_id] = {"name": name, "error": str(e)}

        print(f"✅ Dashboard: {len(results)} indicators", file=sys.stderr)
        return json.dumps({"dashboard": results}, indent=2)

    async def run(self):
        """Run the server"""
        print("🚀 Starting enhanced server...", file=sys.stderr)

        # Test connection
        try:
            print("🔍 Testing FRED API...", file=sys.stderr)
            await self._make_request("series", {"series_id": "GDP", "limit": 1})
            print("✅ FRED API works", file=sys.stderr)
        except Exception as e:
            print(f"⚠️ FRED test failed: {e}", file=sys.stderr)

        from mcp.server.stdio import stdio_server

        try:
            async with stdio_server() as (read_stream, write_stream):
                print("📡 Enhanced server ready with full historical data support", file=sys.stderr)
                await self.server.run(
                    read_stream,
                    write_stream,
                    self.server.create_initialization_options()
                )
        except Exception as e:
            print(f"💥 Server error: {str(e)}", file=sys.stderr)
            traceback.print_exc(file=sys.stderr)
            raise


def main():
    """Entry point"""
    try:
        print("🏦 Enhanced FRED MCP Server v2.0", file=sys.stderr)

        if not os.getenv("FRED_API_KEY"):
            print("❌ Set FRED_API_KEY environment variable", file=sys.stderr)
            print("Get free key at: https://fred.stlouisfed.org/docs/api/api_key.html", file=sys.stderr)
            sys.exit(1)

        server = FredServer()
        asyncio.run(server.run())

    except KeyboardInterrupt:
        print("👋 Stopped", file=sys.stderr)
    except Exception as e:
        print(f"💥 Fatal: {str(e)}", file=sys.stderr)
        traceback.print_exc(file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()