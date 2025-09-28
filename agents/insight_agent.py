"""Insight Agent for generating additional insights from data."""

import os
import google.generativeai as genai
from .base_agent import BaseAgent

class InsightAgent(BaseAgent):
    def __init__(self):
        """Initialize the Insight agent with Google AI."""
        super().__init__()
        # Configure the Google AI client
        genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
        self.model = genai.GenerativeModel('gemini-2.5-flash')
    
    def process(self, data, **kwargs):
        """
        Generate insights from the data.
        
        Args:
            data: The DataFrame containing the CSV data
            **kwargs: Additional arguments including operation type and query
            
        Returns:
            str: Generated insights
        """
        operation = kwargs.get('operation', 'initial_analysis')
        query = kwargs.get('query', '')
        
        # Get data information
        data_info = self._get_data_info(data)
        
        if operation == "initial_analysis":
            # Generate initial insights
            prompt = f"""
            I have a CSV dataset with the following information:
            
            {data_info}
            
            Please provide 3-5 key insights about this dataset. Focus on:
            1. Data distribution
            2. Notable patterns
            3. Potential areas for further analysis
            
            Keep the insights concise and data-driven.
            """
        else:  # query_analysis
            # Generate insights related to the user's query
            prompt = f"""
            I have a CSV dataset with the following information:
            
            {data_info}
            
            The user asked: "{query}"
            
            Based on this query and the dataset, provide 2-3 additional insights that might be relevant 
            but weren't directly asked for. These should complement the main answer.
            """
        
        # Generate insights using Google AI
        response = self.model.generate_content(prompt)
        
        return response.text
    
    def _get_data_info(self, data):
        """
        Get information about the DataFrame to include in the prompt.
        
        Args:
            data: The DataFrame
            
        Returns:
            str: Information about the DataFrame
        """
        # Get basic information
        info = f"Number of rows: {len(data)}\n"
        info += f"Number of columns: {len(data.columns)}\n"
        info += f"Columns: {', '.join(data.columns)}\n\n"
        
        # Add data types
        info += "Data types:\n"
        for col, dtype in data.dtypes.items():
            info += f"- {col}: {dtype}\n"
        
        # Add basic statistics for numeric columns
        numeric_cols = data.select_dtypes(include=['number']).columns
        if len(numeric_cols) > 0:
            info += "\nNumeric column statistics:\n"
            info += data[numeric_cols].describe().to_string()
        
        return info