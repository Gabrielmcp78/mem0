#!/usr/bin/env python3
"""
Foundation Models framework wrapper
Handles low-level framework loading and class access
"""

import objc
from Foundation import NSBundle
from typing import Optional
from .exceptions import FrameworkError


class FoundationModelsFramework:
    """Wrapper for Apple's Foundation Models framework"""
    
    FRAMEWORK_PATH = '/System/Library/Frameworks/FoundationModels.framework'
    
    def __init__(self):
        self._bundle: Optional[NSBundle] = None
        self._loaded = False
        
    def load_framework(self) -> bool:
        """Load the Foundation Models framework"""
        try:
            self._bundle = NSBundle.bundleWithPath_(self.FRAMEWORK_PATH)
            
            if not self._bundle:
                raise FrameworkError("Foundation Models framework not found")
                
            if not self._bundle.load():
                raise FrameworkError("Failed to load Foundation Models framework")
                
            # Load framework classes
            objc.loadBundle(
                'FoundationModels', 
                bundle_path=self.FRAMEWORK_PATH,
                module_globals=globals()
            )
            
            self._loaded = True
            return True
            
        except Exception as e:
            raise FrameworkError(f"Framework loading failed: {e}")
    
    @property
    def is_loaded(self) -> bool:
        """Check if framework is loaded"""
        return self._loaded
    
    def get_system_language_model(self):
        """Get the SystemLanguageModel class"""
        if not self._loaded:
            raise FrameworkError("Framework not loaded")
            
        try:
            return objc.lookUpClass('FoundationModels.SystemLanguageModel')
        except Exception as e:
            raise FrameworkError(f"SystemLanguageModel class not found: {e}")
    
    def get_language_model_session(self):
        """Get the LanguageModelSession class"""
        if not self._loaded:
            raise FrameworkError("Framework not loaded")
            
        try:
            return objc.lookUpClass('FoundationModels.LanguageModelSession')
        except Exception as e:
            raise FrameworkError(f"LanguageModelSession class not found: {e}")