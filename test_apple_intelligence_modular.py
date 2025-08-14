#!/usr/bin/env python3
"""
REFACTORED: This file has been refactored into a modular architecture

The functionality has been moved to:
- tests/foundation_models/ - New modular test package
- test_apple_intelligence_modular_v2.py - Backward compatible interface

For new code, use:
    from tests.foundation_models import run_foundation_models_tests
    success = run_foundation_models_tests()

For CLI usage:
    python -m tests.foundation_models.cli --quick

This file is maintained for backward compatibility only.
"""

# Import the refactored components
from tests.foundation_models import (
    FoundationModelsTestRunner,
    TestReporter,
    TestConfig
)
from apple_intelligence import (
    FoundationModelsFramework,
    AppleIntelligenceModel,
    SemanticAnalyzer,
    AppleIntelligenceError
)
from typing import Dict


class AppleIntelligenceTestSuite:
    """
    DEPRECATED: Use tests.foundation_models.FoundationModelsTestRunner instead
    
    This class is maintained for backward compatibility only.
    The functionality has been refactored into a modular architecture.
    """
    
    def __init__(self):
        # Use the new modular test runner internally
        self._runner = FoundationModelsTestRunner()
        self.results = {}
        
        # Maintain backward compatibility properties
        self.framework = self._runner.test_cases.framework
        self.model = None
        self.analyzer = None
    
    def test_framework_loading(self) -> bool:
        """Test Foundation Models framework loading"""
        print("=== Testing Framework Loading ===")
        
        try:
            success = self.framework.load_framework()
            print("✅ Foundation Models framework loaded")
            return success
        except AppleIntelligenceError as e:
            print(f"❌ Framework loading failed: {e}")
            return False
    
    def test_model_initialization(self) -> bool:
        """Test FoundationModels model initialization"""
        print("=== Testing Model Initialization ===")
        
        try:
            self.model = AppleIntelligenceModel(self.framework)
            self.model.initialize()
            print("✅ FoundationModels model initialized")
            return True
        except AppleIntelligenceError as e:
            print(f"❌ Model initialization failed: {e}")
            return False
    
    def test_availability_check(self) -> bool:
        """Test model availability"""
        print("=== Testing Model Availability ===")
        
        try:
            availability = self.model.check_availability()
            print(f"Model availability: {availability['status']}")
            
            if availability['available']:
                print("✅ FoundationModels is AVAILABLE!")
                return True
            else:
                print(f"❌ FoundationModels not available: {availability['status']}")
                return False
                
        except AppleIntelligenceError as e:
            print(f"❌ Availability check failed: {e}")
            return False
    
    def test_session_creation(self) -> bool:
        """Test language model session creation"""
        print("=== Testing Session Creation ===")
        
        try:
            session = self.model.create_session()
            print(f"✅ LanguageModelSession created: {session}")
            return True
        except AppleIntelligenceError as e:
            print(f"❌ Session creation failed: {e}")
            return False
    
    def test_semantic_analysis_setup(self) -> bool:
        """Test semantic analysis setup"""
        print("=== Testing Semantic Analysis Setup ===")
        
        try:
            self.analyzer = SemanticAnalyzer(self.model)
            self.analyzer.setup()
            print("✅ Semantic analyzer setup complete")
            return True
        except AppleIntelligenceError as e:
            print(f"❌ Semantic analysis setup failed: {e}")
            return False
    
    def test_semantic_analysis(self) -> bool:
        """Test semantic analysis functionality"""
        print("=== Testing Semantic Analysis ===")
        
        if not self.analyzer:
            print("❌ Semantic analyzer not setup")
            return False
        
        try:
            test_text = "I'm testing the mem0 enhanced MCP server tools to verify functionality"
            result = self.analyzer.analyze(test_text)
            
            print(f"Analyzing: {test_text}")
            print(f"Analysis result: {result}")
            print("✅ Semantic analysis ready!")
            return True
            
        except AppleIntelligenceError as e:
            print(f"❌ Semantic analysis failed: {e}")
            return False
    
    def run_all_tests(self) -> Dict[str, bool]:
        """Run all tests and return results - uses refactored implementation"""
        print("⚠️  Using deprecated interface - consider upgrading to tests.foundation_models")
        print("   New usage: from tests.foundation_models import run_foundation_models_tests\n")
        
        self.results = self._runner.run_all_tests()
        
        # Update backward compatibility properties
        self.model = self._runner.test_cases.model
        self.analyzer = self._runner.test_cases.analyzer
        
        return self.results
    
    def print_summary(self):
        """Print test results summary - uses refactored implementation"""
        return self._runner.print_summary()


def main():
    """Main test execution - shows deprecation notice"""
    print("=" * 60)
    print("DEPRECATION NOTICE")
    print("=" * 60)
    print("This file has been refactored into a modular architecture.")
    print("Please use one of these alternatives:")
    print()
    print("1. Simple usage:")
    print("   from tests.foundation_models import run_foundation_models_tests")
    print("   run_foundation_models_tests()")
    print()
    print("2. CLI usage:")
    print("   python -m tests.foundation_models.cli --quick")
    print()
    print("3. Backward compatible:")
    print("   python test_apple_intelligence_modular_v2.py")
    print()
    print("Running tests with deprecated interface...")
    print("=" * 60)
    print()
    
    test_suite = AppleIntelligenceTestSuite()
    test_suite.run_all_tests()
    test_suite.print_summary()


if __name__ == "__main__":
    main()