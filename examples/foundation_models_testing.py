#!/usr/bin/env python3
"""
Example usage of the refactored FoundationModels test suite
Demonstrates different ways to use the modular test architecture
"""

from tests.foundation_models import (
    run_foundation_models_tests,
    run_quick_test,
    FoundationModelsTestRunner,
    TestConfig
)


def example_simple_usage():
    """Example: Simple test execution"""
    print("=== Simple Usage Example ===")
    
    # Run all tests with one function call
    success = run_foundation_models_tests()
    
    if success:
        print("✅ All tests passed!")
    else:
        print("❌ Some tests failed")
    
    return success


def example_quick_check():
    """Example: Quick availability check"""
    print("=== Quick Check Example ===")
    
    # Quick check if FoundationModels is available
    success = run_quick_test()
    
    if success:
        print("✅ FoundationModels is available!")
    else:
        print("❌ FoundationModels not available")
    
    return success


def example_advanced_usage():
    """Example: Advanced test runner usage"""
    print("=== Advanced Usage Example ===")
    
    runner = FoundationModelsTestRunner()
    
    # Run core tests first
    print("Running core tests...")
    core_results = runner.run_specific_tests(TestConfig.CORE_TESTS)
    
    if all(core_results.values()):
        print("✅ Core tests passed, running advanced tests...")
        
        # Run advanced tests
        advanced_results = runner.run_specific_tests(TestConfig.ADVANCED_TESTS)
        
        # Get detailed results
        all_passed = runner.print_summary()
        
        if not all_passed:
            failed_tests = runner.get_failed_tests()
            print(f"Failed tests: {failed_tests}")
    
    else:
        print("❌ Core tests failed, skipping advanced tests")
        failed_tests = runner.get_failed_tests()
        print(f"Failed core tests: {failed_tests}")


def example_custom_test_selection():
    """Example: Custom test selection"""
    print("=== Custom Test Selection Example ===")
    
    runner = FoundationModelsTestRunner()
    
    # Run only specific tests we care about
    important_tests = [
        "framework_loading",
        "model_initialization", 
        "availability_check"
    ]
    
    print(f"Running tests: {', '.join(important_tests)}")
    results = runner.run_specific_tests(important_tests)
    
    # Check results
    for test_name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{test_name}: {status}")
    
    return all(results.values())


def example_error_handling():
    """Example: Proper error handling"""
    print("=== Error Handling Example ===")
    
    try:
        runner = FoundationModelsTestRunner()
        results = runner.run_all_tests()
        
        if not all(results.values()):
            # Handle specific failures
            failed_tests = runner.get_failed_tests()
            
            if "framework_loading" in failed_tests:
                print("⚠️  Framework loading failed - check macOS version and architecture")
            
            if "model_initialization" in failed_tests:
                print("⚠️  Model initialization failed - check FoundationModels availability")
            
            if "availability_check" in failed_tests:
                print("⚠️  Availability check failed - FoundationModels may not be ready")
        
        return runner.print_summary()
        
    except Exception as e:
        print(f"❌ Unexpected error during testing: {e}")
        return False


def main():
    """Run all examples"""
    examples = [
        ("Simple Usage", example_simple_usage),
        ("Quick Check", example_quick_check), 
        ("Advanced Usage", example_advanced_usage),
        ("Custom Selection", example_custom_test_selection),
        ("Error Handling", example_error_handling),
    ]
    
    print("FoundationModels Test Suite Examples")
    print("=" * 50)
    
    for name, example_func in examples:
        print(f"\n{name}:")
        print("-" * len(name))
        
        try:
            success = example_func()
            print(f"Example result: {'✅ Success' if success else '❌ Failed'}")
        except Exception as e:
            print(f"Example error: {e}")
        
        print()


if __name__ == "__main__":
    main()