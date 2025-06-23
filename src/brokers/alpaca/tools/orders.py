"""Order-related tools for Alpaca broker."""

import json
from mcp.types import TextContent
from alpaca.trading.requests import MarketOrderRequest, LimitOrderRequest, ClosePositionRequest
from alpaca.trading.enums import QueryOrderStatus, TimeInForce
from ..client import AlpacaClient
from ....core.logging_config import get_logger
from ....core.utils import log_tool_execution, get_order_side, format_currency
from ....core.exceptions import APIError
from typing import Dict, Any, List

logger = get_logger(__name__)

async def handle_get_orders(client: AlpacaClient, arguments: Dict[str, Any]) -> List[TextContent]:
    """Handle get_orders tool execution."""
    log_tool_execution(logger, "get_orders", arguments)
    
    try:
        status_str = arguments.get("status", "all").lower()
        limit = arguments.get("limit", 10)
        
        # Convert string status to enum
        if status_str == "open":
            status = QueryOrderStatus.OPEN
        elif status_str == "closed":
            status = QueryOrderStatus.CLOSED
        else:
            status = QueryOrderStatus.ALL
        
        orders = client.get_orders(status=status, limit=limit)
        
        if not orders:
            result = {
                "message": f"No {status_str} orders found.",
                "orders": []
            }
        else:
            result = {
                "message": f"Found {len(orders)} {status_str} orders",
                "orders": []
            }
            
            for order in orders:
                order_data = {
                    "id": str(order.id),  # Convert UUID to string
                    "symbol": order.symbol,
                    "qty": float(order.qty),
                    "filled_qty": float(order.filled_qty) if order.filled_qty else 0,
                    "side": order.side,
                    "order_type": order.order_type,
                    "status": order.status,
                    "limit_price": float(order.limit_price) if order.limit_price else None,
                    "stop_price": float(order.stop_price) if order.stop_price else None,
                    "avg_fill_price": float(order.avg_fill_price) if order.avg_fill_price else None,
                    "created_at": order.created_at.isoformat() if order.created_at else None,
                    "updated_at": order.updated_at.isoformat() if order.updated_at else None,
                    "submitted_at": order.submitted_at.isoformat() if order.submitted_at else None,
                }
                result["orders"].append(order_data)
        
        logger.info(f"Successfully retrieved {len(orders)} {status_str} orders")
        return [TextContent(type="text", text=json.dumps(result, indent=2))]
        
    except APIError as e:
        logger.error(f"API error getting orders: {e}")
        return [TextContent(type="text", text=f"Error getting orders: {e}")]
    except Exception as e:
        logger.error(f"Unexpected error getting orders: {e}")
        return [TextContent(type="text", text=f"Unexpected error: {e}")]

async def handle_place_market_order(client: AlpacaClient, arguments: Dict[str, Any]) -> List[TextContent]:
    """Handle place_market_order tool execution."""
    log_tool_execution(logger, "place_market_order", arguments)
    
    try:
        symbol = arguments["symbol"].upper()
        side = get_order_side(arguments["side"])
        quantity = arguments["quantity"]
        
        order_request = MarketOrderRequest(
            symbol=symbol,
            qty=quantity,
            side=side,
            time_in_force=TimeInForce.DAY
        )
        
        order = client.submit_order(order_request)
        
        response = f"""Market order placed successfully:
- Order ID: {order.id}
- Symbol: {order.symbol}
- Side: {order.side}
- Quantity: {order.qty}
- Status: {order.status}
- Submitted At: {order.submitted_at}"""
        
        logger.info(f"Successfully placed market order: {symbol} {side} {quantity}")
        return [TextContent(type="text", text=response)]
        
    except ValueError as e:
        logger.error(f"Invalid parameters for market order: {e}")
        return [TextContent(type="text", text=f"Invalid parameters: {e}")]
    except APIError as e:
        logger.error(f"API error placing market order: {e}")
        return [TextContent(type="text", text=f"Error placing market order: {e}")]
    except Exception as e:
        logger.error(f"Unexpected error placing market order: {e}")
        return [TextContent(type="text", text=f"Unexpected error: {e}")]

async def handle_place_limit_order(client: AlpacaClient, arguments: Dict[str, Any]) -> List[TextContent]:
    """Handle place_limit_order tool execution."""
    log_tool_execution(logger, "place_limit_order", arguments)
    
    try:
        symbol = arguments["symbol"].upper()
        side = get_order_side(arguments["side"])
        quantity = arguments["quantity"]
        limit_price = arguments["limit_price"]
        
        order_request = LimitOrderRequest(
            symbol=symbol,
            qty=quantity,
            side=side,
            limit_price=limit_price,
            time_in_force=TimeInForce.DAY
        )
        
        order = client.submit_order(order_request)
        
        response = f"""Limit order placed successfully:
- Order ID: {order.id}
- Symbol: {order.symbol}
- Side: {order.side}
- Quantity: {order.qty}
- Limit Price: {format_currency(float(order.limit_price))}
- Status: {order.status}
- Submitted At: {order.submitted_at}"""
        
        logger.info(f"Successfully placed limit order: {symbol} {side} {quantity} @ {limit_price}")
        return [TextContent(type="text", text=response)]
        
    except ValueError as e:
        logger.error(f"Invalid parameters for limit order: {e}")
        return [TextContent(type="text", text=f"Invalid parameters: {e}")]
    except APIError as e:
        logger.error(f"API error placing limit order: {e}")
        return [TextContent(type="text", text=f"Error placing limit order: {e}")]
    except Exception as e:
        logger.error(f"Unexpected error placing limit order: {e}")
        return [TextContent(type="text", text=f"Unexpected error: {e}")]

