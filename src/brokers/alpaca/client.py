"""Alpaca broker client wrapper."""

from alpaca.trading.client import TradingClient
from alpaca.data.historical import StockHistoricalDataClient
from alpaca.trading.requests import ClosePositionRequest
from alpaca.trading.enums import QueryOrderStatus
from ...config.settings import AlpacaConfig
from ...core.exceptions import BrokerConnectionError, APIError
from ...core.logging_config import get_logger
from typing import Optional

class AlpacaClient:
    """Wrapper for Alpaca API clients with error handling and logging."""
    
    def __init__(self, config: AlpacaConfig):
        """
        Initialize Alpaca client.
        
        Args:
            config: Alpaca configuration
        """
        self.config = config
        self.logger = get_logger(f"{__name__}.AlpacaClient")
        
        try:
            # Initialize trading client
            self.trading_client = TradingClient(
                api_key=config.api_key,
                secret_key=config.secret_key,
                paper=config.paper,
                url_override=config.base_url
            )
            
            # Initialize data client
            self.data_client = StockHistoricalDataClient(
                api_key=config.api_key,
                secret_key=config.secret_key
            )
            
            self.logger.info(f"Alpaca client initialized (paper: {config.paper})")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize Alpaca client: {e}")
            raise BrokerConnectionError(f"Failed to connect to Alpaca: {e}")
    
    def get_account(self):
        """Get account information with error handling."""
        try:
            return self.trading_client.get_account()
        except Exception as e:
            self.logger.error(f"Failed to get account info: {e}")
            raise APIError(f"Failed to get account info: {e}", "alpaca", e)
    
    def get_all_positions(self):
        """Get all positions with error handling."""
        try:
            return self.trading_client.get_all_positions()
        except Exception as e:
            self.logger.error(f"Failed to get positions: {e}")
            raise APIError(f"Failed to get positions: {e}", "alpaca", e)
    
    def get_orders(self, status: QueryOrderStatus = QueryOrderStatus.ALL, limit: Optional[int] = None):
        """Get orders with error handling."""
        try:
            from alpaca.trading.requests import GetOrdersRequest
            request = GetOrdersRequest(
                status=status,
                limit=limit
            )
            return self.trading_client.get_orders(request)
        except Exception as e:
            self.logger.error(f"Failed to get orders: {e}")
            raise APIError(f"Failed to get orders: {e}", "alpaca", e)
    
    def submit_order(self, order_request):
        """Submit order with error handling."""
        try:
            return self.trading_client.submit_order(order_request)
        except Exception as e:
            self.logger.error(f"Failed to submit order: {e}")
            raise APIError(f"Failed to submit order: {e}", "alpaca", e)
    
    def cancel_all_orders(self):
        """Cancel all orders with error handling."""
        try:
            return self.trading_client.cancel_orders()
        except Exception as e:
            self.logger.error(f"Failed to cancel all orders: {e}")
            raise APIError(f"Failed to cancel all orders: {e}", "alpaca", e)
    
    def close_all_positions(self, cancel_orders: bool = True):
        """Close all positions with error handling."""
        try:
            # Use the correct method name from the Alpaca SDK
            if cancel_orders:
                # Cancel orders first, then close positions
                self.trading_client.cancel_orders()
            # Close all positions
            return self.trading_client.close_all_positions(cancel_orders=cancel_orders)
        except Exception as e:
            self.logger.error(f"Failed to close all positions: {e}")
            raise APIError(f"Failed to close all positions: {e}", "alpaca", e)
    
    def close_position(self, symbol: str, close_request: ClosePositionRequest):
        """Close position with error handling."""
        try:
            return self.trading_client.close_position(symbol, close_request)
        except Exception as e:
            self.logger.error(f"Failed to close position for {symbol}: {e}")
            raise APIError(f"Failed to close position for {symbol}: {e}", "alpaca", e)
    
    def get_latest_quote(self, symbol: str):
        """Get latest quote with error handling."""
        try:
            from alpaca.data.requests import StockLatestQuoteRequest
            request = StockLatestQuoteRequest(symbol_or_symbols=symbol)
            return self.data_client.get_stock_latest_quote(request)
        except Exception as e:
            self.logger.error(f"Failed to get quote for {symbol}: {e}")
            raise APIError(f"Failed to get quote for {symbol}: {e}", "alpaca", e)
    
    def get_stock_bars(self, symbol: str, timeframe, start, end):
        """Get stock bars with error handling."""
        try:
            from alpaca.data.requests import StockBarsRequest
            request = StockBarsRequest(
                symbol_or_symbols=symbol,
                timeframe=timeframe,
                start=start,
                end=end
            )
            return self.data_client.get_stock_bars(request)
        except Exception as e:
            self.logger.error(f"Failed to get bars for {symbol}: {e}")
            raise APIError(f"Failed to get bars for {symbol}: {e}", "alpaca", e) 