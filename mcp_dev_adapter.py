#!/usr/bin/env python3
"""
MCP Dev Adapter - Makes FastMCP 2 work with `mcp dev`

This adapter wraps our FastMCP server to make it compatible with 
the official MCP development inspector (`mcp dev`).
"""

import sys
import os

# Add the project root to Python path
project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Import the official MCP SDK components that mcp dev expects
from mcp.server.fastmcp.server import FastMCP as MCPFastMCP
from mcp.server.fastmcp import Context
from mcp.types import Tool

# Import our actual FastMCP server
from src.main import mcp as fastmcp_server

class FastMCPAdapter(MCPFastMCP):
    """
    Adapter that wraps our FastMCP 2 server to make it compatible
    with the official MCP development tools.
    """
    
    def __init__(self, fastmcp_instance):
        # Initialize the official FastMCP with basic info
        super().__init__(name="invest-pilot")
        self._fastmcp = fastmcp_instance
        
        # Copy tools from our FastMCP instance
        self._copy_tools()
    
    def _copy_tools(self):
        """Copy tools from our FastMCP instance to the official one."""
        # This is a simplified approach - in practice, FastMCP 2 and 
        # official MCP SDK might need more complex bridging
        
        # For now, let's recreate the tools manually to ensure compatibility
        self._register_tools()
    
    def _register_tools(self):
        """Register all our tools with the official MCP SDK format."""
        # Import the actual tool handlers and client function
        from src.main import get_alpaca_client
        from src.brokers.alpaca.tools.account import handle_get_account_info, handle_get_positions
        from src.brokers.alpaca.tools.market_data import handle_get_stock_quote, handle_get_stock_bars, handle_ping
        from src.brokers.alpaca.tools.orders import (
            handle_get_orders, handle_place_market_order, handle_place_limit_order,
            handle_cancel_all_orders, handle_close_all_positions, handle_take_partial_profit
        )
        
        @self.tool()
        async def ping(ctx: Context) -> str:
            """Test if the server is responding."""
            try:
                client = get_alpaca_client()
                result = await handle_ping(client, {})
                return result[0].text
            except Exception as e:
                return f"Ping failed: {e}"
        
        @self.tool()
        async def get_account_info(ctx: Context) -> str:
            """Get the current account information including balances and status."""
            try:
                client = get_alpaca_client()
                result = await handle_get_account_info(client, {})
                return result[0].text
            except Exception as e:
                return f"Failed to get account info: {e}"
        
        @self.tool()
        async def get_positions(ctx: Context) -> str:
            """Get all current positions in the portfolio."""
            try:
                client = get_alpaca_client()
                result = await handle_get_positions(client, {})
                return result[0].text
            except Exception as e:
                return f"Failed to get positions: {e}"
        
        @self.tool()
        async def get_stock_quote(symbol: str, ctx: Context) -> str:
            """Get the latest quote for a stock."""
            try:
                client = get_alpaca_client()
                result = await handle_get_stock_quote(client, {"symbol": symbol})
                return result[0].text
            except Exception as e:
                return f"Failed to get quote for {symbol}: {e}"
        
        @self.tool()
        async def get_stock_bars(symbol: str, ctx: Context, days: int = 5) -> str:
            """Get historical price bars for a stock."""
            try:
                client = get_alpaca_client()
                result = await handle_get_stock_bars(client, {"symbol": symbol, "days": days})
                return result[0].text
            except Exception as e:
                return f"Failed to get bars for {symbol}: {e}"
        
        @self.tool()
        async def get_orders(ctx: Context, status: str = "all", limit: int = 10) -> str:
            """Get orders with the specified status."""
            try:
                client = get_alpaca_client()
                result = await handle_get_orders(client, {"status": status, "limit": limit})
                return result[0].text
            except Exception as e:
                return f"Failed to get orders: {e}"
        
        @self.tool()
        async def place_market_order(symbol: str, side: str, quantity: float, ctx: Context) -> str:
            """Place a market order."""
            try:
                client = get_alpaca_client()
                result = await handle_place_market_order(client, {
                    "symbol": symbol, "side": side, "quantity": quantity
                })
                return result[0].text
            except Exception as e:
                return f"Failed to place market order: {e}"
        
        @self.tool()
        async def place_limit_order(symbol: str, side: str, quantity: float, limit_price: float, ctx: Context) -> str:
            """Place a limit order."""
            try:
                client = get_alpaca_client()
                result = await handle_place_limit_order(client, {
                    "symbol": symbol, "side": side, "quantity": quantity, "limit_price": limit_price
                })
                return result[0].text
            except Exception as e:
                return f"Failed to place limit order: {e}"
        
        @self.tool()
        async def cancel_all_orders(ctx: Context) -> str:
            """Cancel all open orders."""
            try:
                client = get_alpaca_client()
                result = await handle_cancel_all_orders(client, {})
                return result[0].text
            except Exception as e:
                return f"Failed to cancel orders: {e}"
        
        @self.tool()
        async def close_all_positions(ctx: Context, cancel_orders: bool = True) -> str:
            """Close all open positions."""
            try:
                client = get_alpaca_client()
                result = await handle_close_all_positions(client, {"cancel_orders": cancel_orders})
                return result[0].text
            except Exception as e:
                return f"Failed to close positions: {e}"
        
        @self.tool()
        async def take_partial_profit(symbol: str, ctx: Context, profit_threshold: float = 0.2, close_percentage: float = 0.5) -> str:
            """Take partial profit if the position's unrealized profit percent is greater than the threshold."""
            try:
                client = get_alpaca_client()
                result = await handle_take_partial_profit(client, {
                    "symbol": symbol, "profit_threshold": profit_threshold, "close_percentage": close_percentage
                })
                return result[0].text
            except Exception as e:
                return f"Failed to take partial profit for {symbol}: {e}"

# Create the adapter instance that mcp dev will find
mcp = FastMCPAdapter(fastmcp_server)

# Also make it available as 'server' and 'app' (alternative names mcp dev looks for)
server = mcp
app = mcp

if __name__ == "__main__":
    # When run directly, start the adapted server
    print("Starting FastMCP 2 server via MCP Dev Adapter...")
    mcp.run() 