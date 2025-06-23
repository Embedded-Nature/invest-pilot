"""Order-related tools for Alpaca broker."""

import json
from mcp.types import TextContent
from alpaca.trading.requests import (
    MarketOrderRequest, LimitOrderRequest, ClosePositionRequest, 
    OrderRequest, TakeProfitRequest, StopLossRequest, TrailingStopOrderRequest
)
from alpaca.trading.enums import (
    QueryOrderStatus, TimeInForce, OrderClass, OrderType, OrderSide
)
from ..client import AlpacaClient
from ....core.logging_config import get_logger
from ....core.utils import log_tool_execution, get_order_side, format_currency
from ....core.exceptions import APIError
from typing import Dict, Any, List, Optional

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
                    "order_class": order.order_class,
                    "status": order.status,
                    "limit_price": float(order.limit_price) if order.limit_price else None,
                    "stop_price": float(order.stop_price) if order.stop_price else None,
                    "avg_fill_price": float(order.filled_avg_price) if order.filled_avg_price else None,
                    "trail_price": float(order.trail_price) if order.trail_price else None,
                    "trail_percent": float(order.trail_percent) if order.trail_percent else None,
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


# =====================================================
# ADVANCED ORDERS - New Implementation
# =====================================================

async def handle_place_bracket_order(client: AlpacaClient, arguments: Dict[str, Any]) -> List[TextContent]:
    """Handle place_bracket_order tool execution."""
    log_tool_execution(logger, "place_bracket_order", arguments)
    
    try:
        symbol = arguments["symbol"].upper()
        side = get_order_side(arguments["side"])
        quantity = arguments["quantity"]
        order_type = arguments.get("order_type", "market").lower()
        limit_price = arguments.get("limit_price")
        take_profit_price = arguments["take_profit_price"]
        stop_loss_price = arguments["stop_loss_price"]
        stop_loss_limit_price = arguments.get("stop_loss_limit_price")
        time_in_force_str = arguments.get("time_in_force", "gtc").upper()
        
        # Validate required parameters
        if order_type == "limit" and not limit_price:
            raise ValueError("limit_price is required for limit orders")
        
        # Convert time_in_force
        time_in_force = TimeInForce.GTC if time_in_force_str == "GTC" else TimeInForce.DAY
        
        # Convert order type
        alpaca_order_type = OrderType.MARKET if order_type == "market" else OrderType.LIMIT
        
        # Create take profit and stop loss requests
        take_profit = TakeProfitRequest(limit_price=take_profit_price)
        
        if stop_loss_limit_price:
            stop_loss = StopLossRequest(stop_price=stop_loss_price, limit_price=stop_loss_limit_price)
        else:
            stop_loss = StopLossRequest(stop_price=stop_loss_price)
        
        # Create bracket order request using specific order request types
        if order_type == "limit":
            order_request = LimitOrderRequest(
                symbol=symbol,
                qty=quantity,
                side=side,
                limit_price=limit_price,
                time_in_force=time_in_force,
                order_class=OrderClass.BRACKET,
                take_profit=take_profit,
                stop_loss=stop_loss
            )
        else:
            order_request = MarketOrderRequest(
                symbol=symbol,
                qty=quantity,
                side=side,
                time_in_force=time_in_force,
                order_class=OrderClass.BRACKET,
                take_profit=take_profit,
                stop_loss=stop_loss
            )
        
        order = client.submit_order(order_request)
        
        response = f"""Bracket order placed successfully:
- Order ID: {order.id}
- Symbol: {order.symbol}
- Side: {order.side}
- Quantity: {order.qty}
- Order Type: {order.order_type}
- Order Class: {order.order_class}
- Take Profit Price: {format_currency(take_profit_price)}
- Stop Loss Price: {format_currency(stop_loss_price)}
- Status: {order.status}
- Submitted At: {order.submitted_at}"""
        
        if limit_price:
            response += f"\n- Entry Limit Price: {format_currency(limit_price)}"
        if stop_loss_limit_price:
            response += f"\n- Stop Loss Limit Price: {format_currency(stop_loss_limit_price)}"
        
        logger.info(f"Successfully placed bracket order: {symbol} {side} {quantity}")
        return [TextContent(type="text", text=response)]
        
    except ValueError as e:
        logger.error(f"Invalid parameters for bracket order: {e}")
        return [TextContent(type="text", text=f"Invalid parameters: {e}")]
    except APIError as e:
        logger.error(f"API error placing bracket order: {e}")
        return [TextContent(type="text", text=f"Error placing bracket order: {e}")]
    except Exception as e:
        logger.error(f"Unexpected error placing bracket order: {e}")
        return [TextContent(type="text", text=f"Unexpected error: {e}")]


