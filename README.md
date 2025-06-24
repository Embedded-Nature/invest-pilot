# Invest-Pilot MCP Server

Model Context Protocol (MCP) server for trading stocks, checking positions, fetching market data, and managing your account with Alpaca. Built with a **modular architecture** for extensibility and maintainability.

## ✨ Features

- 📊 **Market Data** - Get real-time stock quotes and historical price data
- 💵 **Account Information** - Check your balances, buying power, and status
- 📈 **Position Management** - View current positions and their performance
- 🛒 **Order Placement** - Place market and limit orders through natural language
- 📋 **Order Management** - List, track, and cancel orders
- 💸 **Automated Profit-Taking** - Take partial profits when positions reach a certain threshold
- 🏗️ **Modular Architecture** - Clean, extensible codebase ready for multi-broker support
- 🔧 **Comprehensive Error Handling** - Robust API error handling and logging
- 🧪 **Development Tools** - Built-in MCP Inspector support for testing

## 🏗️ Architecture

The server features a **modular architecture** designed for scalability:

```
invest-pilot/
├── src/
│   ├── main.py                    # New modular entry point
│   ├── core/                      # Shared utilities
│   │   ├── exceptions.py          # Custom exception classes
│   │   ├── logging_config.py      # Centralized logging
│   │   └── utils.py               # Shared utility functions
│   ├── brokers/alpaca/            # Alpaca-specific implementation
│   │   ├── client.py              # API client wrapper
│   │   └── tools/                 # Organized tool modules
│   │       ├── account.py         # Account-related tools
│   │       ├── orders.py          # Order management tools
│   │       └── market_data.py     # Market data tools
│   └── config/                    # Configuration management
│       └── settings.py            # Environment-based settings
├── alpaca_mcp_server.py          # Legacy entry point (backward compatible)
└── tests/                        # Test framework (ready for expansion)
```

## 📋 Prerequisites

