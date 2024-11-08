# pydatabaseconnection/core/__init__.py
"""Core functionality for database connections and operations."""

from .connection import DatabaseConnection
from .template_manager import TemplateManager
#from .dataframe_ops import DataFrameOperations

__all__ = [
    'DatabaseConnection',
    'TemplateManager',
    'DataFrameOperations'
]