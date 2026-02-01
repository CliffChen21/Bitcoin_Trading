"""
Backtest Engine

Run backtests on trading strategies using historical data.
"""
from typing import Optional, Dict
import pandas as pd
from strategies.base_strategy import Strategy
from backtesting.portfolio import Portfolio
from backtesting.performance_metrics import PerformanceMetrics


class BacktestEngine:
    """
    Engine for running backtests on trading strategies.
    
    Attributes:
        strategy (Strategy): Trading strategy to backtest
        portfolio (Portfolio): Portfolio manager
        data (pd.DataFrame): Historical market data
    """
    
    def __init__(self, strategy: Strategy, initial_capital: float = 100000.0, 
                 commission_rate: float = 0.001):
        """
        Initialize the backtest engine.
        
        Args:
            strategy: Trading strategy to backtest
            initial_capital: Starting capital
            commission_rate: Commission rate per trade
        """
        self.strategy = strategy
        self.portfolio = Portfolio(initial_capital, commission_rate)
        self.data = None
        self.results = None
    
    def load_data(self, data: pd.DataFrame):
        """
        Load historical market data.
        
        Args:
            data: DataFrame with market data (must have 'timestamp' column)
        """
        if 'timestamp' not in data.columns:
            raise ValueError("Data must have a 'timestamp' column")
        
        self.data = data.copy()
        self.data = self.data.sort_values('timestamp').reset_index(drop=True)
    
    def run(self, symbol: str = "BTC-PERPETUAL") -> Dict:
        """
        Run the backtest.
        
        Args:
            symbol: Trading symbol
        
        Returns:
            Dictionary with backtest results and metrics
        """
        if self.data is None:
            raise ValueError("No data loaded. Call load_data() first.")
        
        if not self.strategy.is_initialized:
            self.strategy.initialize()
        
        print(f"Running backtest for {self.strategy.name}...")
        print(f"Data points: {len(self.data)}")
        print(f"Date range: {self.data['timestamp'].min()} to {self.data['timestamp'].max()}")
        
        # Generate signals
        signals_df = self.strategy.generate_signals(self.data)
        
        # Ensure we have price information
        if 'price' not in self.data.columns:
            if 'bid_1' in self.data.columns and 'ask_1' in self.data.columns:
                self.data['price'] = (self.data['bid_1'].astype(float) + 
                                     self.data['ask_1'].astype(float)) / 2
        
        # Execute trades based on signals
        for idx, row in signals_df.iterrows():
            if row['signal'] != 0:
                timestamp = row['timestamp']
                price = row['price']
                signal = row['signal']
                size = row.get('size', 1.0)
                
                # Get current position
                current_position = self.portfolio.get_position(symbol)
                
                # Execute trade
                if signal == 1:  # Buy signal
                    side = 'buy'
                    success = self.portfolio.execute_trade(timestamp, symbol, side, price, size)
                    if success:
                        self.strategy.on_order_filled({
                            'timestamp': timestamp,
                            'symbol': symbol,
                            'side': side,
                            'price': price,
                            'quantity': size
                        })
                
                elif signal == -1:  # Sell signal
                    # If we have a position, sell it
                    if current_position > 0:
                        side = 'sell'
                        quantity = min(size, current_position)
                        success = self.portfolio.execute_trade(timestamp, symbol, side, price, quantity)
                        if success:
                            self.strategy.on_order_filled({
                                'timestamp': timestamp,
                                'symbol': symbol,
                                'side': side,
                                'price': price,
                                'quantity': quantity
                            })
            
            # Record equity at each timestamp
            if idx in self.data.index:
                timestamp = self.data.loc[idx, 'timestamp']
                price = self.data.loc[idx, 'price']
                self.portfolio.record_equity(timestamp, {symbol: price})
        
        # Calculate performance metrics
        equity_curve = self.portfolio.get_equity_curve()
        trades_df = self.portfolio.get_trades_df()
        metrics = PerformanceMetrics.calculate_all_metrics(
            equity_curve, trades_df, self.portfolio.initial_capital
        )
        
        # Store results
        self.results = {
            'equity_curve': equity_curve,
            'trades': trades_df,
            'metrics': metrics,
            'portfolio_stats': self.portfolio.get_stats(),
            'signals': signals_df
        }
        
        print(f"\nBacktest completed. Total trades: {len(trades_df)}")
        PerformanceMetrics.print_metrics(metrics)
        
        return self.results
    
    def get_results(self) -> Optional[Dict]:
        """
        Get backtest results.
        
        Returns:
            Dictionary with results or None if backtest hasn't been run
        """
        return self.results
    
    def plot_equity_curve(self):
        """
        Plot the equity curve (requires matplotlib).
        """
        if self.results is None:
            print("No results to plot. Run backtest first.")
            return
        
        try:
            import matplotlib.pyplot as plt
            
            equity_curve = self.results['equity_curve']
            plt.figure(figsize=(12, 6))
            plt.plot(equity_curve['timestamp'], equity_curve['equity'], label='Equity')
            plt.xlabel('Time')
            plt.ylabel('Equity ($)')
            plt.title(f'Equity Curve - {self.strategy.name}')
            plt.legend()
            plt.grid(True)
            plt.tight_layout()
            plt.show()
        except ImportError:
            print("matplotlib not installed. Cannot plot equity curve.")
