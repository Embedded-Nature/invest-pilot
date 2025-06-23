"""Market data tools for Alpaca broker."""

from mcp.types import TextContent
from alpaca.data.timeframe import TimeFrame
from datetime import datetime, timedelta
from ..client import AlpacaClient
from ....core.logging_config import get_logger
from ....core.utils import log_tool_execution, format_currency
from ....core.exceptions import APIError
from typing import Dict, Any, List

logger = get_logger(__name__)

async def handle_get_stock_quote(client: AlpacaClient, arguments: Dict[str, Any]) -> List[TextContent]:
    """Handle get_stock_quote tool execution."""
    log_tool_execution(logger, "get_stock_quote", arguments)
    
    try:
        symbol = arguments["symbol"].upper()
        
        quote_response = client.get_latest_quote(symbol)
        
        if symbol not in quote_response:
            response = f"No quote data found for symbol {symbol}."
            logger.warning(f"No quote data found for {symbol}")
            return [TextContent(type="text", text=response)]
        
        quote = quote_response[symbol]
        
        response = f"""Latest Quote for {symbol}:
- Bid Price: {format_currency(quote.bid_price)}
- Ask Price: {format_currency(quote.ask_price)}
- Bid Size: {quote.bid_size}
- Ask Size: {quote.ask_size}
- Timestamp: {quote.timestamp}"""
        
        logger.info(f"Successfully retrieved quote for {symbol}")
        return [TextContent(type="text", text=response)]
        
    except APIError as e:
        logger.error(f"API error getting quote for {symbol}: {e}")
        return [TextContent(type="text", text=f"Error getting quote for {symbol}: {e}")]
    except Exception as e:
        logger.error(f"Unexpected error getting quote: {e}")
        return [TextContent(type="text", text=f"Unexpected error: {e}")]

async def handle_get_stock_bars(client: AlpacaClient, arguments: Dict[str, Any]) -> List[TextContent]:
    """Handle get_stock_bars tool execution."""
    log_tool_execution(logger, "get_stock_bars", arguments)
    
    try:
        symbol = arguments["symbol"].upper()
        days = arguments.get("days", 5)
        
        # Calculate date range
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days * 2)  # Extra buffer for weekends/holidays
        
        bars_response = client.get_stock_bars(
            symbol=symbol,
            timeframe=TimeFrame.Day,
            start=start_date,
            end=end_date
        )
        
        if symbol not in bars_response or not bars_response[symbol]:
            response = f"No bar data found for symbol {symbol}."
            logger.warning(f"No bar data found for {symbol}")
            return [TextContent(type="text", text=response)]
        
        bars = bars_response[symbol]
        
        # Limit to requested number of days
        bars = bars[-days:] if len(bars) > days else bars
        
        response = f"Historical Price Data for {symbol} (Last {len(bars)} trading days):\n"
        
        for bar in bars:
            response += f"""
Date: {bar.timestamp.strftime('%Y-%m-%d')}
- Open: {format_currency(bar.open)}
- High: {format_currency(bar.high)}
- Low: {format_currency(bar.low)}
- Close: {format_currency(bar.close)}
- Volume: {bar.volume:,}"""
        
        logger.info(f"Successfully retrieved {len(bars)} bars for {symbol}")
        return [TextContent(type="text", text=response)]
        
    except APIError as e:
        logger.error(f"API error getting bars for {symbol}: {e}")
        return [TextContent(type="text", text=f"Error getting bars for {symbol}: {e}")]
    except Exception as e:
        logger.error(f"Unexpected error getting bars: {e}")
        return [TextContent(type="text", text=f"Unexpected error: {e}")]

async def handle_ping(client: AlpacaClient, arguments: Dict[str, Any]) -> List[TextContent]:
    """Handle ping tool execution."""
    log_tool_execution(logger, "ping", arguments)
    
    try:
        # Simple ping by getting account info
        account = client.get_account()
        
        response = f"Pong! Server is responding. Account status: {account.status}"
        
        logger.info("Ping successful")
        return [TextContent(type="text", text=response)]
        
    except APIError as e:
        logger.error(f"Ping failed with API error: {e}")
        return [TextContent(type="text", text=f"Ping failed: {e}")]
    except Exception as e:
        logger.error(f"Ping failed with unexpected error: {e}")
        return [TextContent(type="text", text=f"Ping failed: {e}")] 