async def handle_place_oco_order(client: AlpacaClient, arguments: Dict[str, Any]) -> List[TextContent]:
    """Handle place_oco_order tool execution."""
    log_tool_execution(logger, "place_oco_order", arguments)
    
    try:
        symbol = arguments["symbol"].upper()
        quantity = arguments["quantity"]
        take_profit_price = arguments["take_profit_price"]
        stop_loss_price = arguments["stop_loss_price"]
        stop_loss_limit_price = arguments.get("stop_loss_limit_price")
        time_in_force_str = arguments.get("time_in_force", "gtc").upper()
        
        # Convert time_in_force
        time_in_force = TimeInForce.GTC if time_in_force_str == "GTC" else TimeInForce.DAY
        
        # Create take profit and stop loss requests
        take_profit = TakeProfitRequest(limit_price=take_profit_price)
        
        if stop_loss_limit_price:
            stop_loss = StopLossRequest(stop_price=stop_loss_price, limit_price=stop_loss_limit_price)
        else:
            stop_loss = StopLossRequest(stop_price=stop_loss_price)
        
        # OCO orders are always sell orders for existing positions using limit order
        order_request = LimitOrderRequest(
            symbol=symbol,
            qty=quantity,
            side=OrderSide.SELL,
            limit_price=take_profit_price,  # Use take profit as the limit price
            time_in_force=time_in_force,
            order_class=OrderClass.OCO,
            take_profit=take_profit,
            stop_loss=stop_loss
        )
        
        order = client.submit_order(order_request)
        
        response = f"""OCO order placed successfully:
- Order ID: {order.id}
- Symbol: {order.symbol}
- Side: {order.side}
- Quantity: {order.qty}
- Order Class: {order.order_class}
- Take Profit Price: {format_currency(take_profit_price)}
- Stop Loss Price: {format_currency(stop_loss_price)}
- Status: {order.status}
- Submitted At: {order.submitted_at}"""
        
        if stop_loss_limit_price:
            response += f"\n- Stop Loss Limit Price: {format_currency(stop_loss_limit_price)}"
        
        logger.info(f"Successfully placed OCO order: {symbol} sell {quantity}")
        return [TextContent(type="text", text=response)]
        
    except APIError as e:
        logger.error(f"API error placing OCO order: {e}")
        return [TextContent(type="text", text=f"Error placing OCO order: {e}")]
    except Exception as e:
        logger.error(f"Unexpected error placing OCO order: {e}")
        return [TextContent(type="text", text=f"Unexpected error: {e}")]


