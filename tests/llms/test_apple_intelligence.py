"""
Unit tests for Apple Intelligence LLM provider

This module contains unit tests for the Apple Intelligence LLM provider,
testing initialization, configuration, and response generation.
"""

import pytest
import logging
from unittest.mock import Mock, patch
from typing import Dict, Any

from mem0.llms.apple_intelligence import (
    AppleIntelligenceLLM,
    AppleIntelligenceLlmConfig,
    create_apple_intelligence_llm,
    is_apple_intelligence_llm_available
)
from mem0.utils.apple_intelligence import (
    AppleIntelligenceError,
    AppleIntelligenceUnavailableError
)


class TestAppleIntelligenceLlmConfig:
    """Test Apple Intelligence LLM configuration"""
    
    def test_default_config(self):
        """Test default configuration values"""
        config = AppleIntelligenceLlmConfig()
        
        assert config.model == "apple-intelligence-foundation"
        assert config.temperature == 0.3
        assert config.max_tokens == 500
        assert config.top_p == 0.9
        assert config.top_k == 50
        assert config.enable_neural_engine is True
        assert config.privacy_mode == "strict"
        assert config.fallback_provider is None
    
    def test_custom_config(self):
        """Test custom configuration values"""
        config = AppleIntelligenceLlmConfig(
            model="custom-model",
            temperature=0.7,
            max_tokens=1000,
            top_p=0.8,
            top_k=40,
            enable_neural_engine=False,
            privacy_mode="moderate",
            fallback_provider="ollama"
        )
        
        assert config.model == "custom-model"
        assert config.temperature == 0.7
        assert config.max_tokens == 1000
        assert config.top_p == 0.8
        assert config.top_k == 40
        assert config.enable_neural_engine is False
        assert config.privacy_mode == "moderate"
        assert config.fallback_provider == "ollama"
    
    def test_invalid_privacy_mode(self):
        """Test invalid privacy mode raises error"""
        with pytest.raises(ValueError, match="privacy_mode must be one of"):
            AppleIntelligenceLlmConfig(privacy_mode="invalid")
    
    def test_invalid_temperature(self):
        """Test invalid temperature raises error"""
        with pytest.raises(ValueError, match="temperature must be between"):
            AppleIntelligenceLlmConfig(temperature=1.5)
        
        with pytest.raises(ValueError, match="temperature must be between"):
            AppleIntelligenceLlmConfig(temperature=-0.1)
    
    def test_invalid_top_p(self):
        """Test invalid top_p raises error"""
        with pytest.raises(ValueError, match="top_p must be between"):
            AppleIntelligenceLlmConfig(top_p=1.5)
        
        with pytest.raises(ValueError, match="top_p must be between"):
            AppleIntelligenceLlmConfig(top_p=-0.1)
    
    def test_invalid_max_tokens(self):
        """Test invalid max_tokens raises error"""
        with pytest.raises(ValueError, match="max_tokens must be positive"):
            AppleIntelligenceLlmConfig(max_tokens=0)
        
        with pytest.raises(ValueError, match="max_tokens must be positive"):
            AppleIntelligenceLlmConfig(max_tokens=-10)


