"""Account-related tools for Alpaca broker."""

import json
from mcp.types import TextContent
from ..client import AlpacaClient
from ....core.logging_config import get_logger
from ....core.utils import log_tool_execution, format_currency
from ....core.exceptions import APIError
from typing import Dict, Any, List

logger = get_logger(__name__)

async def handle_get_account_info(client: AlpacaClient, arguments: Dict[str, Any]) -> List[TextContent]:
    """Handle get_account_info tool execution."""
    log_tool_execution(logger, "get_account_info", arguments)
    
    try:
        account = client.get_account()
        
        result = {
            "account_id": str(account.id),  # Convert UUID to string
            "account_number": account.account_number,
            "status": account.status,
            "currency": account.currency,
            "buying_power": float(account.buying_power),
            "cash": float(account.cash),
            "portfolio_value": float(account.portfolio_value),
            "equity": float(account.equity),
            "last_equity": float(account.last_equity),
            "daytrading_buying_power": float(account.daytrading_buying_power),
            "multiplier": int(account.multiplier),
            "pattern_day_trader": account.pattern_day_trader,
            "trading_blocked": account.trading_blocked,
            "transfers_blocked": account.transfers_blocked,
            "account_blocked": account.account_blocked,
            "created_at": account.created_at.isoformat() if account.created_at else None,
        }
        
        logger.info("Successfully retrieved account information")
        return [TextContent(type="text", text=json.dumps(result, indent=2))]
        
    except APIError as e:
        logger.error(f"API error getting account info: {e}")
        return [TextContent(type="text", text=f"Error getting account information: {e}")]
    except Exception as e:
        logger.error(f"Unexpected error getting account info: {e}")
        return [TextContent(type="text", text=f"Unexpected error: {e}")]

async def handle_get_positions(client: AlpacaClient, arguments: Dict[str, Any]) -> List[TextContent]:
    """Handle get_positions tool execution."""
    log_tool_execution(logger, "get_positions", arguments)
    
    try:
        positions = client.get_all_positions()
        
        if not positions:
            result = {
                "message": "No open positions found.",
                "positions": []
            }
        else:
            result = {
                "message": f"Found {len(positions)} open positions",
                "positions": []
            }
            
            for position in positions:
                result["positions"].append({
                    "symbol": position.symbol,
                    "qty": float(position.qty),
                    "side": position.side,
                    "market_value": float(position.market_value),
                    "cost_basis": float(position.cost_basis),
                    "unrealized_pl": float(position.unrealized_pl),
                    "unrealized_plpc": float(position.unrealized_plpc),
                    "current_price": float(position.current_price),
                    "avg_entry_price": float(position.avg_entry_price),
                })
        
        logger.info(f"Successfully retrieved {len(positions)} positions")
        return [TextContent(type="text", text=json.dumps(result, indent=2))]
        
    except APIError as e:
        logger.error(f"API error getting positions: {e}")
        return [TextContent(type="text", text=f"Error getting positions: {e}")]
    except Exception as e:
        logger.error(f"Unexpected error getting positions: {e}")
        return [TextContent(type="text", text=f"Unexpected error: {e}")] 