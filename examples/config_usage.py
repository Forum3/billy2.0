#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Example demonstrating how to use the updated configuration settings
for the NBA Betting Agent.
"""

import os
import sys
import logging
from pprint import pprint

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import the settings module
from config.settings import get_config, load_settings, save_settings

def main():
    # Set up logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Get the default configuration
    config = get_config()
    
    # Display the configuration
    print("\n=== Default Configuration ===")
    pprint(config)
    
    # Access specific configuration sections
    print("\n=== Agent Configuration ===")
    agent_config = config.get('agent', {})
    pprint(agent_config)
    
    print("\n=== Betting Configuration ===")
    betting_config = config.get('betting', {})
    pprint(betting_config)
    
    # Modify configuration values
    config['agent']['test_mode'] = False
    config['betting']['bankroll'] = 2000
    config['polymarket']['api_key'] = 'updated_api_key'
    
    # Save the modified configuration to a file
    save_settings(config, 'config/custom_config.json')
    print("\nSaved modified configuration to config/custom_config.json")
    
    # Load the saved configuration
    loaded_config = load_settings('config/custom_config.json')
    
    print("\n=== Modified Configuration ===")
    pprint(loaded_config)
    
    # Example of using environment variables to override configuration
    print("\n=== Using Environment Variables ===")
    print("You can set environment variables to override configuration values:")
    print("  export NBA_AGENT_BETTING__BANKROLL=5000")
    print("  export NBA_AGENT_AGENT__TEST_MODE=false")
    print("  export NBA_AGENT_POLYMARKET__API_KEY=your_actual_api_key")
    
    # Example of accessing configuration values in code
    print("\n=== Using Configuration Values in Code ===")
    bankroll = config['betting']['bankroll']
    min_bet = config['betting']['min_bet']
    max_bet = config['betting']['max_bet']
    
    print(f"Bankroll: ${bankroll}")
    print(f"Minimum bet: ${min_bet}")
    print(f"Maximum bet: ${max_bet}")
    print(f"Test mode: {'Enabled' if config['agent']['test_mode'] else 'Disabled'}")
    
    # Example of calculating a bet size based on configuration
    ev_percentage = 5.0  # 5% expected value
    kelly_fraction = config['betting']['max_kelly_fraction']
    
    # Simple Kelly calculation
    kelly_percentage = ev_percentage / 100
    conservative_kelly = kelly_percentage * kelly_fraction
    bet_size = conservative_kelly * bankroll
    
    # Apply min/max constraints
    bet_size = max(min_bet, min(bet_size, max_bet))
    
    print(f"\nFor a bet with {ev_percentage}% expected value:")
    print(f"Kelly percentage: {kelly_percentage:.4f}")
    print(f"Conservative Kelly ({kelly_fraction * 100}%): {conservative_kelly:.4f}")
    print(f"Calculated bet size: ${bet_size:.2f}")

if __name__ == "__main__":
    main() 