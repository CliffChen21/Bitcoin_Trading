"""
Example: Create a Custom Strategy

This example shows how to create your own custom trading strategy
by inheriting from the base Strategy class.
"""
import sys
sys.path.insert(0, '/home/runner/work/Bitcoin_Trading/Bitcoin_Trading')

from typing import Dict, Optional
import pandas as pd
import numpy as np
from strategies.base_strategy import Strategy
from backtesting.backtest_engine import BacktestEngine
from data.market_data_provider import MarketDataProvider


class MyCustomStrategy(Strategy):
    """
    Example custom strategy: Buy when price drops 5%, sell when it rises 5%.
    
    This is a simple momentum strategy for demonstration purposes.
    """
    
    def __init__(self, name: str = "Custom_Strategy", parameters: Optional[Dict] = None):
        default_params = {
            'buy_threshold': -0.05,   # Buy when price drops 5%
            'sell_threshold': 0.05,    # Sell when price rises 5%
            'lookback': 10,            # Compare to price 10 periods ago
            'position_size': 1.0
        }
        if parameters:
            default_params.update(parameters)
        super().__init__(name, default_params)
    
    def initialize(self):
        """Initialize the strategy."""
        self.is_initialized = True
        print(f"Initialized {self.name}")
        print(f"Buy when price change < {self.parameters['buy_threshold']*100}%")
        print(f"Sell when price change > {self.parameters['sell_threshold']*100}%")
    
    def generate_signals(self, market_data: pd.DataFrame) -> pd.DataFrame:
        """
        Generate trading signals based on price changes.
        """
        if not self.is_initialized:
            self.initialize()
        
        df = market_data.copy()
        
        # Calculate mid price if needed
        if 'price' not in df.columns:
            if 'bid_1' in df.columns and 'ask_1' in df.columns:
                df['price'] = (df['bid_1'].astype(float) + df['ask_1'].astype(float)) / 2
            else:
                raise ValueError("Market data must contain 'price' or 'bid_1'/'ask_1' columns")
        
        # Calculate price change
        lookback = self.parameters['lookback']
        df['price_change'] = df['price'].pct_change(lookback)
        
        # Generate signals
        df['signal'] = 0
        
        # Buy signal: price dropped significantly
        df.loc[df['price_change'] < self.parameters['buy_threshold'], 'signal'] = 1
        
        # Sell signal: price rose significantly
        df.loc[df['price_change'] > self.parameters['sell_threshold'], 'signal'] = -1
        
        # Add size
        df['size'] = self.parameters['position_size']
        
        # Return only relevant columns
        result = df[['timestamp', 'signal', 'price', 'size']].copy()
        
        return result


def main():
    print("="*60)
    print("CUSTOM STRATEGY EXAMPLE")
    print("="*60)
    
    # Create your custom strategy
    strategy = MyCustomStrategy(
        name="My_Custom_Strategy",
        parameters={
            'buy_threshold': -0.03,
            'sell_threshold': 0.03,
            'lookback': 5,
            'position_size': 1.0
        }
    )
    
    # Generate sample data
    print("\nGenerating sample market data...")
    data_provider = MarketDataProvider(source="csv")
    market_data = data_provider.generate_sample_data(
        n_points=300,
        initial_price=50000.0,
        volatility=0.02
    )
    
    # Run backtest
    print("\nRunning backtest...")
    backtest = BacktestEngine(
        strategy=strategy,
        initial_capital=100000.0,
        commission_rate=0.001
    )
    
    backtest.load_data(market_data)
    results = backtest.run(symbol="BTC-PERPETUAL")
    
    print("\nBacktest complete!")


if __name__ == "__main__":
    main()
