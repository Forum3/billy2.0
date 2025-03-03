#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Run script for the NBA Betting Agent.

This script provides a command-line interface for running the NBA Betting Agent
with various configuration options.
"""

import os
import sys
import argparse
import logging
from datetime import datetime

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

# Import configuration and agent
from config.settings import load_settings, save_settings
from agent.agent import NBABettingAgent

def parse_args():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description="Run the NBA Betting Agent")
    
    parser.add_argument(
        "--config", 
        type=str, 
        help="Path to a custom configuration file"
    )
    
    parser.add_argument(
        "--test-mode", 
        action="store_true", 
        help="Run in test mode (no actual betting)"
    )
    
    parser.add_argument(
        "--no-test-mode", 
        action="store_true", 
        help="Run with actual betting (disables test mode)"
    )
    
    parser.add_argument(
        "--bankroll", 
        type=float, 
        help="Set the bankroll amount"
    )
    
    parser.add_argument(
        "--log-level", 
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        help="Set the logging level"
    )
    
    parser.add_argument(
        "--save-config", 
        type=str, 
        help="Save the current configuration to a file"
    )
    
    return parser.parse_args()

def main():
    """Main entry point for running the NBA Betting Agent."""
    # Parse command-line arguments
    args = parse_args()
    
    # Load configuration
    config = load_settings(args.config)
    
    # Override configuration with command-line arguments
    if args.test_mode:
        config["agent"]["test_mode"] = True
    
    if args.no_test_mode:
        config["agent"]["test_mode"] = False
    
    if args.bankroll:
        config["betting"]["bankroll"] = args.bankroll
    
    if args.log_level:
        config["logging"]["level"] = args.log_level
    
    # Save configuration if requested
    if args.save_config:
        save_settings(config, args.save_config)
        print(f"Configuration saved to {args.save_config}")
        if not args.config:  # If we're not also loading this config, exit
            return
    
    # Set up logging
    log_config = config["logging"]
    log_dir = os.path.dirname(log_config["file"])
    if not os.path.exists(log_dir):
        os.makedirs(log_dir, exist_ok=True)
    
    logging.basicConfig(
        level=getattr(logging, log_config["level"]),
        format=log_config["format"],
        handlers=[
            logging.FileHandler(log_config["file"]),
            logging.StreamHandler()
        ]
    )
    
    logger = logging.getLogger("nba_agent")
    
    # Log startup information
    logger.info("=" * 50)
    logger.info(f"Starting NBA Betting Agent at {datetime.now().isoformat()}")
    logger.info(f"Test mode: {'Enabled' if config['agent']['test_mode'] else 'Disabled'}")
    logger.info(f"Bankroll: ${config['betting']['bankroll']}")
    logger.info("=" * 50)
    
    # Create and run the agent
    agent = NBABettingAgent()
    agent.run()

if __name__ == "__main__":
    main() 