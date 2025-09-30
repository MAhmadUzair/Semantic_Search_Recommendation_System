#!/usr/bin/env python3
"""
Test script to verify logging is working correctly.
This script tests the logging functionality without requiring external services.
"""

import sys
import os
import logging

# Add the backend directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_logging():
    """Test various logging levels."""
    logger.info("Testing logging functionality")
    logger.debug("This is a debug message")
    logger.warning("This is a warning message")
    logger.error("This is an error message")
    
    # Test logging from different modules
    try:
        from app.services.vectordb import logger as vectordb_logger
        vectordb_logger.info("VectorDB logger test")
    except Exception as e:
        logger.error(f"Failed to import vectordb logger: {e}")
    
    try:
        from app.services.embeddings import logger as embeddings_logger
        embeddings_logger.info("Embeddings logger test")
    except Exception as e:
        logger.error(f"Failed to import embeddings logger: {e}")
    
    try:
        from app.services.search_engine import logger as search_logger
        search_logger.info("Search engine logger test")
    except Exception as e:
        logger.error(f"Failed to import search engine logger: {e}")
    
    logger.info("Logging test completed")

if __name__ == "__main__":
    test_logging()
