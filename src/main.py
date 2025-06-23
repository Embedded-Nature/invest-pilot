"""
Invest-Pilot MCP Server - FastMCP v2

A Model Context Protocol (MCP) server providing trading capabilities with Alpaca.
Uses the existing modular tool architecture for clean separation of concerns.
"""

from typing import Optional
from fastmcp import FastMCP, Context

# Core modules
import sys
import os

# Add the project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from src.brokers.alpaca.client import AlpacaClient
from src.config.settings import load_alpaca_config, load_server_config
from src.core.exceptions import InvalidConfigurationError, BrokerConnectionError, APIError
from src.core.logging_config import setup_logging

# Import existing tool handlers
from src.brokers.alpaca.tools.account import handle_get_account_info, handle_get_positions
from src.brokers.alpaca.tools.market_data import handle_get_stock_quote, handle_get_stock_bars, handle_ping
from src.brokers.alpaca.tools.orders import (
    handle_get_orders, handle_place_market_order, handle_place_limit_order,
    handle_cancel_all_orders, handle_close_all_positions, handle_take_partial_profit,
    # Advanced orders
    handle_place_bracket_order, handle_place_oco_order, handle_place_oto_order,
    handle_place_trailing_stop_order
)

# Initialize FastMCP server
mcp = FastMCP(
    name="invest-pilot",
    dependencies=["alpaca-py", "python-dotenv", "pydantic"]
)

# Global client - initialized lazily
_alpaca_client: Optional[AlpacaClient] = None
_logger = None

def get_alpaca_client() -> AlpacaClient:
    """Get or initialize the Alpaca client."""
    global _alpaca_client, _logger
    if _alpaca_client is None:
        try:
            # Load configuration
            server_config = load_server_config()
            alpaca_config = load_alpaca_config()
            
            # Setup logging if not already done
            if _logger is None:
                _logger = setup_logging(level=server_config.log_level, logger_name="invest-pilot")
            
            # Initialize Alpaca client
            _alpaca_client = AlpacaClient(alpaca_config)
            _logger.info("Alpaca client initialized")
        except Exception as e:
            if _logger:
                _logger.error(f"Failed to initialize client: {e}")
            raise
    return _alpaca_client

# ==============================================================================
# Health & Status Tools
# ==============================================================================

@mcp.tool()
async def ping(*, ctx: Context) -> str:
    """Test if the server is responding."""
    await ctx.info("Pinging server...")
    try:
        client = get_alpaca_client()
        result = await handle_ping(client, {})
        return result[0].text
    except Exception as e:
        await ctx.error(f"Ping failed: {e}")
        raise

# ==============================================================================
# Account Tools
# ==============================================================================

@mcp.tool()
async def get_account_info(*, ctx: Context) -> str:
    """Get the current account information including balances and status."""
    await ctx.info("Fetching account information...")
    try:
        client = get_alpaca_client()
        result = await handle_get_account_info(client, {})
        return result[0].text
    except Exception as e:
        await ctx.error(f"Failed to get account info: {e}")
        raise

@mcp.tool()
async def get_positions(*, ctx: Context) -> str:
    """Get all current positions in the portfolio."""
    await ctx.info("Fetching current positions...")
    try:
        client = get_alpaca_client()
        result = await handle_get_positions(client, {})
        return result[0].text
    except Exception as e:
        await ctx.error(f"Failed to get positions: {e}")
        raise

# ==============================================================================
# Market Data Tools
# ==============================================================================

@mcp.tool()
async def get_stock_quote(symbol: str, *, ctx: Context) -> str:
    """
    Get the latest quote for a stock.
    
    Args:
        symbol: Stock ticker symbol (e.g., AAPL, MSFT)
    """
    await ctx.info(f"Fetching quote for {symbol}...")
    try:
        client = get_alpaca_client()
        result = await handle_get_stock_quote(client, {"symbol": symbol})
        return result[0].text
    except Exception as e:
        await ctx.error(f"Failed to get quote for {symbol}: {e}")
        raise

@mcp.tool()
async def get_stock_bars(symbol: str, days: int = 5, *, ctx: Context) -> str:
    """
    Get historical price bars for a stock.
    
    Args:
        symbol: Stock ticker symbol (e.g., AAPL, MSFT)
        days: Number of trading days to look back (default: 5)
    """
    await ctx.info(f"Fetching {days} days of bars for {symbol}...")
    try:
        client = get_alpaca_client()
        result = await handle_get_stock_bars(client, {"symbol": symbol, "days": days})
        return result[0].text
    except Exception as e:
        await ctx.error(f"Failed to get bars for {symbol}: {e}")
        raise

# ==============================================================================
# Order Tools
# ==============================================================================

@mcp.tool()
async def get_orders(status: str = "all", limit: int = 10, *, ctx: Context) -> str:
    """
    Get orders with the specified status.
    
    Args:
        status: Order status to filter by (open, closed, all)
        limit: Maximum number of orders to return (default: 10)
    """
    await ctx.info(f"Fetching {status} orders (limit: {limit})...")
    try:
        client = get_alpaca_client()
        result = await handle_get_orders(client, {"status": status, "limit": limit})
        return result[0].text
    except Exception as e:
        await ctx.error(f"Failed to get orders: {e}")
        raise

