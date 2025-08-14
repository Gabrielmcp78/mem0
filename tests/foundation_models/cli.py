#!/usr/bin/env python3
"""
Command-line interface for FoundationModels tests
Provides easy access to different test scenarios
"""

import sys
import argparse
from typing import List
from .test_runner import FoundationModelsTestRunner
from .config import TestConfig


class TestCLI:
    """Command-line interface for FoundationModels tests"""
    
    def __init__(self):
        self.runner = FoundationModelsTestRunner()
    
    def create_parser(self) -> argparse.ArgumentParser:
        """Create command-line argument parser"""
        parser = argparse.ArgumentParser(
            description="FoundationModels Test Suite",
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog="""
Examples:
  python -m tests.foundation_models.cli                    # Run all tests
  python -m tests.foundation_models.cli --quick            # Quick availability check
  python -m tests.foundation_models.cli --core             # Run core tests only
  python -m tests.foundation_models.cli --tests model_init # Run specific test
            """
        )
        
        parser.add_argument(
            "--quick", 
            action="store_true",
            help="Run quick availability check only"
        )
        
        parser.add_argument(
            "--core",
            action="store_true", 
            help="Run core tests only (framework, model, availability)"
        )
        
        parser.add_argument(
            "--advanced",
            action="store_true",
            help="Run advanced tests only (session, analysis)"
        )
        
        parser.add_argument(
            "--tests",
            nargs="+",
            help="Run specific tests by name",
            choices=TestConfig.ALL_TESTS
        )
        
        parser.add_argument(
            "--list",
            action="store_true",
            help="List available tests"
        )
        
        parser.add_argument(
            "--verbose",
            action="store_true",
            help="Enable verbose output"
        )
        
        return parser
    
    def list_tests(self):
        """List all available tests"""
        print("Available tests:")
        print("\nCore tests:")
        for test in TestConfig.CORE_TESTS:
            print(f"  - {test}")
        
        print("\nAdvanced tests:")
        for test in TestConfig.ADVANCED_TESTS:
            print(f"  - {test}")
    
    def run_quick_test(self) -> bool:
        """Run quick availability check"""
        print("Running quick FoundationModels availability check...")
        results = self.runner.run_specific_tests(TestConfig.CORE_TESTS)
        return self.runner.print_summary()
    
    def run_core_tests(self) -> bool:
        """Run core tests only"""
        print("Running core FoundationModels tests...")
        results = self.runner.run_specific_tests(TestConfig.CORE_TESTS)
        return self.runner.print_summary()
    
    def run_advanced_tests(self) -> bool:
        """Run advanced tests only"""
        print("Running advanced FoundationModels tests...")
        results = self.runner.run_specific_tests(TestConfig.ADVANCED_TESTS)
        return self.runner.print_summary()
    
    def run_specific_tests(self, test_names: List[str]) -> bool:
        """Run specific tests"""
        print(f"Running specific tests: {', '.join(test_names)}")
        results = self.runner.run_specific_tests(test_names)
        return self.runner.print_summary()
    
    def run_all_tests(self) -> bool:
        """Run all tests"""
        print("Running complete FoundationModels test suite...")
        results = self.runner.run_all_tests()
        return self.runner.print_summary()
    
    def main(self):
        """Main CLI entry point"""
        parser = self.create_parser()
        args = parser.parse_args()
        
        if args.list:
            self.list_tests()
            return 0
        
        success = False
        
        try:
            if args.quick:
                success = self.run_quick_test()
            elif args.core:
                success = self.run_core_tests()
            elif args.advanced:
                success = self.run_advanced_tests()
            elif args.tests:
                success = self.run_specific_tests(args.tests)
            else:
                success = self.run_all_tests()
        
        except KeyboardInterrupt:
            print("\n\nTest execution interrupted by user")
            return 1
        except Exception as e:
            print(f"\nUnexpected error: {e}")
            return 1
        
        return 0 if success else 1


def main():
    """CLI entry point"""
    cli = TestCLI()
    sys.exit(cli.main())


if __name__ == "__main__":
    main()