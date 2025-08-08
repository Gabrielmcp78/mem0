"""
Apple Intelligence Embedding Provider

This module provides an embedding provider that uses Apple Intelligence Foundation Models
for generating embeddings locally on-device using the Neural Engine.
"""

import logging
from typing import List, Literal, Optional

from mem0.configs.embeddings.base import BaseEmbedderConfig
from mem0.embeddings.base import EmbeddingBase
from mem0.utils.apple_intelligence import (
    get_foundation_models_interface,
    AppleIntelligenceUnavailableError,
    AppleIntelligenceError
)

logger = logging.getLogger(__name__)


class AppleIntelligenceEmbedder(EmbeddingBase):
    """
    Apple Intelligence embedding provider using Foundation Models framework
    
    This embedder leverages Apple's on-device AI capabilities through the Foundation Models
    framework, ensuring all processing occurs locally on the Neural Engine without external API calls.
    
    Requirements covered:
    - 2.1: Use macOS Foundation Models framework for embedding generation
    - 2.2: Call Apple Intelligence embedding APIs
    - 2.3: Use Apple Intelligence embeddings for similarity matching
    - 2.4: Fail gracefully when Apple Intelligence embeddings are unavailable
    - 2.5: All processing occurs on-device with no external API calls
    """
    
    def __init__(self, config: Optional[BaseEmbedderConfig] = None):
        """
        Initialize the Apple Intelligence embedder
        
        Args:
            config: Embedding configuration options
        """
        super().__init__(config)
        
        # Set default configuration values for Apple Intelligence
        self.config.model = self.config.model or "apple-intelligence-embeddings"
        self.config.embedding_dims = self.config.embedding_dims or 1536
        
        # Apple Intelligence specific settings (not in base config)
        self.neural_engine_optimization = True
        self.privacy_mode = "strict"
        self.batch_size = 1
        
        # Initialize Foundation Models interface
        self._foundation_models = None
        self._initialize_foundation_models()
        
        logger.info(f"Apple Intelligence embedder initialized with model: {self.config.model}, "
                   f"dimensions: {self.config.embedding_dims}, "
                   f"neural_engine_optimization: {self.neural_engine_optimization}")
    
    def _initialize_foundation_models(self) -> None:
        """
        Initialize connection to macOS Foundation Models framework
        
        Requirements covered:
        - 2.1: Use macOS Foundation Models framework for embedding generation
        - 2.4: Fail gracefully when Apple Intelligence embeddings are unavailable
        """
        try:
            self._foundation_models = get_foundation_models_interface()
            
            if not self._foundation_models.is_available:
                error_msg = (f"Apple Intelligence Foundation Models are not available: "
                           f"{self._foundation_models.error_message}")
                logger.error(error_msg)
                raise AppleIntelligenceUnavailableError(error_msg)
            
            logger.info("Successfully connected to Apple Intelligence Foundation Models")
            
        except AppleIntelligenceUnavailableError:
            # Re-raise availability errors
            raise
        except Exception as e:
            error_msg = f"Failed to initialize Apple Intelligence Foundation Models: {str(e)}"
            logger.error(error_msg, exc_info=True)
            raise AppleIntelligenceError(error_msg)
    
    def embed(self, text: str, memory_action: Optional[Literal["add", "search", "update"]] = None) -> List[float]:
        """
        Generate embeddings using Apple Intelligence Foundation Models
        
        Args:
            text: The text to embed
            memory_action: The type of embedding to use ("add", "search", or "update")
        
        Returns:
            List of embedding values
            
        Requirements covered:
        - 2.1: Use macOS Foundation Models framework for embedding generation
        - 2.2: Call Apple Intelligence embedding APIs
        - 2.3: Use Apple Intelligence embeddings for similarity matching
        - 2.5: All processing occurs on-device with no external API calls
        """
        if not text or not text.strip():
            logger.warning("Empty text provided for embedding generation")
            return [0.0] * self.config.embedding_dims
        
        try:
            # Ensure Foundation Models are available
            if not self._foundation_models or not self._foundation_models.is_available:
                raise AppleIntelligenceUnavailableError("Apple Intelligence Foundation Models are not available")
            
            # Preprocess text for optimal Neural Engine processing
            processed_text = self._preprocess_text_for_neural_engine(text)
            
            # Determine embedding type based on memory action
            embedding_type = self._get_embedding_type_for_action(memory_action)
            
            # Log the embedding operation for transparency
            logger.debug(f"Generating embeddings for text (length: {len(processed_text)}) "
                        f"using Apple Intelligence with action: {memory_action}, type: {embedding_type}")
            
            # Generate embeddings using Foundation Models with Neural Engine optimization
            embeddings = self._foundation_models.generate_embeddings(
                text=processed_text,
                dimensions=self.config.embedding_dims,
                memory_action=memory_action,
                embedding_type=embedding_type,
                neural_engine_optimization=self.neural_engine_optimization,
                privacy_mode=self.privacy_mode,
                batch_size=self.batch_size
            )
            
            # Validate and normalize embedding dimensions
            embeddings = self._validate_and_normalize_embeddings(embeddings)
            
            logger.debug(f"Successfully generated {len(embeddings)}-dimensional embeddings using Apple Intelligence")
            return embeddings
            
        except AppleIntelligenceUnavailableError:
            # Re-raise availability errors with context
            error_msg = f"Cannot generate embeddings: Apple Intelligence is unavailable"
            logger.error(error_msg)
            raise AppleIntelligenceUnavailableError(error_msg)
            
        except Exception as e:
            error_msg = f"Error generating embeddings with Apple Intelligence: {str(e)}"
            logger.error(error_msg, exc_info=True)
            raise AppleIntelligenceError(error_msg)
    
    def _preprocess_text_for_neural_engine(self, text: str) -> str:
        """
        Preprocess text for optimal Neural Engine processing
        
        Args:
            text: Input text to preprocess
            
        Returns:
            Preprocessed text optimized for Neural Engine
            
        Requirements covered:
        - 4.2: Utilize Apple's Neural Engine for optimal performance
        """
        # Clean up text for better Neural Engine processing
        processed_text = text.replace("\n", " ").strip()
        
        # Limit text length for optimal Neural Engine performance
        # Apple Intelligence works best with reasonably sized text chunks
        max_length = 8192  # Reasonable limit for embedding generation
        if len(processed_text) > max_length:
            logger.debug(f"Truncating text from {len(processed_text)} to {max_length} characters for Neural Engine optimization")
            processed_text = processed_text[:max_length]
        
        return processed_text
    
    def _get_embedding_type_for_action(self, memory_action: Optional[str]) -> Optional[str]:
        """
        Get the appropriate embedding type for the given memory action
        
        Args:
            memory_action: The memory action ("add", "search", "update")
            
        Returns:
            Embedding type to use for the action
        """
        if memory_action == "add" and hasattr(self.config, 'memory_add_embedding_type'):
            return self.config.memory_add_embedding_type
        elif memory_action == "search" and hasattr(self.config, 'memory_search_embedding_type'):
            return self.config.memory_search_embedding_type
        elif memory_action == "update" and hasattr(self.config, 'memory_update_embedding_type'):
            return self.config.memory_update_embedding_type
        
        return None
    
    def _validate_and_normalize_embeddings(self, embeddings: List[float]) -> List[float]:
        """
        Validate and normalize embedding dimensions
        
        Args:
            embeddings: Raw embeddings from Foundation Models
            
        Returns:
            Validated and normalized embeddings
        """
        if not embeddings:
            logger.warning("Empty embeddings received from Foundation Models")
            return [0.0] * self.config.embedding_dims
        
        # Validate embedding dimensions
        if len(embeddings) != self.config.embedding_dims:
            logger.warning(f"Expected {self.config.embedding_dims} dimensions, "
                         f"got {len(embeddings)}. Adjusting...")
            
            if len(embeddings) > self.config.embedding_dims:
                # Truncate if too many dimensions
                embeddings = embeddings[:self.config.embedding_dims]
            else:
                # Pad with zeros if too few dimensions
                embeddings.extend([0.0] * (self.config.embedding_dims - len(embeddings)))
        
        # Ensure all values are valid floats
        try:
            normalized_embeddings = [float(val) for val in embeddings]
        except (ValueError, TypeError) as e:
            logger.error(f"Invalid embedding values received: {e}")
            return [0.0] * self.config.embedding_dims
        
        return normalized_embeddings
    
    def get_embedding_dimensions(self) -> int:
        """
        Get the number of dimensions in the embeddings
        
        Returns:
            Number of embedding dimensions
        """
        return self.config.embedding_dims
    
    def is_available(self) -> bool:
        """
        Check if Apple Intelligence embeddings are available
        
        Returns:
            True if Apple Intelligence is available, False otherwise
            
        Requirements covered:
        - 2.4: Fail gracefully when Apple Intelligence embeddings are unavailable
        """
        try:
            return (self._foundation_models is not None and 
                   self._foundation_models.is_available)
        except Exception:
            return False
    
    def get_status(self) -> dict:
        """
        Get the status of the Apple Intelligence embedder
        
        Returns:
            Dictionary with status information
            
        Requirements covered:
        - 2.4: Fail gracefully when Apple Intelligence embeddings are unavailable
        """
        try:
            if self._foundation_models:
                system_info = self._foundation_models.get_system_info()
                return {
                    'provider': 'apple_intelligence',
                    'model': self.config.model,
                    'embedding_dims': self.config.embedding_dims,
                    'available': self.is_available(),
                    'foundation_models_status': system_info
                }
            else:
                return {
                    'provider': 'apple_intelligence',
                    'model': self.config.model,
                    'embedding_dims': self.config.embedding_dims,
                    'available': False,
                    'error': 'Foundation Models interface not initialized'
                }
        except Exception as e:
            return {
                'provider': 'apple_intelligence',
                'model': self.config.model,
                'embedding_dims': self.config.embedding_dims,
                'available': False,
                'error': str(e)
            }
    
    def __repr__(self) -> str:
        """String representation of the embedder"""
        return (f"AppleIntelligenceEmbedder(model={self.config.model}, "
                f"dims={self.config.embedding_dims}, "
                f"available={self.is_available()})")