"""
FoundationModels LLM Configuration

This module provides configuration classes for FoundationModels LLM provider.
"""

from typing import Optional
from mem0.configs.llms.base import BaseLlmConfig


class AppleIntelligenceLlmConfig(BaseLlmConfig):
    """
    Configuration class for FoundationModels LLM provider
    
    This class extends BaseLlmConfig with FoundationModels specific options
    for Foundation Models integration.
    """
    
    def __init__(
        self,
        model: str = "apple-intelligence-foundation",
        temperature: float = 0.3,
        max_tokens: int = 500,
        top_p: float = 0.9,
        top_k: int = 50,
        enable_neural_engine: bool = True,
        privacy_mode: str = "strict",
        fallback_provider: Optional[str] = None,
        foundation_model_version: Optional[str] = None,
        **kwargs
    ):
        """
        Initialize FoundationModels LLM configuration
        
        Args:
            model: FoundationModels model identifier
            temperature: Controls randomness (0.0-1.0), lower values are more deterministic
            max_tokens: Maximum tokens to generate
            top_p: Nucleus sampling parameter (0.0-1.0)
            top_k: Top-k sampling parameter
            enable_neural_engine: Whether to use Neural Engine optimization
            privacy_mode: Privacy level (strict, moderate, open)
            fallback_provider: Fallback provider if FoundationModels unavailable
            foundation_model_version: Specific Foundation Models version to use
            **kwargs: Additional configuration options passed to BaseLlmConfig
        """
        super().__init__(
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
            top_p=top_p,
            top_k=top_k,
            **kwargs
        )
        
        # FoundationModels specific configuration
        self.enable_neural_engine = enable_neural_engine
        self.privacy_mode = privacy_mode
        self.fallback_provider = fallback_provider
        self.foundation_model_version = foundation_model_version
        
        # Validate privacy mode
        if privacy_mode not in ["strict", "moderate", "open"]:
            raise ValueError("privacy_mode must be one of: strict, moderate, open")
        
        # Validate temperature range
        if not 0.0 <= temperature <= 1.0:
            raise ValueError("temperature must be between 0.0 and 1.0")
        
        # Validate top_p range
        if not 0.0 <= top_p <= 1.0:
            raise ValueError("top_p must be between 0.0 and 1.0")
        
        # Validate max_tokens
        if max_tokens <= 0:
            raise ValueError("max_tokens must be positive")