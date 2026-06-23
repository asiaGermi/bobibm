"""
watsonx.governance Integration Module

This module provides integration with IBM watsonx.governance for:
- Model registration and tracking
- AI Factsheet management
- Model monitoring and compliance
- Prediction logging for audit trails
"""

from .model_registry import ModelRegistry
from .factsheet_manager import FactsheetManager
from .monitoring import GovernanceMonitor

__all__ = [
    'ModelRegistry',
    'FactsheetManager',
    'GovernanceMonitor'
]

# Made with Bob