# Alpaca MCP Server

Model Context Protocol (MCP) server for trading stocks, checking positions, fetching market data, and managing your account with Alpaca.

## Features

- 📊 **Market Data** - Get real-time stock quotes and historical price data.
- 💵 **Account Information** - Check your balances, buying power, and status.
- 📈 **Position Management** - View current positions and their performance.
- 🛒 **Order Placement** - Place market and limit orders through natural language.
- 📋 **Order Management** - List, track, and cancel orders.
- 💸 **Automated Profit-Taking** - Take partial profits when positions reach a certain threshold.

## Prerequisites

- Python 3.10+
- [uv](https://github.com/astral-sh/uv) (for environment and package management)
- Alpaca API keys
- An MCP client (e.g., Claude for Desktop)

## Installation

1.  Clone this repository:
    ```bash
    git clone https://github.com/embeddednature/alpaca-mcp-server.git
    cd alpaca-mcp-server
    ```

2.  Create a virtual environment and install dependencies using `uv`:
    ```bash
    uv venv
    source .venv/bin/activate
    uv pip install -e .
    ```

3.  Create a `.env` file in the root directory and add your Alpaca API credentials:
    ```
    API_KEY_ID="your_paper_api_key_id"
    API_SECRET_KEY="your_paper_api_secret_key"
    ```

## Usage

### Running the server

Start the server from your terminal:

```bash
uv run alpaca_mcp_server.py
```

The server will start and listen for connections from your MCP client.

### Development and Inspection

To run the server in development mode with the MCP Inspector, which allows you to view available tools and their schemas interactively, use the `dev` command:

```bash
uv run mcp dev alpaca_mcp_server.py
```

This will start the server and provide a URL to access the web-based inspector.

### Configuring with an MCP Client

To connect the server to a client like Claude for Desktop, you need to tell the client how to run the server.

1.  Open your MCP client's configuration.
2.  Add a new server configuration. The command should execute `uv` in the repository's directory to run the server script.

Here is an example for `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "alpaca": {
      "command": "/path/to/your/uv/executable",
      "args": [
        "run",
        "alpaca_mcp_server.py"
      ],
      "cwd": "/path/to/your/alpaca-mcp-server"
    }
  }
}
```

**Note**:
- Make sure to replace the paths for `command` and `cwd` with the correct absolute paths on your system.
- The server loads API keys from the `.env` file, so you don't need to add them to the client configuration.

## Available Tools

The server exposes the following tools for use with your MCP client:

- `ping()` - Test if the server is responsive.
- `get_account_info()` - Get account balances and status.
- `get_positions()` - List all current positions in the portfolio.
- `get_stock_quote(symbol)` - Get the latest quote for a stock.
- `get_stock_bars(symbol, days)` - Get historical price bars for a stock.
- `get_orders(status, limit)` - List orders with a specified status.
- `place_market_order(symbol, side, quantity)` - Place a market order.
- `place_limit_order(symbol, side, quantity, limit_price)` - Place a limit order.
- `cancel_all_orders()` - Cancel all open orders.
- `close_all_positions(cancel_orders)` - Close all open positions.
- `take_partial_profit(symbol, profit_threshold, close_percentage)` - Sell a percentage of a position if profit exceeds a threshold.

## Example Queries

Once the server is connected, you can use natural language to manage your trading account:

- "Can you ping the Alpaca server?"
- "What's my current account balance and buying power?"
- "Show me my current positions."
- "Get the latest quote for AAPL."
- "Show me the price history for TSLA over the last 10 days."
- "Buy 5 shares of MSFT at market price."
- "Sell 10 shares of AMZN with a limit price of $130."
- "If my NVDA position is up by more than 25%, sell half of it."
- "Cancel all my open orders."

## Security Notice

This MCP server has access to your Alpaca trading account and can execute real trades. By default, it runs in paper trading mode. If you switch to live trading, be sure to review every suggested action from your AI assistant before you approve it. The authors are not responsible for any financial losses.

## License

This project is licensed under the MIT License.