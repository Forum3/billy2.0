#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Simple test script for Mem0 batch operations with the official client.
"""

import sys
import os
import logging
from datetime import datetime

# Set up logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))

# Import configuration
from config.settings import get_config

# Import memory client
from agent.memory.mem0_official import Mem0OfficialClient

def main():
    """Test batch operations with the official Mem0Client."""
    logger.info("Starting simple batch operations test with official client...")
    
    # Get configuration
    config = get_config()
    
    # Initialize memory client
    client = Mem0OfficialClient(
        api_key=config['mem0']['api_key'],
        agent_id=config['mem0']['agent_id'],
        base_url=config['mem0']['base_url'],
        cache_ttl=config['mem0'].get('cache_ttl', 300)
    )
    
    logger.info("Official Mem0 client initialized")
    
    # Create test memory items
    memory_items = []
    for i in range(3):
        memory_items.append({
            "content": f"Test batch memory {i} with official client at {datetime.now().isoformat()}",
            "metadata": {
                "type": "test_batch_official",
                "index": i
            }
        })
    
    logger.info(f"Created {len(memory_items)} test memory items")
    
    # Add items in batch
    try:
        logger.info("Calling add_batch...")
        results = client.add_batch(memory_items)
        logger.info(f"Added {len(results)} memory items in batch")
        
        for i, result in enumerate(results):
            logger.info(f"Result {i}: {result}")
        
        logger.info("Batch operations test completed successfully")
        
    except Exception as e:
        logger.error(f"Error testing batch operations: {str(e)}")

if __name__ == "__main__":
    main() 