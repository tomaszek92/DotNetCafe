from qdrant_client import QdrantClient
from qdrant_client.http import models
from typing import List
import logging

logger = logging.getLogger(__name__)

class QdrantManager:
    """Manages Qdrant vector database operations."""
    def __init__(self, host: str = "localhost", port: int = 6333):
        self.client = QdrantClient(host, port=port)
        self.collection_name = "job_advertisements"
        self._ensure_collection_exists()

    def _ensure_collection_exists(self) -> None:
        """Create collection if it doesn't exist."""
        try:
            self.client.get_collection(self.collection_name)
        except Exception:
            logger.info(f"Creating collection: {self.collection_name}")
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=models.VectorParams(
                    size=1024,
                    distance=models.Distance.COSINE
                )
            )

    def upsert_batch(self, points: List[models.PointStruct]) -> None:
        """Upload a batch of points to Qdrant."""
        try:
            self.client.upsert(
                collection_name=self.collection_name,
                points=points
            )
        except Exception as e:
            logger.error(f"Error upserting batch to Qdrant: {e}")
            raise 