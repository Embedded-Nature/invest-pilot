import os
import sys
import logging
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional

from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP

from alpaca.common.exceptions import APIError
from alpaca.trading.client import TradingClient
from alpaca.trading.requests import (
    GetOrdersRequest,
    MarketOrderRequest,
    LimitOrderRequest,
    ClosePositionRequest,
)
from alpaca.trading.enums import OrderSide, TimeInForce, QueryOrderStatus
from alpaca.data.historical import StockHistoricalDataClient
from alpaca.data.requests import StockBarsRequest, StockLatestQuoteRequest
from alpaca.data.timeframe import TimeFrame


# ==============================================================================
# 1. Configuration & Initialization
# ==============================================================================

# Setup basic logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stderr
)
logger = logging.getLogger('alpaca-mcp')

# Load environment variables from .env file
BASE_DIR = Path(__file__).resolve().parent
if (BASE_DIR / '.env').exists():
    load_dotenv(BASE_DIR / '.env')
    logger.info("Environment variables loaded from %s", BASE_DIR / '.env')
else:
    logger.info(".env file not found, using system environment variables.")

# Initialize FastMCP server
mcp = FastMCP("alpaca-trading", "Alpaca Trading API Server")
logger.info("FastMCP server initialized.")

# Initialize Alpaca API clients
API_KEY = os.getenv("API_KEY_ID")
API_SECRET = os.getenv("API_SECRET_KEY")

if not API_KEY or not API_SECRET:
    logger.error("API_KEY_ID and/or API_SECRET_KEY not found in environment variables.")
    raise ValueError("Alpaca API credentials must be set in environment variables.")

try:
    trading_client = TradingClient(API_KEY, API_SECRET, paper=True)
    stock_client = StockHistoricalDataClient(API_KEY, API_SECRET)
    
    account_info = trading_client.get_account()
    logger.info("Alpaca clients initialized successfully for account %s.", account_info.account_number)

except APIError as e:
    logger.error("Failed to initialize Alpaca clients due to API error: %s", e)
    raise
except Exception as e:
    logger.error("An unexpected error occurred during Alpaca client initialization: %s", e)
    raise

# ==============================================================================
# 2. Helper Functions
# ==============================================================================

def _get_order_side(side: str) -> OrderSide:
    """Converts a string to an Alpaca OrderSide enum."""
    side_lower = side.lower()
    if side_lower == "buy":
        return OrderSide.BUY
    elif side_lower == "sell":
        return OrderSide.SELL
    else:
        raise ValueError(f"Invalid order side: '{side}'. Must be 'buy' or 'sell'.")

# ==============================================================================
# 3. MCP Tools
# ==============================================================================

# ------------------------------------------------------------------------------
# Health & Status Tools
# ------------------------------------------------------------------------------
@mcp.tool()
async def ping() -> str:
    """Test if the server is responding."""
    logger.info("Executing ping tool.")
    return "pong"

# ------------------------------------------------------------------------------
# Account Tools
# ------------------------------------------------------------------------------
@mcp.tool()
async def get_account_info() -> str:
    """Get the current account information including balances and status."""
    logger.info("Executing get_account_info tool.")
    try:
        account = trading_client.get_account()
        info = f"""
Account Information:
-------------------
Account ID: {account.id}
Status: {account.status}
Currency: {account.currency}
Buying Power: ${float(account.buying_power):.2f}
Cash: ${float(account.cash):.2f}
Portfolio Value: ${float(account.portfolio_value):.2f}
Equity: ${float(account.equity):.2f}
Long Market Value: ${float(account.long_market_value):.2f}
Short Market Value: ${float(account.short_market_value):.2f}
Pattern Day Trader: {'Yes' if account.pattern_day_trader else 'No'}
Day Trades Remaining: {account.daytrade_count if hasattr(account, 'daytrade_count') else 'Unknown'}
"""
        logger.info("Successfully retrieved account info.")
        return info
    except APIError as e:
        logger.error("API error getting account info: %s", e)
        return f"API error getting account info: {e}"
    except Exception as e:
        logger.error("Unexpected error in get_account_info: %s", e)
        return f"An unexpected error occurred: {e}"

