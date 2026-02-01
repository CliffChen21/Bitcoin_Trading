# Bitcoin Trading Framework

A flexible and extensible framework for developing and backtesting Bitcoin trading strategies.

## Overview

This framework provides:
- **Strategy Abstraction**: Easy-to-use base class for creating custom trading strategies
- **Backtesting Engine**: Comprehensive backtesting with performance metrics
- **Portfolio Management**: Automatic position tracking and P&L calculation
- **Data Provider**: Unified interface for accessing market data from multiple sources
- **Example Strategies**: Ready-to-use strategies to get started quickly

## Quick Start

### 1. Install Dependencies

**Option A: Use the installation script (recommended)**

On Linux/Mac:
```bash
./install.sh
```

On Windows:
```bash
install.bat
```

**Option B: Manual installation**

```bash
pip install -r requirements.txt
```

Or install packages individually:
```bash
pip install pandas numpy sqlalchemy pymysql aiohttp requests
```

### 2. Run an Example

From the repository root:

```bash
# Backtest a Simple Moving Average strategy
PYTHONPATH=. python examples/backtest_sma_example.py

# Backtest a Mean Reversion strategy
PYTHONPATH=. python examples/backtest_meanreversion_example.py

# Create and test your own custom strategy
PYTHONPATH=. python examples/custom_strategy_example.py
```

**Note:** Run examples from the repository root directory with `PYTHONPATH=.` to ensure imports work correctly.

## Creating a Custom Strategy

Creating a new trading strategy is easy! Just inherit from the `Strategy` base class:

```python
from strategies.base_strategy import Strategy
import pandas as pd

class MyStrategy(Strategy):
    def __init__(self, name="MyStrategy", parameters=None):
        super().__init__(name, parameters)
    
    def initialize(self):
        """Setup your strategy (called once)"""
        self.is_initialized = True
        # Initialize indicators, load data, etc.
    
    def generate_signals(self, market_data: pd.DataFrame) -> pd.DataFrame:
        """
        Generate trading signals based on market data.
        
        Returns DataFrame with columns:
        - timestamp: When to trade
        - signal: 1 (buy), -1 (sell), 0 (hold)
        - price: Execution price
        - size: Position size
        """
        # Your strategy logic here
        pass
```

### Strategy Template

See `examples/custom_strategy_example.py` for a complete working example.

## Running a Backtest

```python
from strategies.simple_moving_average import SimpleMovingAverageStrategy
from backtesting.backtest_engine import BacktestEngine
from data.market_data_provider import MarketDataProvider

# 1. Create your strategy
strategy = SimpleMovingAverageStrategy(
    name="SMA_20_50",
    parameters={
        'short_window': 20,
        'long_window': 50,
        'position_size': 1.0
    }
)

# 2. Load market data
data_provider = MarketDataProvider(source="csv")
market_data = data_provider.generate_sample_data(n_points=500)

# 3. Run backtest
backtest = BacktestEngine(
    strategy=strategy,
    initial_capital=100000.0,
    commission_rate=0.001
)
backtest.load_data(market_data)
results = backtest.run(symbol="BTC-PERPETUAL")

# 4. View results
print(results['metrics'])
```

## Framework Architecture

```
Bitcoin_Trading/
├── strategies/              # Trading strategies
│   ├── base_strategy.py    # Abstract base class
│   ├── simple_moving_average.py
│   └── mean_reversion.py
├── backtesting/             # Backtesting framework
│   ├── backtest_engine.py  # Main backtesting engine
│   ├── portfolio.py         # Portfolio management
│   └── performance_metrics.py
├── data/                    # Data access layer
│   └── market_data_provider.py
├── examples/                # Usage examples
│   ├── backtest_sma_example.py
│   ├── backtest_meanreversion_example.py
│   └── custom_strategy_example.py
├── tools/                   # Exchange APIs and utilities
│   ├── deribit_api.py
│   ├── mysql_api.py
│   └── database_writer.py
└── main.py                  # Data collection script
```

## Available Strategies

### 1. Simple Moving Average (SMA)
Generates buy/sell signals based on moving average crossovers.

**Parameters:**
- `short_window`: Short-term MA period (default: 20)
- `long_window`: Long-term MA period (default: 50)
- `position_size`: Position size (default: 1.0)

