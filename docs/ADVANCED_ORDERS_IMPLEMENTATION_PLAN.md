# Advanced Orders Implementation Plan

## Overview

This document outlines the implementation plan for adding advanced order functionality to the Alpaca MCP server. Based on research of the Alpaca API, we can implement sophisticated order types that provide automated risk management and conditional selling capabilities.

## Supported Order Types by Alpaca API

### 1. Bracket Orders
- **Purpose**: Complete position management with entry, take-profit, and stop-loss
- **How it works**: Places 3 orders simultaneously - entry order, take-profit limit order, and stop-loss order
- **Behavior**: Once entry fills, both exit orders activate. When one exit fills, the other cancels
- **Use case**: Automated risk management for new positions

### 2. OCO (One-Cancels-Other) Orders  
- **Purpose**: Exit strategy for existing positions
- **How it works**: Places take-profit and stop-loss orders for current holdings
- **Behavior**: When one order fills, the other automatically cancels
- **Use case**: Adding exit strategy to existing positions

### 3. OTO (One-Triggers-Other) Orders
- **Purpose**: Entry with single exit condition
- **How it works**: Entry order with either take-profit OR stop-loss (not both)
- **Behavior**: Once entry fills, the single exit order activates
- **Use case**: Entry with only upside target or only downside protection

### 4. Trailing Stop Orders
- **Purpose**: Dynamic stop-loss that follows price movement
- **How it works**: Stop price adjusts automatically as stock moves favorably
- **Behavior**: Maintains set distance ($ or %) from high-water mark
- **Use case**: Maximize gains while protecting against reversals

## Implementation Plan

### New Tools to Add

#### 1. `place_bracket_order`
```python
def place_bracket_order(
    symbol: str,
    side: str,  # "buy" or "sell"
    quantity: float,
    order_type: str = "market",  # "market" or "limit"
    limit_price: Optional[float] = None,  # Required if order_type="limit"
    take_profit_price: float,
    stop_loss_price: float,
    stop_loss_limit_price: Optional[float] = None,  # Makes it stop-limit if provided
    time_in_force: str = "gtc"
) -> dict:
```

**Parameters:**
- `symbol`: Stock ticker (e.g., "AAPL")
- `side`: "buy" or "sell" 
- `quantity`: Number of shares
- `order_type`: "market" or "limit" for entry order
- `limit_price`: Entry price (required if order_type="limit")
- `take_profit_price`: Price to take profits
- `stop_loss_price`: Price to trigger stop loss
- `stop_loss_limit_price`: If provided, creates stop-limit instead of stop order
- `time_in_force`: "day" or "gtc"

#### 2. `place_oco_order`
```python
def place_oco_order(
    symbol: str,
    quantity: float,
    take_profit_price: float,
    stop_loss_price: float,
    stop_loss_limit_price: Optional[float] = None,
    time_in_force: str = "gtc"
) -> dict:
```

**Parameters:**
- `symbol`: Stock ticker
- `quantity`: Number of shares to sell
- `take_profit_price`: Limit price for profit taking
- `stop_loss_price`: Stop price for loss protection
- `stop_loss_limit_price`: Optional limit price for stop-limit order
- `time_in_force`: "day" or "gtc"

#### 3. `place_oto_order`
```python
def place_oto_order(
    symbol: str,
    side: str,
    quantity: float,
    order_type: str = "market",
    limit_price: Optional[float] = None,
    take_profit_price: Optional[float] = None,
    stop_loss_price: Optional[float] = None,
    stop_loss_limit_price: Optional[float] = None,
    time_in_force: str = "gtc"
) -> dict:
```

**Parameters:**
- Must provide either `take_profit_price` OR `stop_loss_price` (not both)
- Other parameters same as bracket order

#### 4. `place_trailing_stop_order`
```python
def place_trailing_stop_order(
    symbol: str,
    side: str,
    quantity: float,
    trail_type: str,  # "price" or "percent"
    trail_amount: float,  # Dollar amount or percentage (0.05 = 5%)
    time_in_force: str = "day"
) -> dict:
```

**Parameters:**
- `trail_type`: "price" for dollar amount, "percent" for percentage
- `trail_amount`: Trail distance (e.g., 2.00 for $2, 0.05 for 5%)
- `time_in_force`: "day" or "gtc" (trailing stops work best with "day")

## API Request Examples

### Bracket Order Request
```json
{
  "side": "buy",
  "symbol": "AAPL", 
  "type": "market",
  "qty": "100",
  "time_in_force": "gtc",
  "order_class": "bracket",
  "take_profit": {
    "limit_price": "155.00"
  },
  "stop_loss": {
    "stop_price": "145.00",
    "limit_price": "144.50"
  }
}
```

