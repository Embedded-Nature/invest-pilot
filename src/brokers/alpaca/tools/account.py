"""Account-related tools for Alpaca broker."""

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
        
        response = f"""Account Information:
- Account Number: {account.account_number}
- Status: {account.status}
- Currency: {account.currency}
- Buying Power: {format_currency(float(account.buying_power))}
- Cash: {format_currency(float(account.cash))}
- Portfolio Value: {format_currency(float(account.portfolio_value))}
- Equity: {format_currency(float(account.equity))}
- Day Trading Buying Power: {format_currency(float(account.daytrading_buying_power))}
- Pattern Day Trader: {account.pattern_day_trader}
- Trading Blocked: {account.trading_blocked}
- Transfers Blocked: {account.transfers_blocked}
- Account Blocked: {account.account_blocked}"""
        
        logger.info("Successfully retrieved account information")
        return [TextContent(type="text", text=response)]
        
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
            response = "No open positions found."
        else:
            response = "Current Positions:\n"
            for position in positions:
                unrealized_pl = float(position.unrealized_pl or 0)
                unrealized_plpc = float(position.unrealized_plpc or 0) * 100
                
                response += f"""
- {position.symbol}:
  • Quantity: {position.qty}
  • Side: {position.side}
  • Market Value: {format_currency(float(position.market_value))}
  • Cost Basis: {format_currency(float(position.cost_basis))}
  • Unrealized P&L: {format_currency(unrealized_pl)} ({unrealized_plpc:.2f}%)
  • Current Price: {format_currency(float(position.current_price))}
  • Average Entry Price: {format_currency(float(position.avg_entry_price))}"""
        
        logger.info(f"Successfully retrieved {len(positions)} positions")
        return [TextContent(type="text", text=response)]
        
    except APIError as e:
        logger.error(f"API error getting positions: {e}")
        return [TextContent(type="text", text=f"Error getting positions: {e}")]
    except Exception as e:
        logger.error(f"Unexpected error getting positions: {e}")
        return [TextContent(type="text", text=f"Unexpected error: {e}")] 