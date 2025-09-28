"""CSV Agent for processing and analyzing CSV files."""

import pandas as pd
from .base_agent import BaseAgent

class CSVAgent(BaseAgent):
    def __init__(self):
        """Initialize the CSV agent."""
        super().__init__()
    
    def validate_csv_structure(self, df):
        """
        Validate that the CSV file has a basic valid structure.
        Now supports any CSV format, not just fraud detection datasets.
        
        Args:
            df: The DataFrame to validate
            
        Returns:
            tuple: (is_valid, error_message)
        """
        # Basic validation - ensure we have data
        if df.empty:
            return False, "Invalid file: CSV file is empty."
        
        # Ensure we have at least one column
        if len(df.columns) == 0:
            return False, "Invalid file: CSV file has no columns."
        
        # Ensure we have at least one row of data
        if len(df) == 0:
            return False, "Invalid file: CSV file has no data rows."
        
        # Check for completely empty columns
        empty_columns = df.columns[df.isnull().all()].tolist()
        if empty_columns:
            return False, f"Invalid file: Columns {empty_columns} are completely empty."
        
        return True, ""
    
    def process(self, file, **kwargs):
        """
        Process a CSV file with generic support for any CSV format.
        
        Args:
            file: The CSV file to process
            **kwargs: Additional arguments
            
        Returns:
            DataFrame or str: The processed data or error message
        """
        try:
            # Read the CSV file with automatic delimiter detection
            # This is now handled by the FileService
            df = pd.read_csv(file)
            
            # Validate CSV structure (now generic)
            is_valid, error_message = self.validate_csv_structure(df)
            if not is_valid:
                return error_message
            
            # Basic data cleaning
            # Remove duplicate rows
            df = df.drop_duplicates()
            
            # Handle missing values more intelligently
            for col in df.columns:
                if pd.api.types.is_numeric_dtype(df[col]):
                    # For numeric columns, fill with median instead of 0
                    df[col] = df[col].fillna(df[col].median())
                else:
                    # For non-numeric columns, fill with mode or 'Unknown'
                    mode_value = df[col].mode()
                    if len(mode_value) > 0:
                        df[col] = df[col].fillna(mode_value[0])
                    else:
                        df[col] = df[col].fillna('Unknown')
            
            return df
            
        except Exception as e:
            return f"Error processing file: {str(e)}"