#!/usr/bin/env python3
"""
Factory for creating FoundationModels components
Provides clean object creation with proper error handling
"""

from typing import Optional, Tuple
from .framework import FoundationModelsFramework
from .model import AppleIntelligenceModel
from .analyzer import SemanticAnalyzer
from .exceptions import AppleIntelligenceError
from .status import StatusChecker


class AppleIntelligenceFactory:
    """Factory for creating FoundationModels components"""
    
    def __init__(self):
        self._status_checker = StatusChecker()
    
    def create_framework(self) -> Optional[FoundationModelsFramework]:
        """Create and load Foundation Models framework"""
        try:
            framework = FoundationModelsFramework()
            framework.load_framework()
            return framework
        except AppleIntelligenceError:
            return None
    
    def create_model(self, framework: Optional[FoundationModelsFramework] = None) -> Optional[AppleIntelligenceModel]:
        """Create and initialize FoundationModels model"""
        try:
            if framework is None:
                framework = self.create_framework()
                if framework is None:
                    return None
            
            model = AppleIntelligenceModel(framework)
            model.initialize()
            
            # Verify availability
            availability = model.check_availability()
            if not availability['available']:
                return None
            
            return model
        except AppleIntelligenceError:
            return None
    
    def create_semantic_analyzer(self, model: Optional[AppleIntelligenceModel] = None) -> Optional[SemanticAnalyzer]:
        """Create a ready-to-use semantic analyzer"""
        try:
            if model is None:
                model = self.create_model()
                if model is None:
                    return None
            
            analyzer = SemanticAnalyzer(model)
            analyzer.setup()
            return analyzer
            
        except AppleIntelligenceError:
            return None
    
    def create_complete_stack(self) -> Optional[Tuple[FoundationModelsFramework, AppleIntelligenceModel, SemanticAnalyzer]]:
        """Create complete FoundationModels stack"""
        try:
            framework = self.create_framework()
            if framework is None:
                return None
            
            model = self.create_model(framework)
            if model is None:
                return None
            
            analyzer = self.create_semantic_analyzer(model)
            if analyzer is None:
                return None
            
            return framework, model, analyzer
            
        except AppleIntelligenceError:
            return None
    
    def is_available(self) -> bool:
        """Check if FoundationModels is available for creation"""
        return self._status_checker.is_available()


# Global factory instance
_factory = AppleIntelligenceFactory()

# Convenience functions
def create_semantic_analyzer() -> Optional[SemanticAnalyzer]:
    """Create a ready-to-use semantic analyzer"""
    return _factory.create_semantic_analyzer()

def create_model() -> Optional[AppleIntelligenceModel]:
    """Create an initialized FoundationModels model"""
    return _factory.create_model()

def create_framework() -> Optional[FoundationModelsFramework]:
    """Create and load Foundation Models framework"""
    return _factory.create_framework()