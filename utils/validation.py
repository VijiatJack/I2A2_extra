"""
Validation utilities for the CSV AI Parser application.

This module contains validation functions for user input, data analysis questions,
and other validation logic following the Single Responsibility Principle.
"""

from typing import Dict, List
from .constants import MIN_QUESTION_LENGTH, MAX_QUESTION_LENGTH


class DataAnalysisValidator:
    """
    Validator class for data analysis related questions.
    
    This class encapsulates all validation logic for determining if a user query
    is related to data analysis, supporting both Portuguese and English.
    """
    
    def __init__(self):
        """Initialize the validator with predefined contexts."""
        self._data_contexts = self._initialize_data_contexts()
        self._question_indicators = self._initialize_question_indicators()
        self._basic_data_terms = self._initialize_basic_data_terms()
    
    def _initialize_data_contexts(self) -> Dict[str, List[str]]:
        """Initialize data analysis contexts in Portuguese and English."""
        return {
            # Data description contexts
            'data_description': [
                # Portuguese
                'tipos de dados', 'dados numéricos', 'dados categóricos', 'distribuição', 'variável', 
                'histograma', 'intervalo', 'mínimo', 'máximo', 'média', 'mediana', 'tendência central',
                'variabilidade', 'desvio padrão', 'variância', 'estatística', 'resumo',
                # English
                'data types', 'numeric data', 'categorical data', 'distribution', 'variable',
                'histogram', 'range', 'minimum', 'maximum', 'mean', 'median', 'central tendency',
                'variability', 'standard deviation', 'variance', 'statistics', 'summary'
            ],
            
            # Pattern and trend contexts
            'patterns_trends': [
                # Portuguese
                'padrões', 'tendências', 'temporal', 'frequente', 'agrupamento', 'cluster',
                'comportamento', 'evolução', 'série temporal', 'sazonalidade',
                # English
                'patterns', 'trends', 'temporal', 'frequent', 'clustering', 'cluster',
                'behavior', 'evolution', 'time series', 'seasonality'
            ],
            
            # Anomaly detection contexts
            'anomalies': [
                # Portuguese
                'anomalias', 'outliers', 'valores atípicos', 'discrepantes', 'anômalos',
                'irregulares', 'suspeitos', 'incomuns',
                # English
                'anomalies', 'outliers', 'atypical values', 'discrepant', 'anomalous',
                'irregular', 'suspicious', 'unusual'
            ],
            
            # Variable relationships contexts
            'relationships': [
                # Portuguese
                'relação', 'correlação', 'associação', 'dependência', 'influência',
                'dispersão', 'tabela cruzada', 'conexão', 'vínculo',
                # English
                'relationship', 'correlation', 'association', 'dependency', 'influence',
                'scatter', 'cross table', 'connection', 'link'
            ],
            
            # Fraud detection specific contexts
            'fraud_detection': [
                # Portuguese
                'fraude', 'fraudulento', 'transação', 'pagamento', 'suspeita', 'irregular',
                'detecção', 'classificação', 'normal', 'regular', 'legítimo',
                # English
                'fraud', 'fraudulent', 'transaction', 'payment', 'suspicious', 'irregular',
                'detection', 'classification', 'normal', 'regular', 'legitimate'
            ],
            
            # General data analysis contexts
            'general_analysis': [
                # Portuguese
                'dados', 'arquivo', 'csv', 'análise', 'exploração', 'investigação',
                'interpretação', 'insights', 'conclusões', 'resultados', 'descobertas',
                'opinião', 'avaliação', 'qualidade', 'estrutura',
                # English
                'data', 'file', 'csv', 'analysis', 'exploration', 'investigation',
                'interpretation', 'insights', 'conclusions', 'results', 'findings',
                'opinion', 'evaluation', 'quality', 'structure'
            ]
        }
    
    def _initialize_question_indicators(self) -> List[str]:
        """Initialize question indicator words in Portuguese and English."""
        return [
            # Portuguese
            'qual', 'quais', 'como', 'onde', 'quando', 'por que', 'porque', 'quantos', 'quantas',
            'existe', 'existem', 'há', 'pode', 'podem', 'deve', 'devem', 'é', 'são',
            # English
            'what', 'which', 'how', 'where', 'when', 'why', 'how many', 'how much',
            'is', 'are', 'can', 'could', 'should', 'would', 'do', 'does', 'did'
        ]
    
    def _initialize_basic_data_terms(self) -> List[str]:
        """Initialize basic data-related terms in Portuguese and English."""
        return [
            # Portuguese
            'dados', 'arquivo', 'csv', 'tabela', 'coluna', 'linha', 'valor', 'campo',
            # English
            'data', 'file', 'csv', 'table', 'column', 'row', 'value', 'field'
        ]
    
    def validate_question_length(self, query: str) -> bool:
        """
        Validate if the question length is within acceptable limits.
        
        Args:
            query (str): The user query to validate
            
        Returns:
            bool: True if length is valid, False otherwise
        """
        return MIN_QUESTION_LENGTH <= len(query.strip()) <= MAX_QUESTION_LENGTH
    
    def has_data_context(self, query: str) -> bool:
        """
        Check if query contains any relevant data analysis context terms.
        
        Args:
            query (str): The user query to check
            
        Returns:
            bool: True if query contains data analysis context, False otherwise
        """
        query_lower = query.lower()
        
        for context_category, terms in self._data_contexts.items():
            if any(term in query_lower for term in terms):
                return True
        
        return False
    
    def has_question_indicators(self, query: str) -> bool:
        """
        Check if query contains question indicator words.
        
        Args:
            query (str): The user query to check
            
        Returns:
            bool: True if query contains question indicators, False otherwise
        """
        query_lower = query.lower()
        return any(indicator in query_lower for indicator in self._question_indicators)
    
    def has_basic_data_terms(self, query: str) -> bool:
        """
        Check if query contains basic data-related terms.
        
        Args:
            query (str): The user query to check
            
        Returns:
            bool: True if query contains basic data terms, False otherwise
        """
        query_lower = query.lower()
        return any(term in query_lower for term in self._basic_data_terms)
    
    def is_valid_data_analysis_question(self, query: str) -> bool:
        """
        Comprehensive validation for data analysis questions.
        
        This method combines multiple validation checks to determine if a query
        is a valid data analysis question.
        
        Args:
            query (str): The user query to validate
            
        Returns:
            bool: True if query is a valid data analysis question, False otherwise
        """
        if not query or not isinstance(query, str):
            return False
        
        # Check length constraints
        if not self.validate_question_length(query):
            return False
        
        # Check for data analysis context
        has_context = self.has_data_context(query)
        
        # Check for question indicators and basic data terms
        has_indicators = self.has_question_indicators(query)
        has_data_terms = self.has_basic_data_terms(query)
        
        # A valid question should have either:
        # 1. Strong data analysis context, OR
        # 2. Question indicators AND basic data terms
        return has_context or (has_indicators and has_data_terms)


