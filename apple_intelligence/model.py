#!/usr/bin/env python3
"""
FoundationModels model wrapper
Handles model initialization, availability checking, and session management
"""

from typing import Optional, Dict, Any
from .framework import FoundationModelsFramework
from .exceptions import ModelError


class AppleIntelligenceModel:
    """High-level interface to FoundationModels model"""
    
    AVAILABILITY_STATUS = {
        0: "available",
        1: "unavailable - device not eligible", 
        2: "unavailable - FoundationModels not enabled",
        3: "unavailable - model not ready",
        4: "unavailable - other"
    }
    
    def __init__(self, framework: FoundationModelsFramework):
        self.framework = framework
        self._model = None
        self._session = None
        
    def initialize(self) -> bool:
        """Initialize the Foundation Models system language model"""
        try:
            SystemLanguageModel = self.framework.get_system_language_model()
            # In Swift: SystemLanguageModel.default is a static property, not method
            self._model = SystemLanguageModel.default
            return True
        except Exception as e:
            raise ModelError(f"Model initialization failed: {e}")
    
    def check_availability(self) -> Dict[str, Any]:
        """Check model availability status"""
        if not self._model:
            raise ModelError("Model not initialized")
            
        try:
            # In Swift: model.availability is a property, not method
            availability_code = self._model.availability
            status = self.AVAILABILITY_STATUS.get(
                availability_code, 
                f"unknown status: {availability_code}"
            )
            
            return {
                "code": availability_code,
                "status": status,
                "available": availability_code == 0
            }
        except Exception as e:
            raise ModelError(f"Availability check failed: {e}")
    
    def create_session(self, instructions: Optional[str] = None):
        """Create a language model session"""
        if not self._model:
            raise ModelError("Model not initialized")
            
        try:
            LanguageModelSession = self.framework.get_language_model_session()
            
            if instructions:
                self._session = LanguageModelSession.alloc().initWithInstructions_(instructions)
            else:
                self._session = LanguageModelSession.alloc().init()
                
            return self._session
        except Exception as e:
            raise ModelError(f"Session creation failed: {e}")
    
    @property
    def session(self):
        """Get current session"""
        return self._session
    
    @property
    def model(self):
        """Get current model"""
        return self._model