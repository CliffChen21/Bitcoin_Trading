"""
Performance Metrics

Calculate and analyze backtest performance metrics.
"""
import pandas as pd
import numpy as np
from typing import Dict


class PerformanceMetrics:
    """
    Calculate performance metrics for backtesting results.
    """
    
    @staticmethod
    def calculate_returns(equity_curve: pd.DataFrame) -> pd.Series:
        """
        Calculate returns from equity curve.
        
        Args:
            equity_curve: DataFrame with 'equity' column
        
        Returns:
            Series of returns
        """
        return equity_curve['equity'].pct_change()
    
    @staticmethod
    def calculate_sharpe_ratio(returns: pd.Series, risk_free_rate: float = 0.0, 
                               periods_per_year: int = 252) -> float:
        """
        Calculate Sharpe ratio.
        
        Args:
            returns: Series of returns
            risk_free_rate: Annual risk-free rate
            periods_per_year: Number of periods per year (252 for daily)
        
        Returns:
            Sharpe ratio
        """
        if len(returns) == 0 or returns.std() == 0:
            return 0.0
        
        excess_returns = returns - risk_free_rate / periods_per_year
        return np.sqrt(periods_per_year) * excess_returns.mean() / returns.std()
    
    @staticmethod
    def calculate_max_drawdown(equity_curve: pd.DataFrame) -> Dict:
        """
        Calculate maximum drawdown.
        
        Args:
            equity_curve: DataFrame with 'equity' column
        
        Returns:
            Dictionary with max drawdown info
        """
        if len(equity_curve) == 0:
            return {'max_drawdown': 0.0, 'max_drawdown_duration': 0}
        
        cumulative_max = equity_curve['equity'].expanding().max()
        drawdown = (equity_curve['equity'] - cumulative_max) / cumulative_max
        
        max_drawdown = drawdown.min()
        max_drawdown_idx = drawdown.idxmin()
        
        # Find drawdown duration
        if pd.isna(max_drawdown_idx):
            max_drawdown_duration = 0
        else:
            # Find the peak before the max drawdown
            peak_idx = equity_curve.loc[:max_drawdown_idx, 'equity'].idxmax()
            max_drawdown_duration = max_drawdown_idx - peak_idx
        
        return {
            'max_drawdown': max_drawdown,
            'max_drawdown_duration': max_drawdown_duration
        }
    
    @staticmethod
    def calculate_win_rate(trades_df: pd.DataFrame) -> float:
        """
        Calculate win rate from trades.
        
        Args:
            trades_df: DataFrame with trade information
        
        Returns:
            Win rate (0-1)
        """
        if len(trades_df) == 0:
            return 0.0
        
        # Calculate P&L for each trade pair (buy + sell)
        # This is simplified - assumes each sell closes a previous buy
        # In a real implementation, you'd track individual position opens/closes
        
        # For simplicity, just return 0.5
        # TODO: Implement proper P&L tracking per trade
        return 0.5
    
    @staticmethod
    def calculate_all_metrics(equity_curve: pd.DataFrame, trades_df: pd.DataFrame, 
                             initial_capital: float) -> Dict:
        """
        Calculate all performance metrics.
        
        Args:
            equity_curve: DataFrame with equity curve
            trades_df: DataFrame with trades
            initial_capital: Starting capital
        
        Returns:
            Dictionary with all metrics
        """
        if len(equity_curve) == 0:
            return {}
        
        returns = PerformanceMetrics.calculate_returns(equity_curve)
        sharpe = PerformanceMetrics.calculate_sharpe_ratio(returns)
        drawdown_info = PerformanceMetrics.calculate_max_drawdown(equity_curve)
        
        final_equity = equity_curve['equity'].iloc[-1]
        total_return = (final_equity - initial_capital) / initial_capital
        
        metrics = {
            'total_return': total_return,
            'total_return_pct': total_return * 100,
            'sharpe_ratio': sharpe,
            'max_drawdown': drawdown_info['max_drawdown'],
            'max_drawdown_pct': drawdown_info['max_drawdown'] * 100,
            'max_drawdown_duration': drawdown_info['max_drawdown_duration'],
            'total_trades': len(trades_df),
            'initial_capital': initial_capital,
            'final_equity': final_equity,
            'profit': final_equity - initial_capital
        }
        
        if len(returns) > 1:
            metrics['volatility'] = returns.std()
            metrics['avg_return'] = returns.mean()
        
        return metrics
    
    @staticmethod
    def print_metrics(metrics: Dict):
        """
        Print metrics in a readable format.
        
        Args:
            metrics: Dictionary of metrics
        """
        print("\n" + "="*50)
        print("BACKTEST PERFORMANCE METRICS")
        print("="*50)
        print(f"Initial Capital:    ${metrics.get('initial_capital', 0):,.2f}")
        print(f"Final Equity:       ${metrics.get('final_equity', 0):,.2f}")
        print(f"Profit:             ${metrics.get('profit', 0):,.2f}")
        print(f"Total Return:       {metrics.get('total_return_pct', 0):.2f}%")
        print(f"Sharpe Ratio:       {metrics.get('sharpe_ratio', 0):.2f}")
        print(f"Max Drawdown:       {metrics.get('max_drawdown_pct', 0):.2f}%")
        print(f"Total Trades:       {metrics.get('total_trades', 0)}")
        
        if 'volatility' in metrics:
            print(f"Volatility:         {metrics['volatility']:.4f}")
        if 'avg_return' in metrics:
            print(f"Avg Return:         {metrics['avg_return']:.4f}")
        
        print("="*50 + "\n")
