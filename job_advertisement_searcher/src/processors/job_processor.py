import pandas as pd
from pathlib import Path
import zlib
from typing import Optional, List
import logging
import time
from qdrant_client.http import models
from processors.html_processor import HTMLProcessor
from processors.embedding_generator import EmbeddingGenerator
from database.qdrant_manager import QdrantManager

logger = logging.getLogger(__name__)

class JobAdvertisementProcessor:
    """Main processor for job advertisements."""
    def __init__(self):
        self.html_processor = HTMLProcessor()
        self.embedding_generator = EmbeddingGenerator()
        self.qdrant_manager = QdrantManager()

    def _create_point(self, row: pd.Series, embedding: List[float]) -> models.PointStruct:
        """Create a Qdrant point from a dataframe row and its embedding."""
        return models.PointStruct(
            id=row['Id'],
            vector=embedding,
            payload={
                'title': row['Title'],
                'body': row['Body_Markdown'],
                'original_body': row['Body']
            }
        )

    def _log_progress(self, current: int, total: int, start_time: float, prefix: str = "Progress"):
        """Log progress with percentage and time estimates."""
        elapsed_time = time.time() - start_time
        progress = (current + 1) / total
        eta = elapsed_time / (progress) * (1 - progress) if progress > 0 else 0
        
        logger.info(
            f"{prefix}: {current + 1}/{total} ({progress:.1%}) - "
            f"Elapsed: {elapsed_time:.1f}s - "
            f"ETA: {eta:.1f}s"
        )

    def process_advertisements(self, csv_path: str, num_rows: Optional[int] = None) -> pd.DataFrame:
        """Process job advertisements from CSV file."""
        try:
            start_time = time.time()
            logger.info("Starting job advertisement processing")
            
            # Read and preprocess data
            df = pd.read_csv(csv_path)
            logger.info(f"Loaded {len(df)} advertisements from CSV")
            
            if num_rows is not None:
                df = df.head(num_rows)
                logger.info(f"Limited processing to {num_rows} advertisements")
            
            # Convert HTML to Markdown
            logger.info("Converting HTML to Markdown")
            df['Body_Markdown'] = df['Body'].apply(self.html_processor.to_markdown)
            
            # Process advertisements and create points
            total_rows = len(df)
            points = []
            processed = 0
            skipped = 0
            
            logger.info("Starting embedding generation")
            for idx, row in df.iterrows():
                text_to_embed = f"{row['Title']}\n\n{row['Body_Markdown']}"
                embedding = self.embedding_generator.get_embedding(text_to_embed)
                
                if embedding is None:
                    skipped += 1
                    logger.warning(f"Skipping row {idx} due to embedding failure")
                    continue
                
                points.append(self._create_point(row, embedding))
                processed += 1
                
                if processed % 10 == 0 or processed == total_rows:
                    self._log_progress(processed, total_rows, start_time, "Embedding generation")
            
            logger.info(f"Completed embedding generation. Processed: {processed}, Skipped: {skipped}")
            
            # Upload to Qdrant in batches
            if points:
                batch_size = 100
                total_batches = (len(points) + batch_size - 1) // batch_size
                logger.info(f"Starting upload to Qdrant in {total_batches} batches")
                
                for i in range(0, len(points), batch_size):
                    batch = points[i:i + batch_size]
                    self.qdrant_manager.upsert_batch(batch)
                    batch_num = i // batch_size + 1
                    self._log_progress(batch_num - 1, total_batches, start_time, "Qdrant upload")
            
            # Save processed data
            output_path = Path(csv_path).parent / 'processed_advertisements.csv'
            df.to_csv(output_path, index=False)
            logger.info(f"Saved processed data to {output_path}")
            
            total_time = time.time() - start_time
            logger.info(
                f"Processing completed in {total_time:.1f}s. "
                f"Success rate: {processed}/{total_rows} ({processed/total_rows:.1%})"
            )
            
            return df
            
        except Exception as e:
            logger.error(f"Error processing advertisements: {e}")
            raise 