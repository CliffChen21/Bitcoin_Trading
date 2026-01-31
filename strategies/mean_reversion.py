"""
Mean Reversion Strategy

This strategy assumes that prices will revert to their mean. It generates buy signals
when the price is significantly below the mean, and sell signals when it's above.
"""
from typing import Dict, Optional
import pandas as pd
import numpy as np
from strategies.base_strategy import Strategy


class MeanReversionStrategy(Strategy):
    """
    Mean reversion strategy based on z-score.
    
    Parameters:
        window (int): Period for calculating mean and std (default: 20)
        entry_threshold (float): Z-score threshold for entry (default: 2.0)
        exit_threshold (float): Z-score threshold for exit (default: 0.5)
        position_size (float): Size of each position (default: 1.0)
    """
    
    def __init__(self, name: str = "MeanReversion_Strategy", parameters: Optional[Dict] = None):
        default_params = {
            'window': 20,
            'entry_threshold': 2.0,
            'exit_threshold': 0.5,
            'position_size': 1.0
        }
        if parameters:
            default_params.update(parameters)
        super().__init__(name, default_params)
        
        self.current_position = 0  # 0: no position, 1: long, -1: short
    
    def initialize(self):
        """Initialize the strategy."""
        self.is_initialized = True
        print(f"Initialized {self.name} with parameters: {self.parameters}")
    
    def generate_signals(self, market_data: pd.DataFrame) -> pd.DataFrame:
        """
        Generate trading signals based on mean reversion.
        
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
        
        # Calculate rolling statistics
        df['rolling_mean'] = df['price'].rolling(window=self.parameters['window']).mean()
        df['rolling_std'] = df['price'].rolling(window=self.parameters['window']).std()
        
        # Calculate z-score
        df['z_score'] = (df['price'] - df['rolling_mean']) / df['rolling_std']
        
        # Generate signals
        df['signal'] = 0
        df['position'] = 0
        
        entry_threshold = self.parameters['entry_threshold']
        exit_threshold = self.parameters['exit_threshold']
        
        for i in range(1, len(df)):
            current_position = df.loc[i-1, 'position']
            z_score = df.loc[i, 'z_score']
            
            if pd.isna(z_score):
                df.loc[i, 'position'] = current_position
                continue
            
            # Entry signals
            if current_position == 0:
                if z_score < -entry_threshold:  # Price too low, buy
                    df.loc[i, 'signal'] = 1
                    df.loc[i, 'position'] = 1
                elif z_score > entry_threshold:  # Price too high, sell
                    df.loc[i, 'signal'] = -1
                    df.loc[i, 'position'] = -1
                else:
                    df.loc[i, 'position'] = 0
            
            # Exit signals
            elif current_position == 1:  # Currently long
                if z_score > -exit_threshold:  # Exit long
                    df.loc[i, 'signal'] = -1
                    df.loc[i, 'position'] = 0
                else:
                    df.loc[i, 'position'] = 1
            
            elif current_position == -1:  # Currently short
                if z_score < exit_threshold:  # Exit short
                    df.loc[i, 'signal'] = 1
                    df.loc[i, 'position'] = 0
                else:
                    df.loc[i, 'position'] = -1
        
        # Add size
        df['size'] = self.parameters['position_size']
        
        # Select relevant columns
        result = df[['timestamp', 'signal', 'price', 'size', 'z_score']].copy()
        
        return result
    
    def on_order_filled(self, order: Dict):
        """Callback when an order is filled."""
        if order['side'] == 'buy':
            self.current_position = 1
        elif order['side'] == 'sell':
            self.current_position = -1
        print(f"Order filled: {order}, Current position: {self.current_position}")
    
    def on_market_data(self, data: Dict):
        """Callback when new market data arrives."""
        pass
