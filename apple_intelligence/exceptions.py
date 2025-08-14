#!/usr/bin/env python3
"""
FoundationModels exception hierarchy
Provides clean error handling for FoundationModels operations
"""


class AppleIntelligenceError(Exception):
    """Base exception for FoundationModels related errors"""
    pass


class FrameworkError(AppleIntelligenceError):
    """Framework loading or initialization errors"""
    pass


class ModelError(AppleIntelligenceError):
    """Model initialization or operation errors"""
    pass


class AnalysisError(AppleIntelligenceError):
    """Semantic analysis errors"""
    pass


class AvailabilityError(AppleIntelligenceError):
    """Availability checking errors"""
    pass