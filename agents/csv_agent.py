"""CSV Agent for processing and analyzing CSV files."""

import pandas as pd
from .base_agent import BaseAgent

class CSVAgent(BaseAgent):
    def __init__(self):
        """Initialize the CSV agent."""
        super().__init__()
        # Define expected column structure
        self.expected_columns = 31
        self.expected_headers = ['Time'] + [f'V{i}' for i in range(1, 29)] + ['Amount', 'Class']
    
    def validate_csv_structure(self, df):
        """
        Validate that the CSV file has the expected structure.
        
        Args:
            df: The DataFrame to validate
            
        Returns:
            tuple: (is_valid, error_message)
        """
        # Check number of columns
        if len(df.columns) != self.expected_columns:
            return False, f"Invalid file: Expected {self.expected_columns} columns, but found {len(df.columns)}."
        
        # Check column headers
        for i, expected_header in enumerate(self.expected_headers):
            if df.columns[i] != expected_header:
                return False, f"Invalid file: Expected column {i+1} to be '{expected_header}', but found '{df.columns[i]}'."
        
        # Validate data types and content
        # Check if Time column contains numeric values
        if not pd.api.types.is_numeric_dtype(df['Time']):
            return False, "Invalid file: 'Time' column must contain numeric values."
        
        # Check if Class column contains only 0 and 1
        if not set(df['Class'].unique()).issubset({0, 1}):
            return False, "Invalid file: 'Class' column must contain only 0 and 1 values."
        
        # Check if Amount column contains numeric values
        if not pd.api.types.is_numeric_dtype(df['Amount']):
            return False, "Invalid file: 'Amount' column must contain numeric values."
        
        return True, ""
    
    def process(self, file, **kwargs):
        """
        Process a CSV file.
        
        Args:
            file: The CSV file to process
            **kwargs: Additional arguments
            
        Returns:
            DataFrame or str: The processed data or error message
        """
        try:
            # Read the CSV file
            df = pd.read_csv(file)
            
            # Validate CSV structure
            is_valid, error_message = self.validate_csv_structure(df)
            if not is_valid:
                return error_message
            
            # Basic data cleaning
            # Remove duplicate rows
            df = df.drop_duplicates()
            
            # Handle missing values (fill numeric with 0)
            for col in df.columns:
                if pd.api.types.is_numeric_dtype(df[col]):
                    df[col] = df[col].fillna(0)
            
            return df
            
        except Exception as e:
            return f"Error processing file: {str(e)}"