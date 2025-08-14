#!/usr/bin/env python3
"""
High-level FoundationModels client interface
Provides a clean, easy-to-use API for FoundationModels operations
"""

from typing import Optional, Dict, Any
from apple_intelligence_framework import AppleIntelligenceError
from .factory import AppleIntelligenceFactory
from .status import StatusChecker


class AppleIntelligenceClient:
    """High-level client for FoundationModels operations"""
    
    def __init__(self, auto_initialize: bool = True):
        """
        Initialize FoundationModels client
        
        Args:
            auto_initialize: Automatically initialize components on creation
        """
        self._factory = AppleIntelligenceFactory()
        self._status_checker = StatusChecker()
        self._framework = None
        self._model = None
        self._analyzer = None
        self._initialized = False
        
        if auto_initialize:
            self._initialize()
    
    def _initialize(self) -> bool:
        """Initialize FoundationModels components"""
        try:
            # Create complete stack
            result = self._factory.create_complete_stack()
            if result is None:
                return False
            
            self._framework, self._model, self._analyzer = result
            self._initialized = True
            return True
            
        except AppleIntelligenceError:
            return False
    
    @property
    def is_ready(self) -> bool:
        """Check if client is ready for operations"""
        return self._initialized and self._analyzer is not None
    
    @property
    def is_available(self) -> bool:
        """Check if FoundationModels is available on this system"""
        return self._status_checker.is_available()
    
    def get_status(self) -> Dict[str, Any]:
        """Get detailed status information"""
        if not self._initialized:
            return {
                "initialized": False,
                "available": self.is_available,
                "ready": False,
                "error": "Client not initialized"
            }
        
        try:
            availability = self._model.check_availability() if self._model else {"available": False}
            return {
                "initialized": self._initialized,
                "available": availability.get("available", False),
                "ready": self.is_ready,
                "status": availability.get("status", "unknown"),
                "framework_loaded": self._framework is not None,
                "model_initialized": self._model is not None,
                "analyzer_ready": self._analyzer is not None
            }
        except Exception as e:
            return {
                "initialized": self._initialized,
                "available": False,
                "ready": False,
                "error": str(e)
            }
    
    def analyze_text(self, text: str) -> Dict[str, Any]:
        """
        Analyze text using FoundationModels
        
        Args:
            text: Text to analyze
            
        Returns:
            Analysis results or error information
        """
        if not self.is_ready:
            return {
                "error": "Client not ready",
                "status": self.get_status()
            }
        
        try:
            return self._analyzer.analyze(text)
        except AppleIntelligenceError as e:
            return {
                "error": f"Analysis failed: {e}",
                "text": text
            }
    
    def create_session(self, instructions: Optional[str] = None):
        """
        Create a new language model session
        
        Args:
            instructions: Optional custom instructions for the session
            
        Returns:
            Session object or None if failed
        """
        if not self._model:
            return None
        
        try:
            return self._model.create_session(instructions)
        except AppleIntelligenceError:
            return None
    
    def reinitialize(self) -> bool:
        """Reinitialize the client (useful if system state changed)"""
        self._initialized = False
        self._framework = None
        self._model = None
        self._analyzer = None
        
        # Clear status cache to force fresh check
        self._status_checker.clear_cache()
        
        return self._initialize()
    
    def __repr__(self) -> str:
        """String representation of client"""
        status = "ready" if self.is_ready else "not ready"
        return f"AppleIntelligenceClient(status={status})"