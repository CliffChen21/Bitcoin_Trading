"""
Simple Moving Average (SMA) Strategy

This strategy generates buy signals when the short-term moving average crosses above
the long-term moving average, and sell signals when it crosses below.
"""
from typing import Dict, Optional
import pandas as pd
import numpy as np
from strategies.base_strategy import Strategy


class SimpleMovingAverageStrategy(Strategy):
    """
    Simple Moving Average crossover strategy.
    
    Parameters:
        short_window (int): Period for short-term moving average (default: 20)
        long_window (int): Period for long-term moving average (default: 50)
        position_size (float): Size of each position (default: 1.0)
    """
    
    def __init__(self, name: str = "SMA_Strategy", parameters: Optional[Dict] = None):
        default_params = {
            'short_window': 20,
            'long_window': 50,
            'position_size': 1.0
        }
        if parameters:
            default_params.update(parameters)
        super().__init__(name, default_params)
        
        self.short_ma = None
        self.long_ma = None
        self.previous_signal = 0
    
    def initialize(self):
        """Initialize the strategy."""
        self.is_initialized = True
        print(f"Initialized {self.name} with parameters: {self.parameters}")
    
    def generate_signals(self, market_data: pd.DataFrame) -> pd.DataFrame:
        """
        Generate trading signals based on SMA crossover.
        
        Args:
            market_data: DataFrame with columns 'timestamp', 'price' (or 'bid'/'ask')
        
        Returns:
            DataFrame with trading signals
        """
        if not self.is_initialized:
            self.initialize()
        
        # Make a copy to avoid modifying the original data
        df = market_data.copy()
        
        # Calculate mid price if bid/ask are available
        if 'price' not in df.columns:
            if 'bid_1' in df.columns and 'ask_1' in df.columns:
                df['price'] = (df['bid_1'].astype(float) + df['ask_1'].astype(float)) / 2
            else:
                raise ValueError("Market data must contain 'price' or 'bid_1'/'ask_1' columns")
        
        # Calculate moving averages
        df['short_ma'] = df['price'].rolling(window=self.parameters['short_window']).mean()
        df['long_ma'] = df['price'].rolling(window=self.parameters['long_window']).mean()
        
        # Generate signals
        df['signal'] = 0
        
        # Buy signal: short MA crosses above long MA
        df.loc[df['short_ma'] > df['long_ma'], 'signal'] = 1
        
        # Sell signal: short MA crosses below long MA
        df.loc[df['short_ma'] < df['long_ma'], 'signal'] = -1
        
        # Only generate signal on crossover (change in signal)
        df['prev_signal'] = df['signal'].shift(1)
        df['signal'] = df.apply(
            lambda row: row['signal'] if row['signal'] != row['prev_signal'] else 0,
            axis=1
        )
        
        # Add size
        df['size'] = self.parameters['position_size']
        
        # Select relevant columns
        result = df[['timestamp', 'signal', 'price', 'size']].copy()
        
        return result
    
    def on_order_filled(self, order: Dict):
        """Callback when an order is filled."""
        print(f"Order filled: {order}")
    
    def on_market_data(self, data: Dict):
        """Callback when new market data arrives."""
        pass
