"""
Base Strategy Class

This module defines the abstract base class for all trading strategies.
All custom strategies should inherit from this class and implement the required methods.
"""
from abc import ABC, abstractmethod
from typing import Dict, List, Optional
import pandas as pd


class Strategy(ABC):
    """
    Abstract base class for trading strategies.
    
    All custom strategies must inherit from this class and implement:
    - initialize()
    - generate_signals()
    
    Attributes:
        name (str): Name of the strategy
        parameters (Dict): Strategy-specific parameters
    """
    
    def __init__(self, name: str, parameters: Optional[Dict] = None):
        """
        Initialize the strategy.
        
        Args:
            name: Name of the strategy
            parameters: Dictionary of strategy-specific parameters
        """
        self.name = name
        self.parameters = parameters or {}
        self.is_initialized = False
    
    @abstractmethod
    def initialize(self):
        """
        Initialize the strategy.
        
        This method is called once before the strategy starts generating signals.
        Use this to set up any indicators, load historical data, or perform
        any one-time setup operations.
        """
        pass
    
    @abstractmethod
    def generate_signals(self, market_data: pd.DataFrame) -> pd.DataFrame:
        """
        Generate trading signals based on market data.
        
        Args:
            market_data: DataFrame with columns like 'timestamp', 'bid', 'ask', 
                        'bid_vol', 'ask_vol', etc.
        
        Returns:
            DataFrame with at least the following columns:
                - timestamp: Timestamp of the signal
                - signal: 1 for buy, -1 for sell, 0 for hold
                - price: Price at which to execute the signal
                - size: Size of the position (optional)
        """
        pass
    
    def on_order_filled(self, order: Dict):
        """
        Callback when an order is filled.
        
        Args:
            order: Dictionary containing order information
                   (order_id, symbol, side, price, quantity, timestamp)
        """
        pass
    
    def on_market_data(self, data: Dict):
        """
        Callback when new market data arrives.
        
        Args:
            data: Dictionary containing market data (bid, ask, timestamp, etc.)
        """
        pass
    
    def get_parameters(self) -> Dict:
        """
        Get the strategy parameters.
        
        Returns:
            Dictionary of strategy parameters
        """
        return self.parameters
    
    def set_parameters(self, parameters: Dict):
        """
        Update strategy parameters.
        
        Args:
            parameters: Dictionary of parameters to update
        """
        self.parameters.update(parameters)
    
    def __repr__(self):
        return f"{self.__class__.__name__}(name='{self.name}', parameters={self.parameters})"
