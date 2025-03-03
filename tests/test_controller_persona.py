#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import logging
from pprint import pprint
from dotenv import load_dotenv

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import configuration and modules
from config.settings import get_config
from agent.controller import AgentController

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

def main():
    """Test the AgentController with Billy's persona"""
    print("Testing AgentController with Billy's Persona")
    
    # Load environment variables
    load_dotenv()
    
    # Get configuration
    config = get_config()
    
    # Initialize controller
    controller = AgentController(config)
    
    # Test formatting messages with Billy's persona
    messages = [
        "Agent initialization complete",
        "Found 3 betting opportunities",
        "Wallet balance is $1500.75",
        "Error connecting to API"
    ]
    
    print("\nTesting message formatting with Billy's persona:")
    for message in messages:
        formatted = controller.format_response(message)
        print(f"  Original: {message}")
        print(f"  Billy's style: {formatted}")
        print()
    
    # Test Billy's daily summary
    print("\nTesting Billy's daily summary:")
    daily_summary = controller.comm_manager.format_daily_summary()
    print(f"  {daily_summary}")
    
    # Test error message formatting
    print("\nTesting error message formatting:")
    error_message = controller.comm_manager.format_error_message("Connection failed")
    print(f"  {error_message}")
    
    print("\nTest completed")

if __name__ == "__main__":
    main() 