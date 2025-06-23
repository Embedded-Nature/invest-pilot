# Architecture Refactor Plan: Invest-Pilot MCP Server

## Overview

This document outlines the architectural refactoring plan to transform the current monolithic `alpaca_mcp_server.py` into a modular, extensible, and reusable codebase that can support:

1. All missing Alpaca MCP functions (16 functions)
2. Future MCP tools for other brokers/services
3. Easy maintenance and testing
4. Clear separation of concerns

## Current State Analysis

### Problems with Current Architecture
- **Monolithic Structure**: Single 500+ line file with all functionality
- **Limited Extensibility**: Hard to add new brokers or services
- **Code Duplication**: Similar patterns repeated across functions
- **Testing Challenges**: Difficult to unit test individual components
- **Maintenance Issues**: Changes require touching the main file

### Current Strengths to Preserve
- ✅ Excellent logging and error handling
- ✅ Clear function documentation
- ✅ Robust API client initialization
- ✅ Helper functions for common operations

## Proposed Architecture

### 1. Folder Structure

```
invest-pilot/
├── src/
│   ├── __init__.py
│   ├── main.py                     # Entry point and server initialization
│   ├── core/
│   │   ├── __init__.py
│   │   ├── base_client.py          # Abstract base for all MCP clients
│   │   ├── exceptions.py           # Custom exception classes
│   │   ├── logging_config.py       # Centralized logging configuration
│   │   └── utils.py                # Shared utilities
│   ├── brokers/
│   │   ├── __init__.py
│   │   ├── alpaca/
│   │   │   ├── __init__.py
│   │   │   ├── client.py           # Alpaca API client wrapper
│   │   │   ├── tools/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── account.py      # Account & position tools
│   │   │   │   ├── market_data.py  # Market data tools
│   │   │   │   ├── orders.py       # Order management tools
│   │   │   │   ├── options.py      # Options trading tools
│   │   │   │   ├── watchlists.py   # Watchlist management tools
│   │   │   │   └── corporate.py    # Corporate actions tools
│   │   │   └── models.py           # Alpaca-specific data models
│   │   └── interactive_brokers/    # Future IB integration
│   │       └── ...
│   └── config/
│       ├── __init__.py
│       └── settings.py             # Configuration management
├── tests/
│   ├── __init__.py
│   ├── unit/
│   │   ├── brokers/
│   │   │   └── alpaca/
│   │   │       └── tools/
│   │   └── core/
│   └── integration/
├── docs/
│   ├── api/                        # Auto-generated API docs
│   └── ...                         # Existing docs
├── examples/
│   ├── basic_trading.py
│   └── options_strategies.py
├── pyproject.toml
├── README.md
└── .env.example
```

### 2. Design Patterns

#### A. Plugin Architecture
- **Base MCP Client**: Abstract class defining the interface for all broker integrations
- **Broker Plugins**: Each broker (Alpaca, IB, etc.) implements the base interface
- **Tool Categories**: Logical grouping of related functions (account, orders, market data)

#### B. Factory Pattern
- **Tool Factory**: Dynamically loads and registers tools from different brokers
- **Client Factory**: Creates appropriate broker clients based on configuration

#### C. Dependency Injection
- **Service Container**: Manages dependencies between components
- **Configuration Injection**: Environment-specific settings injected at runtime

#### D. Observer Pattern
- **Event System**: For logging, monitoring, and extending functionality
- **Hook System**: Allow custom logic injection at key points

### 3. Core Components

#### A. Base Client (`src/core/base_client.py`)
```python
from abc import ABC, abstractmethod
from typing import Dict, Any, List
from mcp.server.fastmcp import FastMCP

class BaseMCPClient(ABC):
    """Abstract base class for all MCP broker clients."""
    
    def __init__(self, mcp_server: FastMCP, config: Dict[str, Any]):
        self.mcp_server = mcp_server
        self.config = config
        self.tools = {}
    
    @abstractmethod
    def initialize(self) -> None:
        """Initialize the broker client and API connections."""
        pass
    
    @abstractmethod
    def register_tools(self) -> None:
        """Register all MCP tools with the server."""
        pass
    
    @abstractmethod
    def health_check(self) -> bool:
        """Perform a health check on the broker connection."""
        pass
```

