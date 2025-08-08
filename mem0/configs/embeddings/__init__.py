"""
Mem0 Embedding Configuration Classes

This module contains configuration classes for various embedding providers.
"""

from mem0.configs.embeddings.base import BaseEmbedderConfig
from mem0.configs.embeddings.apple_intelligence import AppleIntelligenceEmbedderConfig

__all__ = [
    'BaseEmbedderConfig',
    'AppleIntelligenceEmbedderConfig'
]