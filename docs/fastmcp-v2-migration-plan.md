# FastMCP v2 Migration Plan

## Overview

Based on the [FastMCP v2 repository](https://github.com/jlowin/fastmcp), we need to migrate from our current implementation to the modern FastMCP v2 API. This migration will solve our server connection issues and provide a cleaner, more maintainable codebase.

## Current Issues

1. **Server not staying running**: Our current `main.py` exits after initialization instead of blocking and waiting for connections
2. **Outdated FastMCP usage**: We're using patterns that don't align with FastMCP v2's simpler API
3. **Complex initialization**: Our current approach has unnecessary complexity for client initialization

## FastMCP v2 Key Improvements

### 1. **Simplified Server Creation**
```python
from fastmcp import FastMCP

mcp = FastMCP("invest-pilot")

@mcp.tool()
def tool_name(param: str) -> str:
    """Tool description."""
    return result

if __name__ == "__main__":
    mcp.run()  # Automatically handles STDIO transport and blocks
```

### 2. **Built-in Context Support**
```python
from fastmcp import FastMCP, Context

@mcp.tool()
async def tool_name(param: str, ctx: Context) -> str:
    await ctx.info("Processing...")
    return result
```

### 3. **Automatic Transport Detection**
- Default STDIO transport for MCP clients
- No manual server setup required
- `mcp.run()` handles everything automatically

## Migration Strategy

### Phase 1: Core FastMCP v2 Conversion (1-2 hours)

1. **Update Dependencies**
   - Upgrade to FastMCP v2 in `pyproject.toml`
   - Remove any outdated MCP dependencies

2. **Simplify Main Entry Point**
   - Replace complex initialization with simple FastMCP v2 pattern
   - Remove manual client management
   - Use `@mcp.tool()` decorators directly

3. **Update Tool Definitions**
   - Convert from handler functions to direct tool functions
   - Use FastMCP v2's automatic parameter handling
   - Add proper type hints and docstrings

### Phase 2: Architecture Cleanup (1 hour)

1. **Streamline Folder Structure**
   - Keep modular broker structure but simplify interfaces
   - Remove unnecessary abstraction layers
   - Focus on Alpaca implementation

2. **Simplify Client Management**
   - Use FastMCP v2's built-in client handling
   - Remove custom client initialization
   - Leverage context injection for API calls

### Phase 3: Enhanced Features (Optional)

1. **Add Context Usage**
   - Use `ctx.info()` for better logging to MCP clients
   - Implement progress reporting for long operations
   - Add error handling with context

2. **Testing Integration**
   - Use FastMCP v2's in-memory testing capabilities
   - Add unit tests with Client(mcp) pattern

## Detailed Implementation Plan

### 1. New Main Entry Point Structure

```python
"""
Invest-Pilot MCP Server - FastMCP v2
"""
from fastmcp import FastMCP, Context
from src.brokers.alpaca.client import AlpacaClient
from src.config.settings import load_alpaca_config

# Initialize server
mcp = FastMCP("invest-pilot")

# Global client - initialized lazily
_alpaca_client = None

def get_alpaca_client() -> AlpacaClient:
    global _alpaca_client
    if _alpaca_client is None:
        config = load_alpaca_config()
        _alpaca_client = AlpacaClient(config)
    return _alpaca_client

@mcp.tool()
async def ping(ctx: Context) -> str:
    """Test if the server is responding."""
    await ctx.info("Pinging server...")
    return "Pong! Server is running."

@mcp.tool()
async def get_account_info(ctx: Context) -> str:
    """Get the current account information including balances and status."""
    await ctx.info("Fetching account information...")
    client = get_alpaca_client()
    # Implementation here
    return result

# ... other tools

if __name__ == "__main__":
    mcp.run()
```

### 2. Simplified Tool Implementation

Instead of our current handler pattern:
```python
# OLD - Complex handler pattern
async def handle_get_account_info(client: AlpacaClient, args: Dict[str, Any]) -> List[TextContent]:
    # Complex implementation
    return [TextContent(type="text", text=json.dumps(result, indent=2))]
```

New FastMCP v2 pattern:
```python
# NEW - Direct tool function
@mcp.tool()
async def get_account_info(ctx: Context) -> str:
    """Get the current account information including balances and status."""
    await ctx.info("Fetching account information...")
    client = get_alpaca_client()
    account = client.get_account()
    return f"Account: {account.status}\nBuying Power: ${account.buying_power}\nCash: ${account.cash}"
```

### 3. Updated Dependencies

```toml
[dependencies]
fastmcp = "^2.8.0"  # Latest FastMCP v2
alpaca-py = "^0.30.1"
pydantic = "^2.0.0"
python-dotenv = "^1.0.0"
```

## Benefits of Migration

1. **Fixes Connection Issues**: FastMCP v2's `mcp.run()` properly blocks and waits for connections
2. **Cleaner Code**: Eliminates complex handler patterns and manual client management
3. **Better Error Handling**: Built-in context for logging and error reporting to MCP clients
4. **Easier Testing**: In-memory client testing capabilities
5. **Future-Proof**: Aligns with modern MCP development patterns

## File Changes Required

### Files to Modify:
- `src/main.py` - Complete rewrite using FastMCP v2 patterns
- `pyproject.toml` - Update dependencies
- Tool modules - Simplify to return strings directly instead of TextContent objects

### Files to Keep:
- `src/brokers/alpaca/client.py` - Core Alpaca client wrapper
- `src/config/settings.py` - Configuration management
- `src/core/exceptions.py` - Custom exceptions
- All documentation in `docs/`

### Files to Remove:
- Complex handler functions in tool modules (replace with direct tool functions)

## Testing Plan

1. **Local Testing**: Use `uv run src/main.py` to verify server starts and stays running
2. **MCP Inspector**: Test all tools work correctly in MCP inspector
3. **Cursor Integration**: Verify Cursor can connect and use tools
4. **Unit Tests**: Add FastMCP v2 in-memory testing

## Timeline

- **Phase 1**: 1-2 hours - Core migration and connection fix
- **Phase 2**: 1 hour - Architecture cleanup
- **Testing**: 30 minutes - Verify all tools work

**Total Estimated Time**: 2-3 hours

## Next Steps

1. **Approval**: Wait for user confirmation to proceed
2. **Dependencies**: Update `pyproject.toml` with FastMCP v2
3. **Main Migration**: Rewrite `src/main.py` with new pattern
4. **Tool Migration**: Convert all tools to direct functions
5. **Testing**: Verify server runs and connects properly

This migration will solve our current connection issues and provide a much cleaner, more maintainable codebase aligned with modern MCP development practices. 