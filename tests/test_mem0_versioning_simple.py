#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Simple test script for Mem0 memory versioning.
"""

import sys
import os
import logging
import time
from datetime import datetime

# Set up logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))

# Import configuration
from config.settings import get_config

# Import memory client
from agent.memory.mem0_client import Mem0Client

def main():
    """Test versioning functionality with the custom Mem0Client."""
    logger.info("Starting simple versioning test...")
    
    # Get configuration
    config = get_config()
    
    # Initialize memory client
    client = Mem0Client(
        api_key=config['mem0']['api_key'],
        agent_id=config['mem0']['agent_id'],
        base_url=config['mem0']['base_url'],
        cache_ttl=config['mem0'].get('cache_ttl', 300)
    )
    
    logger.info("Mem0 client initialized")
    memory_id = None
    
    try:
        # Step 1: Create a new memory item
        logger.info("Step 1: Creating a new memory item...")
        memory_item = {
            "content": f"Initial content at {datetime.now().isoformat()}",
            "metadata": {
                "type": "test_versioning_simple",
                "initial": True,
                "version": 1  # Set initial version explicitly
            }
        }
        
        result = client.add(memory_item)
        logger.info(f"Add result: {result}")
        
        memory_id = result.get("id")
        if not memory_id:
            logger.warning("No memory ID returned, using a test ID")
            memory_id = "test_memory_id"  # Use a test ID for demonstration
        
        logger.info(f"Created memory item with ID: {memory_id}")
        
        # Wait for the API to process the request
        time.sleep(2)
        
        # Step 2: Update the memory item
        logger.info("Step 2: Updating the memory item...")
        updates = {
            "content": f"Updated content at {datetime.now().isoformat()}",
            "metadata": {
                "updated": True,
                "version": 2  # Set updated version explicitly
            }
        }
        
        updated = client.update(memory_id, updates)
        logger.info(f"Update result: {updated}")
        
        # Wait for the API to process the request
        time.sleep(2)
        
        # Step 3: Demonstrate versioning functionality
        logger.info("Step 3: Demonstrating versioning functionality...")
        
        # Get the current memory item
        current = client.get(memory_id)
        logger.info(f"Current memory item: {current}")
        
        # List available versions
        versions = client.list_versions(memory_id)
        logger.info(f"Available versions: {versions}")
        
        # Get a specific version
        if versions and len(versions) > 1:
            previous_version = versions[1]  # Get the previous version
            previous = client.get_version(memory_id, previous_version)
            logger.info(f"Previous version ({previous_version}): {previous}")
        
        logger.info("Versioning test completed successfully")
        
    except Exception as e:
        logger.error(f"Error testing versioning: {str(e)}")
    
    finally:
        # Clean up
        if memory_id and memory_id != "test_memory_id":
            try:
                client.delete(memory_id)
                logger.info(f"Deleted memory item with ID: {memory_id}")
            except Exception as cleanup_error:
                logger.error(f"Error cleaning up: {str(cleanup_error)}")

if __name__ == "__main__":
    main() 