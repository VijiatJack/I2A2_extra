"""
Data analysis service for the CSV AI Parser application.

This module provides data analysis functionality following
the Single Responsibility Principle and Clean Code practices.
"""

import pandas as pd
from typing import Dict, Any, Optional
from datetime import datetime


class DataService:
    """
    Service class for data analysis operations.
    
    This class encapsulates all data analysis logic, providing
    a clean interface for data processing and analysis.
    """
    
    def __init__(self):
        """Initialize the data service."""
        self._data: Optional[pd.DataFrame] = None
        self._analysis_cache: Optional[Dict[str, Any]] = None
    
    def set_data(self, data: pd.DataFrame) -> None:
        """
        Set the data for analysis.
        
        Args:
            data (pd.DataFrame): The data to analyze
        """
        self._data = data
        self._analysis_cache = None  # Clear cache when data changes
    
    def get_data(self) -> Optional[pd.DataFrame]:
        """
        Get the current data.
        
        Returns:
            Optional[pd.DataFrame]: Current data or None if not set
        """
        return self._data
    
    def analyze_data(self, data: Optional[pd.DataFrame] = None) -> Dict[str, Any]:
        """
        Perform comprehensive data analysis.
        
        Args:
            data (Optional[pd.DataFrame]): Data to analyze. If None, uses stored data.
            
        Returns:
            Dict[str, Any]: Analysis results containing records, time, and amounts analysis
            
        Raises:
            ValueError: If no data is available for analysis
        """
        if data is not None:
            self.set_data(data)
        
        if self._data is None:
            raise ValueError("No data available for analysis")
        
        # Return cached analysis if available
        if self._analysis_cache is not None:
            return self._analysis_cache
        
        df = self._data
        
        # Records analysis
        records_analysis = self._analyze_records(df)
        
        # Time analysis
        time_analysis = self._analyze_time_patterns(df)
        
        # Amount analysis
        amounts_analysis = self._analyze_amounts(df)
        
        self._analysis_cache = {
            'records': records_analysis,
            'time': time_analysis,
            'amounts': amounts_analysis
        }
        
        return self._analysis_cache
    
    def _analyze_records(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Analyze record distribution.
        
        Args:
            df (pd.DataFrame): Data to analyze
            
        Returns:
            Dict[str, Any]: Records analysis results
        """
        total_records = len(df)
        
        # Check if this is fraud detection data
        if 'Class' in df.columns:
            regular_count = len(df[df['Class'] == 0])
            fraudulent_count = len(df[df['Class'] == 1])
        else:
            # For general datasets, assume no fraud classification
            regular_count = total_records
            fraudulent_count = 0
        
        regular_percentage = (regular_count / total_records * 100) if total_records > 0 else 0
        fraud_percentage = (fraudulent_count / total_records * 100) if total_records > 0 else 0
        
        return {
            'total': total_records,
            'regular': regular_count,
            'fraudulent': fraudulent_count,
            'regular_percentage': regular_percentage,
            'fraud_percentage': fraud_percentage
        }
    
    def _analyze_time_patterns(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Analyze time patterns in the data.
        
        Args:
            df (pd.DataFrame): Data to analyze
            
        Returns:
            Dict[str, Any]: Time analysis results
        """
        time_analysis = {
            'total_days': 0,
            'total_hours': 0,
            'has_time_data': False
        }
        
        # Look for time-related columns
        time_columns = [col for col in df.columns if 'time' in col.lower() or 'date' in col.lower()]
        
        if time_columns:
            time_col = time_columns[0]  # Use the first time column found
            
            try:
                # Try to convert to datetime if not already
                if not pd.api.types.is_datetime64_any_dtype(df[time_col]):
                    time_series = pd.to_datetime(df[time_col], errors='coerce')
                else:
                    time_series = df[time_col]
                
                # Remove NaT values
                time_series = time_series.dropna()
                
                if len(time_series) > 1:
                    time_range = time_series.max() - time_series.min()
                    time_analysis.update({
                        'total_days': time_range.total_seconds() / (24 * 3600),
                        'total_hours': time_range.total_seconds() / 3600,
                        'has_time_data': True,
                        'start_time': time_series.min(),
                        'end_time': time_series.max()
                    })
            except Exception:
                # If time parsing fails, keep default values
                pass
        
        return time_analysis
    
    def _analyze_amounts(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Analyze amount distributions.
        
        Args:
            df (pd.DataFrame): Data to analyze
            
        Returns:
            Dict[str, Any]: Amounts analysis results
        """
        amounts_analysis = {}
        
        # Look for amount-related columns
        amount_columns = [col for col in df.columns if 'amount' in col.lower() or 'value' in col.lower()]
        
        if amount_columns:
            amount_col = amount_columns[0]  # Use the first amount column found
            
            # Check if this is fraud detection data
            if 'Class' in df.columns:
                regular_amounts = df[df['Class'] == 0][amount_col]
                fraud_amounts = df[df['Class'] == 1][amount_col]
                
                amounts_analysis.update({
                    'regular_min': regular_amounts.min() if len(regular_amounts) > 0 else 0,
                    'regular_max': regular_amounts.max() if len(regular_amounts) > 0 else 0,
                    'regular_avg': regular_amounts.mean() if len(regular_amounts) > 0 else 0,
                    'regular_total': regular_amounts.sum() if len(regular_amounts) > 0 else 0,
                    'fraud_min': fraud_amounts.min() if len(fraud_amounts) > 0 else 0,
                    'fraud_max': fraud_amounts.max() if len(fraud_amounts) > 0 else 0,
                    'fraud_avg': fraud_amounts.mean() if len(fraud_amounts) > 0 else 0,
                    'fraud_total': fraud_amounts.sum() if len(fraud_amounts) > 0 else 0
                })
                
                # Calculate percentages
                total_amount = amounts_analysis['regular_total'] + amounts_analysis['fraud_total']
                if total_amount > 0:
                    amounts_analysis.update({
                        'regular_percentage': (amounts_analysis['regular_total'] / total_amount) * 100,
                        'fraud_percentage': (amounts_analysis['fraud_total'] / total_amount) * 100
                    })
                else:
                    amounts_analysis.update({
                        'regular_percentage': 0,
                        'fraud_percentage': 0
                    })
            else:
                # For general datasets
                all_amounts = df[amount_col]
                amounts_analysis.update({
                    'min': all_amounts.min(),
                    'max': all_amounts.max(),
                    'avg': all_amounts.mean(),
                    'total': all_amounts.sum(),
                    'std': all_amounts.std()
                })
        
        return amounts_analysis
    
    def get_data_summary(self, data: Optional[pd.DataFrame] = None) -> Dict[str, Any]:
        """
        Get a summary of the data structure and basic statistics.
        
        Args:
            data (Optional[pd.DataFrame]): Data to summarize. If None, uses stored data.
            
        Returns:
            Dict[str, Any]: Data summary including shape, columns, and basic stats
            
        Raises:
            ValueError: If no data is available
        """
        if data is not None:
            df = data
        elif self._data is not None:
            df = self._data
        else:
            raise ValueError("No data available for summary")
        
        return {
            'shape': df.shape,
            'columns': list(df.columns),
            'dtypes': df.dtypes.to_dict(),
            'null_counts': df.isnull().sum().to_dict(),
            'memory_usage': df.memory_usage(deep=True).sum(),
            'numeric_columns': list(df.select_dtypes(include=['number']).columns),
            'categorical_columns': list(df.select_dtypes(include=['object', 'category']).columns)
        }