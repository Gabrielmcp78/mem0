#!/usr/bin/env python3
"""
FoundationModels status checking and caching
Provides efficient availability checking with caching
"""

import platform
from typing import Dict, Any, Optional
from apple_intelligence_framework import AppleIntelligenceError


class StatusChecker:
    """Handles FoundationModels availability checking with caching"""
    
    def __init__(self):
        self._cached_status: Optional[Dict[str, Any]] = None
        self._cache_valid = False
    
    def is_available(self, use_cache: bool = True) -> bool:
        """
        Quick boolean check for FoundationModels availability
        
        Args:
            use_cache: Use cached result if available
            
        Returns:
            True if FoundationModels is available
        """
        status = self.check_availability(use_cache)
        return status.get("available", False)
    
    def check_availability(self, use_cache: bool = True) -> Dict[str, Any]:
        """
        Comprehensive availability check with detailed status
        
        Args:
            use_cache: Use cached result if available
            
        Returns:
            Detailed status information
        """
        if use_cache and self._cache_valid and self._cached_status:
            return self._cached_status
        
        status = self._perform_availability_check()
        
        # Cache the result
        self._cached_status = status
        self._cache_valid = True
        
        return status
    
    def _perform_availability_check(self) -> Dict[str, Any]:
        """Perform the actual availability check"""
        # Check basic system requirements
        system_check = self._check_system_requirements()
        if not system_check["compatible"]:
            return {
                "available": False,
                "status": system_check["reason"],
                "system_compatible": False,
                "framework_available": False,
                "model_available": False
            }
        
        # Check framework availability
        framework_check = self._check_framework_availability()
        if not framework_check["available"]:
            return {
                "available": False,
                "status": framework_check["reason"],
                "system_compatible": True,
                "framework_available": False,
                "model_available": False
            }
        
        # Check model availability
        model_check = self._check_model_availability()
        
        return {
            "available": model_check["available"],
            "status": model_check["status"],
            "system_compatible": True,
            "framework_available": True,
            "model_available": model_check["available"],
            "details": model_check
        }
    
    def _check_system_requirements(self) -> Dict[str, Any]:
        """Check if system meets basic requirements"""
        try:
            # Check macOS version
            if platform.system() != "Darwin":
                return {
                    "compatible": False,
                    "reason": "FoundationModels requires macOS"
                }
            
            # Check macOS version (need 15.1+)
            version = platform.mac_ver()[0]
            if version:
                major, minor = map(int, version.split('.')[:2])
                if major < 15 or (major == 15 and minor < 1):
                    return {
                        "compatible": False,
                        "reason": f"macOS {version} detected, need 15.1+"
                    }
            
            # Check architecture (need Apple Silicon)
            arch = platform.machine()
            if arch not in ["arm64"]:
                return {
                    "compatible": False,
                    "reason": f"Architecture {arch} not supported, need Apple Silicon"
                }
            
            return {
                "compatible": True,
                "reason": "System requirements met"
            }
            
        except Exception as e:
            return {
                "compatible": False,
                "reason": f"System check failed: {e}"
            }
    
    def _check_framework_availability(self) -> Dict[str, Any]:
        """Check if Foundation Models framework is available"""
        try:
            from apple_intelligence_framework import FoundationModels
            
            framework = FoundationModels()
            framework.load_framework()
            
            return {
                "available": True,
                "reason": "Foundation Models framework loaded successfully"
            }
            
        except AppleIntelligenceError as e:
            return {
                "available": False,
                "reason": f"Framework loading failed: {e}"
            }
        except Exception as e:
            return {
                "available": False,
                "reason": f"Unexpected framework error: {e}"
            }
    
    def _check_model_availability(self) -> Dict[str, Any]:
        """Check if FoundationModels model is available"""
        try:
            from apple_intelligence_framework import FoundationModels, AppleIntelligenceModel
            
            # Load framework
            framework = FoundationModels()
            framework.load_framework()
            
            # Initialize model
            model = AppleIntelligenceModel(framework)
            model.initialize()
            
            # Check availability
            availability = model.check_availability()
            
            return {
                "available": availability["available"],
                "status": availability["status"],
                "code": availability["code"],
                "details": availability
            }
            
        except AppleIntelligenceError as e:
            return {
                "available": False,
                "status": f"Model check failed: {e}",
                "code": -1
            }
        except Exception as e:
            return {
                "available": False,
                "status": f"Unexpected model error: {e}",
                "code": -1
            }
    
    def clear_cache(self):
        """Clear cached status to force fresh check"""
        self._cached_status = None
        self._cache_valid = False
    
    def get_cached_status(self) -> Optional[Dict[str, Any]]:
        """Get cached status without performing new check"""
        return self._cached_status if self._cache_valid else None


# Global status checker instance
_status_checker = StatusChecker()

# Convenience functions
def is_apple_intelligence_ready(use_cache: bool = True) -> bool:
    """Quick check if FoundationModels is ready"""
    return _status_checker.is_available(use_cache)

def get_apple_intelligence_status(use_cache: bool = True) -> Dict[str, Any]:
    """Get detailed FoundationModels status"""
    return _status_checker.check_availability(use_cache)

def clear_status_cache():
    """Clear cached status to force fresh check"""
    _status_checker.clear_cache()