#### B. Tool Base Class (`src/core/base_tool.py`)
```python
from abc import ABC, abstractmethod
from typing import Any, Dict
import logging

class BaseTool(ABC):
    """Base class for all MCP tools."""
    
    def __init__(self, client: Any, logger: logging.Logger):
        self.client = client
        self.logger = logger
    
    @abstractmethod
    async def execute(self, **kwargs) -> str:
        """Execute the tool's main functionality."""
        pass
    
    def log_execution(self, tool_name: str, params: Dict[str, Any]) -> None:
        """Standard logging for tool execution."""
        self.logger.info(f"Executing {tool_name} with params: {params}")
```

#### C. Configuration Management (`src/config/settings.py`)
```python
from pydantic import BaseSettings
from typing import Dict, Any, Optional

class Settings(BaseSettings):
    # Environment
    environment: str = "development"
    
    # Alpaca Configuration
    alpaca_api_key: Optional[str] = None
    alpaca_secret_key: Optional[str] = None
    alpaca_paper_trading: bool = True
    
    # Future broker configs
    ib_api_key: Optional[str] = None
    # ... other brokers
    
    # Server Configuration
    log_level: str = "INFO"
    max_concurrent_requests: int = 10
    
    class Config:
        env_file = ".env"
        case_sensitive = False
```

### 4. Tool Organization

#### A. Alpaca Tools Structure
```python
# src/brokers/alpaca/tools/account.py
class AccountTools(BaseTool):
    async def get_account_info(self) -> str: ...
    async def get_positions(self) -> str: ...
    async def get_open_position(self, symbol: str) -> str: ...

# src/brokers/alpaca/tools/orders.py  
class OrderTools(BaseTool):
    async def place_market_order(self, symbol: str, side: str, quantity: float) -> str: ...
    async def place_limit_order(self, symbol: str, side: str, quantity: float, limit_price: float) -> str: ...
    async def place_stock_order(self, symbol: str, side: str, quantity: float, order_type: str, **kwargs) -> str: ...
    async def cancel_order_by_id(self, order_id: str) -> str: ...
    async def cancel_all_orders(self) -> str: ...

# src/brokers/alpaca/tools/options.py
class OptionsTools(BaseTool):
    async def get_option_contracts(self, underlying_symbol: str, expiration_date: str) -> str: ...
    async def get_option_latest_quote(self, option_symbol: str) -> str: ...
    async def get_option_snapshot(self, symbols: str) -> str: ...
    async def place_option_market_order(self, legs: str, order_class: str, quantity: int) -> str: ...
```

#### B. Tool Registration System
```python
# src/brokers/alpaca/client.py
class AlpacaMCPClient(BaseMCPClient):
    def register_tools(self) -> None:
        # Account tools
        account_tools = AccountTools(self.trading_client, self.logger)
        self.mcp_server.tool()(account_tools.get_account_info)
        self.mcp_server.tool()(account_tools.get_positions)
        
        # Order tools  
        order_tools = OrderTools(self.trading_client, self.logger)
        self.mcp_server.tool()(order_tools.place_market_order)
        # ... register all tools
```

### 5. Entry Point Refactor (`src/main.py`)
```python
from src.core.logging_config import setup_logging
from src.config.settings import Settings
from src.brokers.alpaca.client import AlpacaMCPClient
from mcp.server.fastmcp import FastMCP

def create_server() -> FastMCP:
    # Load configuration
    settings = Settings()
    
    # Setup logging
    logger = setup_logging(settings.log_level)
    
    # Create MCP server
    mcp = FastMCP("invest-pilot", "Multi-Broker Trading MCP Server")
    
    # Initialize broker clients
    if settings.alpaca_api_key:
        alpaca_client = AlpacaMCPClient(mcp, settings.dict())
        alpaca_client.initialize()
        alpaca_client.register_tools()
    
    # Future: Add other brokers
    # if settings.ib_api_key:
    #     ib_client = InteractiveBrokersMCPClient(mcp, settings.dict())
    
    return mcp

if __name__ == "__main__":
    server = create_server()
    server.run(transport='stdio')
```

### 6. Main Server File Strategy

