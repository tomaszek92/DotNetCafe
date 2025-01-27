import logging
from processors.job_processor import JobAdvertisementProcessor

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    try:
        processor = JobAdvertisementProcessor()
        csv_path = 'data/job_advertisements.csv'
        processed_df = processor.process_advertisements(csv_path)
        logger.info(f"Successfully processed {len(processed_df)} advertisements")
    except Exception as e:
        logger.error(f"Application failed: {e}")
        raise

if __name__ == "__main__":
    main() 