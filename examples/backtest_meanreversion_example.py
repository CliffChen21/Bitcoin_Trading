"""
Example: Backtest a Mean Reversion Strategy

This example demonstrates how to backtest a mean reversion strategy.
"""
import sys
sys.path.insert(0, '/home/runner/work/Bitcoin_Trading/Bitcoin_Trading')

from strategies.mean_reversion import MeanReversionStrategy
from backtesting.backtest_engine import BacktestEngine
from data.market_data_provider import MarketDataProvider


def main():
    print("="*60)
    print("BACKTESTING EXAMPLE: Mean Reversion Strategy")
    print("="*60)
    
    # Step 1: Create a strategy
    strategy = MeanReversionStrategy(
        name="MeanReversion_20_2.0",
        parameters={
            'window': 20,
            'entry_threshold': 2.0,
            'exit_threshold': 0.5,
            'position_size': 1.0
        }
    )
    
    # Step 2: Generate sample data
    print("\nGenerating sample market data...")
    data_provider = MarketDataProvider(source="csv")
    market_data = data_provider.generate_sample_data(
        n_points=500,
        initial_price=50000.0,
        volatility=0.02
    )
    print(f"Generated {len(market_data)} data points")
    
    # Step 3: Run backtest
    backtest = BacktestEngine(
        strategy=strategy,
        initial_capital=100000.0,
        commission_rate=0.001
    )
    
    backtest.load_data(market_data)
    results = backtest.run(symbol="BTC-PERPETUAL")
    
    # Step 4: Display results
    print("\n" + "="*60)
    print("RESULTS SUMMARY")
    print("="*60)
    
    if len(results['trades']) > 0:
        print(f"\nTotal trades: {len(results['trades'])}")
        print(f"First trade: {results['trades'].iloc[0].to_dict()}")
        print(f"Last trade: {results['trades'].iloc[-1].to_dict()}")


if __name__ == "__main__":
    main()
