"""Market data tools for Alpaca broker."""

import json
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
        
        quote = client.get_latest_quote(symbol)
        
        if not quote:
            result = {
                "symbol": symbol,
                "message": f"No quote data found for symbol {symbol}."
            }
            logger.warning(f"No quote data found for {symbol}")
            return [TextContent(type="text", text=json.dumps(result, indent=2))]
        
        result = {
            "symbol": symbol,
            "bid_price": float(quote.bid_price),
            "bid_size": int(quote.bid_size),
            "ask_price": float(quote.ask_price),
            "ask_size": int(quote.ask_size),
            "timestamp": quote.timestamp.isoformat() if quote.timestamp else None,
        }
        
        logger.info(f"Successfully retrieved quote for {symbol}")
        return [TextContent(type="text", text=json.dumps(result, indent=2))]
        
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
        
        # Use the simplified client method that handles the date calculation internally
        bars = client.get_stock_bars(symbol=symbol, days=days)
        
        if not bars:
            result = {
                "symbol": symbol,
                "message": f"No bar data found for symbol {symbol}.",
                "bars": []
            }
            logger.warning(f"No bar data found for {symbol}")
            return [TextContent(type="text", text=json.dumps(result, indent=2))]
        
        # Limit to requested number of days
        bars = bars[-days:] if len(bars) > days else bars
        
        result = {
            "symbol": symbol,
            "days_requested": days,
            "bars_returned": len(bars),
            "bars": []
        }
        
        for bar in bars:
            result["bars"].append({
                "timestamp": bar.timestamp.isoformat() if bar.timestamp else None,
                "open": float(bar.open),
                "high": float(bar.high),
                "low": float(bar.low),
                "close": float(bar.close),
                "volume": int(bar.volume),
                "trade_count": int(bar.trade_count) if bar.trade_count else None,
                "vwap": float(bar.vwap) if bar.vwap else None,
            })
        
        logger.info(f"Successfully retrieved {len(bars)} bars for {symbol}")
        return [TextContent(type="text", text=json.dumps(result, indent=2))]
        
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
        
        result = {
            "status": "success",
            "message": "Pong! Server is responding.",
            "account_id": str(account.id),
            "account_status": account.status,
            "timestamp": datetime.now().isoformat()
        }
        
        logger.info("Ping successful")
        return [TextContent(type="text", text=json.dumps(result, indent=2))]
        
    except APIError as e:
        logger.error(f"Ping failed with API error: {e}")
        return [TextContent(type="text", text=f"Ping failed: {e}")]
    except Exception as e:
        logger.error(f"Ping failed with unexpected error: {e}")
        return [TextContent(type="text", text=f"Ping failed: {e}")] 