"""Insight Agent for generating additional insights from data."""

import os
import google.generativeai as genai
from .base_agent import BaseAgent
from services.data_analysis_service import DataAnalysisService
from utils.constants import DEFAULT_MODEL_NAME, API_KEY_ENV_VAR

class InsightAgent(BaseAgent):
    def __init__(self):
        """Initialize the Insight agent with Google AI."""
        super().__init__()
        # Configure the Google AI client
        genai.configure(api_key=os.getenv(API_KEY_ENV_VAR))
        self.model = genai.GenerativeModel(DEFAULT_MODEL_NAME)
        self.data_analysis_service = DataAnalysisService()
    
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
        Get comprehensive information about the DataFrame to include in the prompt.
        
        Args:
            data: The DataFrame
            
        Returns:
            str: Comprehensive information about the DataFrame
        """
        # Use the comprehensive data analysis service for better context
        return self.data_analysis_service.get_ai_optimized_context(data, context_type="comprehensive")