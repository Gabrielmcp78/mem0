#!/usr/bin/env python3
"""
Test runner for FoundationModels tests
Orchestrates test execution and reporting
"""

from typing import Dict, List, Tuple, Callable
from .test_cases import FoundationModelsTestCases
from .test_reporter import TestReporter


class FoundationModelsTestRunner:
    """Orchestrates FoundationModels test execution"""
    
    def __init__(self):
        self.test_cases = FoundationModelsTestCases()
        self.reporter = TestReporter()
        self.results: Dict[str, bool] = {}
    
    def get_test_suite(self) -> List[Tuple[str, Callable[[], bool]]]:
        """Get the complete test suite"""
        return [
            ("framework_loading", self.test_cases.test_framework_loading),
            ("model_initialization", self.test_cases.test_model_initialization),
            ("availability_check", self.test_cases.test_availability_check),
            ("session_creation", self.test_cases.test_session_creation),
            ("semantic_analysis_setup", self.test_cases.test_semantic_analysis_setup),
            ("semantic_analysis", self.test_cases.test_semantic_analysis),
        ]
    
    def run_all_tests(self) -> Dict[str, bool]:
        """Run all tests and collect results"""
        self.reporter.print_header()
        
        test_suite = self.get_test_suite()
        results = {}
        
        for test_name, test_func in test_suite:
            try:
                results[test_name] = test_func()
                self.reporter.add_spacing()
            except Exception as e:
                self.reporter.print_unexpected_error(test_name, e)
                results[test_name] = False
                self.reporter.add_spacing()
        
        self.results = results
        return results
    
    def run_specific_tests(self, test_names: List[str]) -> Dict[str, bool]:
        """Run only specific tests"""
        test_suite = {name: func for name, func in self.get_test_suite()}
        results = {}
        
        for test_name in test_names:
            if test_name in test_suite:
                try:
                    results[test_name] = test_suite[test_name]()
                except Exception as e:
                    self.reporter.print_unexpected_error(test_name, e)
                    results[test_name] = False
            else:
                self.reporter.print_test_not_found(test_name)
                results[test_name] = False
        
        self.results = results
        return results
    
    def print_summary(self) -> bool:
        """Print test results summary"""
        return self.reporter.print_summary(self.results)
    
    def get_failed_tests(self) -> List[str]:
        """Get list of failed test names"""
        return [name for name, passed in self.results.items() if not passed]
    
    def get_passed_tests(self) -> List[str]:
        """Get list of passed test names"""
        return [name for name, passed in self.results.items() if passed]