### OCO Order Request
```json
{
  "side": "sell",
  "symbol": "AAPL",
  "type": "limit", 
  "qty": "100",
  "time_in_force": "gtc",
  "order_class": "oco",
  "take_profit": {
    "limit_price": "155.00"
  },
  "stop_loss": {
    "stop_price": "145.00",
    "limit_price": "144.50"
  }
}
```

### Trailing Stop Request
```json
{
  "side": "sell",
  "symbol": "AAPL",
  "type": "trailing_stop",
  "qty": "100", 
  "time_in_force": "day",
  "trail_percent": "0.05"
}
```

## Implementation Steps

### Phase 1: Core Implementation
1. **Add new order tools** to `src/brokers/alpaca/tools/orders.py`
2. **Update tool registration** in `src/brokers/alpaca/tools/__init__.py`
3. **Add validation logic** for order parameters
4. **Implement error handling** for API responses

### Phase 2: Enhanced Features
1. **Add percentage-based calculations** (e.g., "set stop loss 5% below entry")
2. **Position size validation** (ensure sufficient shares for OCO orders)
3. **Price validation** (ensure take-profit > entry > stop-loss for buy orders)
4. **Risk/reward ratio calculations**

### Phase 3: Utility Functions
1. **`calculate_bracket_prices`** - Helper for R:R ratio-based bracket orders
2. **`get_optimal_trailing_distance`** - Suggest trail amounts based on volatility
3. **`validate_bracket_order`** - Pre-flight checks for order validity

## File Structure Changes

```
src/brokers/alpaca/tools/
├── __init__.py          # Add new tool imports
├── orders.py            # Add 4 new order functions
├── advanced_orders.py   # New file for advanced order utilities
└── order_validation.py  # New file for validation helpers
```

## Risk Considerations

### Order Validation
- Ensure take-profit price > entry price > stop-loss price (for buy orders)
- Validate sufficient buying power for bracket orders
- Check position size for OCO orders (can't sell more than owned)
- Verify price increments meet exchange requirements

### Error Handling
- Handle partial fills on bracket orders
- Manage order rejection scenarios
- Provide clear error messages for invalid parameters
- Log all order attempts for debugging

### Safety Features
- Maximum position size limits
- Maximum loss percentage validation
- Confirmation prompts for large orders
- Paper trading mode detection

## Testing Strategy

### Unit Tests
- Test all parameter combinations
- Validate error handling
- Test price calculation helpers
- Mock API responses

### Integration Tests  
- Test with paper trading account
- Verify order execution flow
- Test order cancellation scenarios
- Validate order status tracking

### Manual Testing
- Create test scenarios for each order type
- Verify dashboard integration
- Test edge cases (market gaps, halts)
- Validate risk management features

## Usage Examples

### Bracket Order with Risk/Reward Ratio
```python
# Buy 100 AAPL with 2:1 risk/reward ratio
place_bracket_order(
    symbol="AAPL",
    side="buy", 
    quantity=100,
    order_type="limit",
    limit_price=150.00,
    take_profit_price=154.00,  # $4 profit
    stop_loss_price=148.00,    # $2 loss
    stop_loss_limit_price=147.50
)
```

### OCO Exit Strategy
```python
# Add exit strategy to existing 100 AAPL shares
place_oco_order(
    symbol="AAPL",
    quantity=100,
    take_profit_price=155.00,
    stop_loss_price=145.00
)
```

### Trailing Stop
```python
# Trailing stop with 3% trail
place_trailing_stop_order(
    symbol="AAPL", 
    side="sell",
    quantity=100,
    trail_type="percent",
    trail_amount=0.03  # 3%
)
```

## Documentation Updates

### README.md
- Add advanced order examples
- Update feature list
- Add risk management section

### API Documentation
- Document all new tools
- Provide usage examples
- Add troubleshooting guide

## Timeline

- **Week 1**: Core implementation (Phase 1)
- **Week 2**: Enhanced features and validation (Phase 2) 
- **Week 3**: Utility functions and testing (Phase 3)
- **Week 4**: Documentation and refinement

## Success Metrics

- All 4 order types successfully implemented
- Comprehensive test coverage (>90%)
- Clear documentation with examples
- Successful paper trading validation
- Positive user feedback on ease of use

## Future Enhancements

- **Portfolio-level risk management**: Position sizing based on portfolio percentage
- **Multi-asset bracket orders**: Spread orders across multiple symbols
- **Dynamic take-profit/stop-loss**: Adjust based on volatility or technical indicators
- **Order templates**: Save and reuse common order configurations
- **Performance analytics**: Track success rates of different order strategies 