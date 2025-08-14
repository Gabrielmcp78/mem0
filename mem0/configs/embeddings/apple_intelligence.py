"""
FoundationModels Embedding Configuration

This module provides configuration classes for FoundationModels embedding provider.
"""

from typing import Optional
from mem0.configs.embeddings.base import BaseEmbedderConfig


class AppleIntelligenceEmbedderConfig(BaseEmbedderConfig):
    """
    Configuration class for FoundationModels embedding provider
    
    This class extends BaseEmbedderConfig with FoundationModels specific options
    for Foundation Models integration.
    """
    
    def __init__(
        self,
        model: str = "apple-intelligence-embeddings",
        embedding_dims: int = 1536,
        enable_neural_engine: bool = True,
        privacy_mode: str = "strict",
        batch_size: int = 32,
        normalize_embeddings: bool = True,
        fallback_provider: Optional[str] = None,
        foundation_model_version: Optional[str] = None,
        **kwargs
    ):
        """
        Initialize FoundationModels embedding configuration
        
        Args:
            model: FoundationModels embedding model identifier
            embedding_dims: Dimension of the embedding vectors (default: 1536)
            enable_neural_engine: Whether to use Neural Engine optimization
            privacy_mode: Privacy level (strict, moderate, open)
            batch_size: Number of texts to process in a single batch
            normalize_embeddings: Whether to normalize embedding vectors
            fallback_provider: Fallback provider if FoundationModels unavailable
            foundation_model_version: Specific Foundation Models version to use
            **kwargs: Additional configuration options passed to BaseEmbedderConfig
        """
        super().__init__(
            model=model,
            embedding_dims=embedding_dims,
            **kwargs
        )
        
        # FoundationModels specific configuration
        self.enable_neural_engine = enable_neural_engine
        self.privacy_mode = privacy_mode
        self.batch_size = batch_size
        self.normalize_embeddings = normalize_embeddings
        self.fallback_provider = fallback_provider
        self.foundation_model_version = foundation_model_version
        
        # Validate privacy mode
        if privacy_mode not in ["strict", "moderate", "open"]:
            raise ValueError("privacy_mode must be one of: strict, moderate, open")
        
        # Validate embedding dimensions
        if embedding_dims <= 0:
            raise ValueError("embedding_dims must be positive")
        
        # Validate batch size
        if batch_size <= 0:
            raise ValueError("batch_size must be positive")
        
        # Validate batch size doesn't exceed reasonable limits
        if batch_size > 1000:
            raise ValueError("batch_size should not exceed 1000 for optimal performance")