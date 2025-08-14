#!/usr/bin/env python3
"""
Test reporting utilities for FoundationModels tests
Handles all output formatting and result presentation
"""

from typing import Dict
from .config import TestConfig


class TestReporter:
    """Handles test output and reporting"""
    
    @staticmethod
    def print_header():
        """Print main test suite header"""
        print("=== FoundationModels Test Suite ===\n")
    
    @staticmethod
    def print_test_header(test_name: str):
        """Print individual test header"""
        print(f"=== Testing {test_name} ===")
    
    @staticmethod
    def print_success(message: str):
        """Print success message"""
        print(f"{TestConfig.SUCCESS_EMOJI} {message}")
    
    @staticmethod
    def print_failure(message: str):
        """Print failure message"""
        print(f"{TestConfig.FAILURE_EMOJI} {message}")
    
    @staticmethod
    def print_info(message: str):
        """Print informational message"""
        print(f"{TestConfig.INFO_EMOJI}  {message}")
    
    @staticmethod
    def print_unexpected_error(test_name: str, error: Exception):
        """Print unexpected error message"""
        print(f"❌ Unexpected error in {test_name}: {error}")
    
    @staticmethod
    def print_test_not_found(test_name: str):
        """Print test not found message"""
        print(f"❌ Test '{test_name}' not found")
    
    @staticmethod
    def add_spacing():
        """Add spacing between tests"""
        print()
    
    def print_summary(self, results: Dict[str, bool]) -> bool:
        """Print comprehensive test results summary"""
        print("=== Test Summary ===")
        
        # Print individual results
        for test_name, passed in results.items():
            status = "✅ PASS" if passed else "❌ FAIL"
            formatted_name = self._format_test_name(test_name)
            print(f"{formatted_name}: {status}")
        
        # Calculate statistics
        total_tests = len(results)
        passed_tests = sum(results.values())
        failed_tests = total_tests - passed_tests
        
        print(f"\nTests run: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {failed_tests}")
        
        # Print final status
        all_passed = all(results.values())
        
        messages = TestConfig.get_test_messages()
        
        if all_passed:
            print(f"\n{TestConfig.CELEBRATION_EMOJI} {messages['final_success']}")
            print(messages['final_info'])
        else:
            print(f"\n{TestConfig.WARNING_EMOJI}  {messages['final_warning']}")
            self._print_failure_details(results)
        
        return all_passed
    
    @staticmethod
    def _format_test_name(test_name: str) -> str:
        """Format test name for display"""
        return test_name.replace("_", " ").title()
    
    def _print_failure_details(self, results: Dict[str, bool]):
        """Print details about failed tests"""
        failed_tests = [name for name, passed in results.items() if not passed]
        
        if failed_tests:
            print(f"\nFailed tests:")
            for test_name in failed_tests:
                formatted_name = self._format_test_name(test_name)
                print(f"  - {formatted_name}")
            
            print("\nTroubleshooting:")
            for tip in TestConfig.get_troubleshooting_tips():
                print(f"  - {tip}")