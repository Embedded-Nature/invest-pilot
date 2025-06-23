# Function Comparison Table

## Quick Reference: Invest-Pilot vs Official Alpaca MCP

| Category | Function | Invest-Pilot | Official Alpaca | Priority |
|----------|----------|--------------|-----------------|----------|
| **Health** | `ping()` | ✅ | ❌ | - |
| **Account** | `get_account_info()` | ✅ | ✅ | - |
| **Positions** | `get_positions()` | ✅ | ✅ | - |
| **Positions** | `get_open_position(symbol)` | ❌ | ✅ | High |
| **Positions** | `close_position(symbol, qty/percentage)` | ❌ | ✅ | High |
| **Positions** | `close_all_positions(cancel_orders)` | ✅ | ✅ | - |
| **Custom** | `take_partial_profit(symbol, threshold, percentage)` | ✅ | ❌ | - |
| **Market Data** | `get_stock_quote(symbol)` | ✅ | ✅ | - |
| **Market Data** | `get_stock_bars(symbol, days)` | ✅ | ✅ | - |
| **Market Data** | `get_stock_latest_trade(symbol)` | ❌ | ✅ | Medium |
| **Market Data** | `get_stock_latest_bar(symbol)` | ❌ | ✅ | Medium |
| **Market Data** | `get_stock_trades(symbol, start, end)` | ❌ | ✅ | Low |
| **Orders** | `get_orders(status, limit)` | ✅ | ✅ | - |
| **Orders** | `place_market_order(symbol, side, quantity)` | ✅ | ✅ | - |
| **Orders** | `place_limit_order(symbol, side, quantity, limit_price)` | ✅ | ✅ | - |
| **Orders** | `place_stock_order(symbol, side, qty, order_type, ...)` | ❌ | ✅ | High |
| **Orders** | `cancel_order_by_id(order_id)` | ❌ | ✅ | High |
| **Orders** | `cancel_all_orders()` | ✅ | ✅ | - |
| **Options** | `get_option_contracts(underlying, expiration)` | ❌ | ✅ | High |
| **Options** | `get_option_latest_quote(option_symbol)` | ❌ | ✅ | High |
| **Options** | `get_option_snapshot(symbols)` | ❌ | ✅ | High |
| **Options** | `place_option_market_order(legs, class, qty)` | ❌ | ✅ | High |
| **Market Info** | `get_market_clock()` | ❌ | ✅ | Medium |
| **Market Info** | `get_market_calendar(start, end)` | ❌ | ✅ | Medium |
| **Corporate** | `get_corporate_announcements(...)` | ❌ | ✅ | Medium |
| **Watchlists** | `create_watchlist(name, symbols)` | ❌ | ✅ | Medium |
| **Watchlists** | `update_watchlist(id, name, symbols)` | ❌ | ✅ | Medium |
| **Watchlists** | `get_watchlists()` | ❌ | ✅ | Medium |
| **Assets** | `get_asset_info(symbol)` | ❌ | ✅ | Low |
| **Assets** | `get_all_assets(status)` | ❌ | ✅ | Low |

## Summary Statistics

- **Total Functions in Official Alpaca**: 25 functions
- **Total Functions in Invest-Pilot**: 11 functions
- **Shared Functions**: 9 functions
- **Missing from Invest-Pilot**: 16 functions (64%)
- **Unique to Invest-Pilot**: 2 functions (`ping`, `take_partial_profit`)

## Missing Function Breakdown by Priority

### High Priority (7 functions)
- `get_open_position(symbol)`
- `close_position(symbol, qty/percentage)`
- `place_stock_order(...)` (unified order placement)
- `cancel_order_by_id(order_id)`
- `get_option_contracts(...)`
- `get_option_latest_quote(...)`
- `get_option_snapshot(...)`
- `place_option_market_order(...)`

### Medium Priority (6 functions)
- `get_stock_latest_trade(symbol)`
- `get_stock_latest_bar(symbol)`
- `get_market_clock()`
- `get_market_calendar(...)`
- `get_corporate_announcements(...)`
- `create_watchlist(...)`
- `update_watchlist(...)`
- `get_watchlists()`

### Low Priority (3 functions)
- `get_stock_trades(...)`
- `get_asset_info(symbol)`
- `get_all_assets(status)` 