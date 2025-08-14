#!/usr/bin/env python3
"""
FoundationModels Package - Clean, modular interface for FoundationModels operations
"""

from .client import AppleIntelligenceClient
from .factory import (
    create_semantic_analyzer,
    create_model,
    create_framework,
    AppleIntelligenceFactory
)
from .status import (
    is_apple_intelligence_ready,
    get_apple_intelligence_status,
    clear_status_cache,
    StatusChecker
)

# Import modular components for advanced usage
from .exceptions import AppleIntelligenceError
from .framework import FoundationModelsFramework
from .model import AppleIntelligenceModel
from .analyzer import SemanticAnalyzer

# Package version
__version__ = "1.0.0"

# Main exports
__all__ = [
    # High-level client interface
    "AppleIntelligenceClient",
    
    # Factory functions
    "create_semantic_analyzer",
    "create_model", 
    "create_framework",
    "AppleIntelligenceFactory",
    
    # Status checking
    "is_apple_intelligence_ready",
    "get_apple_intelligence_status",
    "clear_status_cache",
    "StatusChecker",
    
    # Modular components (advanced usage)
    "AppleIntelligenceError",
    "FoundationModelsFramework",
    "AppleIntelligenceModel", 
    "SemanticAnalyzer",
]