#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Minimal test script for Mem0 initialization using MemoryClient.
"""

import logging
from mem0 import MemoryClient

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    """Test basic Mem0 initialization with MemoryClient."""
    
    # Set API key
    api_key = "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"
    
    try:
        logger.info("Initializing Mem0 client...")
        
        # Print the version of mem0ai
        import mem0
        logger.info(f"Using mem0ai version: {mem0.__version__}")
        
        # Initialize using the MemoryClient class
        client = MemoryClient(api_key=api_key)
        logger.info("Mem0 client initialized successfully")
        
        # Test adding a memory
        messages = [
            {"role": "user", "content": "This is a test message"},
            {"role": "assistant", "content": "This is a test response"}
        ]
        result = client.add(messages, user_id="test_user")
        
        logger.info(f"Added memory: {result}")
        
        return True
    except Exception as e:
        logger.error(f"Error initializing Mem0 client: {str(e)}")
        return False

if __name__ == "__main__":
    main() 