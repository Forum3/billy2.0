#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Test script for Mem0 integration.

This script tests both the custom Mem0Client and the official Mem0OfficialClient
to verify that they work correctly with your API key.
"""

import sys
import os
import logging
from datetime import datetime

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))

# Import configuration
from config.settings import get_config

# Import memory clients
from agent.memory.mem0_client import Mem0Client
from agent.memory.mem0_official import Mem0OfficialClient

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_custom_client():
    """Test the custom Mem0Client implementation."""
    logger.info("Testing custom Mem0Client...")
    
    # Get configuration
    config = get_config()
    
    # Initialize memory client
    try:
        memory = Mem0Client(
            api_key=config['mem0']['api_key'],
            agent_id=config['mem0']['agent_id'],
            base_url=config['mem0']['base_url']
        )
        
        logger.info("Custom Mem0Client initialized successfully")
        
        # Test adding a memory item
        memory_item = {
            "content": f"Test memory from custom client at {datetime.now().isoformat()}",
            "metadata": {
                "type": "test",
                "client": "custom"
            }
        }
        
        result = memory.add(memory_item)
        logger.info(f"Added memory item with custom client: {result}")
        
        return True
    except Exception as e:
        logger.error(f"Error testing custom Mem0Client: {str(e)}")
        return False

def test_official_client():
    """Test the Mem0OfficialClient implementation with Claude 3.7 Sonnet."""
    logger.info("Testing Mem0OfficialClient with Claude 3.7 Sonnet...")
    
    # Get configuration
    config = get_config()
    
    # Initialize memory client
    try:
        memory = Mem0OfficialClient(
            api_key=config['mem0']['api_key'],
            agent_id=config['mem0']['agent_id'],
            base_url=config['mem0']['base_url']
        )
        
        logger.info("Mem0OfficialClient initialized successfully with Claude 3.7 Sonnet")
        
        # Test adding a memory item
        memory_item = {
            "content": f"Test memory from official client using Claude 3.7 Sonnet at {datetime.now().isoformat()}",
            "metadata": {
                "type": "test",
                "client": "official",
                "model": "claude-3-7-sonnet-20250219"
            }
        }
        
        result = memory.add(memory_item)
        logger.info(f"Added memory item with official client: {result}")
        
        return True
    except Exception as e:
        logger.error(f"Error testing Mem0OfficialClient: {str(e)}")
        return False

def main():
    """Run the tests."""
    logger.info("Starting Mem0 integration tests...")
    
    # Test custom client
    custom_result = test_custom_client()
    
    # Test official client
    official_result = test_official_client()
    
    # Print summary
    logger.info("Mem0 integration test results:")
    logger.info(f"Custom client: {'SUCCESS' if custom_result else 'FAILURE'}")
    logger.info(f"Official client: {'SUCCESS' if official_result else 'FAILURE'}")
    
    if custom_result and official_result:
        logger.info("All tests passed!")
    else:
        logger.warning("Some tests failed. Check the logs for details.")

if __name__ == "__main__":
    main() 