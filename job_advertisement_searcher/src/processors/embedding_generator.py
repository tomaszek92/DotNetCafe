import ollama
from typing import Optional, List
import logging

logger = logging.getLogger(__name__)

class EmbeddingGenerator:
    """Handles text embedding generation using Ollama."""
    def __init__(self, model_name: str = 'mxbai-embed-large'):
        self.model_name = model_name

    def get_embedding(self, text: str) -> Optional[List[float]]:
        """Generate embedding for the given text."""
        try:
            response = ollama.embeddings(
                model=self.model_name,
                prompt=text
            )
            return response['embedding']
        except Exception as e:
            logger.error(f"Error generating embedding: {e}")
            return None 