async def handle_place_oto_order(client: AlpacaClient, arguments: Dict[str, Any]) -> List[TextContent]:
    """Handle place_oto_order tool execution."""
    log_tool_execution(logger, "place_oto_order", arguments)
    
    try:
        symbol = arguments["symbol"].upper()
        side = get_order_side(arguments["side"])
        quantity = arguments["quantity"]
        order_type = arguments.get("order_type", "market").lower()
        limit_price = arguments.get("limit_price")
        take_profit_price = arguments.get("take_profit_price")
        stop_loss_price = arguments.get("stop_loss_price")
        stop_loss_limit_price = arguments.get("stop_loss_limit_price")
        time_in_force_str = arguments.get("time_in_force", "gtc").upper()
        
        # Validate that exactly one of take_profit_price or stop_loss_price is provided
        if not ((take_profit_price is None) ^ (stop_loss_price is None)):
            raise ValueError("Must provide exactly one of take_profit_price or stop_loss_price for OTO orders")
        
        # Validate required parameters
        if order_type == "limit" and not limit_price:
            raise ValueError("limit_price is required for limit orders")
        
        # Convert time_in_force and order type
        time_in_force = TimeInForce.GTC if time_in_force_str == "GTC" else TimeInForce.DAY
        alpaca_order_type = OrderType.MARKET if order_type == "market" else OrderType.LIMIT
        
        # Create the exit order (either take profit or stop loss)
        exit_order = None
        exit_description = ""
        
        if take_profit_price:
            exit_order = TakeProfitRequest(limit_price=take_profit_price)
            exit_description = f"Take Profit Price: {format_currency(take_profit_price)}"
        else:
            if stop_loss_limit_price:
                exit_order = StopLossRequest(stop_price=stop_loss_price, limit_price=stop_loss_limit_price)
                exit_description = f"Stop Loss Price: {format_currency(stop_loss_price)}, Limit: {format_currency(stop_loss_limit_price)}"
            else:
                exit_order = StopLossRequest(stop_price=stop_loss_price)
                exit_description = f"Stop Loss Price: {format_currency(stop_loss_price)}"
        
        # Create OTO order request using specific order request types
        common_kwargs = {
            "symbol": symbol,
            "qty": quantity,
            "side": side,
            "time_in_force": time_in_force,
            "order_class": OrderClass.OTO
        }
        
        # Add the appropriate exit order
        if take_profit_price:
            common_kwargs["take_profit"] = exit_order
        else:
            common_kwargs["stop_loss"] = exit_order
        
        # Create order request based on type
        if order_type == "limit":
            order_request = LimitOrderRequest(
                limit_price=limit_price,
                **common_kwargs
            )
        else:
            order_request = MarketOrderRequest(**common_kwargs)
        
        order = client.submit_order(order_request)
        
        response = f"""OTO order placed successfully:
- Order ID: {order.id}
- Symbol: {order.symbol}
- Side: {order.side}
- Quantity: {order.qty}
- Order Type: {order.order_type}
- Order Class: {order.order_class}
- {exit_description}
- Status: {order.status}
- Submitted At: {order.submitted_at}"""
        
        if limit_price:
            response += f"\n- Entry Limit Price: {format_currency(limit_price)}"
        
        logger.info(f"Successfully placed OTO order: {symbol} {side} {quantity}")
        return [TextContent(type="text", text=response)]
        
    except ValueError as e:
        logger.error(f"Invalid parameters for OTO order: {e}")
        return [TextContent(type="text", text=f"Invalid parameters: {e}")]
    except APIError as e:
        logger.error(f"API error placing OTO order: {e}")
        return [TextContent(type="text", text=f"Error placing OTO order: {e}")]
    except Exception as e:
        logger.error(f"Unexpected error placing OTO order: {e}")
        return [TextContent(type="text", text=f"Unexpected error: {e}")]


async def handle_place_trailing_stop_order(client: AlpacaClient, arguments: Dict[str, Any]) -> List[TextContent]:
    """Handle place_trailing_stop_order tool execution."""
    log_tool_execution(logger, "place_trailing_stop_order", arguments)
    
    try:
        symbol = arguments["symbol"].upper()
        side = get_order_side(arguments["side"])
        quantity = arguments["quantity"]
        trail_type = arguments["trail_type"].lower()
        trail_amount = arguments["trail_amount"]
        time_in_force_str = arguments.get("time_in_force", "day").upper()
        
        # Validate trail_type
        if trail_type not in ["price", "percent"]:
            raise ValueError("trail_type must be 'price' or 'percent'")
        
        # Convert time_in_force
        time_in_force = TimeInForce.GTC if time_in_force_str == "GTC" else TimeInForce.DAY
        
        # Create trailing stop order request
        if trail_type == "price":
            order_request = TrailingStopOrderRequest(
                symbol=symbol,
                qty=quantity,
                side=side,
                time_in_force=time_in_force,
                trail_price=trail_amount
            )
            trail_description = f"Trail Amount: ${trail_amount}"
        else:  # percent
            order_request = TrailingStopOrderRequest(
                symbol=symbol,
                qty=quantity,
                side=side,
                time_in_force=time_in_force,
                trail_percent=trail_amount
            )
            trail_description = f"Trail Percentage: {trail_amount * 100:.2f}%"
        
        order = client.submit_order(order_request)
        
        response = f"""Trailing stop order placed successfully:
- Order ID: {order.id}
- Symbol: {order.symbol}
- Side: {order.side}
- Quantity: {order.qty}
- Order Type: {order.order_type}
- {trail_description}
- Time in Force: {time_in_force}
- Status: {order.status}
- Submitted At: {order.submitted_at}"""
        
        logger.info(f"Successfully placed trailing stop order: {symbol} {side} {quantity}")
        return [TextContent(type="text", text=response)]
        
    except ValueError as e:
        logger.error(f"Invalid parameters for trailing stop order: {e}")
        return [TextContent(type="text", text=f"Invalid parameters: {e}")]
    except APIError as e:
        logger.error(f"API error placing trailing stop order: {e}")
        return [TextContent(type="text", text=f"Error placing trailing stop order: {e}")]
    except Exception as e:
        logger.error(f"Unexpected error placing trailing stop order: {e}")
        return [TextContent(type="text", text=f"Unexpected error: {e}")] 