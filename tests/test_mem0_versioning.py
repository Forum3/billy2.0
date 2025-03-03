#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Test script for Mem0 memory versioning.

This script tests the versioning functionality for both
the custom Mem0Client and the official Mem0OfficialClient.
"""

import sys
import os
import logging
import time
from datetime import datetime
from typing import Dict, Any, Optional

# Set up logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))

# Import configuration
from config.settings import get_config

# Import memory clients
from agent.memory.mem0_client import Mem0Client
from agent.memory.mem0_official import Mem0OfficialClient

def test_versioning(client, client_name: str) -> bool:
    """
    Test versioning functionality for a memory client.
    
    Args:
        client: Memory client instance
        client_name: Name of the client for logging
        
    Returns:
        Boolean indicating success or failure
    """
    success = True
    memory_id = None
    
    try:
        # Step 1: Create a new memory item
        logger.info(f"Step 1: Creating a new memory item with {client_name}...")
        memory_item = {
            "content": f"Initial content from {client_name} at {datetime.now().isoformat()}",
            "metadata": {
                "type": "test_versioning",
                "client": client_name
            }
        }
        
        result = client.add(memory_item)
        memory_id = result.get("id")
        
        if not memory_id:
            logger.error(f"Failed to create memory item with {client_name}")
            return False
        
        logger.info(f"Created memory item with ID: {memory_id}")
        
        # Wait for the API to process the request
        time.sleep(1)
        
        # Step 2: Get the initial version
        logger.info(f"Step 2: Getting the initial version...")
        initial = client.get(memory_id)
        
        if not initial:
            logger.error(f"Failed to get initial memory item with {client_name}")
            return False
        
        initial_version = initial.get('metadata', {}).get('version', 0)
        logger.info(f"Initial version: {initial_version}")
        
        # Step 3: Update the memory item
        logger.info(f"Step 3: Updating the memory item...")
        updates = {
            "content": f"Updated content from {client_name} at {datetime.now().isoformat()}",
            "metadata": {
                "updated": True
            }
        }
        
        updated = client.update(memory_id, updates)
        
        if not updated:
            logger.error(f"Failed to update memory item with {client_name}")
            return False
        
        updated_version = updated.get('metadata', {}).get('version', 0)
        logger.info(f"Updated version: {updated_version}")
        
        # Verify that the version was incremented
        if updated_version != initial_version + 1:
            logger.error(f"Version was not incremented correctly: {updated_version} != {initial_version + 1}")
            success = False
        
        # Wait for the API to process the request
        time.sleep(1)
        
        # Step 4: List available versions
        logger.info(f"Step 4: Listing available versions...")
        versions = client.list_versions(memory_id)
        
        logger.info(f"Available versions: {versions}")
        
        # Verify that both versions are available
        if len(versions) < 2:
            logger.error(f"Expected at least 2 versions, got {len(versions)}")
            success = False
        
        # Step 5: Get a specific version
        logger.info(f"Step 5: Getting a specific version...")
        previous_version = client.get_version(memory_id, initial_version)
        
        if not previous_version:
            logger.error(f"Failed to get previous version with {client_name}")
            success = False
        else:
            logger.info(f"Previous version content: {previous_version.get('content')}")
            
            # Verify that the content matches the initial content
            if previous_version.get('content') != memory_item.get('content'):
                logger.error(f"Previous version content does not match initial content")
                success = False
        
        # Step 6: Roll back to the initial version
        logger.info(f"Step 6: Rolling back to the initial version...")
        rolled_back = client.rollback(memory_id, initial_version)
        
        if not rolled_back:
            logger.error(f"Failed to roll back to initial version with {client_name}")
            success = False
        else:
            logger.info(f"Rolled back version: {rolled_back.get('metadata', {}).get('version', 0)}")
            
            # Verify that the content matches the initial content
            if rolled_back.get('content') != memory_item.get('content'):
                logger.error(f"Rolled back content does not match initial content")
                success = False
        
        # Step 7: Clean up
        logger.info(f"Step 7: Cleaning up...")
        if memory_id:
            client.delete(memory_id)
            logger.info(f"Deleted memory item with ID: {memory_id}")
        
        return success
        
    except Exception as e:
        logger.error(f"Error testing versioning with {client_name}: {str(e)}")
        
        # Clean up
        if memory_id:
            try:
                client.delete(memory_id)
                logger.info(f"Deleted memory item with ID: {memory_id}")
            except Exception as cleanup_error:
                logger.error(f"Error cleaning up: {str(cleanup_error)}")
        
        return False

def main():
    """Run the tests."""
    logger.info("Starting Mem0 versioning tests...")
    
    # Get configuration
    config = get_config()
    
    # Test custom client
    custom_success = False
    try:
        logger.info("Testing versioning with custom Mem0Client...")
        
        # Initialize memory client
        custom_client = Mem0Client(
            api_key=config['mem0']['api_key'],
            agent_id=config['mem0']['agent_id'],
            base_url=config['mem0']['base_url'],
            cache_ttl=config['mem0'].get('cache_ttl', 300)
        )
        
        custom_success = test_versioning(custom_client, "custom_client")
        
    except Exception as e:
        logger.error(f"Error testing custom Mem0Client: {str(e)}")
    
    # Test official client
    official_success = False
    try:
        logger.info("Testing versioning with Mem0OfficialClient...")
        
        # Initialize memory client
        official_client = Mem0OfficialClient(
            api_key=config['mem0']['api_key'],
            agent_id=config['mem0']['agent_id'],
            base_url=config['mem0']['base_url'],
            cache_ttl=config['mem0'].get('cache_ttl', 300)
        )
        
        official_success = test_versioning(official_client, "official_client")
        
    except Exception as e:
        logger.error(f"Error testing Mem0OfficialClient: {str(e)}")
    
    # Print summary
    logger.info("Mem0 versioning test results:")
    logger.info(f"Custom client: {'SUCCESS' if custom_success else 'FAILURE'}")
    logger.info(f"Official client: {'SUCCESS' if official_success else 'FAILURE'}")
    
    if custom_success and official_success:
        logger.info("All tests passed!")
    else:
        logger.warning("Some tests failed. Check the logs for details.")

if __name__ == "__main__":
    main() 