class TestAppleIntelligenceLLM:
    """Test Apple Intelligence LLM provider"""
    
    @patch('mem0.llms.apple_intelligence.get_foundation_models_interface')
    def test_initialization_success(self, mock_get_interface):
        """Test successful LLM initialization"""
        # Mock successful interface
        mock_interface = Mock()
        mock_interface.is_available = True
        mock_interface.error_message = None
        mock_get_interface.return_value = mock_interface
        
        llm = AppleIntelligenceLLM()
        
        assert llm.is_available is True
        assert llm.error_message is None
        assert llm.config.model == "apple-intelligence-foundation"
    
    @patch('mem0.llms.apple_intelligence.get_foundation_models_interface')
    def test_initialization_failure(self, mock_get_interface):
        """Test LLM initialization failure"""
        # Mock failed interface
        mock_interface = Mock()
        mock_interface.is_available = False
        mock_interface.error_message = "Apple Intelligence not available"
        mock_get_interface.return_value = mock_interface
        
        llm = AppleIntelligenceLLM()
        
        assert llm.is_available is False
        assert "Apple Intelligence not available" in llm.error_message
    
    @patch('mem0.llms.apple_intelligence.get_foundation_models_interface')
    def test_custom_config_initialization(self, mock_get_interface):
        """Test initialization with custom config"""
        # Mock successful interface
        mock_interface = Mock()
        mock_interface.is_available = True
        mock_get_interface.return_value = mock_interface
        
        config = AppleIntelligenceLlmConfig(
            model="custom-model",
            temperature=0.7,
            max_tokens=1000
        )
        
        llm = AppleIntelligenceLLM(config)
        
        assert llm.config.model == "custom-model"
        assert llm.config.temperature == 0.7
        assert llm.config.max_tokens == 1000
    
    @patch('mem0.llms.apple_intelligence.get_foundation_models_interface')
    def test_generate_response_success(self, mock_get_interface):
        """Test successful response generation"""
        # Mock successful interface
        mock_interface = Mock()
        mock_interface.is_available = True
        mock_interface.generate_text.return_value = "Test response from Apple Intelligence"
        mock_get_interface.return_value = mock_interface
        
        llm = AppleIntelligenceLLM()
        
        messages = [
            {"role": "user", "content": "Hello"}
        ]
        
        response = llm.generate_response(messages)
        
        assert response == "Test response from Apple Intelligence"
        mock_interface.generate_text.assert_called_once()
    
    @patch('mem0.llms.apple_intelligence.get_foundation_models_interface')
    def test_generate_response_unavailable(self, mock_get_interface):
        """Test response generation when Apple Intelligence unavailable"""
        # Mock unavailable interface
        mock_interface = Mock()
        mock_interface.is_available = False
        mock_interface.error_message = "Apple Intelligence not available"
        mock_get_interface.return_value = mock_interface
        
        llm = AppleIntelligenceLLM()
        
        messages = [
            {"role": "user", "content": "Hello"}
        ]
        
        with pytest.raises(AppleIntelligenceUnavailableError):
            llm.generate_response(messages)
    
    @patch('mem0.llms.apple_intelligence.get_foundation_models_interface')
    def test_generate_response_with_tools(self, mock_get_interface):
        """Test response generation with tools"""
        # Mock successful interface
        mock_interface = Mock()
        mock_interface.is_available = True
        mock_interface.generate_text.return_value = "Test response with tools"
        mock_get_interface.return_value = mock_interface
        
        llm = AppleIntelligenceLLM()
        
        messages = [
            {"role": "user", "content": "Hello"}
        ]
        tools = [{"name": "test_tool", "description": "A test tool"}]
        
        response = llm.generate_response(messages, tools=tools)
        
        assert isinstance(response, dict)
        assert response["content"] == "Test response with tools"
        assert response["tool_calls"] == []
    
    @patch('mem0.llms.apple_intelligence.get_foundation_models_interface')
    def test_message_formatting(self, mock_get_interface):
        """Test message formatting for Apple Intelligence"""
        # Mock successful interface
        mock_interface = Mock()
        mock_interface.is_available = True
        mock_interface.generate_text.return_value = "Formatted response"
        mock_get_interface.return_value = mock_interface
        
        llm = AppleIntelligenceLLM()
        
        messages = [
            {"role": "system", "content": "You are helpful"},
            {"role": "user", "content": "Hello"},
            {"role": "assistant", "content": "Hi there"},
            {"role": "user", "content": "How are you?"}
        ]
        
        llm.generate_response(messages)
        
        # Check that generate_text was called with formatted prompt
        call_args = mock_interface.generate_text.call_args[0]
        prompt = call_args[0]
        
        assert "System: You are helpful" in prompt
        assert "User: Hello" in prompt
        assert "Assistant: Hi there" in prompt
        assert "User: How are you?" in prompt
    
    @patch('mem0.llms.apple_intelligence.get_foundation_models_interface')
    def test_get_model_info(self, mock_get_interface):
        """Test getting model information"""
        # Mock successful interface
        mock_interface = Mock()
        mock_interface.is_available = True
        mock_interface.get_system_info.return_value = {
            'macos_version': (15, 1),
            'platform': 'Darwin'
        }
        mock_get_interface.return_value = mock_interface
        
        llm = AppleIntelligenceLLM()
        info = llm.get_model_info()
        
        assert info['provider'] == 'apple_intelligence'
        assert info['model'] == 'apple-intelligence-foundation'
        assert info['available'] is True
        assert info['local_processing'] is True
        assert info['neural_engine_optimized'] is True
        assert info['privacy_mode'] == 'strict'
        assert info['macos_version'] == (15, 1)
        assert info['platform'] == 'Darwin'


class TestUtilityFunctions:
    """Test utility functions"""
    
    @patch('mem0.llms.apple_intelligence.check_apple_intelligence_availability')
    def test_is_apple_intelligence_llm_available(self, mock_check):
        """Test availability check function"""
        mock_check.return_value = True
        assert is_apple_intelligence_llm_available() is True
        
        mock_check.return_value = False
        assert is_apple_intelligence_llm_available() is False
    
    def test_create_apple_intelligence_llm_default(self):
        """Test creating LLM with default config"""
        with patch('mem0.llms.apple_intelligence.get_foundation_models_interface') as mock_get_interface:
            mock_interface = Mock()
            mock_interface.is_available = True
            mock_get_interface.return_value = mock_interface
            
            llm = create_apple_intelligence_llm()
            
            assert isinstance(llm, AppleIntelligenceLLM)
            assert llm.config.model == "apple-intelligence-foundation"
    
    def test_create_apple_intelligence_llm_custom(self):
        """Test creating LLM with custom config"""
        with patch('mem0.llms.apple_intelligence.get_foundation_models_interface') as mock_get_interface:
            mock_interface = Mock()
            mock_interface.is_available = True
            mock_get_interface.return_value = mock_interface
            
            config = {
                "model": "custom-model",
                "temperature": 0.7,
                "max_tokens": 1000
            }
            
            llm = create_apple_intelligence_llm(config)
            
            assert isinstance(llm, AppleIntelligenceLLM)
            assert llm.config.model == "custom-model"
            assert llm.config.temperature == 0.7
            assert llm.config.max_tokens == 1000


if __name__ == "__main__":
    pytest.main([__file__])