#!/usr/bin/env python3
"""
Refactored FoundationModels test suite - Clean, modular interface
This is the new recommended way to test FoundationModels functionality
"""

from tests.foundation_models import (
    FoundationModelsTestRunner,
    run_foundation_models_tests,
    run_quick_test
)


class AppleIntelligenceTestSuite:
    """
    Backward compatibility wrapper for the refactored test suite
    Maintains the same interface while using modular components
    """
    
    def __init__(self):
        self.runner = FoundationModelsTestRunner()
        self.results = {}
    
    def run_all_tests(self):
        """Run all tests - maintains backward compatibility"""
        self.results = self.runner.run_all_tests()
        return self.results
    
    def print_summary(self):
        """Print test summary - maintains backward compatibility"""
        return self.runner.print_summary()
    
    # Individual test methods for backward compatibility
    def test_framework_loading(self):
        return self.runner.test_cases.test_framework_loading()
    
    def test_model_initialization(self):
        return self.runner.test_cases.test_model_initialization()
    
    def test_availability_check(self):
        return self.runner.test_cases.test_availability_check()
    
    def test_session_creation(self):
        return self.runner.test_cases.test_session_creation()
    
    def test_semantic_analysis_setup(self):
        return self.runner.test_cases.test_semantic_analysis_setup()
    
    def test_semantic_analysis(self):
        return self.runner.test_cases.test_semantic_analysis()


def main():
    """Main test execution with multiple options"""
    import sys
    
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == "quick":
            # Quick test - just check availability
            print("Running quick FoundationModels test...")
            success = run_quick_test()
            sys.exit(0 if success else 1)
        
        elif command == "specific":
            # Run specific tests
            if len(sys.argv) < 3:
                print("Usage: python test_apple_intelligence_modular_v2.py specific test1 test2 ...")
                sys.exit(1)
            
            test_names = sys.argv[2:]
            runner = FoundationModelsTestRunner()
            runner.run_specific_tests(test_names)
            success = runner.print_summary()
            sys.exit(0 if success else 1)
        
        elif command == "help":
            print("FoundationModels Test Suite")
            print("Usage:")
            print("  python test_apple_intelligence_modular_v2.py           # Run all tests")
            print("  python test_apple_intelligence_modular_v2.py quick     # Quick availability check")
            print("  python test_apple_intelligence_modular_v2.py specific test1 test2  # Run specific tests")
            print("  python test_apple_intelligence_modular_v2.py help      # Show this help")
            print("\nAvailable tests:")
            print("  - framework_loading")
            print("  - model_initialization") 
            print("  - availability_check")
            print("  - session_creation")
            print("  - semantic_analysis_setup")
            print("  - semantic_analysis")
            sys.exit(0)
    
    # Default: run all tests
    success = run_foundation_models_tests()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()