- Python 3.10+
- [uv](https://github.com/astral-sh/uv) (for environment and package management)
- Alpaca API keys
- An MCP client (e.g., Claude for Desktop)

## 🚀 Installation

1.  Clone this repository:
   ```bash
    git clone https://github.com/Embedded-Nature/invest-pilot.git
    cd invest-pilot
   ```

2.  Create a virtual environment and install dependencies using `uv`:
   ```bash
    uv venv
    source .venv/bin/activate  # On Windows: .venv\Scripts\activate
    uv pip install -e .
    ```

3.  Set up your environment variables:
    ```bash
    # Create .env file or set environment variables directly
    export ALPACA_API_KEY="your_paper_api_key_id"
    export ALPACA_SECRET_KEY="your_paper_api_secret_key"
    export ALPACA_PAPER="true"  # Set to "false" for live trading
    export LOG_LEVEL="INFO"     # Optional: DEBUG, INFO, WARNING, ERROR
   ```

## 🎯 Usage

### Running the Server

**For production use (direct server):**
```bash
uv run src/main.py
```

**For development and testing (with MCP Inspector):**
```bash
uv run mcp dev mcp_dev_adapter.py
```

The inspector runs at `http://localhost:6274` and provides a web interface to test all tools interactively. Look for the URL with the pre-filled authentication token in the terminal output.

> **Note**: We use `mcp_dev_adapter.py` which bridges our FastMCP 2 server with the official MCP development tools, giving you the best of both worlds: modern FastMCP features with the beautiful MCP inspector UI.

### Configuring with an MCP Client

To connect the server to a client like Claude for Desktop:

**Example `claude_desktop_config.json`:**
```json
{
  "mcpServers": {
    "invest-pilot": {
      "command": "/path/to/your/uv/executable",
      "args": [
        "run",
        "src/main.py"
      ],
      "cwd": "/path/to/your/invest-pilot",
      "env": {
        "ALPACA_API_KEY": "your_paper_api_key_id",
        "ALPACA_SECRET_KEY": "your_paper_api_secret_key",
        "ALPACA_PAPER": "true"
      }
    }
  }
}
```

**Note**: Replace paths with absolute paths on your system. You can set environment variables either in the config or in a `.env` file.

## 🛠️ Available Tools

The server exposes **11 tools** organized by functionality:

### 🏥 Health & Status
- `ping()` - Test if the server is responsive

### 💰 Account Management
- `get_account_info()` - Get account balances and status
- `get_positions()` - List all current positions in the portfolio

### 📊 Market Data
- `get_stock_quote(symbol)` - Get the latest quote for a stock
- `get_stock_bars(symbol, days=5)` - Get historical price bars for a stock

### 📋 Order Management
- `get_orders(status="all", limit=10)` - List orders with specified status
- `place_market_order(symbol, side, quantity)` - Place a market order
- `place_limit_order(symbol, side, quantity, limit_price)` - Place a limit order
- `cancel_all_orders()` - Cancel all open orders
- `close_all_positions(cancel_orders=True)` - Close all open positions

### 💸 Advanced Features
- `take_partial_profit(symbol, profit_threshold=0.2, close_percentage=0.5)` - Automated profit-taking

## 💬 Example Queries

Once connected, you can use natural language to manage your trading account:

**Basic Operations:**
- "Can you ping the Alpaca server?"
- "What's my current account balance and buying power?"
- "Show me my current positions."

**Market Data:**
- "Get the latest quote for AAPL."
- "Show me the price history for TSLA over the last 10 days."

**Trading:**
- "Buy 5 shares of MSFT at market price."
- "Sell 10 shares of AMZN with a limit price of $130."
- "Cancel all my open orders."

**Advanced:**
- "If my NVDA position is up by more than 25%, sell half of it."
- "Take partial profit on my AAPL shares if they're up 20% or more."

## 🔧 Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `ALPACA_API_KEY` | Your Alpaca API key | **Required** |
| `ALPACA_SECRET_KEY` | Your Alpaca secret key | **Required** |
| `ALPACA_PAPER` | Use paper trading (true/false) | `true` |
| `ALPACA_BASE_URL` | Custom Alpaca base URL | Auto-detected |
| `LOG_LEVEL` | Logging level | `INFO` |

### Logging

The server includes comprehensive logging:
- **INFO**: General operations and successful actions
- **WARNING**: Non-critical issues
- **ERROR**: API errors and failures
- **DEBUG**: Detailed execution information

## 🔒 Security Notice

This MCP server has access to your Alpaca trading account and can execute real trades. By default, it runs in **paper trading mode**. 

**⚠️ Important**: If you switch to live trading (`ALPACA_PAPER=false`), carefully review every suggested action from your AI assistant before approval. The authors are not responsible for any financial losses.

## 🧪 Development

### Architecture Benefits

The modular architecture provides:
- **Extensibility**: Easy to add new brokers or tools
- **Maintainability**: Clear separation of concerns
- **Testability**: Isolated components for unit testing
- **Scalability**: Plugin-based design for future features

### Development Workflow

**Using the MCP Inspector for Testing:**
```bash
uv run mcp dev mcp_dev_adapter.py
```

This command:
1. Starts your FastMCP 2 server through the adapter
2. Launches the official MCP Inspector at `http://localhost:6274`
3. Provides real-time testing of all tools with a beautiful web UI
4. Shows authentication tokens and connection details

The `mcp_dev_adapter.py` bridges FastMCP 2 with the official MCP development tools, so you get:
- ✅ Modern FastMCP 2 features and performance
- ✅ Official MCP Inspector's gorgeous UI
- ✅ Real-time tool testing and debugging

### Adding New Tools

1. Create tool handlers in appropriate modules under `src/brokers/alpaca/tools/`
2. Add tool decorators in `src/main.py` 
3. Update the corresponding tools in `mcp_dev_adapter.py`
4. Update documentation

### Future Roadmap

- **Multi-broker support** (Interactive Brokers, TD Ameritrade, etc.)
- **Advanced order types** (stop-loss, trailing stops, brackets)
- **Portfolio analytics** and risk management
- **Market intelligence** and screening tools
- **Comprehensive testing suite**



###  📄 License
This project is licensed under the Apache License 2.0.
© 2025 Embedded Nature LLC. All rights reserved.

See the [LICENSE](LICENSE) file for full terms.
For commercial use, redistribution, or proprietary integration, please contact: isaac@embeddednature.com.

### 🤝 Contributing
Contributions are welcome — feel free to open a Pull Request.
For major changes, please start with an issue to discuss scope and direction.

**Built with intent, for the agentic systems era.**

