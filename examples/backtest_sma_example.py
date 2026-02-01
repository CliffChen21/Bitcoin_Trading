"""
Example: Backtest a Simple Moving Average Strategy

This example demonstrates how to:
1. Create a trading strategy
2. Load or generate market data
3. Run a backtest
4. Analyze the results
"""

from strategies.simple_moving_average import SimpleMovingAverageStrategy
from backtesting.backtest_engine import BacktestEngine
from data.market_data_provider import MarketDataProvider


def main():
    print("="*60)
    print("BACKTESTING EXAMPLE: Simple Moving Average Strategy")
    print("="*60)
    
    # Step 1: Create a strategy with custom parameters
    strategy = SimpleMovingAverageStrategy(
        name="SMA_20_50",
        parameters={
            'short_window': 20,
            'long_window': 50,
            'position_size': 1.0
        }
    )
    
    # Step 2: Generate sample data for backtesting
    # In a real scenario, you would load historical data from database or CSV
    print("\nGenerating sample market data...")
    data_provider = MarketDataProvider(source="csv")
    market_data = data_provider.generate_sample_data(
        n_points=500,
        initial_price=50000.0,
        volatility=0.02
    )
    print(f"Generated {len(market_data)} data points")
    print(f"Date range: {market_data['timestamp'].min()} to {market_data['timestamp'].max()}")
    print(f"Price range: ${market_data['price'].min():.2f} to ${market_data['price'].max():.2f}")
    
    # Step 3: Create backtest engine
    backtest = BacktestEngine(
        strategy=strategy,
        initial_capital=100000.0,
        commission_rate=0.001  # 0.1% commission
    )
    
    # Step 4: Load data and run backtest
    backtest.load_data(market_data)
    results = backtest.run(symbol="BTC-PERPETUAL")
    
    # Step 5: Analyze results
    print("\n" + "="*60)
    print("TRADE SUMMARY")
    print("="*60)
    trades_df = results['trades']
    if len(trades_df) > 0:
        print(f"\nFirst 5 trades:")
        print(trades_df.head())
        
        print(f"\nLast 5 trades:")
        print(trades_df.tail())
    else:
        print("No trades executed")
    
    print("\n" + "="*60)
    print("PORTFOLIO STATS")
    print("="*60)
    portfolio_stats = results['portfolio_stats']
    for key, value in portfolio_stats.items():
        print(f"{key}: {value}")


if __name__ == "__main__":
    main()