# Create a global validator instance
_validator = DataAnalysisValidator()


def is_data_analysis_question(query: str) -> bool:
    """
    Check if the query is related to data analysis using contextual validation.
    Supports both Portuguese and English questions.
    
    This is a convenience function that uses the DataAnalysisValidator class.
    
    Args:
        query (str): The user query to validate
        
    Returns:
        bool: True if query is a valid data analysis question, False otherwise
    """
    return _validator.is_valid_data_analysis_question(query)


def validate_file_upload(file_size: int, file_extension: str) -> tuple[bool, str]:
    """
    Validate uploaded file parameters.
    
    Args:
        file_size (int): Size of the file in bytes
        file_extension (str): File extension (e.g., '.csv')
        
    Returns:
        tuple[bool, str]: (is_valid, error_message)
    """
    from .constants import MAX_FILE_SIZE_MB, SUPPORTED_FILE_EXTENSIONS
    
    # Check file extension
    if file_extension.lower() not in SUPPORTED_FILE_EXTENSIONS:
        return False, f"Unsupported file type. Supported types: {', '.join(SUPPORTED_FILE_EXTENSIONS)}"
    
    # Check file size
    max_size_bytes = MAX_FILE_SIZE_MB * 1024 * 1024
    if file_size > max_size_bytes:
        return False, f"File too large. Maximum size: {MAX_FILE_SIZE_MB}MB"
    
    return True, ""