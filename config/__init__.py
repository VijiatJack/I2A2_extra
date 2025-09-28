"""
Configuration package for the CSV AI Parser application.

This package contains configuration management modules following
the Single Responsibility Principle and Clean Code practices.
"""

from .settings import AppSettings, get_app_settings

__all__ = ['AppSettings', 'get_app_settings']