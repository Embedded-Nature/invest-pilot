# Troubleshooting Guide for Alpaca MCP Server

This guide covers common issues encountered when setting up and running the Alpaca MCP server, particularly focusing on environment setup and configuration issues.

## Common Errors and Solutions

### 1. "Failed to spawn: `alpaca-py`" / "ENOENT Error"

**Error Message:**
```
error: Failed to spawn: `alpaca-py`
Caused by: No such file or directory (os error 2)
```

**Solutions:**
1. **Use Full Paths**: On macOS, use absolute paths in your configuration:
```json
{
  "command": "/Users/username/.local/bin/uv",
  "args": [
    "run",
    "--with",
    "mcp[cli]>=1.2.0",
    "alpaca-py",
    "python-dotenv",
    "--",
    "python",
    "/absolute/path/to/alpaca_mcp_server.py"
  ]
}
```

2. **Use Virtual Environment**: Set up and use a virtual environment:
```bash
# Create and activate virtual environment
uv venv
source .venv/bin/activate

# Install required packages
uv pip install "mcp[cli]>=1.2.0" alpaca-py python-dotenv
```

### 2. "ModuleNotFoundError: No module named 'mcp'"

**Solutions:**
1. **Install Required Packages**:
```bash
uv pip install "mcp[cli]>=1.2.0" alpaca-py python-dotenv
```

2. **Verify Installation**:
```bash
uv pip list | grep -E "alpaca|mcp|python-dotenv"
```

## Running the Server Locally

### 1. Basic Setup

```bash
# Create virtual environment
uv venv

# Activate virtual environment
source .venv/bin/activate

# Install dependencies
uv pip install "mcp[cli]>=1.2.0" alpaca-py python-dotenv
```

### 2. Test Server Locally

```bash
# Direct Python execution
python -u alpaca_mcp_server.py

# Or using MCP CLI
mcp c stdio "python alpaca_mcp_server.py" repl
```

## Configuration Files

### 1. Claude Desktop Configuration

```json
{
  "mcpServers": {
    "alpaca-trading": {
      "command": "python",
      "args": [
        "-u",
        "alpaca_mcp_server.py"
      ],
      "env": {
        "API_KEY_ID": "your_key",
        "API_SECRET_KEY": "your_secret",
        "PYTHONUNBUFFERED": "1",
        "VIRTUAL_ENV": "${workspaceFolder}/alpaca_agent/.venv",
        "PATH": "${workspaceFolder}/alpaca_agent/.venv/bin:${env:PATH}"
      },
      "cwd": "${workspaceFolder}/alpaca-mcp-server",
      "transport": "stdio"
    }
  }
}
```

### 2. Environment Variables

Create a `.env` file in your project root:
```env
API_KEY_ID=your_alpaca_api_key
API_SECRET_KEY=your_alpaca_secret_key
```

## Best Practices

1. **Virtual Environment**:
   - Always use a virtual environment
   - Activate it before running the server
   - Keep it separate from other Python projects

2. **Path Management**:
   - Use absolute paths in configurations
   - Include virtual environment in PATH
   - Set PYTHONPATH appropriately

3. **Debugging**:
   - Use `-u` flag with Python for unbuffered output
   - Set PYTHONUNBUFFERED=1 in environment
   - Enable logging in the server code

## Server Verification

To verify your server is working:

1. **Check Dependencies**:
```bash
uv pip list | grep -E "alpaca|mcp|python-dotenv"
```

2. **Test Connection**:
```bash
mcp c stdio "python alpaca_mcp_server.py" call ping
```

3. **Check Account**:
```bash
mcp c stdio "python alpaca_mcp_server.py" call get_account_info
```

## Common Pitfalls

1. **UV Installation**: Make sure `uv` is installed and in your PATH
2. **Python Version**: Use Python 3.10 or higher
3. **Package Conflicts**: Use a clean virtual environment
4. **Path Issues**: Use absolute paths in configurations
5. **Environment Variables**: Ensure they're properly set and accessible

## Additional Resources

- [MCP Documentation](https://modelcontextprotocol.io/docs/tools/debugging)
- [Alpaca API Documentation](https://alpaca.markets/docs/api-references/)
- [UV Documentation](https://github.com/astral-sh/uv)