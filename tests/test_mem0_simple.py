#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Simple test script for Mem0 initialization.
"""

import os
import logging
from mem0 import Memory
from mem0.configs.base import MemoryConfig

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    """Test basic Mem0 initialization."""
    
    # Set API keys
    anthropic_api_key = "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"
    openai_api_key = "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"
    
    # Set agent ID
    agent_id = "test_agent"
    
    try:
        logger.info("Initializing Mem0 client...")
        
        # Print the version of mem0ai
        import mem0
        logger.info(f"Using mem0ai version: {mem0.__version__}")
        
        # Create a config for the Memory class
        config = MemoryConfig(
            llm={
                "provider": "anthropic",
                "config": {
                    "api_key": anthropic_api_key,
                    "model": "claude-3-7-sonnet-20250219"
                }
            },
            embedder={
                "provider": "openai",
                "config": {
                    "api_key": openai_api_key,
                    "model": "text-embedding-ada-002"
                }
            },
            vector_store={
                "provider": "qdrant",
                "config": {
                    "collection_name": agent_id
                }
            }
        )
        
        # Initialize using the config
        client = Memory(config=config)
        logger.info("Mem0 client initialized successfully")
        
        # Test adding a memory
        result = client.add(
            messages="This is a test memory",
            agent_id=agent_id,
            metadata={"type": "test"}
        )
        
        logger.info(f"Added memory: {result}")
        
        return True
    except Exception as e:
        logger.error(f"Error initializing Mem0 client: {str(e)}")
        return False

if __name__ == "__main__":
    main() 