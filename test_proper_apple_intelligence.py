#!/usr/bin/env python3
"""
Simple FoundationModels test using modular components
This is a lightweight wrapper around the modular test suite
"""

from test_apple_intelligence_modular import AppleIntelligenceTestSuite
from apple_intelligence import is_apple_intelligence_ready, AppleIntelligenceClient


def test_apple_intelligence():
    """Test basic FoundationModels functionality"""
    test_suite = AppleIntelligenceTestSuite()
    
    # Run core tests
    framework_ok = test_suite.test_framework_loading()
    if not framework_ok:
        return False
        
    model_ok = test_suite.test_model_initialization()
    if not model_ok:
        return False
        
    availability_ok = test_suite.test_availability_check()
    if not availability_ok:
        return False
        
    session_ok = test_suite.test_session_creation()
    return session_ok


def test_semantic_analysis():
    """Test semantic analysis setup"""
    test_suite = AppleIntelligenceTestSuite()
    
    try:
        # Quick setup
        test_suite.test_framework_loading()
        test_suite.test_model_initialization()
        
        availability = test_suite.model.check_availability()
        if not availability['available']:
            return {
                "status": "failed",
                "error": f"Model not available: {availability['status']}",
                "model_available": False,
                "framework_loaded": True
            }
        
        # Test semantic analysis
        analyzer_ok = test_suite.test_semantic_analysis_setup()
        analysis_ok = test_suite.test_semantic_analysis()
        
        if analyzer_ok and analysis_ok:
            return {
                "status": "ready",
                "session": test_suite.analyzer._session,
                "model_available": True,
                "framework_loaded": True
            }
        else:
            return {
                "status": "failed",
                "error": "Semantic analysis setup failed",
                "model_available": True,
                "framework_loaded": True
            }
            
    except Exception as e:
        return {
            "status": "failed",
            "error": str(e),
            "model_available": False,
            "framework_loaded": False
        }


if __name__ == "__main__":
    # Test basic FoundationModels
    basic_test = test_apple_intelligence()
    
    # Test semantic analysis setup
    semantic_test = test_semantic_analysis()
    
    # Summary
    print("\n=== Test Summary ===")
    print(f"Basic FoundationModels: {'✅ PASS' if basic_test else '❌ FAIL'}")
    print(f"Semantic Analysis Setup: {'✅ PASS' if semantic_test.get('status') == 'ready' else '❌ FAIL'}")
    
    if basic_test and semantic_test.get('status') == 'ready':
        print("\n🎉 Foundation Models is properly configured and ready!")
        print("The mem0 enhanced MCP server should now use Foundation Models.")
    else:
        print("\n⚠️  Foundation Models not fully available")