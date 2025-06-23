"""Custom exceptions for Invest-Pilot MCP Server."""

class InvestPilotError(Exception):
    """Base exception class for Invest-Pilot errors."""
    pass

class BrokerConnectionError(InvestPilotError):
    """Raised when there's an issue connecting to a broker API."""
    pass

class InvalidConfigurationError(InvestPilotError):
    """Raised when configuration is invalid or missing."""
    pass

class ToolExecutionError(InvestPilotError):
    """Raised when a tool fails to execute properly."""
    pass

class APIError(InvestPilotError):
    """Raised when broker API returns an error."""
    def __init__(self, message: str, broker: str, api_error: Exception = None):
        super().__init__(message)
        self.broker = broker
        self.api_error = api_error 