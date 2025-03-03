#!/usr/bin/env python3
"""
Test script for Mem0 memory consolidation functionality.

This script tests the memory consolidation feature in both the custom and official Mem0 clients.
"""

import os
import sys
import time
import logging
import json
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional

# Add the parent directory to the path so we can import the agent modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agent.memory.mem0_client import Mem0Client
from agent.memory.mem0_official import Mem0OfficialClient

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

def test_consolidation(client, client_name: str) -> bool:
    """
    Test memory consolidation functionality.
    
    Args:
        client: Mem0 client instance
        client_name: Name of the client for logging
        
    Returns:
        Boolean indicating success or failure
    """
    logger.info(f"Testing memory consolidation with {client_name}...")
    
    # Step 1: Create test memories with different timestamps
    logger.info(f"Step 1: Creating test memories with different timestamps using {client_name}...")
    
    # Create memories with timestamps spanning the last 60 days
    memory_ids = []
    for days_ago in [60, 50, 40, 30, 20, 10, 5, 1]:
        timestamp = (datetime.now() - timedelta(days=days_ago)).isoformat()
        
        memory_item = {
            "content": f"Test memory from {days_ago} days ago",
            "metadata": {
                "timestamp": timestamp,
                "test_type": "consolidation_test",
                "days_ago": days_ago
            }
        }
        
        result = client.add(memory_item)
        if result and result.get("id"):
            memory_ids.append(result["id"])
            logger.info(f"Created memory item with ID {result['id']} and timestamp {timestamp}")
        else:
            logger.warning(f"Failed to create memory item with timestamp {timestamp}")
    
    if not memory_ids:
        logger.error("Failed to create any test memories")
        return False
    
    # Wait a moment for the memories to be indexed
    time.sleep(2)
    
    # Step 2: Consolidate memories older than 30 days
    logger.info(f"Step 2: Consolidating memories older than 30 days using {client_name}...")
    
    consolidation_result = client.consolidate_memories(
        query="test_type:consolidation_test",
        days=30,
        delete_originals=False
    )
    
    if not consolidation_result or not consolidation_result.get("id"):
        logger.error("Failed to consolidate memories")
        return False
    
    logger.info(f"Successfully consolidated memories with result: {json.dumps(consolidation_result, indent=2)}")
    
    # Step 3: Verify the consolidation
    logger.info(f"Step 3: Verifying consolidation using {client_name}...")
    
    # Get the consolidation memory
    consolidation_memory = client.get(consolidation_result["id"])
    if not consolidation_memory:
        logger.error(f"Failed to retrieve consolidation memory with ID {consolidation_result['id']}")
        return False
    
    # Check the metadata
    metadata = consolidation_memory.get("metadata", {})
    if metadata.get("type") != "consolidation":
        logger.error(f"Consolidation memory has incorrect type: {metadata.get('type')}")
        return False
    
    original_count = metadata.get("original_count", 0)
    logger.info(f"Consolidation memory contains {original_count} original memories")
    
    # Step 4: Test consolidation with deletion
    logger.info(f"Step 4: Testing consolidation with deletion using {client_name}...")
    
    # Create more test memories
    deletion_memory_ids = []
    for days_ago in [45, 35]:
        timestamp = (datetime.now() - timedelta(days=days_ago)).isoformat()
        
        memory_item = {
            "content": f"Test memory for deletion from {days_ago} days ago",
            "metadata": {
                "timestamp": timestamp,
                "test_type": "deletion_test",
                "days_ago": days_ago
            }
        }
        
        result = client.add(memory_item)
        if result and result.get("id"):
            deletion_memory_ids.append(result["id"])
            logger.info(f"Created memory item for deletion with ID {result['id']} and timestamp {timestamp}")
        else:
            logger.warning(f"Failed to create memory item for deletion with timestamp {timestamp}")
    
    if not deletion_memory_ids:
        logger.error("Failed to create any test memories for deletion")
        return False
    
    # Wait a moment for the memories to be indexed
    time.sleep(2)
    
    # Consolidate with deletion
    deletion_consolidation_result = client.consolidate_memories(
        query="test_type:deletion_test",
        days=30,
        delete_originals=True
    )
    
    if not deletion_consolidation_result or not deletion_consolidation_result.get("id"):
        logger.error("Failed to consolidate memories with deletion")
        return False
    
    logger.info(f"Successfully consolidated memories with deletion: {json.dumps(deletion_consolidation_result, indent=2)}")
    
    # Verify deletion
    for memory_id in deletion_memory_ids:
        memory = client.get(memory_id)
        if memory:
            logger.warning(f"Memory with ID {memory_id} was not deleted after consolidation")
        else:
            logger.info(f"Memory with ID {memory_id} was successfully deleted after consolidation")
    
    # Step 5: Clean up
    logger.info(f"Step 5: Cleaning up test memories using {client_name}...")
    
    # Delete all test memories
    all_memory_ids = memory_ids + [consolidation_result["id"], deletion_consolidation_result["id"]]
    for memory_id in all_memory_ids:
        if client.delete(memory_id):
            logger.info(f"Deleted memory with ID {memory_id}")
        else:
            logger.warning(f"Failed to delete memory with ID {memory_id}")
    
    logger.info(f"Memory consolidation test with {client_name} completed successfully")
    return True

def main():
    """Main function to run the tests."""
    logger.info("Starting Mem0 consolidation tests...")
    
    # Get API key from environment variable
    api_key = os.environ.get("MEM0_API_KEY")
    if not api_key:
        logger.error("MEM0_API_KEY environment variable not set")
        sys.exit(1)
    
    # Test with custom client
    custom_client = Mem0Client(api_key=api_key, agent_id="nba_betting_agent")
    custom_result = test_consolidation(custom_client, "custom_client")
    
    # Test with official client
    try:
        official_client = Mem0OfficialClient(api_key=api_key, agent_id="nba_betting_agent")
        official_result = test_consolidation(official_client, "official_client")
    except ImportError:
        logger.warning("Official Mem0 client not available, skipping test")
        official_result = False
    
    # Print results
    logger.info("Mem0 consolidation test results:")
    logger.info(f"Custom client: {'SUCCESS' if custom_result else 'FAILURE'}")
    logger.info(f"Official client: {'SUCCESS' if official_result else 'FAILURE'}")
    
    if custom_result and official_result:
        logger.info("All tests passed!")
    else:
        logger.warning("Some tests failed. Check the logs for details.")

if __name__ == "__main__":
    main() 