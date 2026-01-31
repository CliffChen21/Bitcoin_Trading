"""
Market Data Provider

Unified interface for accessing market data from various sources.
"""
from typing import Optional, Dict
import pandas as pd

# Optional imports - only load if needed
try:
    from tools.mysql_api import SQLEngine
except ImportError:
    SQLEngine = None

try:
    from tools.deribit_api import Deribit
except ImportError:
    Deribit = None


class MarketDataProvider:
    """
    Provides market data from various sources (database, exchange API, CSV).
    """
    
    def __init__(self, source: str = "database", config: Optional[Dict] = None):
        """
        Initialize the market data provider.
        
        Args:
            source: Data source ('database', 'exchange', or 'csv')
            config: Configuration dictionary (tokens, file paths, etc.)
        """
        self.source = source
        self.config = config or {}
        self.db = None
        self.exchange_client = None
        
        if source == "database":
            if SQLEngine is None:
                raise ImportError("SQLEngine not available. Install pymysql and sqlalchemy.")
            self.db = SQLEngine()
        elif source == "exchange":
            if Deribit is None:
                raise ImportError("Deribit not available. Install required dependencies.")
            if 'tokens' not in config:
                raise ValueError("Exchange source requires 'tokens' in config")
            self.exchange_client = Deribit(config['tokens'])
    
    def get_historical_data(self, symbol: str = "BTC-PERPETUAL", 
                           table_name: Optional[str] = None,
                           start_time: Optional[str] = None,
                           end_time: Optional[str] = None,
                           limit: Optional[int] = None) -> pd.DataFrame:
        """
        Get historical market data.
        
        Args:
            symbol: Trading symbol
            table_name: Database table name (for database source)
            start_time: Start timestamp
            end_time: End timestamp
            limit: Maximum number of records
        
        Returns:
            DataFrame with historical data
        """
        if self.source == "database":
            return self._get_from_database(table_name, start_time, end_time, limit)
        elif self.source == "csv":
            return self._get_from_csv(self.config.get('csv_path'))
        else:
            raise ValueError(f"Historical data not available for source: {self.source}")
    
    def _get_from_database(self, table_name: str, start_time: Optional[str] = None,
                          end_time: Optional[str] = None, 
                          limit: Optional[int] = None) -> pd.DataFrame:
        """
        Get data from database.
        
        Args:
            table_name: Table name
            start_time: Start timestamp
            end_time: End timestamp
            limit: Maximum records
        
        Returns:
            DataFrame with data
        """
        if not table_name:
            raise ValueError("table_name is required for database source")
        
        # Validate table name to prevent SQL injection
        # Only allow alphanumeric characters and underscores
        import re
        if not re.match(r'^[a-zA-Z0-9_]+$', table_name):
            raise ValueError("Invalid table name. Only alphanumeric characters and underscores allowed.")
        
        # Validate limit is an integer if provided
        if limit is not None:
            try:
                limit = int(limit)
                if limit <= 0:
                    raise ValueError("Limit must be positive")
            except (ValueError, TypeError):
                raise ValueError("Limit must be a positive integer")
        
        # Build SQL query with parameterized queries
        from sqlalchemy import text
        
        sql = f"SELECT * FROM {table_name}"
        params = {}
        
        conditions = []
        if start_time:
            conditions.append("id >= :start_time")
            params['start_time'] = start_time
        if end_time:
            conditions.append("id <= :end_time")
            params['end_time'] = end_time
        
        if conditions:
            sql += " WHERE " + " AND ".join(conditions)
        
        sql += " ORDER BY id"
        
        if limit:
            sql += f" LIMIT {int(limit)}"
        
        try:
            result = self.db.execute(text(sql), params) if params else self.db.execute(text(sql))
            df = pd.DataFrame(result.fetchall(), columns=result.keys())
            
            # Rename 'id' column to 'timestamp' if it exists
            if 'id' in df.columns:
                df.rename(columns={'id': 'timestamp'}, inplace=True)
            
            return df
        except Exception as e:
            print(f"Error fetching data from database: {e}")
            return pd.DataFrame()
    
    def _get_from_csv(self, csv_path: str) -> pd.DataFrame:
        """
        Get data from CSV file.
        
        Args:
            csv_path: Path to CSV file
        
        Returns:
            DataFrame with data
        """
        if not csv_path:
            raise ValueError("csv_path is required for csv source")
        
        try:
            df = pd.read_csv(csv_path)
            return df
        except Exception as e:
            print(f"Error reading CSV file: {e}")
            return pd.DataFrame()
    
    def get_live_data(self, symbol: str = "BTC-PERPETUAL", depth: int = 5) -> Dict:
        """
        Get live market data from exchange.
        
        Args:
            symbol: Trading symbol
            depth: Order book depth
        
        Returns:
            Dictionary with live market data
        """
        if self.source != "exchange":
            raise ValueError("Live data only available for 'exchange' source")
        
        if not self.exchange_client:
            raise ValueError("Exchange client not initialized")
        
        return self.exchange_client.get_order_book(symbol, depth)
    
    @staticmethod
    def generate_sample_data(n_points: int = 1000, initial_price: float = 50000.0,
                            volatility: float = 0.02) -> pd.DataFrame:
        """
        Generate sample market data for testing.
        
        Args:
            n_points: Number of data points
            initial_price: Starting price
            volatility: Price volatility
        
        Returns:
            DataFrame with sample data
        """
        import numpy as np
        from datetime import datetime, timedelta
        
        # Generate random walk
        returns = np.random.normal(0, volatility, n_points)
        prices = initial_price * np.exp(np.cumsum(returns))
        
        # Generate timestamps
        start_time = datetime.now() - timedelta(days=n_points)
        timestamps = [start_time + timedelta(days=i) for i in range(n_points)]
        
        # Create DataFrame
        df = pd.DataFrame({
            'timestamp': timestamps,
            'price': prices,
            'bid_1': prices * 0.9995,  # Slightly below mid price
            'ask_1': prices * 1.0005,  # Slightly above mid price
            'bid_vol_1': np.random.uniform(0.1, 10, n_points),
            'ask_vol_1': np.random.uniform(0.1, 10, n_points)
        })
        
        return df
