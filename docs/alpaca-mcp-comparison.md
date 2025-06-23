# Alpaca MCP Server Comparison

This document compares the Invest-Pilot implementation with the official [Alpaca MCP Server](https://github.com/alpacahq/alpaca-mcp-server) to identify missing functions and opportunities for enhancement.

## Current Implementation Status

### ✅ Implemented Functions

| Function | Invest-Pilot | Official Alpaca | Notes |
|----------|--------------|-----------------|-------|
| `ping()` | ✅ | ❌ | Custom health check |
| `get_account_info()` | ✅ | ✅ | Basic account information |
| `get_positions()` | ✅ | ✅ | All current positions |
| `get_stock_quote(symbol)` | ✅ | ✅ | Real-time stock quotes |
| `get_stock_bars(symbol, days)` | ✅ | ✅ | Historical price data |
| `get_orders(status, limit)` | ✅ | ✅ | Order history and status |
| `place_market_order(symbol, side, quantity)` | ✅ | ✅ | Basic market orders |
| `place_limit_order(symbol, side, quantity, limit_price)` | ✅ | ✅ | Basic limit orders |
| `cancel_all_orders()` | ✅ | ✅ | Cancel all open orders |
| `close_all_positions(cancel_orders)` | ✅ | ✅ | Liquidate all positions |
| `take_partial_profit(symbol, profit_threshold, close_percentage)` | ✅ | ❌ | Custom profit-taking tool |

### ❌ Missing Functions (Present in Official Alpaca MCP)

#### Account & Position Management
| Function | Description | Priority |
|----------|-------------|----------|
| `get_open_position(symbol)` | Get detailed info on specific position | High |
| `close_position(symbol, qty/percentage)` | Close part or all of a specific position | High |

#### Advanced Stock Trading
| Function | Description | Priority |
|----------|-------------|----------|
| `place_stock_order(symbol, side, quantity, order_type, ...)` | Unified order placement with all order types | High |
| `get_stock_latest_trade(symbol)` | Latest market trade price | Medium |
| `get_stock_latest_bar(symbol)` | Most recent OHLC bar | Medium |
| `get_stock_trades(symbol, start_time, end_time)` | Trade-level history | Low |
| `cancel_order_by_id(order_id)` | Cancel specific order | High |

#### Options Trading (Major Gap)
| Function | Description | Priority |
|----------|-------------|----------|
| `get_option_contracts(underlying_symbol, expiration_date)` | Fetch option contracts | High |
| `get_option_latest_quote(option_symbol)` | Latest bid/ask on contract | High |
| `get_option_snapshot(symbol_or_symbols)` | Get Greeks and underlying data | High |
| `place_option_market_order(legs, order_class, quantity)` | Execute option strategies | High |

#### Market Information & Corporate Actions
| Function | Description | Priority |
|----------|-------------|----------|
| `get_market_clock()` | Market open/close schedule | Medium |
| `get_market_calendar(start, end)` | Holidays and trading days | Medium |
| `get_corporate_announcements(...)` | Earnings, dividends, splits | Medium |

#### Watchlist Management
| Function | Description | Priority |
|----------|-------------|----------|
| `create_watchlist(name, symbols)` | Create new watchlist | Medium |
| `update_watchlist(id, name, symbols)` | Modify existing watchlist | Medium |
| `get_watchlists()` | Retrieve all saved watchlists | Medium |

#### Asset Information
| Function | Description | Priority |
|----------|-------------|----------|
| `get_asset_info(symbol)` | Search asset metadata | Low |
| `get_all_assets(status)` | List all tradable instruments | Low |

## Feature Comparison Summary

### Invest-Pilot Strengths
- ✅ **Custom Health Check**: `ping()` function for server monitoring
- ✅ **Automated Profit Taking**: `take_partial_profit()` for risk management
- ✅ **Enhanced Logging**: Comprehensive logging throughout all functions
- ✅ **Better Error Handling**: Specific API error handling vs generic exceptions
- ✅ **Code Organization**: Well-structured with clear sections and helper functions

### Official Alpaca Strengths
- ✅ **Options Trading**: Complete options trading functionality with Greeks
- ✅ **Advanced Order Types**: Support for stop, stop-limit, and trailing stop orders
- ✅ **Market Data Depth**: More granular market data access
- ✅ **Corporate Actions**: Access to earnings, dividends, and split data
- ✅ **Watchlist Management**: Full watchlist CRUD operations
- ✅ **Asset Discovery**: Comprehensive asset search and filtering

## Implementation Roadmap

### Phase 1: Core Missing Functions (High Priority)
1. `get_open_position(symbol)` - Individual position details
2. `close_position(symbol, qty/percentage)` - Targeted position closing
3. `cancel_order_by_id(order_id)` - Specific order cancellation
4. `place_stock_order(...)` - Unified order placement with all order types

### Phase 2: Options Trading (High Priority)
1. `get_option_contracts(...)` - Option contract discovery
2. `get_option_latest_quote(...)` - Option quotes
3. `get_option_snapshot(...)` - Greeks and option analytics
4. `place_option_market_order(...)` - Option strategy execution

### Phase 3: Market Intelligence (Medium Priority)
1. `get_market_clock()` - Market status
2. `get_market_calendar(...)` - Trading calendar
3. `get_corporate_announcements(...)` - Corporate actions

### Phase 4: Portfolio Management (Medium Priority)
1. `create_watchlist(...)` - Watchlist creation
2. `update_watchlist(...)` - Watchlist management
3. `get_watchlists()` - Watchlist retrieval

### Phase 5: Advanced Features (Low Priority)
1. `get_asset_info(...)` - Asset metadata
2. `get_all_assets(...)` - Asset discovery
3. `get_stock_trades(...)` - Detailed trade history

## Technical Considerations

### API Dependencies
- **Options Trading**: Requires option data subscriptions
- **Corporate Actions**: May require additional API permissions
- **Real-time Data**: Some functions may require market data subscriptions

### Implementation Notes
- Consider maintaining the enhanced logging and error handling from Invest-Pilot
- Preserve the modular structure and helper functions
- Add comprehensive docstrings for new functions
- Implement proper parameter validation
- Consider rate limiting for API calls

## Conclusion

While Invest-Pilot has a solid foundation with enhanced logging and custom features, it's missing approximately **60% of the functionality** available in the official Alpaca MCP server, particularly:

1. **Options Trading** (complete gap)
2. **Advanced Order Types** (stop, stop-limit, trailing)
3. **Market Intelligence** (corporate actions, calendar)
4. **Watchlist Management** (complete gap)

The roadmap above provides a structured approach to achieving feature parity while maintaining the enhanced architecture and custom features that make Invest-Pilot unique. 