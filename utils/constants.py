"""
Constants for the CSV AI Parser application.

This module contains all application-wide constants to maintain consistency
and make configuration changes easier.
"""

# File handling constants
SUPPORTED_FILE_EXTENSIONS = ['.csv']
MAX_FILE_SIZE_MB = 500
ENCODING_DEFAULT = 'utf-8'

# Chart and visualization constants
DEFAULT_CHART_SIZE = (10, 6)
CHART_DPI = 100
TEMP_FILE_PREFIX = 'temp_graph'

# API and model constants
DEFAULT_MODEL_NAME = 'gemini-2.5-flash'
API_KEY_ENV_VAR = 'GEMINI_API_KEY'
API_TIMEOUT_SECONDS = 30

# Data analysis constants
FRAUD_COLUMN_NAMES = ['Class', 'fraud', 'is_fraud']
TIME_COLUMN_NAMES = ['Time', 'time', 'timestamp', 'date', 'Date']
AMOUNT_COLUMN_NAMES = ['Amount', 'amount', 'value', 'Value']

# UI constants
DEFAULT_LANGUAGE = "pt_BR"
SUPPORTED_LANGUAGES = ["pt_BR", "en_US"]

# Session state keys
SESSION_KEYS = {
    'LANGUAGE': 'language',
    'DATA': 'data',
    'FILE_PROCESSED': 'file_processed',
    'ANALYSIS_RESULTS': 'analysis_results',
    'CURRENT_FILE_NAME': 'current_file_name'
}

# Validation constants
MIN_QUESTION_LENGTH = 3
MAX_QUESTION_LENGTH = 500