@mcp.tool()
async def place_market_order(symbol: str, side: str, quantity: float, *, ctx: Context) -> str:
    """
    Place a market order.
    
    Args:
        symbol: Stock ticker symbol (e.g., AAPL, MSFT)
        side: Order side (buy or sell)
        quantity: Number of shares to buy or sell
    """
    await ctx.info(f"Placing market {side} order for {quantity} shares of {symbol}...")
    try:
        client = get_alpaca_client()
        result = await handle_place_market_order(client, {
            "symbol": symbol, "side": side, "quantity": quantity
        })
        return result[0].text
    except Exception as e:
        await ctx.error(f"Failed to place market order: {e}")
        raise

@mcp.tool()
async def place_limit_order(symbol: str, side: str, quantity: float, limit_price: float, *, ctx: Context) -> str:
    """
    Place a limit order.
    
    Args:
        symbol: Stock ticker symbol (e.g., AAPL, MSFT)
        side: Order side (buy or sell)
        quantity: Number of shares to buy or sell
        limit_price: Limit price for the order
    """
    await ctx.info(f"Placing limit {side} order for {quantity} shares of {symbol} at ${limit_price}...")
    try:
        client = get_alpaca_client()
        result = await handle_place_limit_order(client, {
            "symbol": symbol, "side": side, "quantity": quantity, "limit_price": limit_price
        })
        return result[0].text
    except Exception as e:
        await ctx.error(f"Failed to place limit order: {e}")
        raise

@mcp.tool()
async def cancel_all_orders(*, ctx: Context) -> str:
    """Cancel all open orders."""
    await ctx.info("Cancelling all open orders...")
    try:
        client = get_alpaca_client()
        result = await handle_cancel_all_orders(client, {})
        return result[0].text
    except Exception as e:
        await ctx.error(f"Failed to cancel orders: {e}")
        raise

@mcp.tool()
async def close_all_positions(cancel_orders: bool = True, *, ctx: Context) -> str:
    """
    Close all open positions.
    
    Args:
        cancel_orders: Whether to cancel all open orders before closing positions (default: True)
    """
    await ctx.info("Closing all positions...")
    try:
        client = get_alpaca_client()
        result = await handle_close_all_positions(client, {"cancel_orders": cancel_orders})
        return result[0].text
    except Exception as e:
        await ctx.error(f"Failed to close positions: {e}")
        raise

@mcp.tool()
async def take_partial_profit(symbol: str, profit_threshold: float = 0.2, close_percentage: float = 0.5, *, ctx: Context) -> str:
    """
    Take partial profit if the position's unrealized profit percent is greater than the threshold.
    Closes a percentage of the position if the threshold is met.
    
    Args:
        symbol: Stock ticker symbol (e.g., AAPL, MSFT)
        profit_threshold: The minimum profit percent (as a decimal, e.g., 0.2 for 20%) to trigger partial close
        close_percentage: The percentage of the position to close (as a decimal, e.g., 0.5 for 50%)
    """
    await ctx.info(f"Checking profit threshold for {symbol}...")
    try:
        client = get_alpaca_client()
        result = await handle_take_partial_profit(client, {
            "symbol": symbol, "profit_threshold": profit_threshold, "close_percentage": close_percentage
        })
        return result[0].text
    except Exception as e:
        await ctx.error(f"Failed to take partial profit for {symbol}: {e}")
        raise

# ==============================================================================
# Advanced Order Tools
# ==============================================================================

@mcp.tool()
async def place_bracket_order(
    symbol: str, 
    side: str, 
    quantity: float, 
    take_profit_price: float,
    stop_loss_price: float,
    order_type: str = "market",
    limit_price: float = None,
    stop_loss_limit_price: float = None,
    time_in_force: str = "gtc",
    *, ctx: Context
) -> str:
    """
    Place a bracket order (entry + take profit + stop loss).
    
    Args:
        symbol: Stock ticker symbol (e.g., AAPL, MSFT)
        side: Order side (buy or sell)
        quantity: Number of shares to buy or sell
        take_profit_price: Price to take profits
        stop_loss_price: Price to trigger stop loss
        order_type: Order type for entry order (market or limit, default: market)
        limit_price: Entry price (required if order_type is limit)
        stop_loss_limit_price: Limit price for stop loss (makes it stop-limit order)
        time_in_force: Time in force (day or gtc, default: gtc)
    """
    await ctx.info(f"Placing bracket order for {quantity} shares of {symbol}...")
    try:
        client = get_alpaca_client()
        result = await handle_place_bracket_order(client, {
            "symbol": symbol, "side": side, "quantity": quantity,
            "order_type": order_type, "limit_price": limit_price,
            "take_profit_price": take_profit_price, "stop_loss_price": stop_loss_price,
            "stop_loss_limit_price": stop_loss_limit_price, "time_in_force": time_in_force
        })
        return result[0].text
    except Exception as e:
        await ctx.error(f"Failed to place bracket order: {e}")
        raise