@mcp.tool()
async def get_positions() -> str:
    """Get all current positions in the portfolio."""
    logger.info("Executing get_positions tool.")
    try:
        positions = trading_client.get_all_positions()
        
        if not positions:
            logger.info("No open positions found.")
            return "No open positions found."
        
        result = "Current Positions:\n-------------------\n"
        for position in positions:
            result += f"""
Symbol: {position.symbol}
Quantity: {position.qty} shares
Market Value: ${float(position.market_value):.2f}
Average Entry Price: ${float(position.avg_entry_price):.2f}
Current Price: ${float(position.current_price):.2f}
Unrealized P/L: ${float(position.unrealized_pl):.2f} ({float(position.unrealized_plpc) * 100:.2f}%)
-------------------
"""
        logger.info("Successfully retrieved %d positions.", len(positions))
        return result
    except APIError as e:
        logger.error("API error getting positions: %s", e)
        return f"API error getting positions: {e}"
    except Exception as e:
        logger.error("Unexpected error in get_positions: %s", e)
        return f"An unexpected error occurred: {e}"


# ------------------------------------------------------------------------------
# Market Data Tools
# ------------------------------------------------------------------------------
@mcp.tool()
async def get_stock_quote(symbol: str) -> str:
    """
    Get the latest quote for a stock.
    
    Args:
        symbol: Stock ticker symbol (e.g., AAPL, MSFT)
    """
    logger.info("Executing get_stock_quote for symbol: %s", symbol)
    try:
        request_params = StockLatestQuoteRequest(symbol_or_symbols=symbol)
        quotes = stock_client.get_stock_latest_quote(request_params)
        
        if symbol in quotes:
            quote = quotes[symbol]
            response = f"""
Latest Quote for {symbol}:
------------------------
Ask Price: ${quote.ask_price:.2f}
Bid Price: ${quote.bid_price:.2f}
Ask Size: {quote.ask_size}
Bid Size: {quote.bid_size}
Timestamp: {quote.timestamp}
"""
            logger.info("Successfully retrieved quote for %s.", symbol)
            return response
        else:
            logger.warning("No quote data found for symbol: %s", symbol)
            return f"No quote data found for {symbol}."
    except APIError as e:
        logger.error("API error fetching quote for %s: %s", symbol, e)
        return f"API error fetching quote for {symbol}: {e}"
    except Exception as e:
        logger.error("Unexpected error in get_stock_quote for %s: %s", symbol, e)
        return f"An unexpected error occurred: {e}"

@mcp.tool()
async def get_stock_bars(symbol: str, days: int = 5) -> str:
    """
    Get historical price bars for a stock.
    
    Args:
        symbol: Stock ticker symbol (e.g., AAPL, MSFT)
        days: Number of trading days to look back (default: 5)
    """
    logger.info("Executing get_stock_bars for symbol: %s, days: %d", symbol, days)
    try:
        start_time = datetime.now() - timedelta(days=days)
        
        request_params = StockBarsRequest(
            symbol_or_symbols=symbol,
            timeframe=TimeFrame.Day,
            start=start_time
        )
        
        bars = stock_client.get_stock_bars(request_params)
        
        if symbol in bars and bars[symbol]:
            result = f"Historical Data for {symbol} (Last {len(bars[symbol])} trading days):\n"
            result += "---------------------------------------------------\n"
            
            for bar in bars[symbol]:
                result += f"Date: {bar.timestamp.date()}, Open: ${bar.open:.2f}, High: ${bar.high:.2f}, Low: ${bar.low:.2f}, Close: ${bar.close:.2f}, Volume: {bar.volume}\n"
            
            logger.info("Successfully retrieved %d bars for %s.", len(bars[symbol]), symbol)
            return result
        else:
            logger.warning("No historical data found for %s in the last %d days.", symbol, days)
            return f"No historical data found for {symbol} in the last {days} days."
    except APIError as e:
        logger.error("API error fetching bars for %s: %s", symbol, e)
        return f"API error fetching historical data for {symbol}: {e}"
    except Exception as e:
        logger.error("Unexpected error in get_stock_bars for %s: %s", symbol, e)
        return f"An unexpected error occurred: {e}"

