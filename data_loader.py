import pandas as pd
import numpy as np
from typing import Dict, List, Tuple
import json

class DataLoader:
    """Load and manage holdings and trades data from CSV files"""
    
    def __init__(self, holdings_path: str, trades_path: str):
        self.holdings_df = None
        self.trades_df = None
        self.load_data(holdings_path, trades_path)
    
    def load_data(self, holdings_path: str, trades_path: str):
        """Load CSV files into DataFrames"""
        try:
            self.holdings_df = pd.read_csv(holdings_path)
            self.trades_df = pd.read_csv(trades_path)
            print(f"✓ Holdings data loaded: {len(self.holdings_df)} records")
            print(f"✓ Trades data loaded: {len(self.trades_df)} records")
        except Exception as e:
            print(f"Error loading data: {e}")
    
    def get_holdings_summary(self) -> Dict:
        """Get summary statistics from holdings data"""
        if self.holdings_df is None:
            return {}
        
        summary = {
            "total_records": len(self.holdings_df),
            "columns": self.holdings_df.columns.tolist(),
            "memory_usage": str(self.holdings_df.memory_usage(deep=True).sum() / 1024 / 1024)[:5] + " MB"
        }
        
        # Get unique values for key columns
        if 'PortfolioName' in self.holdings_df.columns:
            summary["portfolios"] = self.holdings_df['PortfolioName'].nunique()
        if 'SecurityTypeNameSecNameStartQtyStartPrice' in self.holdings_df.columns:
            summary["unique_securities"] = self.holdings_df['SecurityTypeNameSecNameStartQtyStartPrice'].nunique()
        
        return summary
    
    def get_trades_summary(self) -> Dict:
        """Get summary statistics from trades data"""
        if self.trades_df is None:
            return {}
        
        summary = {
            "total_records": len(self.trades_df),
            "columns": self.trades_df.columns.tolist(),
            "memory_usage": str(self.trades_df.memory_usage(deep=True).sum() / 1024 / 1024)[:5] + " MB"
        }
        
        if 'PortfolioName' in self.trades_df.columns:
            summary["num_portfolios"] = self.trades_df['PortfolioName'].nunique()
        
        return summary
    
    def search_holdings(self, query: str = None, **kwargs) -> List[Dict]:
        """Search holdings data by criteria"""
        if self.holdings_df is None:
            return []
        
        result_df = self.holdings_df.copy()
        
        if query:
            # Search across all columns
            mask = result_df.astype(str).apply(lambda x: x.str.contains(query, case=False, na=False)).any(axis=1)
            result_df = result_df[mask]
        
        for key, value in kwargs.items():
            if key in result_df.columns:
                result_df = result_df[result_df[key].astype(str).str.contains(str(value), case=False, na=False)]
        
        return result_df.head(10).to_dict('records')
    
    def search_trades(self, query: str = None, **kwargs) -> List[Dict]:
        """Search trades data by criteria"""
        if self.trades_df is None:
            return []
        
        result_df = self.trades_df.copy()
        
        if query:
            # Search across all columns
            mask = result_df.astype(str).apply(lambda x: x.str.contains(query, case=False, na=False)).any(axis=1)
            result_df = result_df[mask]
        
        for key, value in kwargs.items():
            if key in result_df.columns:
                result_df = result_df[result_df[key].astype(str).str.contains(str(value), case=False, na=False)]
        
        return result_df.head(10).to_dict('records')
    
    def get_column_names(self) -> Dict:
        """Get all column names from both datasets"""
        return {
            "holdings_columns": self.holdings_df.columns.tolist() if self.holdings_df is not None else [],
            "trades_columns": self.trades_df.columns.tolist() if self.trades_df is not None else []
        }