#### Current File: `alpaca_mcp_server.py`
**Option A: Replace (Recommended)**
- Rename current file to `alpaca_mcp_server_legacy.py`
- Replace with a simple import wrapper:
```python
# alpaca_mcp_server.py - Backward compatibility wrapper
from src.main import create_server

if __name__ == "__main__":
    server = create_server()
    server.run(transport='stdio')
```

**Option B: Keep Both**
- Keep current `alpaca_mcp_server.py` unchanged
- Add new `src/main.py` as the primary entry point
- Update documentation to use new entry point

#### New Primary Entry Point: `src/main.py`
This becomes the main server file that:
- Loads configuration from environment/settings
- Initializes the MCP server
- Discovers and loads broker plugins
- Registers all tools from active brokers
- Starts the server

#### Additional Entry Points
```
invest-pilot/
├── alpaca_mcp_server.py        # Legacy compatibility or simple wrapper
├── src/
│   ├── main.py                 # Primary entry point
│   └── cli.py                  # Optional: CLI commands for management
└── pyproject.toml              # Can specify entry points here
```

#### PyProject.toml Entry Points
```toml
[project.scripts]
invest-pilot = "src.main:main"
alpaca-mcp = "alpaca_mcp_server:main"  # Legacy support

[project.entry-points."mcp.servers"]
invest-pilot = "src.main:create_server"
```

## Implementation Strategy

### Phase 1: Foundation (Week 1)
1. Create the new folder structure
2. Implement core base classes and utilities
3. Move existing functionality to new structure
4. Ensure all current tools still work

### Phase 2: Missing Alpaca Functions (Week 2-3)
1. Implement high-priority missing functions:
   - `get_open_position(symbol)`
   - `close_position(symbol, qty/percentage)`
   - `cancel_order_by_id(order_id)`
   - `place_stock_order(...)` (unified order placement)

2. Add options trading tools:
   - `get_option_contracts(...)`
   - `get_option_latest_quote(...)`
   - `get_option_snapshot(...)`
   - `place_option_market_order(...)`

### Phase 3: Market Intelligence (Week 4)
1. Market information tools:
   - `get_market_clock()`
   - `get_market_calendar(...)`
   - `get_corporate_announcements(...)`

2. Watchlist management:
   - `create_watchlist(...)`
   - `update_watchlist(...)`
   - `get_watchlists()`

### Phase 4: Polish & Documentation (Week 5)
1. Add comprehensive tests
2. Generate API documentation
3. Create usage examples
4. Performance optimization

## Benefits of This Architecture

### Extensibility
- **New Brokers**: Easy to add Interactive Brokers, TD Ameritrade, etc.
- **New Tool Categories**: Simple to add crypto, forex, or other asset classes
- **Plugin System**: Third-party developers can add tools

### Maintainability
- **Separation of Concerns**: Each tool category in its own module
- **Single Responsibility**: Each class has one clear purpose
- **Easy Testing**: Individual components can be unit tested

### Reusability
- **Shared Core**: Common functionality across all brokers
- **Tool Templates**: New tools follow established patterns
- **Configuration Management**: Environment-specific settings

### Performance
- **Lazy Loading**: Only load tools for configured brokers
- **Connection Pooling**: Shared API client instances
- **Caching**: Cache frequently accessed data

## Migration Strategy

### Backward Compatibility
- Keep the current `alpaca_mcp_server.py` as a legacy fallback
- Provide a migration guide for existing users
- Ensure all existing functionality works identically

### Testing Strategy
- Unit tests for each tool class
- Integration tests for broker clients
- End-to-end tests for complete workflows
- Performance benchmarks

## Questions for Confirmation

1. **Folder Structure**: Do you approve of the proposed folder structure?
2. **Design Patterns**: Are you comfortable with the plugin architecture approach?
3. **Migration Strategy**: Should we maintain backward compatibility during the transition?
4. **Implementation Timeline**: Does the 5-week phased approach work for your timeline?
5. **Additional Requirements**: Are there any specific requirements or constraints I should consider?

## Next Steps

Upon your approval, I will:
1. Create the new folder structure
2. Implement the core base classes
3. Migrate existing functionality to the new architecture
4. Begin implementing the missing high-priority functions

This architecture will position Invest-Pilot as a robust, extensible platform for AI-driven trading across multiple brokers and asset classes. 