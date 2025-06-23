"""Shared utility functions for Invest-Pilot MCP Server."""

from alpaca.trading.enums import OrderSide
from typing import Dict, Any
import logging

def get_order_side(side: str) -> OrderSide:
    """
    Converts a string to an Alpaca OrderSide enum.
    
    Args:
        side: Order side as string ('buy' or 'sell')
        
    Returns:
        OrderSide enum value
        
    Raises:
        ValueError: If side is not 'buy' or 'sell'
    """
    side_lower = side.lower()
    if side_lower == "buy":
        return OrderSide.BUY
    elif side_lower == "sell":
        return OrderSide.SELL
    else:
        raise ValueError(f"Invalid order side: '{side}'. Must be 'buy' or 'sell'.")

def log_tool_execution(logger: logging.Logger, tool_name: str, params: Dict[str, Any]) -> None:
    """
    Standard logging for tool execution.
    
    Args:
        logger: Logger instance
        tool_name: Name of the tool being executed
        params: Parameters passed to the tool
    """
    # Filter out sensitive information if any
    safe_params = {k: v for k, v in params.items() if k.lower() not in ['password', 'token', 'key']}
    logger.info(f"Executing {tool_name} with params: {safe_params}")

def format_currency(amount: float) -> str:
    """
    Format a float as currency string.
    
    Args:
        amount: Amount to format
        
    Returns:
        Formatted currency string
    """
    return f"${amount:.2f}"

def format_percentage(value: float) -> str:
    """
    Format a float as percentage string.
    
    Args:
        value: Value to format (as decimal, e.g., 0.25 for 25%)
        
    Returns:
        Formatted percentage string
    """
    return f"{value * 100:.2f}%" 