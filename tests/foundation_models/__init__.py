#!/usr/bin/env python3
"""
FoundationModels test package
Provides modular, maintainable testing for FoundationModels functionality
"""

from .test_runner import FoundationModelsTestRunner
from .test_cases import FoundationModelsTestCases
from .test_reporter import TestReporter
from .config import TestConfig
from .cli import TestCLI

__all__ = [
    "FoundationModelsTestRunner",
    "FoundationModelsTestCases", 
    "TestReporter",
    "TestConfig",
    "TestCLI",
]


def run_foundation_models_tests():
    """Convenience function to run all FoundationModels tests"""
    runner = FoundationModelsTestRunner()
    runner.run_all_tests()
    return runner.print_summary()


def run_quick_test():
    """Quick test to check if FoundationModels is available"""
    runner = FoundationModelsTestRunner()
    results = runner.run_specific_tests([
        "framework_loading",
        "model_initialization", 
        "availability_check"
    ])
    return runner.print_summary()