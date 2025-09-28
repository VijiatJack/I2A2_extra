"""
File handling service for the CSV AI Parser application.

This module provides file handling functionality following
the Single Responsibility Principle and Clean Code practices.
"""

import pandas as pd
import streamlit as st
from typing import Union, Tuple, Optional
import io
from utils.validation import validate_file_upload
from utils.constants import MAX_FILE_SIZE_MB, SUPPORTED_FILE_EXTENSIONS


class FileService:
    """
    Service class for file handling operations.
    
    This class encapsulates all file processing logic, providing
    a clean interface for file validation, reading, and processing.
    """
    
    def __init__(self):
        """Initialize the file service."""
        pass
    
    def validate_uploaded_file(self, uploaded_file) -> Tuple[bool, str]:
        """
        Validate an uploaded file.
        
        Args:
            uploaded_file: Streamlit uploaded file object
            
        Returns:
            Tuple[bool, str]: (is_valid, error_message)
        """
        if uploaded_file is None:
            return False, "No file uploaded"
        
        # Get file extension
        file_extension = self._get_file_extension(uploaded_file.name)
        
        # Validate file
        return validate_file_upload(uploaded_file.size, file_extension)
    
    def process_uploaded_file(self, uploaded_file) -> Union[pd.DataFrame, str]:
        """
        Process an uploaded CSV file.
        
        Args:
            uploaded_file: Streamlit uploaded file object
            
        Returns:
            Union[pd.DataFrame, str]: Processed DataFrame or error message
        """
        # Validate file first
        is_valid, error_message = self.validate_uploaded_file(uploaded_file)
        if not is_valid:
            return error_message
        
        try:
            # Read the CSV file
            df = self._read_csv_file(uploaded_file)
            
            # Validate DataFrame
            validation_result = self._validate_dataframe(df)
            if validation_result is not None:
                return validation_result
            
            # Clean and prepare the data
            df = self._clean_dataframe(df)
            
            return df
            
        except Exception as e:
            return f"Error processing file: {str(e)}"
    
    def _get_file_extension(self, filename: str) -> str:
        """
        Get file extension from filename.
        
        Args:
            filename (str): Name of the file
            
        Returns:
            str: File extension (e.g., '.csv')
        """
        return '.' + filename.split('.')[-1].lower() if '.' in filename else ''
    
    def _read_csv_file(self, uploaded_file) -> pd.DataFrame:
        """
        Read CSV file with various encoding attempts.
        
        Args:
            uploaded_file: Streamlit uploaded file object
            
        Returns:
            pd.DataFrame: Loaded DataFrame
            
        Raises:
            Exception: If file cannot be read with any encoding
        """
        # Reset file pointer
        uploaded_file.seek(0)
        
        # Try different encodings
        encodings = ['utf-8', 'latin-1', 'iso-8859-1', 'cp1252']
        
        for encoding in encodings:
            try:
                uploaded_file.seek(0)
                df = pd.read_csv(uploaded_file, encoding=encoding)
                return df
            except UnicodeDecodeError:
                continue
            except Exception as e:
                if encoding == encodings[-1]:  # Last encoding attempt
                    raise e
                continue
        
        raise Exception("Could not read file with any supported encoding")
    
    def _validate_dataframe(self, df: pd.DataFrame) -> Optional[str]:
        """
        Validate the loaded DataFrame.
        
        Args:
            df (pd.DataFrame): DataFrame to validate
            
        Returns:
            Optional[str]: Error message if validation fails, None if valid
        """
        if df is None:
            return "Failed to load data from file"
        
        if df.empty:
            return "The uploaded file is empty"
        
        if len(df.columns) == 0:
            return "The uploaded file has no columns"
        
        # Check for minimum data requirements
        if len(df) < 2:
            return "The file must contain at least 2 rows of data"
        
        # Check for reasonable column count
        if len(df.columns) > 1000:
            return "The file has too many columns (maximum 1000 supported)"
        
        return None
    
    def _clean_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Clean and prepare the DataFrame for analysis.
        
        Args:
            df (pd.DataFrame): DataFrame to clean
            
        Returns:
            pd.DataFrame: Cleaned DataFrame
        """
        # Make a copy to avoid modifying the original
        cleaned_df = df.copy()
        
        # Remove completely empty rows
        cleaned_df = cleaned_df.dropna(how='all')
        
        # Remove completely empty columns
        cleaned_df = cleaned_df.dropna(axis=1, how='all')
        
        # Strip whitespace from string columns
        string_columns = cleaned_df.select_dtypes(include=['object']).columns
        for col in string_columns:
            cleaned_df[col] = cleaned_df[col].astype(str).str.strip()
        
        # Convert numeric columns that might be stored as strings
        for col in cleaned_df.columns:
            if cleaned_df[col].dtype == 'object':
                # Try to convert to numeric
                numeric_series = pd.to_numeric(cleaned_df[col], errors='coerce')
                # If more than 50% of values are numeric, convert the column
                if numeric_series.notna().sum() / len(cleaned_df) > 0.5:
                    cleaned_df[col] = numeric_series
        
        return cleaned_df
    
    def get_file_info(self, uploaded_file) -> dict:
        """
        Get information about the uploaded file.
        
        Args:
            uploaded_file: Streamlit uploaded file object
            
        Returns:
            dict: File information including name, type, and size
        """
        if uploaded_file is None:
            return {}
        
        return {
            'name': uploaded_file.name,
            'type': uploaded_file.type,
            'size': uploaded_file.size,
            'size_mb': round(uploaded_file.size / (1024 * 1024), 2),
            'extension': self._get_file_extension(uploaded_file.name)
        }
    
    def export_dataframe_to_csv(self, df: pd.DataFrame, filename: str = "processed_data.csv") -> bytes:
        """
        Export DataFrame to CSV format for download.
        
        Args:
            df (pd.DataFrame): DataFrame to export
            filename (str): Name for the exported file
            
        Returns:
            bytes: CSV data as bytes
        """
        output = io.StringIO()
        df.to_csv(output, index=False)
        return output.getvalue().encode('utf-8')
    
    def get_data_preview(self, df: pd.DataFrame, num_rows: int = 5) -> dict:
        """
        Get a preview of the data for display.
        
        Args:
            df (pd.DataFrame): DataFrame to preview
            num_rows (int): Number of rows to include in preview
            
        Returns:
            dict: Data preview information
        """
        return {
            'head': df.head(num_rows),
            'tail': df.tail(num_rows),
            'shape': df.shape,
            'columns': list(df.columns),
            'dtypes': df.dtypes.to_dict(),
            'memory_usage_mb': round(df.memory_usage(deep=True).sum() / (1024 * 1024), 2)
        }