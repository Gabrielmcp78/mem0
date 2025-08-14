#!/usr/bin/env python3
"""
FoundationModels Framework - Backward compatibility wrapper
This file maintains backward compatibility while using the new modular structure
"""

# Import from the new modular package for backward compatibility
from apple_intelligence import (
    AppleIntelligenceError,
    FoundationModelsFramework as FoundationModels,  # Alias for backward compatibility
    AppleIntelligenceModel,
    SemanticAnalyzer
)

# Re-export everything for backward compatibility
__all__ = [
    "AppleIntelligenceError",
    "FoundationModels",
    "AppleIntelligenceModel", 
    "SemanticAnalyzer",
]