#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Test script for Mem0 integration.
"""

import os
from mem0 import Memory

def main():
    # Initialize Mem0 client with API key
    api_key = "m0-T4igXztudPWn8RgRATwUkxzpNKFBNIzuZUnAUUbW"
    agent_id = "nba_betting_agent"  # This should match your agent ID in config
    
    # Initialize the Memory client
    memory = Memory(
        api_key=api_key,
        agent_id=agent_id
    )
    
    # Test adding a memory
    memory_item = {
        "content": "Test memory from official Mem0 client",
        "metadata": {
            "type": "test",
            "timestamp": "2023-01-01T12:00:00Z"
        }
    }
    
    result = memory.add(memory_item)
    print(f"Added memory item: {result}")
    
    # Test searching for memory items
    search_params = {
        "query": "test",
        "metadata_filter": {
            "type": "test"
        },
        "limit": 5
    }
    
    results = memory.search(search_params)
    print(f"Found {len(results)} memory items")
    
    # Print the results
    for item in results:
        print(f"Memory ID: {item.get('id')}")
        print(f"Content: {item.get('content')}")
        print(f"Metadata: {item.get('metadata')}")
        print("---")

if __name__ == "__main__":
    main() 