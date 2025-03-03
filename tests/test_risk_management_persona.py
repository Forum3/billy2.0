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
from agent.modules.risk_management import RiskManagementModule
from agent.memory.mem0_client import Mem0Client
from agent.memory.mem0_official import Mem0OfficialClient

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

def main():
    """Test the RiskManagementModule with Billy's persona"""
    print("Testing RiskManagementModule with Billy's Persona")
    
    # Load environment variables
    load_dotenv()
    
    # Get configuration
    config = get_config()
    
    # Initialize memory client
    if config['mem0'].get('use_official_client', False):
        print("Using official Mem0 client")
        try:
            memory = Mem0OfficialClient(
                api_key=config['mem0']['api_key'],
                agent_id=config['mem0']['agent_id'],
                base_url=config['mem0'].get('base_url', "https://api.mem0.ai"),
                cache_ttl=config['mem0'].get('cache_ttl', 300)
            )
        except Exception as e:
            print(f"Failed to initialize official Mem0 client: {str(e)}")
            print("Falling back to custom Mem0 client")
            memory = Mem0Client(
                api_key=config['mem0']['api_key'],
                agent_id=config['mem0']['agent_id'],
                base_url=config['mem0'].get('base_url', "https://api.mem0.ai"),
                cache_ttl=config['mem0'].get('cache_ttl', 300)
            )
    else:
        print("Using custom Mem0 client")
        memory = Mem0Client(
            api_key=config["mem0"]["api_key"],
            agent_id=config["mem0"]["agent_id"],
            base_url=config['mem0'].get('base_url', "https://api.mem0.ai"),
            cache_ttl=config['mem0'].get('cache_ttl', 300)
        )
    
    # Initialize risk management module
    risk_module = RiskManagementModule(memory, config)
    
    # Test validate_betting_decision with different scenarios
    print("\nTesting validate_betting_decision with different scenarios:")
    
    # Test case 1: Valid bet
    valid_decision = {
        "game_id": "test_game_1",
        "team": "Los Angeles Lakers",
        "should_bet": True,
        "expected_value": 5.0,  # 5% edge
        "bet_size": 50.0
    }
    
    print("\nTest Case 1: Valid bet with 5% edge")
    result = risk_module.validate_betting_decision(valid_decision)
    print(f"  Should bet: {result['should_bet']}")
    print(f"  Bet size: ${result['bet_size']:.2f}")
    
    # Test case 2: Edge below threshold
    low_edge_decision = {
        "game_id": "test_game_2",
        "team": "Golden State Warriors",
        "should_bet": True,
        "expected_value": 1.0,  # 1% edge, below threshold
        "bet_size": 50.0
    }
    
    print("\nTest Case 2: Edge below threshold (1%)")
    result = risk_module.validate_betting_decision(low_edge_decision)
    print(f"  Should bet: {result['should_bet']}")
    print(f"  Risk management note: {result.get('risk_management_note', 'None')}")
    
    # Test case 3: Bet size adjustment
    large_bet_decision = {
        "game_id": "test_game_3",
        "team": "Boston Celtics",
        "should_bet": True,
        "expected_value": 8.0,  # 8% edge
        "bet_size": 200.0  # Above max bet
    }
    
    print("\nTest Case 3: Bet size adjustment (200 -> 100)")
    result = risk_module.validate_betting_decision(large_bet_decision)
    print(f"  Should bet: {result['should_bet']}")
    print(f"  Original bet size: $200.00")
    print(f"  Adjusted bet size: ${result['bet_size']:.2f}")
    print(f"  Risk management note: {result.get('risk_management_note', 'None')}")
    
    # Test update_bankroll
    print("\nTesting update_bankroll:")
    
    # Test win scenario
    print("\nTest Case 4: Win scenario (+$75)")
    risk_module.update_bankroll(75.0, True)
    print(f"  New bankroll: ${risk_module.bankroll:.2f}")
    
    # Test loss scenario
    print("\nTest Case 5: Loss scenario (-$50)")
    risk_module.update_bankroll(50.0, False)
    print(f"  New bankroll: ${risk_module.bankroll:.2f}")
    
    # Test get_risk_metrics
    print("\nTesting get_risk_metrics:")
    metrics = risk_module.get_risk_metrics()
    print(f"  Bankroll: ${metrics['bankroll']:.2f}")
    print(f"  Daily bet limit: {metrics['limits']['daily_bet_limit']}")
    print(f"  Daily loss limit: ${metrics['limits']['daily_loss_limit']:.2f}")
    print(f"  Min EV threshold: {metrics['thresholds']['min_ev_threshold']}%")
    
    print("\nTest completed")

if __name__ == "__main__":
    main() 