# ------------------------------------------------------------------------------
# Order Management Tools
# ------------------------------------------------------------------------------
@mcp.tool()
async def get_orders(status: str = "all", limit: int = 10) -> str:
    """
    Get orders with the specified status.
    
    Args:
        status: Order status to filter by (open, closed, all)
        limit: Maximum number of orders to return (default: 10)
    """
    logger.info("Executing get_orders with status: %s, limit: %d", status, limit)
    try:
        status_map = {
            "open": QueryOrderStatus.OPEN,
            "closed": QueryOrderStatus.CLOSED,
            "all": QueryOrderStatus.ALL,
        }
        query_status = status_map.get(status.lower(), QueryOrderStatus.ALL)
            
        request_params = GetOrdersRequest(status=query_status, limit=limit)
        orders = trading_client.get_orders(request_params)
        
        if not orders:
            logger.info("No %s orders found.", status)
            return f"No {status} orders found."
        
        result = f"{status.capitalize()} Orders (Last {len(orders)}):\n"
        result += "-----------------------------------\n"
        
        for order in orders:
            result += f"""
Symbol: {order.symbol}
ID: {order.id}
Type: {order.type}
Side: {order.side}
Quantity: {order.qty}
Status: {order.status}
Submitted At: {order.submitted_at}
"""
            if order.filled_at:
                result += f"Filled At: {order.filled_at}\n"
            if order.filled_avg_price:
                result += f"Filled Price: ${float(order.filled_avg_price):.2f}\n"
            result += "-----------------------------------\n"
            
        logger.info("Successfully retrieved %d orders.", len(orders))
        return result
    except APIError as e:
        logger.error("API error fetching orders: %s", e)
        return f"API error fetching orders: {e}"
    except Exception as e:
        logger.error("Unexpected error in get_orders: %s", e)
        return f"An unexpected error occurred: {e}"

@mcp.tool()
async def place_market_order(symbol: str, side: str, quantity: float) -> str:
    """
    Place a market order.
    
    Args:
        symbol: Stock ticker symbol (e.g., AAPL, MSFT)
        side: Order side (buy or sell)
        quantity: Number of shares to buy or sell
    """
    logger.info("Attempting to place market order: %s %s %s", side, quantity, symbol)
    try:
        order_side = _get_order_side(side)
        
        order_data = MarketOrderRequest(
            symbol=symbol,
            qty=quantity,
            side=order_side,
            time_in_force=TimeInForce.DAY
        )
        
        order = trading_client.submit_order(order_data)
        
        response = f"""
Market Order Placed Successfully:
--------------------------------
Order ID: {order.id}
Symbol: {order.symbol}
Side: {order.side}
Quantity: {order.qty}
Type: {order.type}
Time In Force: {order.time_in_force}
Status: {order.status}
"""
        logger.info("Successfully placed market order %s for %s.", order.id, symbol)
        return response
    except (APIError, ValueError) as e:
        logger.error("Error placing market order for %s: %s", symbol, e)
        return f"Error placing market order: {e}"
    except Exception as e:
        logger.error("Unexpected error in place_market_order for %s: %s", symbol, e)
        return f"An unexpected error occurred: {e}"

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
    logger.info("Attempting to place limit order: %s %s %s @ %s", side, quantity, symbol, limit_price)
    try:
        order_side = _get_order_side(side)
        
        order_data = LimitOrderRequest(
            symbol=symbol,
            qty=quantity,
            side=order_side,
            time_in_force=TimeInForce.DAY,
            limit_price=limit_price
        )
        
        order = trading_client.submit_order(order_data)
        
        response = f"""
Limit Order Placed Successfully:
-------------------------------
Order ID: {order.id}
Symbol: {order.symbol}
Side: {order.side}
Quantity: {order.qty}
Type: {order.type}
Limit Price: ${float(order.limit_price):.2f}
Time In Force: {order.time_in_force}
Status: {order.status}
"""
        logger.info("Successfully placed limit order %s for %s.", order.id, symbol)
        return response
    except (APIError, ValueError) as e:
        logger.error("Error placing limit order for %s: %s", symbol, e)
        return f"Error placing limit order: {e}"
    except Exception as e:
        logger.error("Unexpected error in place_limit_order for %s: %s", symbol, e)
        return f"An unexpected error occurred: {e}"

