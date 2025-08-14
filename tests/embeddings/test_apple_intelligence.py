"""
Tests for FoundationModels Embedding Provider

This module contains unit tests for the FoundationModels embedding provider.
"""

import pytest
from unittest.mock import Mock, patch
from typing import List

from mem0.embeddings.apple_intelligence import AppleIntelligenceEmbedder
from mem0.configs.embeddings.base import BaseEmbedderConfig
from mem0.utils.apple_intelligence import (
    AppleIntelligenceUnavailableError,
    AppleIntelligenceError
)


class TestAppleIntelligenceEmbedder:
    """Test cases for FoundationModels embedder"""
    
    def test_init_with_default_config(self):
        """Test initialization with default configuration"""
        with patch('mem0.embeddings.apple_intelligence.get_foundation_models_interface') as mock_interface:
            mock_foundation_models = Mock()
            mock_foundation_models.is_available = True
            mock_interface.return_value = mock_foundation_models
            
            embedder = AppleIntelligenceEmbedder()
            
            assert embedder.config.model == "apple-intelligence-embeddings"
            assert embedder.config.embedding_dims == 1536
            assert embedder.config.neural_engine_optimization is True
            assert embedder.config.privacy_mode == "strict"
    
    def test_init_with_custom_config(self):
        """Test initialization with custom config"""
        config = BaseEmbedderConfig(
            model="custom-apple-model",
            embedding_dims=768
        )
        
        with patch('mem0.embeddings.apple_intelligence.get_foundation_models_interface') as mock_interface:
            mock_foundation_models = Mock()
            mock_foundation_models.is_available = True
            mock_interface.return_value = mock_foundation_models
            
            embedder = AppleIntelligenceEmbedder(config)
            
            assert embedder.config.model == "custom-apple-model"
            assert embedder.config.embedding_dims == 768
            assert embedder.neural_engine_optimization is True  # Default value
            assert embedder.privacy_mode == "strict"  # Default value
    
    def test_init_with_base_config(self):
        """Test initialization with base embedder config"""
        config = BaseEmbedderConfig(
            model="test-model",
            embedding_dims=512
        )
        
        with patch('mem0.embeddings.apple_intelligence.get_foundation_models_interface') as mock_interface:
            mock_foundation_models = Mock()
            mock_foundation_models.is_available = True
            mock_interface.return_value = mock_foundation_models
            
            embedder = AppleIntelligenceEmbedder(config)
            
            assert embedder.config.model == "test-model"
            assert embedder.config.embedding_dims == 512
            assert embedder.neural_engine_optimization is True  # Default value
    
    def test_init_apple_intelligence_unavailable(self):
        """Test initialization when FoundationModels is unavailable"""
        with patch('mem0.embeddings.apple_intelligence.get_foundation_models_interface') as mock_interface:
            mock_foundation_models = Mock()
            mock_foundation_models.is_available = False
            mock_foundation_models.error_message = "macOS version too old"
            mock_interface.return_value = mock_foundation_models
            
            with pytest.raises(AppleIntelligenceUnavailableError):
                AppleIntelligenceEmbedder()
    
    def test_embed_success(self):
        """Test successful embedding generation"""
        with patch('mem0.embeddings.apple_intelligence.get_foundation_models_interface') as mock_interface:
            mock_foundation_models = Mock()
            mock_foundation_models.is_available = True
            mock_foundation_models.generate_embeddings.return_value = [0.1] * 1536
            mock_interface.return_value = mock_foundation_models
            
            embedder = AppleIntelligenceEmbedder()
            result = embedder.embed("test text")
            
            assert len(result) == 1536
            assert all(isinstance(x, float) for x in result)
            mock_foundation_models.generate_embeddings.assert_called_once()
    
    def test_embed_with_memory_action(self):
        """Test embedding generation with memory action"""
        with patch('mem0.embeddings.apple_intelligence.get_foundation_models_interface') as mock_interface:
            mock_foundation_models = Mock()
            mock_foundation_models.is_available = True
            mock_foundation_models.generate_embeddings.return_value = [0.15] * 1536
            mock_interface.return_value = mock_foundation_models
            
            embedder = AppleIntelligenceEmbedder()
            result = embedder.embed("test text", memory_action="search")
            
            assert len(result) == 1536
            # Verify the Foundation Models interface was called with the memory action
            call_args = mock_foundation_models.generate_embeddings.call_args
            assert call_args[1]['memory_action'] == "search"
    
    def test_embed_empty_text(self):
        """Test embedding generation with empty text"""
        with patch('mem0.embeddings.apple_intelligence.get_foundation_models_interface') as mock_interface:
            mock_foundation_models = Mock()
            mock_foundation_models.is_available = True
            mock_interface.return_value = mock_foundation_models
            
            embedder = AppleIntelligenceEmbedder()
            result = embedder.embed("")
            
            assert len(result) == 1536
            assert all(x == 0.0 for x in result)
            # Should not call Foundation Models for empty text
            mock_foundation_models.generate_embeddings.assert_not_called()
    
    def test_embed_apple_intelligence_unavailable(self):
        """Test embedding generation when FoundationModels becomes unavailable"""
        with patch('mem0.embeddings.apple_intelligence.get_foundation_models_interface') as mock_interface:
            mock_foundation_models = Mock()
            mock_foundation_models.is_available = False
            mock_interface.return_value = mock_foundation_models
            
            embedder = AppleIntelligenceEmbedder()
            embedder._foundation_models = mock_foundation_models
            
            with pytest.raises(AppleIntelligenceUnavailableError):
                embedder.embed("test text")
    
    def test_embed_dimension_mismatch(self):
        """Test embedding generation with dimension mismatch"""
        with patch('mem0.embeddings.apple_intelligence.get_foundation_models_interface') as mock_interface:
            mock_foundation_models = Mock()
            mock_foundation_models.is_available = True
            # Return wrong number of dimensions
            mock_foundation_models.generate_embeddings.return_value = [0.1] * 1000
            mock_interface.return_value = mock_foundation_models
            
            embedder = AppleIntelligenceEmbedder()
            result = embedder.embed("test text")
            
            # Should be padded to correct dimensions
            assert len(result) == 1536
            assert result[:1000] == [0.1] * 1000
            assert result[1000:] == [0.0] * 536
    
    def test_get_embedding_dimensions(self):
        """Test getting embedding dimensions"""
        with patch('mem0.embeddings.apple_intelligence.get_foundation_models_interface') as mock_interface:
            mock_foundation_models = Mock()
            mock_foundation_models.is_available = True
            mock_interface.return_value = mock_foundation_models
            
            embedder = AppleIntelligenceEmbedder()
            assert embedder.get_embedding_dimensions() == 1536
    
    def test_is_available(self):
        """Test availability check"""
        with patch('mem0.embeddings.apple_intelligence.get_foundation_models_interface') as mock_interface:
            mock_foundation_models = Mock()
            mock_foundation_models.is_available = True
            mock_interface.return_value = mock_foundation_models
            
            embedder = AppleIntelligenceEmbedder()
            assert embedder.is_available() is True
    
    def test_get_status(self):
        """Test status information"""
        with patch('mem0.embeddings.apple_intelligence.get_foundation_models_interface') as mock_interface:
            mock_foundation_models = Mock()
            mock_foundation_models.is_available = True
            mock_foundation_models.get_system_info.return_value = {
                'available': True,
                'macos_version': (15, 1)
            }
            mock_interface.return_value = mock_foundation_models
            
            embedder = AppleIntelligenceEmbedder()
            status = embedder.get_status()
            
            assert status['provider'] == 'apple_intelligence'
            assert status['model'] == 'apple-intelligence-embeddings'
            assert status['embedding_dims'] == 1536
            assert status['available'] is True
            assert 'foundation_models_status' in status
    
    def test_repr(self):
        """Test string representation"""
        with patch('mem0.embeddings.apple_intelligence.get_foundation_models_interface') as mock_interface:
            mock_foundation_models = Mock()
            mock_foundation_models.is_available = True
            mock_interface.return_value = mock_foundation_models
            
            embedder = AppleIntelligenceEmbedder()
            repr_str = repr(embedder)
            
            assert "AppleIntelligenceEmbedder" in repr_str
            assert "apple-intelligence-embeddings" in repr_str
            assert "1536" in repr_str


