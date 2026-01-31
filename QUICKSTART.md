# Quick Start Guide

This guide will help you get started with the Bitcoin Trading Framework in 5 minutes!

## Installation

1. **Clone the repository:**
```bash
git clone https://github.com/CliffChen21/Bitcoin_Trading.git
cd Bitcoin_Trading
```

2. **Install dependencies:**
```bash
pip install pandas numpy
```

Optional (for database and live trading):
```bash
pip install sqlalchemy pymysql aiohttp requests
```

## Run Your First Backtest

The easiest way to get started is to run one of the example backtests:

```bash
python examples/backtest_sma_example.py
```

You should see output like:
```
============================================================
BACKTESTING EXAMPLE: Simple Moving Average Strategy
============================================================

Generating sample market data...
Generated 500 data points
...
==================================================
BACKTEST PERFORMANCE METRICS
==================================================
Initial Capital:    $100,000.00
Final Equity:       $95,153.18
Profit:             $-4,846.82
Total Return:       -4.85%
Sharpe Ratio:       -0.21
Max Drawdown:       -13.51%
Total Trades:       10
==================================================
```

## Create Your First Custom Strategy

Create a new file `my_strategy.py`:

```python
from strategies.base_strategy import Strategy
import pandas as pd

class MyFirstStrategy(Strategy):
    def __init__(self, name="MyFirstStrategy", parameters=None):
        default_params = {'threshold': 0.02, 'position_size': 1.0}
        if parameters:
            default_params.update(parameters)
        super().__init__(name, default_params)
    
    def initialize(self):
        self.is_initialized = True
        print(f"Strategy {self.name} initialized!")
    
    def generate_signals(self, market_data: pd.DataFrame) -> pd.DataFrame:
        df = market_data.copy()
        
        # Calculate price if needed
        if 'price' not in df.columns:
            df['price'] = (df['bid_1'].astype(float) + df['ask_1'].astype(float)) / 2
        
        # Simple strategy: buy when price drops, sell when it rises
        df['price_change'] = df['price'].pct_change()
        df['signal'] = 0
        
        # Buy signal
        df.loc[df['price_change'] < -self.parameters['threshold'], 'signal'] = 1
        # Sell signal
        df.loc[df['price_change'] > self.parameters['threshold'], 'signal'] = -1
        
        df['size'] = self.parameters['position_size']
        
        return df[['timestamp', 'signal', 'price', 'size']]
```

## Backtest Your Strategy

```python
from backtesting.backtest_engine import BacktestEngine
from data.market_data_provider import MarketDataProvider
from my_strategy import MyFirstStrategy

# Create strategy
strategy = MyFirstStrategy(parameters={'threshold': 0.02})

# Generate sample data
data_provider = MarketDataProvider(source="csv")
market_data = data_provider.generate_sample_data(n_points=500)

# Run backtest
backtest = BacktestEngine(strategy=strategy, initial_capital=100000.0)
backtest.load_data(market_data)
results = backtest.run()
```

## What's Next?

1. **Explore example strategies:**
   - `examples/backtest_sma_example.py` - Simple Moving Average
   - `examples/backtest_meanreversion_example.py` - Mean Reversion
   - `examples/custom_strategy_example.py` - Custom Strategy Template

2. **Read the full documentation:**
   - See `README.md` for detailed information

3. **Use real data:**
   - Connect to your database
   - Load historical data from CSV
   - Use live exchange data

4. **Optimize your strategy:**
   - Test different parameters
   - Analyze performance metrics
   - Improve risk management

## Tips

- Start with simple strategies and gradually add complexity
- Always backtest before live trading
- Use realistic commission rates
- Consider transaction costs and slippage
- Monitor risk metrics (Sharpe ratio, max drawdown)

## Need Help?

- Check the examples in the `examples/` directory
- Read strategy implementations in `strategies/` directory
- See the comprehensive `README.md` for full documentation

Happy trading! 🚀
