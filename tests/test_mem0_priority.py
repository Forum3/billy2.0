#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Test script for Mem0 memory prioritization.

This script tests the prioritization functionality for both
the custom Mem0Client and the official Mem0OfficialClient.
"""

import sys
import os
import logging
import time
from datetime import datetime
from typing import Dict, Any, List

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

def test_prioritization(client, client_name: str) -> bool:
    """
    Test prioritization functionality for a memory client.
    
    Args:
        client: Memory client instance
        client_name: Name of the client for logging
        
    Returns:
        Boolean indicating success or failure
    """
    success = True
    memory_ids = []
    
    try:
        # Step 1: Create memory items with different priorities
        logger.info(f"Step 1: Creating memory items with different priorities using {client_name}...")
        
        priorities = [3, 8, 1, 5, 10]
        for i, priority in enumerate(priorities):
            memory_item = {
                "content": f"Test memory {i} with priority {priority} from {client_name} at {datetime.now().isoformat()}",
                "metadata": {
                    "type": "test_priority",
                    "client": client_name,
                    "index": i,
                    "priority": priority
                }
            }
            
            result = client.add(memory_item)
            memory_id = result.get("id")
            
            if memory_id:
                memory_ids.append(memory_id)
                logger.info(f"Created memory item with ID: {memory_id} and priority: {priority}")
            else:
                logger.warning(f"Failed to create memory item with priority {priority}")
        
        # Wait for the API to process the requests
        time.sleep(2)
        
        # Step 2: Search by priority
        logger.info(f"Step 2: Searching by priority using {client_name}...")
        
        # Search for high priority items (priority >= 8)
        high_priority_items = client.search_by_priority(
            query="",
            min_priority=8,
            limit=10
        )
        
        logger.info(f"Found {len(high_priority_items)} high priority items")
        for item in high_priority_items:
            priority = item.get("metadata", {}).get("priority", 0)
            logger.info(f"High priority item: {item.get('id')} with priority {priority}")
            
            # Verify that all items have priority >= 8
            if priority < 8:
                logger.error(f"Item with priority {priority} should not be in high priority results")
                success = False
        
        # Search for medium priority items (3 <= priority <= 7)
        medium_priority_items = client.search_by_priority(
            query="",
            min_priority=3,
            max_priority=7,
            limit=10
        )
        
        logger.info(f"Found {len(medium_priority_items)} medium priority items")
        for item in medium_priority_items:
            priority = item.get("metadata", {}).get("priority", 0)
            logger.info(f"Medium priority item: {item.get('id')} with priority {priority}")
            
            # Verify that all items have 3 <= priority <= 7
            if priority < 3 or priority > 7:
                logger.error(f"Item with priority {priority} should not be in medium priority results")
                success = False
        
        # Step 3: Update priority
        if memory_ids:
            logger.info(f"Step 3: Updating priority using {client_name}...")
            
            # Update the priority of the first memory item
            memory_id = memory_ids[0]
            new_priority = 9
            
            updated = client.update_priority(memory_id, new_priority)
            
            if updated:
                logger.info(f"Updated priority of memory item {memory_id} to {new_priority}")
                
                # Verify that the priority was updated
                updated_priority = updated.get("metadata", {}).get("priority", 0)
                if updated_priority != new_priority:
                    logger.error(f"Priority was not updated correctly: {updated_priority} != {new_priority}")
                    success = False
            else:
                logger.error(f"Failed to update priority of memory item {memory_id}")
                success = False
        
        # Step 4: Search with sorting by priority
        logger.info(f"Step 4: Searching with sorting by priority using {client_name}...")
        
        sorted_items = client.search({
            "query": "",
            "metadata_filter": {"type": "test_priority"},
            "sort_by_priority": True,
            "limit": 10
        })
        
        logger.info(f"Found {len(sorted_items)} items sorted by priority")
        
        # Verify that items are sorted by priority (highest first)
        prev_priority = None
        for item in sorted_items:
            priority = item.get("metadata", {}).get("priority", 0)
            logger.info(f"Sorted item: {item.get('id')} with priority {priority}")
            
            if prev_priority is not None and priority > prev_priority:
                logger.error(f"Items are not sorted correctly: {priority} > {prev_priority}")
                success = False
            
            prev_priority = priority
        
        # Step 5: Clean up
        logger.info(f"Step 5: Cleaning up...")
        for memory_id in memory_ids:
            client.delete(memory_id)
            logger.info(f"Deleted memory item with ID: {memory_id}")
        
        return success
        
    except Exception as e:
        logger.error(f"Error testing prioritization with {client_name}: {str(e)}")
        
        # Clean up
        for memory_id in memory_ids:
            try:
                client.delete(memory_id)
                logger.info(f"Deleted memory item with ID: {memory_id}")
            except Exception as cleanup_error:
                logger.error(f"Error cleaning up: {str(cleanup_error)}")
        
        return False

def main():
    """Run the tests."""
    logger.info("Starting Mem0 prioritization tests...")
    
    # Get configuration
    config = get_config()
    
    # Test custom client
    custom_success = False
    try:
        logger.info("Testing prioritization with custom Mem0Client...")
        
        # Initialize memory client
        custom_client = Mem0Client(
            api_key=config['mem0']['api_key'],
            agent_id=config['mem0']['agent_id'],
            base_url=config['mem0']['base_url'],
            cache_ttl=config['mem0'].get('cache_ttl', 300)
        )
        
        custom_success = test_prioritization(custom_client, "custom_client")
        
    except Exception as e:
        logger.error(f"Error testing custom Mem0Client: {str(e)}")
    
    # Test official client
    official_success = False
    try:
        logger.info("Testing prioritization with Mem0OfficialClient...")
        
        # Initialize memory client
        official_client = Mem0OfficialClient(
            api_key=config['mem0']['api_key'],
            agent_id=config['mem0']['agent_id'],
            base_url=config['mem0']['base_url'],
            cache_ttl=config['mem0'].get('cache_ttl', 300)
        )
        
        official_success = test_prioritization(official_client, "official_client")
        
    except Exception as e:
        logger.error(f"Error testing Mem0OfficialClient: {str(e)}")
    
    # Print summary
    logger.info("Mem0 prioritization test results:")
    logger.info(f"Custom client: {'SUCCESS' if custom_success else 'FAILURE'}")
    logger.info(f"Official client: {'SUCCESS' if official_success else 'FAILURE'}")
    
    if custom_success and official_success:
        logger.info("All tests passed!")
    else:
        logger.warning("Some tests failed. Check the logs for details.")

if __name__ == "__main__":
    main() 