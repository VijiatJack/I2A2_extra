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
        self._current_data_context = None
    
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
    
    def set_data_context(self, data_columns: List[str], data_types: Dict[str, str] = None) -> None:
        """
        Set the current data context based on the loaded CSV file.
        
        Args:
            data_columns (List[str]): List of column names from the CSV
            data_types (Dict[str, str]): Optional dictionary of column names to data types
        """
        self._current_data_context = {
            'columns': [col.lower() for col in data_columns],
            'original_columns': data_columns,
            'data_types': data_types or {}
        }
    
    def _extract_column_references(self, query: str) -> List[str]:
        """
        Extract potential column references from the query.
        
        Args:
            query (str): The user query
            
        Returns:
            List[str]: List of potential column names found in the query
        """
        if not self._current_data_context:
            return []
        
        query_lower = query.lower()
        found_columns = []
        
        for original_col, lower_col in zip(self._current_data_context['original_columns'], 
                                         self._current_data_context['columns']):
            # Check for exact column name matches
            if lower_col in query_lower:
                found_columns.append(original_col)
            
            # Check for partial matches for common column patterns
            words = lower_col.split('_')
            if len(words) > 1:
                for word in words:
                    if len(word) > 2 and word in query_lower:
                        found_columns.append(original_col)
                        break
        
        return found_columns
    
    def _has_relevant_data_terms(self, query: str) -> bool:
        """
        Check if query contains terms that are relevant to the current dataset.
        
        Args:
            query (str): The user query
            
        Returns:
            bool: True if query contains relevant terms for the current data
        """
        if not self._current_data_context:
            return self.has_basic_data_terms(query)
        
        query_lower = query.lower()
        
        # Check for direct column references
        column_refs = self._extract_column_references(query)
        if column_refs:
            return True
        
        # Check for data type related terms
        columns = self._current_data_context['columns']
        
        # Geographic terms
        geo_terms = ['state', 'states', 'estado', 'estados', 'city', 'cities', 'cidade', 'cidades', 
                    'country', 'countries', 'país', 'países', 'region', 'regions', 'região', 'regiões',
                    'address', 'endereço', 'location', 'localização', 'zip', 'cep', 'postal']
        
        has_geo_columns = any(any(geo in col for geo in ['state', 'city', 'country', 'region', 'address', 'zip', 'postal', 'location']) 
                             for col in columns)
        
        if has_geo_columns and any(term in query_lower for term in geo_terms):
            return True
        
        # Financial terms
        financial_terms = ['amount', 'value', 'price', 'cost', 'money', 'dollar', 'currency',
                          'valor', 'preço', 'custo', 'dinheiro', 'moeda', 'transaction', 'transação',
                          'payment', 'pagamento', 'fraud', 'fraude', 'bin', 'card', 'cartão']
        
        has_financial_columns = any(any(fin in col for fin in ['amount', 'value', 'price', 'cost', 'transaction', 'payment', 'fraud', 'bin', 'card']) 
                                   for col in columns)
        
        if has_financial_columns and any(term in query_lower for term in financial_terms):
            return True
        
        # Time-related terms
        time_terms = ['time', 'date', 'day', 'month', 'year', 'hour', 'minute', 'when', 'period',
                     'tempo', 'data', 'dia', 'mês', 'ano', 'hora', 'minuto', 'quando', 'período']
        
        has_time_columns = any(any(time in col for time in ['time', 'date', 'day', 'month', 'year', 'hour', 'created', 'updated']) 
                              for col in columns)
        
        if has_time_columns and any(term in query_lower for term in time_terms):
            return True
        
        # Category/classification terms
        category_terms = ['type', 'category', 'class', 'group', 'status', 'kind',
                         'tipo', 'categoria', 'classe', 'grupo', 'status', 'espécie']
        
        has_category_columns = any(any(cat in col for cat in ['type', 'category', 'class', 'group', 'status', 'kind']) 
                                  for col in columns)
        
        if has_category_columns and any(term in query_lower for term in category_terms):
            return True
        
        # Numeric analysis terms
        numeric_terms = ['count', 'total', 'sum', 'average', 'mean', 'max', 'min', 'distribution',
                        'contar', 'total', 'soma', 'média', 'máximo', 'mínimo', 'distribuição']
        
        if any(term in query_lower for term in numeric_terms):
            return True
        
        # Fall back to basic data terms
        return self.has_basic_data_terms(query)
    
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
        is a valid data analysis question based on the current data context.
        
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
        
        # Check for question indicators
        has_indicators = self.has_question_indicators(query)
        
        # Use context-aware validation if data context is available
        if self._current_data_context:
            has_relevant_terms = self._has_relevant_data_terms(query)
            # A valid question should have question indicators AND relevant terms for the current data
            return has_indicators and has_relevant_terms
        else:
            # Fall back to original logic if no data context is set
            has_context = self.has_data_context(query)
            has_data_terms = self.has_basic_data_terms(query)
            # A valid question should have either strong data analysis context, OR question indicators AND basic data terms
            return has_context or (has_indicators and has_data_terms)


# Create a global validator instance
_validator = DataAnalysisValidator()


def is_data_analysis_question(query: str, data_columns: List[str] = None) -> bool:
    """
    Check if the query is related to data analysis using contextual validation.
    Supports both Portuguese and English questions.
    
    This is a convenience function that uses the DataAnalysisValidator class.
    
    Args:
        query (str): The user query to validate
        data_columns (List[str]): Optional list of column names from the current dataset
        
    Returns:
        bool: True if query is a valid data analysis question, False otherwise
    """
    # Set data context if provided
    if data_columns:
        _validator.set_data_context(data_columns)
    
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