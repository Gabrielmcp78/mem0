#!/usr/bin/env python3
"""
Configuration for FoundationModels tests
Centralizes test settings and constants
"""

from typing import Dict, Any


class TestConfig:
    """Configuration settings for FoundationModels tests"""
    
    # Test text samples
    SAMPLE_TEXT = "I'm testing the mem0 enhanced MCP server tools to verify functionality"
    COMPLEX_TEXT = "The FoundationModels framework provides on-device AI processing with privacy-first design"
    
    # Test timeouts (in seconds)
    FRAMEWORK_LOAD_TIMEOUT = 30
    MODEL_INIT_TIMEOUT = 60
    ANALYSIS_TIMEOUT = 10
    
    # Output formatting
    SUCCESS_EMOJI = "✅"
    FAILURE_EMOJI = "❌"
    INFO_EMOJI = "ℹ️"
    CELEBRATION_EMOJI = "🎉"
    WARNING_EMOJI = "⚠️"
    
    # Test categories
    CORE_TESTS = [
        "framework_loading",
        "model_initialization",
        "availability_check"
    ]
    
    ADVANCED_TESTS = [
        "session_creation",
        "semantic_analysis_setup", 
        "semantic_analysis"
    ]
    
    ALL_TESTS = CORE_TESTS + ADVANCED_TESTS
    
    @classmethod
    def get_test_messages(cls) -> Dict[str, str]:
        """Get test-specific messages"""
        return {
            "framework_success": "Foundation Models framework loaded",
            "model_success": "FoundationModels model initialized",
            "availability_success": "FoundationModels is AVAILABLE!",
            "session_success": "LanguageModelSession created",
            "analyzer_success": "Semantic analyzer setup complete",
            "analysis_success": "Semantic analysis ready!",
            "final_success": "Foundation Models is properly configured and ready!",
            "final_info": "The mem0 enhanced MCP server should now use Foundation Models.",
            "final_warning": "Foundation Models not fully available"
        }
    
    @classmethod
    def get_troubleshooting_tips(cls) -> list[str]:
        """Get troubleshooting tips for failed tests"""
        return [
            "Ensure you're running on macOS 15.1+ with Apple Silicon",
            "Check that FoundationModels framework is available",
            "Verify PyObjC is properly installed",
            "Try restarting your terminal/IDE",
            "Check system resources and memory availability"
        ]