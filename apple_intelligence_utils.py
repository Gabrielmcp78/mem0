#!/usr/bin/env python3
"""
FoundationModels utilities - Backward compatibility wrapper
This file maintains backward compatibility while using the new modular structure
"""

# Import specific functions to avoid star import warnings
from apple_intelligence import (
    is_apple_intelligence_ready,
    get_apple_intelligence_status,
    AppleIntelligenceClient,
    create_semantic_analyzer,
)

# Legacy compatibility functions
def quick_availability_check() -> bool:
    """Quick check if FoundationModels is available (legacy function)"""
    return is_apple_intelligence_ready()

class SimpleAppleIntelligence:
    """Legacy compatibility class - use AppleIntelligenceClient instead"""
    
    def __init__(self):
        self._client = None
    
    def initialize(self) -> bool:
        """Initialize FoundationModels (legacy method)"""
        try:
            self._client = AppleIntelligenceClient()
            return self._client.is_ready
        except Exception:
            return False
    
    def analyze_text(self, text: str):
        """Analyze text using FoundationModels (legacy method)"""
        if not self._client:
            raise RuntimeError("Not initialized - call initialize() first")
        return self._client.analyze_text(text)
    
    @property
    def is_ready(self) -> bool:
        """Check if ready (legacy property)"""
        return self._client and self._client.is_ready

# Maintain backward compatibility by re-exporting the main interfaces
__all__ = [
    "quick_availability_check",
    "create_semantic_analyzer", 
    "is_apple_intelligence_ready",
    "get_apple_intelligence_status",
    "SimpleAppleIntelligence",
    "AppleIntelligenceClient",
]
