#!/usr/bin/env python3
"""
Individual test cases for FoundationModels functionality
Each test is focused and independent
"""

from apple_intelligence import (
    FoundationModelsFramework,
    AppleIntelligenceModel,
    SemanticAnalyzer,
    AppleIntelligenceError
)
from .test_reporter import TestReporter
from .config import TestConfig


class FoundationModelsTestCases:
    """Individual test cases for FoundationModels"""
    
    def __init__(self):
        self.framework = FoundationModelsFramework()
        self.model = None
        self.analyzer = None
        self.reporter = TestReporter()
    
    def test_framework_loading(self) -> bool:
        """Test Foundation Models framework loading"""
        self.reporter.print_test_header("Framework Loading")
        
        try:
            success = self.framework.load_framework()
            messages = TestConfig.get_test_messages()
            self.reporter.print_success(messages['framework_success'])
            return success
        except AppleIntelligenceError as e:
            self.reporter.print_failure(f"Framework loading failed: {e}")
            return False
    
    def test_model_initialization(self) -> bool:
        """Test FoundationModels model initialization"""
        self.reporter.print_test_header("Model Initialization")
        
        try:
            self.model = AppleIntelligenceModel(self.framework)
            self.model.initialize()
            self.reporter.print_success("FoundationModels model initialized")
            return True
        except AppleIntelligenceError as e:
            self.reporter.print_failure(f"Model initialization failed: {e}")
            return False
    
    def test_availability_check(self) -> bool:
        """Test model availability"""
        self.reporter.print_test_header("Model Availability")
        
        if not self.model:
            self.reporter.print_failure("Model not initialized")
            return False
        
        try:
            availability = self.model.check_availability()
            self.reporter.print_info(f"Model availability: {availability['status']}")
            
            if availability['available']:
                self.reporter.print_success("FoundationModels is AVAILABLE!")
                return True
            else:
                self.reporter.print_failure(f"FoundationModels not available: {availability['status']}")
                return False
                
        except AppleIntelligenceError as e:
            self.reporter.print_failure(f"Availability check failed: {e}")
            return False
    
    def test_session_creation(self) -> bool:
        """Test language model session creation"""
        self.reporter.print_test_header("Session Creation")
        
        if not self.model:
            self.reporter.print_failure("Model not initialized")
            return False
        
        try:
            session = self.model.create_session()
            self.reporter.print_success(f"LanguageModelSession created: {session}")
            return True
        except AppleIntelligenceError as e:
            self.reporter.print_failure(f"Session creation failed: {e}")
            return False
    
    def test_semantic_analysis_setup(self) -> bool:
        """Test semantic analysis setup"""
        self.reporter.print_test_header("Semantic Analysis Setup")
        
        if not self.model:
            self.reporter.print_failure("Model not initialized")
            return False
        
        try:
            self.analyzer = SemanticAnalyzer(self.model)
            self.analyzer.setup()
            self.reporter.print_success("Semantic analyzer setup complete")
            return True
        except AppleIntelligenceError as e:
            self.reporter.print_failure(f"Semantic analysis setup failed: {e}")
            return False
    
    def test_semantic_analysis(self) -> bool:
        """Test semantic analysis functionality"""
        self.reporter.print_test_header("Semantic Analysis")
        
        if not self.analyzer:
            self.reporter.print_failure("Semantic analyzer not setup")
            return False
        
        try:
            test_text = TestConfig.SAMPLE_TEXT
            result = self.analyzer.analyze(test_text)
            
            self.reporter.print_info(f"Analyzing: {test_text}")
            self.reporter.print_info(f"Analysis result: {result}")
            self.reporter.print_success("Semantic analysis ready!")
            return True
            
        except AppleIntelligenceError as e:
            self.reporter.print_failure(f"Semantic analysis failed: {e}")
            return False