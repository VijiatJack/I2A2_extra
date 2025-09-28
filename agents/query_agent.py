"""Query Agent for processing user queries using Google AI."""

import os
import google.generativeai as genai
from .base_agent import BaseAgent

class QueryAgent(BaseAgent):
    def __init__(self):
        """Initialize the Query agent with Google AI."""
        super().__init__()
        # Configure the Google AI client
        genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
        self.model = genai.GenerativeModel('gemini-2.5-flash')
    
    def process(self, data, **kwargs):
        """
        Process a user query about the data using Google AI.
        
        Args:
            data: The DataFrame containing the CSV data
            **kwargs: Additional arguments including the user query
            
        Returns:
            str: The response to the query
        """
        query = kwargs.get('query', '')
        if not query:
            return "Please provide a query."
        
        # Get data information
        data_info = self._get_data_info(data)
        
        # Construct prompt for Google AI
        prompt = f"""
        I have a CSV dataset with the following information:
        
        {data_info}
        
        Based on this dataset, please answer the following question:
        {query}
        
        Provide a clear and concise answer based only on the data provided.
        """
        
        # Generate response using Google AI
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
        
        # Add sample data (first 5 rows)
        info += "Sample data (first 5 rows):\n"
        info += data.head().to_string()
        
        return info