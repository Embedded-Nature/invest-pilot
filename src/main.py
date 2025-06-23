"""
Invest-Pilot MCP Server - Modular Architecture

A Model Context Protocol (MCP) server providing trading capabilities with Alpaca.
This is the new modular entry point for the refactored codebase.
"""

import asyncio
from typing import Dict, Any

from mcp.server.fastmcp import FastMCP

# Core modules
import sys
import os

# Add the project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from src.core.logging_config import setup_logging, get_logger
from src.core.exceptions import InvalidConfigurationError, BrokerConnectionError, APIError
from src.config.settings import load_alpaca_config, load_server_config

# Alpaca broker modules
from src.brokers.alpaca.client import AlpacaClient
from src.brokers.alpaca.tools.account import handle_get_account_info, handle_get_positions
from src.brokers.alpaca.tools.orders import (
    handle_get_orders, handle_place_market_order, handle_place_limit_order,
    handle_cancel_all_orders, handle_close_all_positions, handle_take_partial_profit
)
from src.brokers.alpaca.tools.market_data import handle_get_stock_quote, handle_get_stock_bars, handle_ping

# Global variables
mcp = FastMCP("invest-pilot", "Invest-Pilot MCP Server - Modular Architecture")
alpaca_client: AlpacaClient = None
logger = None

def _get_client() -> AlpacaClient:
    """Get or initialize the Alpaca client."""
    global alpaca_client, logger
    if alpaca_client is None:
        try:
            # Load configuration
            server_config = load_server_config()
            alpaca_config = load_alpaca_config()
            
            # Setup logging if not already done
            if logger is None:
                logger = setup_logging(level=server_config.log_level, logger_name="invest-pilot")
            
            # Initialize Alpaca client
            alpaca_client = AlpacaClient(alpaca_config)
            logger.info("Alpaca client initialized")
        except Exception as e:
            if logger:
                logger.error(f"Failed to initialize client: {e}")
            raise
    return alpaca_client

# ==============================================================================
# Health & Status Tools
# ==============================================================================

@mcp.tool()
async def ping() -> str:
    """Test if the server is responding."""
    result = await handle_ping(_get_client(), {})
    return result[0].text

# ==============================================================================
# Account Tools
# ==============================================================================

@mcp.tool()
async def get_account_info() -> str:
    """Get the current account information including balances and status."""
    result = await handle_get_account_info(_get_client(), {})
    return result[0].text

@mcp.tool()
async def get_positions() -> str:
    """Get all current positions in the portfolio."""
    result = await handle_get_positions(_get_client(), {})
    return result[0].text

# ==============================================================================
# Market Data Tools
# ==============================================================================

@mcp.tool()
async def get_stock_quote(symbol: str) -> str:
    """
    Get the latest quote for a stock.
    
    Args:
        symbol: Stock ticker symbol (e.g., AAPL, MSFT)
    """
    result = await handle_get_stock_quote(_get_client(), {"symbol": symbol})
    return result[0].text

@mcp.tool()
async def get_stock_bars(symbol: str, days: int = 5) -> str:
    """
    Get historical price bars for a stock.
    
    Args:
        symbol: Stock ticker symbol (e.g., AAPL, MSFT)
        days: Number of trading days to look back (default: 5)
    """
    result = await handle_get_stock_bars(_get_client(), {"symbol": symbol, "days": days})
    return result[0].text

# ==============================================================================
# Order Tools
# ==============================================================================

@mcp.tool()
async def get_orders(status: str = "all", limit: int = 10) -> str:
    """
    Get orders with the specified status.
    
    Args:
        status: Order status to filter by (open, closed, all)
        limit: Maximum number of orders to return (default: 10)
    """
    result = await handle_get_orders(_get_client(), {"status": status, "limit": limit})
    return result[0].text

@mcp.tool()
async def place_market_order(symbol: str, side: str, quantity: float) -> str:
    """
    Place a market order.
    
    Args:
        symbol: Stock ticker symbol (e.g., AAPL, MSFT)
        side: Order side (buy or sell)
        quantity: Number of shares to buy or sell
    """
    result = await handle_place_market_order(_get_client(), {
        "symbol": symbol, "side": side, "quantity": quantity
    })
    return result[0].text

@mcp.tool()
async def place_limit_order(symbol: str, side: str, quantity: float, limit_price: float) -> str:
    """
    Place a limit order.
    
    Args:
        symbol: Stock ticker symbol (e.g., AAPL, MSFT)
        side: Order side (buy or sell)
        quantity: Number of shares to buy or sell
        limit_price: Limit price for the order
    """
    result = await handle_place_limit_order(_get_client(), {
        "symbol": symbol, "side": side, "quantity": quantity, "limit_price": limit_price
    })
    return result[0].text

@mcp.tool()
async def cancel_all_orders() -> str:
    """Cancel all open orders."""
    result = await handle_cancel_all_orders(_get_client(), {})
    return result[0].text

@mcp.tool()
async def close_all_positions(cancel_orders: bool = True) -> str:
    """
    Close all open positions.
    
    Args:
        cancel_orders: Whether to cancel all open orders before closing positions (default: True)
    """
    result = await handle_close_all_positions(_get_client(), {"cancel_orders": cancel_orders})
    return result[0].text

@mcp.tool()
async def take_partial_profit(symbol: str, profit_threshold: float = 0.2, close_percentage: float = 0.5) -> str:
    """
    Take partial profit if the position's unrealized profit percent is greater than the threshold.
    Closes a percentage of the position if the threshold is met.
    
    Args:
        symbol: Stock ticker symbol (e.g., AAPL, MSFT)
        profit_threshold: The minimum profit percent (as a decimal, e.g., 0.2 for 20%) to trigger partial close
        close_percentage: The percentage of the position to close (as a decimal, e.g., 0.5 for 50%)
    """
    result = await handle_take_partial_profit(_get_client(), {
        "symbol": symbol, "profit_threshold": profit_threshold, "close_percentage": close_percentage
    })
    return result[0].text

# ==============================================================================
# Main Entry Point
# ==============================================================================

# Initialize configuration and client on module load
try:
    server_config = load_server_config()
    alpaca_config = load_alpaca_config()
    
    # Setup logging
    logger = setup_logging(level=server_config.log_level, logger_name="invest-pilot")
    logger.info("Starting Invest-Pilot MCP Server")
    
    # Initialize Alpaca client  
    alpaca_client = AlpacaClient(alpaca_config)
    logger.info("Alpaca client initialized successfully")
    
    # Log available tools
    tools = [
        "ping", "get_account_info", "get_positions", "get_stock_quote", "get_stock_bars",
        "get_orders", "place_market_order", "place_limit_order", "cancel_all_orders",
        "close_all_positions", "take_partial_profit"
    ]
    logger.info(f"Loaded {len(tools)} tools: {tools}")
    
except Exception as e:
    print(f"Error initializing server: {e}")
    exit(1)

# FastMCP handles the server startup automatically
# No need for main() function or asyncio.run() 