### 2. Mean Reversion
Buys when price is significantly below mean, sells when above.

**Parameters:**
- `window`: Period for calculating mean/std (default: 20)
- `entry_threshold`: Z-score threshold for entry (default: 2.0)
- `exit_threshold`: Z-score threshold for exit (default: 0.5)
- `position_size`: Position size (default: 1.0)

## Data Sources

The framework supports multiple data sources:

### 1. Database (MySQL)
```python
from data.market_data_provider import MarketDataProvider

provider = MarketDataProvider(source="database")
data = provider.get_historical_data(
    table_name="deribit_btc_perpetual_tick",
    limit=1000
)
```

### 2. CSV Files
```python
provider = MarketDataProvider(
    source="csv",
    config={'csv_path': 'path/to/data.csv'}
)
data = provider.get_historical_data()
```

### 3. Live Exchange Data
```python
import json

with open("Tokens.json", 'r') as f:
    tokens = json.load(f)

provider = MarketDataProvider(
    source="exchange",
    config={'tokens': tokens}
)
live_data = provider.get_live_data(symbol="BTC-PERPETUAL")
```

### 4. Generated Sample Data
```python
provider = MarketDataProvider(source="csv")
sample_data = provider.generate_sample_data(
    n_points=1000,
    initial_price=50000.0,
    volatility=0.02
)
```

## Performance Metrics

The backtesting engine automatically calculates:

- **Total Return**: Overall profit/loss percentage
- **Sharpe Ratio**: Risk-adjusted return
- **Maximum Drawdown**: Largest peak-to-trough decline
- **Total Trades**: Number of trades executed
- **Volatility**: Standard deviation of returns
- **Average Return**: Mean return per period

## Adding New Strategies

To add a new strategy to the framework:

1. Create a new file in `strategies/` directory
2. Inherit from `Strategy` base class
3. Implement `initialize()` and `generate_signals()` methods
4. (Optional) Override `on_order_filled()` and `on_market_data()` callbacks

Example:
```python
# strategies/my_new_strategy.py
from strategies.base_strategy import Strategy
import pandas as pd

class MyNewStrategy(Strategy):
    def initialize(self):
        self.is_initialized = True
        # Setup code here
    
    def generate_signals(self, market_data: pd.DataFrame) -> pd.DataFrame:
        # Your trading logic here
        signals = pd.DataFrame({
            'timestamp': market_data['timestamp'],
            'signal': 0,  # Your signals
            'price': market_data['price'],
            'size': 1.0
        })
        return signals
```

## Running Backtests with Historical Data

If you have historical data in the database:

```python
from data.market_data_provider import MarketDataProvider

# Load real historical data
provider = MarketDataProvider(source="database")
historical_data = provider.get_historical_data(
    table_name="deribit_btc_perpetual_tick",
    limit=10000  # Last 10,000 records
)

# Run backtest with historical data
backtest.load_data(historical_data)
results = backtest.run()
```

## Data Collection

The original data collection functionality is still available:

```bash
# Start collecting live market data to database
python main.py
```

## Configuration

### Database Configuration

Edit `tools/mysql_api.py` to configure your database:

```python
class Config:
    HOST = "your_host"
    DATABASE = "your_database"
    USER = "your_user"
    PASSWORD = "your_password"
```

### Exchange API Tokens

Create a `Tokens.json` file with your API credentials:

```json
{
    "Deribit": {
        "Read": {
            "id": "your_client_id",
            "secret": "your_client_secret"
        }
    }
}
```

## Testing

Run the test suite:

```bash
python test.py
```

## Best Practices

1. **Always backtest**: Test your strategy on historical data before live trading
2. **Parameter optimization**: Experiment with different parameter values
3. **Risk management**: Use appropriate position sizing
4. **Commission awareness**: Include realistic commission rates in backtests
5. **Data quality**: Ensure your historical data is clean and complete

## Contributing

To contribute a new strategy:

1. Create your strategy in `strategies/` directory
2. Add an example in `examples/` directory
3. Update this README with strategy documentation
4. Ensure your strategy passes basic backtests

## License

This project is for educational purposes.

## Support

For issues or questions, please open an issue on GitHub.

---

**Happy Trading! 🚀📈**
