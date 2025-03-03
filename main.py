#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
NBA Betting Agent - Main Entry Point
"""

import os
import sys
import argparse
import logging
import signal
import time
from pathlib import Path

# Import configuration
from config.settings import get_config

# Import agent controller
from agent.controller import AgentController

def setup_logging():
    """Set up logging configuration"""
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    config = get_config()
    log_config = config["logging"]
    logging.basicConfig(
        level=getattr(logging, log_config["level"]),
        format=log_config["format"],
        handlers=[
            logging.FileHandler(log_config["file"]),
            logging.StreamHandler()
        ]
    )
    
    return logging.getLogger("nba_agent.main")

def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description='NBA Betting Agent')
    
    parser.add_argument('--test', action='store_true', 
                        help='Run in test mode (no actual bets placed)')
    
    parser.add_argument('--sim', action='store_true',
                        help='Run in simulation mode (with historical data)')
    
    parser.add_argument('--live', action='store_true',
                        help='Run in live mode (with actual betting)')
    
    parser.add_argument('--config', type=str,
                        help='Path to custom configuration file')
    
    return parser.parse_args()

def main():
    """Main entry point for the NBA Betting Agent"""
    # Parse command line arguments
    args = parse_arguments()
    
    # Load configuration
    config = get_config()
    
    # Update configuration based on arguments
    if args.test:
        config["agent"]["test_mode"] = True
    elif args.sim:
        config["agent"]["test_mode"] = True
        config["agent"]["simulation_mode"] = True
    elif args.live:
        config["agent"]["test_mode"] = False
    
    # Set up logging
    logger = setup_logging()
    
    # Log startup information
    logger.info("Starting NBA Betting Agent")
    if args.test:
        logger.info("Running in TEST mode - no actual bets will be placed")
    elif args.sim:
        logger.info("Running in SIMULATION mode with historical data")
    elif args.live:
        logger.info("Running in LIVE mode - REAL bets will be placed!")
    
    # Check for API keys in live mode
    if config["agent"]["test_mode"] == False:
        if config["polymarket"]["api_key"] == "your_polymarket_api_key_here":
            logger.error("Polymarket API key not configured for live mode")
            sys.exit(1)
    
    # Initialize the agent controller
    agent = AgentController(config)
    
    # Set up signal handling for graceful shutdown
    def signal_handler(sig, frame):
        logger.info("Received shutdown signal")
        agent.stop()
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Start the agent
    try:
        agent.start()
    except KeyboardInterrupt:
        logger.info("Keyboard interrupt received")
    except Exception as e:
        logger.error(f"Unhandled exception: {str(e)}", exc_info=True)
    finally:
        agent.stop()
        logger.info("NBA Betting Agent shutdown complete")

if __name__ == "__main__":
    main() 