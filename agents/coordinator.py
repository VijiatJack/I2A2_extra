"""Coordinator agent that manages the workflow between specialized agents."""

import pandas as pd
from .csv_agent import CSVAgent
from .query_agent import QueryAgent
from .insight_agent import InsightAgent

class CoordinatorAgent:
    def __init__(self):
        """Initialize the coordinator agent and its sub-agents."""
        self.csv_agent = CSVAgent()
        self.query_agent = QueryAgent()
        self.insight_agent = InsightAgent()
        self.data = None
        self.insights = None
    
    def process_file(self, file):
        """
        Process the uploaded CSV file.
        
        Args:
            file: The uploaded CSV file
            
        Returns:
            DataFrame or str: A preview of the processed data or error message
        """
        # Process the CSV file using the CSV agent
        result = self.csv_agent.process(file)
        
        # Check if result is an error message (string)
        if isinstance(result, str):
            # Return the error message
            return result
        
        # Store the valid data
        self.data = result
        
        # Generate initial insights
        self.insights = self.insight_agent.process(self.data, operation="initial_analysis")
        
        # Return the full dataset for analysis, not just preview
        return self.data
    
    def process_query(self, query):
        """
        Process a user query about the data.
        
        Args:
            query: The user's query string
            
        Returns:
            tuple: (response, insights) The response to the query and additional insights
        """
        # Import streamlit to access session state
        import streamlit as st
        
        # Check if data exists in session state first, then fallback to instance data
        if hasattr(st, 'session_state') and st.session_state.get('data') is not None:
            data_to_use = st.session_state.data
        elif self.data is not None:
            data_to_use = self.data
        else:
            return "Please upload a CSV file first.", None
        
        # Get current language from session state
        current_language = getattr(st.session_state, 'language', 'en_US')
        
        # Check if this is a general opinion request about the file
        opinion_keywords = [
            # Portuguese
            'opinião', 'avaliação', 'qualidade', 'estrutura', 'resumo', 'análise geral',
            'o que você acha', 'como você avalia', 'sua opinião', 'parecer',
            # English
            'opinion', 'evaluation', 'quality', 'structure', 'summary', 'general analysis',
            'what do you think', 'how do you evaluate', 'your opinion', 'assessment'
        ]
        
        is_opinion_request = any(keyword in query.lower() for keyword in opinion_keywords)
        
        if is_opinion_request:
            # Generate a technical opinion about the dataset
            response = self._generate_technical_opinion(data_to_use)
            insights = None
        else:
            # Process the query using the query agent
            response = self.query_agent.process(data_to_use, query=query, language=current_language)
            
            # Generate additional insights based on the query
            insights = self.insight_agent.process(data_to_use, query=query, operation="query_analysis", language=current_language)
        
        return response, insights
    
    def _generate_technical_opinion(self, data):
        """
        Generate a technical opinion about the dataset.
        
        Args:
            data: The pandas DataFrame to analyze
            
        Returns:
            str: Technical opinion about the dataset
        """
        try:
            # Basic dataset characteristics
            n_rows, n_cols = data.shape
            
            # Check for fraud column
            has_fraud_col = any(col.lower() in ['class', 'fraud', 'is_fraud'] for col in data.columns)
            
            # Data quality assessment
            missing_values = data.isnull().sum().sum()
            duplicate_rows = data.duplicated().sum()
            
            # Generate technical opinion
            opinion = f"**Technical Assessment:**\n\n"
            opinion += f"• Dataset dimensions: {n_rows:,} records × {n_cols} features\n"
            
            if has_fraud_col:
                fraud_col = next(col for col in data.columns if col.lower() in ['class', 'fraud', 'is_fraud'])
                fraud_count = data[fraud_col].sum() if data[fraud_col].dtype in ['int64', 'bool'] else len(data[data[fraud_col] == 1])
                fraud_rate = (fraud_count / n_rows) * 100
                opinion += f"• Fraud detection dataset with {fraud_rate:.2f}% fraud rate\n"
            
            opinion += f"• Data quality: {missing_values} missing values, {duplicate_rows} duplicates\n"
            
            # Column types assessment
            numeric_cols = len(data.select_dtypes(include=['number']).columns)
            categorical_cols = len(data.select_dtypes(include=['object']).columns)
            opinion += f"• Feature composition: {numeric_cols} numeric, {categorical_cols} categorical\n"
            
            # Brief recommendation
            if missing_values > 0:
                opinion += f"• Recommendation: Address missing values before analysis\n"
            if duplicate_rows > 0:
                opinion += f"• Recommendation: Consider removing {duplicate_rows} duplicate records\n"
            
            opinion += f"• Overall: {'Well-structured' if missing_values == 0 and duplicate_rows == 0 else 'Requires preprocessing'} dataset suitable for analysis"
            
            return opinion
            
        except Exception as e:
            return f"Error generating technical opinion: {str(e)}"