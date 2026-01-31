"""
Portfolio Management

This module tracks positions, cash, and P&L during backtesting.
"""
from typing import Dict, List
import pandas as pd


class Portfolio:
    """
    Manages portfolio state during backtesting.
    
    Attributes:
        initial_capital (float): Starting capital
        cash (float): Current cash balance
        positions (Dict): Current positions {symbol: quantity}
        trades (List): History of all trades
    """
    
    def __init__(self, initial_capital: float = 100000.0, commission_rate: float = 0.001):
        """
        Initialize the portfolio.
        
        Args:
            initial_capital: Starting capital in USD
            commission_rate: Commission rate per trade (default: 0.1%)
        """
        self.initial_capital = initial_capital
        self.cash = initial_capital
        self.commission_rate = commission_rate
        self.positions = {}  # {symbol: quantity}
        self.trades = []
        self.equity_curve = []
    
    def execute_trade(self, timestamp, symbol: str, side: str, price: float, quantity: float):
        """
        Execute a trade.
        
        Args:
            timestamp: Trade timestamp
            symbol: Trading symbol
            side: 'buy' or 'sell'
            price: Execution price
            quantity: Trade quantity
        """
        trade_value = price * quantity
        commission = trade_value * self.commission_rate
        
        if side == 'buy':
            total_cost = trade_value + commission
            if total_cost > self.cash:
                # Insufficient funds
                return False
            
            self.cash -= total_cost
            self.positions[symbol] = self.positions.get(symbol, 0) + quantity
        
        elif side == 'sell':
            if self.positions.get(symbol, 0) < quantity:
                # Insufficient position
                return False
            
            total_proceeds = trade_value - commission
            self.cash += total_proceeds
            self.positions[symbol] = self.positions.get(symbol, 0) - quantity
        
        # Record the trade
        trade = {
            'timestamp': timestamp,
            'symbol': symbol,
            'side': side,
            'price': price,
            'quantity': quantity,
            'commission': commission,
            'cash': self.cash
        }
        self.trades.append(trade)
        
        return True
    
    def get_position(self, symbol: str) -> float:
        """
        Get current position for a symbol.
        
        Args:
            symbol: Trading symbol
        
        Returns:
            Current quantity held
        """
        return self.positions.get(symbol, 0)
    
    def get_portfolio_value(self, current_prices: Dict[str, float]) -> float:
        """
        Calculate total portfolio value.
        
        Args:
            current_prices: Dictionary of {symbol: price}
        
        Returns:
            Total portfolio value (cash + positions value)
        """
        positions_value = sum(
            self.positions.get(symbol, 0) * current_prices.get(symbol, 0)
            for symbol in self.positions
        )
        return self.cash + positions_value
    
    def record_equity(self, timestamp, current_prices: Dict[str, float]):
        """
        Record current equity value.
        
        Args:
            timestamp: Current timestamp
            current_prices: Dictionary of {symbol: price}
        """
        portfolio_value = self.get_portfolio_value(current_prices)
        self.equity_curve.append({
            'timestamp': timestamp,
            'equity': portfolio_value,
            'cash': self.cash,
            'positions_value': portfolio_value - self.cash
        })
    
    def get_equity_curve(self) -> pd.DataFrame:
        """
        Get equity curve as DataFrame.
        
        Returns:
            DataFrame with equity curve
        """
        return pd.DataFrame(self.equity_curve)
    
    def get_trades_df(self) -> pd.DataFrame:
        """
        Get trade history as DataFrame.
        
        Returns:
            DataFrame with trade history
        """
        return pd.DataFrame(self.trades)
    
    def get_stats(self) -> Dict:
        """
        Get portfolio statistics.
        
        Returns:
            Dictionary with portfolio stats
        """
        equity_df = self.get_equity_curve()
        if len(equity_df) == 0:
            return {}
        
        final_equity = equity_df['equity'].iloc[-1]
        total_return = (final_equity - self.initial_capital) / self.initial_capital
        
        return {
            'initial_capital': self.initial_capital,
            'final_equity': final_equity,
            'total_return': total_return,
            'total_trades': len(self.trades),
            'final_cash': self.cash,
            'final_positions': self.positions.copy()
        }