@mcp.tool()
async def place_oco_order(
    symbol: str,
    quantity: float,
    take_profit_price: float,
    stop_loss_price: float,
    stop_loss_limit_price: float = None,
    time_in_force: str = "gtc",
    *, ctx: Context
) -> str:
    """
    Place an OCO (One-Cancels-Other) order for existing positions.
    
    Args:
        symbol: Stock ticker symbol (e.g., AAPL, MSFT)
        quantity: Number of shares to sell
        take_profit_price: Limit price for profit taking
        stop_loss_price: Stop price for loss protection
        stop_loss_limit_price: Limit price for stop loss (makes it stop-limit order)
        time_in_force: Time in force (day or gtc, default: gtc)
    """
    await ctx.info(f"Placing OCO order for {quantity} shares of {symbol}...")
    try:
        client = get_alpaca_client()
        result = await handle_place_oco_order(client, {
            "symbol": symbol, "quantity": quantity,
            "take_profit_price": take_profit_price, "stop_loss_price": stop_loss_price,
            "stop_loss_limit_price": stop_loss_limit_price, "time_in_force": time_in_force
        })
        return result[0].text
    except Exception as e:
        await ctx.error(f"Failed to place OCO order: {e}")
        raise

@mcp.tool()
async def place_oto_order(
    symbol: str,
    side: str,
    quantity: float,
    order_type: str = "market",
    limit_price: float = None,
    take_profit_price: float = None,
    stop_loss_price: float = None,
    stop_loss_limit_price: float = None,
    time_in_force: str = "gtc",
    *, ctx: Context
) -> str:
    """
    Place an OTO (One-Triggers-Other) order with single exit condition.
    
    Args:
        symbol: Stock ticker symbol (e.g., AAPL, MSFT)
        side: Order side (buy or sell)
        quantity: Number of shares to buy or sell
        order_type: Order type for entry order (market or limit, default: market)
        limit_price: Entry price (required if order_type is limit)
        take_profit_price: Price to take profits (provide this OR stop_loss_price)
        stop_loss_price: Price to trigger stop loss (provide this OR take_profit_price)
        stop_loss_limit_price: Limit price for stop loss (makes it stop-limit order)
        time_in_force: Time in force (day or gtc, default: gtc)
    """
    await ctx.info(f"Placing OTO order for {quantity} shares of {symbol}...")
    try:
        client = get_alpaca_client()
        result = await handle_place_oto_order(client, {
            "symbol": symbol, "side": side, "quantity": quantity,
            "order_type": order_type, "limit_price": limit_price,
            "take_profit_price": take_profit_price, "stop_loss_price": stop_loss_price,
            "stop_loss_limit_price": stop_loss_limit_price, "time_in_force": time_in_force
        })
        return result[0].text
    except Exception as e:
        await ctx.error(f"Failed to place OTO order: {e}")
        raise

@mcp.tool()
async def place_trailing_stop_order(
    symbol: str,
    side: str,
    quantity: float,
    trail_type: str,
    trail_amount: float,
    time_in_force: str = "day",
    *, ctx: Context
) -> str:
    """
    Place a trailing stop order.
    
    Args:
        symbol: Stock ticker symbol (e.g., AAPL, MSFT)
        side: Order side (buy or sell)
        quantity: Number of shares to buy or sell
        trail_type: Trail type (price or percent)
        trail_amount: Trail distance (dollar amount for price, decimal for percent e.g. 0.05 = 5%)
        time_in_force: Time in force (day or gtc, default: day)
    """
    await ctx.info(f"Placing trailing stop order for {quantity} shares of {symbol}...")
    try:
        client = get_alpaca_client()
        result = await handle_place_trailing_stop_order(client, {
            "symbol": symbol, "side": side, "quantity": quantity,
            "trail_type": trail_type, "trail_amount": trail_amount,
            "time_in_force": time_in_force
        })
        return result[0].text
    except Exception as e:
        await ctx.error(f"Failed to place trailing stop order: {e}")
        raise

# ==============================================================================
# Server Startup
# ==============================================================================

if __name__ == "__main__":
    # Initialize configuration and logging
    try:
        server_config = load_server_config()
        _logger = setup_logging(level=server_config.log_level, logger_name="invest-pilot")
        _logger.info("Starting Invest-Pilot MCP Server (FastMCP v2)")
        
        # Log available tools
        tools = [
            "ping", "get_account_info", "get_positions", "get_stock_quote", "get_stock_bars",
            "get_orders", "place_market_order", "place_limit_order", "cancel_all_orders",
            "close_all_positions", "take_partial_profit",
            # Advanced orders
            "place_bracket_order", "place_oco_order", "place_oto_order", "place_trailing_stop_order"
        ]
        _logger.info(f"Loaded {len(tools)} tools: {tools}")
        _logger.info("MCP Server is ready and waiting for connections...")
        
        # Start the MCP server - this will block and keep the server running
        mcp.run()
        
    except Exception as e:
        if _logger:
            _logger.error(f"Error starting server: {e}")
        else:
            print(f"Error starting server: {e}")
        exit(1) 