async def handle_cancel_all_orders(client: AlpacaClient, arguments: Dict[str, Any]) -> List[TextContent]:
    """Handle cancel_all_orders tool execution."""
    log_tool_execution(logger, "cancel_all_orders", arguments)
    
    try:
        cancelled_orders = client.cancel_all_orders()
        
        if not cancelled_orders:
            response = "No orders to cancel."
        else:
            response = f"Successfully cancelled {len(cancelled_orders)} orders:\n"
            for order in cancelled_orders:
                response += f"- {order.symbol} {order.side} {order.qty} (Order ID: {order.id})\n"
        
        logger.info(f"Successfully cancelled {len(cancelled_orders)} orders")
        return [TextContent(type="text", text=response)]
        
    except APIError as e:
        logger.error(f"API error cancelling orders: {e}")
        return [TextContent(type="text", text=f"Error cancelling orders: {e}")]
    except Exception as e:
        logger.error(f"Unexpected error cancelling orders: {e}")
        return [TextContent(type="text", text=f"Unexpected error: {e}")]

async def handle_close_all_positions(client: AlpacaClient, arguments: Dict[str, Any]) -> List[TextContent]:
    """Handle close_all_positions tool execution."""
    log_tool_execution(logger, "close_all_positions", arguments)
    
    try:
        cancel_orders = arguments.get("cancel_orders", True)
        
        closed_positions = client.close_all_positions(cancel_orders=cancel_orders)
        
        if not closed_positions:
            response = "No positions to close."
        else:
            response = f"Successfully closed {len(closed_positions)} positions:\n"
            for position in closed_positions:
                response += f"- {position.symbol} {position.side} {position.qty}\n"
        
        logger.info(f"Successfully closed {len(closed_positions)} positions")
        return [TextContent(type="text", text=response)]
        
    except APIError as e:
        logger.error(f"API error closing positions: {e}")
        return [TextContent(type="text", text=f"Error closing positions: {e}")]
    except Exception as e:
        logger.error(f"Unexpected error closing positions: {e}")
        return [TextContent(type="text", text=f"Unexpected error: {e}")]

async def handle_take_partial_profit(client: AlpacaClient, arguments: Dict[str, Any]) -> List[TextContent]:
    """Handle take_partial_profit tool execution."""
    log_tool_execution(logger, "take_partial_profit", arguments)
    
    try:
        symbol = arguments["symbol"].upper()
        profit_threshold = arguments.get("profit_threshold", 0.2)
        close_percentage = arguments.get("close_percentage", 0.5)
        
        # Get all positions and find the one for this symbol
        positions = client.get_all_positions()
        position = None
        
        for pos in positions:
            if pos.symbol == symbol:
                position = pos
                break
        
        if not position:
            response = f"No position found for symbol {symbol}."
            logger.warning(f"No position found for {symbol}")
            return [TextContent(type="text", text=response)]
        
        # Calculate unrealized profit percentage
        unrealized_plpc = float(position.unrealized_plpc or 0)
        
        if unrealized_plpc < profit_threshold:
            response = f"""Position for {symbol} does not meet profit threshold:
- Current profit: {unrealized_plpc:.2%}
- Required threshold: {profit_threshold:.2%}
- No action taken."""
            logger.info(f"Profit threshold not met for {symbol}: {unrealized_plpc:.2%} < {profit_threshold:.2%}")
            return [TextContent(type="text", text=response)]
        
        # Close the specified percentage of the position
        close_request = ClosePositionRequest(percentage=close_percentage)
        
        result = client.close_position(symbol, close_request)
        
        response = f"""Partial profit taken for {symbol}:
- Profit percentage: {unrealized_plpc:.2%}
- Threshold met: {profit_threshold:.2%}
- Closed percentage: {close_percentage:.2%}
- Order ID: {result.id}
- Status: {result.status}"""
        
        logger.info(f"Successfully took partial profit for {symbol}: {close_percentage:.2%} of position")
        return [TextContent(type="text", text=response)]
        
    except APIError as e:
        logger.error(f"API error taking partial profit: {e}")
        return [TextContent(type="text", text=f"Error taking partial profit: {e}")]
    except Exception as e:
        logger.error(f"Unexpected error taking partial profit: {e}")
        return [TextContent(type="text", text=f"Unexpected error: {e}")] 