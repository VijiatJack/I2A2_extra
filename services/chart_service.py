"""
Chart generation service for the CSV AI Parser application.

This module provides chart generation functionality following
the Single Responsibility Principle and Clean Code practices.
"""

import pandas as pd
import matplotlib.pyplot as plt
from typing import Optional, Tuple
import os
import tempfile
from config.settings import get_app_settings


class ChartService:
    """
    Service class for chart generation operations.
    
    This class encapsulates all chart generation logic, providing
    a clean interface for creating various types of visualizations.
    """
    
    def __init__(self):
        """Initialize the chart service."""
        self._settings = get_app_settings()
        self._temp_files = []  # Track temporary files for cleanup
    
    def generate_chart(self, data: pd.DataFrame, chart_type: str) -> str:
        """
        Generate a chart based on the specified type.
        
        Args:
            data (pd.DataFrame): Data to visualize
            chart_type (str): Type of chart to generate
            
        Returns:
            str: Path to the generated chart image
            
        Raises:
            ValueError: If chart type is not supported or data is invalid
        """
        if data is None or data.empty:
            raise ValueError("Data cannot be None or empty")
        
        chart_generators = {
            'fraud_distribution': self._generate_fraud_distribution,
            'amount_distribution': self._generate_amount_distribution,
            'time_series': self._generate_time_series
        }
        
        if chart_type not in chart_generators:
            raise ValueError(f"Unsupported chart type: {chart_type}")
        
        return chart_generators[chart_type](data)
    
    def _generate_fraud_distribution(self, data: pd.DataFrame) -> str:
        """
        Generate fraud vs regular distribution chart.
        
        Args:
            data (pd.DataFrame): Data containing fraud classification
            
        Returns:
            str: Path to the generated chart
        """
        plt.figure(figsize=(
            self._settings.default_chart_width / 100,
            self._settings.default_chart_height / 100
        ))
        
        if 'Class' not in data.columns:
            # Create a simple data distribution chart for general datasets
            plt.hist(data.iloc[:, 0] if len(data.columns) > 0 else [], bins=30, alpha=0.7)
            plt.xlabel('Values')
            plt.ylabel('Frequency')
            plt.title('Data Distribution')
        else:
            # Fraud detection specific chart
            fraud_counts = data['Class'].value_counts()
            labels = ['Regular', 'Fraudulent']
            colors = ['#2ca02c', '#d62728']  # Green for regular, red for fraud
            
            plt.pie(fraud_counts.values, labels=labels, colors=colors, autopct='%1.1f%%', startangle=90)
            plt.title('Fraud vs Regular Transactions Distribution')
        
        return self._save_and_return_path()
    
    def _generate_amount_distribution(self, data: pd.DataFrame) -> str:
        """
        Generate amount distribution chart.
        
        Args:
            data (pd.DataFrame): Data containing amount information
            
        Returns:
            str: Path to the generated chart
        """
        plt.figure(figsize=(
            self._settings.default_chart_width / 100,
            self._settings.default_chart_height / 100
        ))
        
        # Find amount column
        amount_columns = [col for col in data.columns if 'amount' in col.lower() or 'value' in col.lower()]
        
        if not amount_columns:
            # Use the first numeric column if no amount column found
            numeric_columns = data.select_dtypes(include=['number']).columns
            if len(numeric_columns) > 0:
                amount_column = numeric_columns[0]
            else:
                raise ValueError("No numeric columns found for amount distribution")
        else:
            amount_column = amount_columns[0]
        
        if 'Class' in data.columns:
            # Separate distributions for fraud detection data
            regular_amounts = data[data['Class'] == 0][amount_column]
            fraud_amounts = data[data['Class'] == 1][amount_column]
            
            plt.hist(regular_amounts, bins=50, alpha=0.7, label='Regular', color='#2ca02c')
            if len(fraud_amounts) > 0:
                plt.hist(fraud_amounts, bins=50, alpha=0.7, label='Fraudulent', color='#d62728')
            
            plt.xlabel('Amount')
            plt.ylabel('Frequency')
            plt.title('Amount Distribution by Transaction Type')
            plt.legend()
        else:
            # General amount distribution
            plt.hist(data[amount_column], bins=50, alpha=0.7, color='#1f77b4')
            plt.xlabel(f'{amount_column}')
            plt.ylabel('Frequency')
            plt.title(f'{amount_column} Distribution')
        
        return self._save_and_return_path()
    
    def _generate_time_series(self, data: pd.DataFrame) -> str:
        """
        Generate time series chart.
        
        Args:
            data (pd.DataFrame): Data containing time information
            
        Returns:
            str: Path to the generated chart
        """
        plt.figure(figsize=(
            self._settings.default_chart_width / 100,
            self._settings.default_chart_height / 100
        ))
        
        # Find time column
        time_columns = [col for col in data.columns if 'time' in col.lower() or 'date' in col.lower()]
        
        if not time_columns:
            raise ValueError("No time columns found for time series chart")
        
        time_column = time_columns[0]
        
        try:
            # Convert to datetime if not already
            if not pd.api.types.is_datetime64_any_dtype(data[time_column]):
                time_data = pd.to_datetime(data[time_column], errors='coerce')
            else:
                time_data = data[time_column]
            
            # Create a copy of data with the time column
            df_with_time = data.copy()
            df_with_time[time_column] = time_data
            
            # Remove rows with invalid dates
            df_with_time = df_with_time.dropna(subset=[time_column])
            
            if len(df_with_time) == 0:
                raise ValueError("No valid time data found")
            
            # Group by time periods (daily aggregation)
            df_with_time['date'] = df_with_time[time_column].dt.date
            
            if 'Class' in data.columns:
                # Fraud detection time series
                df_grouped = df_with_time.groupby(['date', 'Class']).size().unstack(fill_value=0)
                
                if 0 in df_grouped.columns:
                    plt.plot(df_grouped.index, df_grouped[0], label='Regular', color='#2ca02c')
                if 1 in df_grouped.columns:
                    plt.plot(df_grouped.index, df_grouped[1], label='Fraudulent', color='#d62728')
                
                plt.xlabel('Date')
                plt.ylabel('Number of Transactions')
                plt.title('Transactions Over Time')
                plt.legend()
            else:
                # General time series
                df_grouped = df_with_time.groupby('date').size()
                plt.plot(df_grouped.index, df_grouped.values, color='#1f77b4')
                plt.xlabel('Date')
                plt.ylabel('Count')
                plt.title('Data Points Over Time')
            
            plt.xticks(rotation=45)
            plt.tight_layout()
            
        except Exception as e:
            raise ValueError(f"Error generating time series chart: {str(e)}")
        
        return self._save_and_return_path()
    
    def _save_and_return_path(self) -> str:
        """
        Save the current matplotlib figure and return the file path.
        
        Returns:
            str: Path to the saved chart file
        """
        # Create a temporary file
        temp_file = tempfile.NamedTemporaryFile(suffix='.png', delete=False)
        temp_path = temp_file.name
        temp_file.close()
        
        # Save the figure
        plt.savefig(temp_path, dpi=100, bbox_inches='tight')
        plt.close()
        
        # Track the temporary file for cleanup
        self._temp_files.append(temp_path)
        
        return temp_path
    
    def cleanup_temp_files(self) -> None:
        """Clean up temporary chart files."""
        for temp_file in self._temp_files:
            try:
                if os.path.exists(temp_file):
                    os.remove(temp_file)
            except Exception:
                pass  # Ignore cleanup errors
        
        self._temp_files.clear()
    
    def get_supported_chart_types(self) -> dict:
        """
        Get supported chart types with descriptions.
        
        Returns:
            dict: Dictionary of chart types and their descriptions
        """
        return {
            'fraud_distribution': 'Fraud vs Regular Distribution',
            'amount_distribution': 'Amount Distribution',
            'time_series': 'Transactions Over Time'
        }
    
    def validate_chart_requirements(self, data: pd.DataFrame, chart_type: str) -> Tuple[bool, str]:
        """
        Validate if data meets requirements for the specified chart type.
        
        Args:
            data (pd.DataFrame): Data to validate
            chart_type (str): Type of chart to validate for
            
        Returns:
            Tuple[bool, str]: (is_valid, error_message)
        """
        if data is None or data.empty:
            return False, "Data cannot be None or empty"
        
        if chart_type == 'fraud_distribution':
            return True, ""  # Can work with any data
        
        elif chart_type == 'amount_distribution':
            amount_columns = [col for col in data.columns if 'amount' in col.lower() or 'value' in col.lower()]
            numeric_columns = data.select_dtypes(include=['number']).columns
            
            if not amount_columns and len(numeric_columns) == 0:
                return False, "No numeric columns found for amount distribution"
            return True, ""
        
        elif chart_type == 'time_series':
            time_columns = [col for col in data.columns if 'time' in col.lower() or 'date' in col.lower()]
            if not time_columns:
                return False, "No time columns found for time series chart"
            return True, ""
        
        else:
            return False, f"Unsupported chart type: {chart_type}"