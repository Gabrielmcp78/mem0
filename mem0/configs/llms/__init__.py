"""
Mem0 LLM Configuration Classes

This module contains configuration classes for various LLM providers.
"""

from mem0.configs.llms.base import BaseLlmConfig
from mem0.configs.llms.apple_intelligence import AppleIntelligenceLlmConfig

__all__ = [
    'BaseLlmConfig',
    'AppleIntelligenceLlmConfig'
]