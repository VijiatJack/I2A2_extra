"""
Application settings and configuration management.

This module provides centralized configuration management for the CSV AI Parser
application, following the Single Responsibility Principle.
"""

import os
from dataclasses import dataclass
from typing import Optional
from dotenv import load_dotenv


@dataclass
class AppSettings:
    """
    Application settings configuration class.
    
    This class encapsulates all application configuration settings,
    providing a single source of truth for configuration values.
    """
    
    # API Configuration
    GEMINI_API_KEY: str
    
    # File Upload Configuration
    max_file_size_mb: int = 10
    supported_file_extensions: tuple = ('.csv',)
    
    # UI Configuration
    page_title: str = "CSV AI Parser"
    page_icon: str = "📊"
    layout: str = "wide"
    
    # Session Configuration
    session_timeout_minutes: int = 30
    
    # Chart Configuration
    default_chart_width: int = 800
    default_chart_height: int = 600
    chart_color_palette: tuple = ('#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd')
    
    # Validation Configuration
    min_question_length: int = 10
    max_question_length: int = 500
    
    # Agent Configuration
    max_retries: int = 3
    request_timeout_seconds: int = 30
    
    # Environment Configuration
    debug_mode: bool = False
    log_level: str = "INFO"
    
    def __post_init__(self):
        """Validate settings after initialization."""
        if not self.GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY is required but not provided")
        
        if self.max_file_size_mb <= 0:
            raise ValueError("max_file_size_mb must be positive")
        
        if self.min_question_length >= self.max_question_length:
            raise ValueError("min_question_length must be less than max_question_length")


class SettingsManager:
    """
    Settings manager for loading and managing application configuration.
    
    This class follows the Singleton pattern to ensure consistent
    configuration throughout the application.
    """
    
    _instance: Optional['SettingsManager'] = None
    _settings: Optional[AppSettings] = None
    
    def __new__(cls) -> 'SettingsManager':
        """Ensure singleton instance."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def load_settings(self, env_file: str = '.env') -> AppSettings:
        """
        Load application settings from environment variables.
        
        Args:
            env_file (str): Path to the environment file
            
        Returns:
            AppSettings: Loaded application settings
            
        Raises:
            ValueError: If required settings are missing or invalid
        """
        if self._settings is not None:
            return self._settings
        
        # Load environment variables
        load_dotenv(env_file)
        
        # Get required settings
        GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
        if not GEMINI_API_KEY:
            raise ValueError(
                "GEMINI_API_KEY not found in environment variables. "
                "Please check your .env file."
            )
        
        # Get optional settings with defaults
        max_file_size_mb = int(os.getenv('MAX_FILE_SIZE_MB', '10'))
        debug_mode = os.getenv('DEBUG_MODE', 'false').lower() == 'true'
        log_level = os.getenv('LOG_LEVEL', 'INFO').upper()
        
        # Chart configuration
        chart_width = int(os.getenv('CHART_WIDTH', '800'))
        chart_height = int(os.getenv('CHART_HEIGHT', '600'))
        
        # Validation configuration
        min_question_length = int(os.getenv('MIN_QUESTION_LENGTH', '10'))
        max_question_length = int(os.getenv('MAX_QUESTION_LENGTH', '500'))
        
        # Agent configuration
        max_retries = int(os.getenv('MAX_RETRIES', '3'))
        request_timeout = int(os.getenv('REQUEST_TIMEOUT_SECONDS', '30'))
        
        self._settings = AppSettings(
            GEMINI_API_KEY=GEMINI_API_KEY,
            max_file_size_mb=max_file_size_mb,
            debug_mode=debug_mode,
            log_level=log_level,
            default_chart_width=chart_width,
            default_chart_height=chart_height,
            min_question_length=min_question_length,
            max_question_length=max_question_length,
            max_retries=max_retries,
            request_timeout_seconds=request_timeout
        )
        
        return self._settings
    
    def get_settings(self) -> AppSettings:
        """
        Get current application settings.
        
        Returns:
            AppSettings: Current application settings
            
        Raises:
            RuntimeError: If settings haven't been loaded yet
        """
        if self._settings is None:
            raise RuntimeError("Settings not loaded. Call load_settings() first.")
        return self._settings
    
    def reload_settings(self, env_file: str = '.env') -> AppSettings:
        """
        Reload application settings from environment variables.
        
        Args:
            env_file (str): Path to the environment file
            
        Returns:
            AppSettings: Reloaded application settings
        """
        self._settings = None
        return self.load_settings(env_file)


# Global settings manager instance
_settings_manager = SettingsManager()


def get_app_settings(env_file: str = '.env') -> AppSettings:
    """
    Get application settings (convenience function).
    
    Args:
        env_file (str): Path to the environment file
        
    Returns:
        AppSettings: Application settings
    """
    try:
        return _settings_manager.get_settings()
    except RuntimeError:
        return _settings_manager.load_settings(env_file)


def reload_app_settings(env_file: str = '.env') -> AppSettings:
    """
    Reload application settings (convenience function).
    
    Args:
        env_file (str): Path to the environment file
        
    Returns:
        AppSettings: Reloaded application settings
    """
    return _settings_manager.reload_settings(env_file)