@mcp.tool()
async def cancel_all_orders() -> str:
    """Cancel all open orders."""
    logger.info("Executing cancel_all_orders tool.")
    try:
        cancel_statuses = trading_client.cancel_orders()
        # The response is a list of objects with order_id and status (HTTP status).
        # We can summarize it for the user.
        canceled_count = sum(1 for s in cancel_statuses if 200 <= s.status < 300)
        failed_count = len(cancel_statuses) - canceled_count
        
        response = f"Attempted to cancel all orders. {canceled_count} succeeded, {failed_count} failed."
        logger.info(response)
        return response
    except APIError as e:
        logger.error("API error canceling all orders: %s", e)
        return f"API error canceling orders: {e}"
    except Exception as e:
        logger.error("Unexpected error in cancel_all_orders: %s", e)
        return f"An unexpected error occurred: {e}"


# ------------------------------------------------------------------------------
# Position Management Tools
# ------------------------------------------------------------------------------
@mcp.tool()
async def close_all_positions(cancel_orders: bool = True) -> str:
    """
    Close all open positions by submitting market orders.
    
    Args:
        cancel_orders: Whether to cancel all open orders before closing positions (default: True).
    """
    logger.info("Executing close_all_positions with cancel_orders=%s.", cancel_orders)
    try:
        close_responses = trading_client.close_all_positions(cancel_orders=cancel_orders)
        
        if not close_responses:
            return "No positions to close."

        success_count = sum(1 for r in close_responses if 200 <= r.status < 300)
        fail_count = len(close_responses) - success_count
        
        response = f"Attempted to close all positions. {success_count} succeeded, {fail_count} failed."
        logger.info(response)
        return response
    except APIError as e:
        logger.error("API error closing all positions: %s", e)
        return f"API error closing positions: {e}"
    except Exception as e:
        logger.error("Unexpected error in close_all_positions: %s", e)
        return f"An unexpected error occurred: {e}"

@mcp.tool()
async def take_partial_profit(symbol: str, profit_threshold: float = 0.2, close_percentage: float = 0.5) -> str:
    """
    Take partial profit if the position's unrealized profit percent is greater than the threshold.
    Closes a percentage of the position if the threshold is met.
    Args:
        symbol: Stock ticker symbol (e.g., AAPL, MSFT)
        profit_threshold: The minimum profit percent (as a decimal, e.g., 0.2 for 20%) to trigger partial close.
        close_percentage: The percentage of the position to close (as a decimal, e.g., 0.5 for 50%).
    """
    logger.info(
        "Executing take_partial_profit for %s with threshold=%s and percentage=%s",
        symbol, profit_threshold, close_percentage
    )
    try:
        position = trading_client.get_open_position(symbol)
        
        profit_pct = float(position.unrealized_plpc)
        
        if profit_pct > profit_threshold:
            qty_to_close = float(position.qty) * close_percentage
            logger.info(
                "Profit threshold met for %s (%s%% > %s%%). Closing %s%% of position (%s shares).",
                symbol, profit_pct * 100, profit_threshold * 100, close_percentage * 100, qty_to_close
            )
            
            close_req = ClosePositionRequest(percentage=str(close_percentage * 100))
            order = trading_client.close_position(symbol, close_req)

            response = (
                f"Partial profit taken: Submitted order to close {close_percentage * 100}% of {symbol} position "
                f"at {profit_pct*100:.2f}% profit. Order ID: {order.id}"
            )
            logger.info(response)
            return response
        else:
            response = (
                f"Profit threshold not met for {symbol}. Current profit: {profit_pct*100:.2f}%, "
                f"Threshold: {profit_threshold*100:.2f}%. No action taken."
            )
            logger.info(response)
            return response
    except APIError as e:
        if "position not found" in str(e).lower():
            logger.warning("No open position found for symbol: %s", symbol)
            return f"No open position found for {symbol}."
        logger.error("API error in take_partial_profit for %s: %s", symbol, e)
        return f"API error taking partial profit for {symbol}: {e}"
    except Exception as e:
        logger.error("Unexpected error in take_partial_profit for %s: %s", symbol, e)
        return f"An unexpected error occurred: {e}"

# ==============================================================================
# 4. Server Execution
# ==============================================================================
if __name__ == "__main__":
    logger.info("Starting Alpaca MCP server...")
    try:
        mcp.run(transport='stdio')
    except Exception as e:
        logger.critical("Server failed to start or crashed: %s", e)
        sys.exit(1)