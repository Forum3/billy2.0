#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import logging
from pprint import pprint

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import the persona and formatter modules
from agent.persona.billy import BillyPersona
from agent.utils.response_formatter import BillyResponseFormatter

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

def main():
    """Test the BillyResponseFormatter functionality"""
    print("\n=== Testing BillyResponseFormatter ===")
    
    # Initialize the persona and formatter
    persona = BillyPersona()
    formatter = BillyResponseFormatter(persona)
    
    # Test format_betting_advice
    print("\nTesting format_betting_advice:")
    betting_advice_data = {
        "game": "Los Angeles Lakers vs Golden State Warriors",
        "bet_type": "Moneyline",
        "odds": "-110",
        "analysis": "Lakers have a strong home record and Warriors are on a back-to-back."
    }
    formatted = formatter.format_betting_advice(betting_advice_data)
    print(f"  {formatted}")
    
    # Test format_market_data
    print("\nTesting format_market_data:")
    market_data = {
        "away_team": "Golden State Warriors",
        "home_team": "Los Angeles Lakers",
        "spread": "Lakers -3.5 (-110)",
        "total": "Over/Under 224.5",
        "moneyline": "Lakers -160, Warriors +140",
        "start_time": "7:30 PM ET"
    }
    formatted = formatter.format_market_data(market_data)
    print(f"  {formatted}")
    
    # Test format_edge_analysis
    print("\nTesting format_edge_analysis:")
    edge_data = {
        "away_team": "Golden State Warriors",
        "home_team": "Los Angeles Lakers",
        "bet_team": "Los Angeles Lakers",
        "edge": 0.08  # 8% edge
    }
    formatted = formatter.format_edge_analysis(edge_data)
    print(f"  {formatted}")
    
    # Test format_research_summary
    print("\nTesting format_research_summary:")
    research_data = [
        {"game_id": "1", "home_team": "Lakers", "away_team": "Warriors", "edge": 0.08},
        {"game_id": "2", "home_team": "Celtics", "away_team": "76ers", "edge": 0.05},
        {"game_id": "3", "home_team": "Bucks", "away_team": "Heat", "edge": 0.03}
    ]
    formatted = formatter.format_research_summary(research_data)
    print(f"  {formatted}")
    
    # Test format_error_message
    print("\nTesting format_error_message:")
    error_messages = [
        "Connection timeout when connecting to API",
        "API rate limit exceeded",
        "Memory storage error",
        "Generic error message"
    ]
    for error in error_messages:
        formatted = formatter.format_error_message(error)
        print(f"  Error: {error}")
        print(f"  Formatted: {formatted}")
        print()
    
    # Test format_bet_placement
    print("\nTesting format_bet_placement:")
    bet_data = {
        "team": "Los Angeles Lakers",
        "amount": 75.0,
        "odds": "-110",
        "book": "DraftKings"
    }
    formatted = formatter.format_bet_placement(bet_data)
    print(f"  {formatted}")
    
    # Test format_bet_outcome
    print("\nTesting format_bet_outcome:")
    # Win scenario
    win_data = {
        "team": "Los Angeles Lakers",
        "amount": 75.0,
        "profit": 68.18,  # $75 at -110 odds
        "won": True
    }
    formatted = formatter.format_bet_outcome(win_data)
    print(f"  Win scenario: {formatted}")
    
    # Loss scenario
    loss_data = {
        "team": "Golden State Warriors",
        "amount": 50.0,
        "profit": 0,
        "won": False
    }
    formatted = formatter.format_bet_outcome(loss_data)
    print(f"  Loss scenario: {formatted}")
    
    # Test format_daily_metrics
    print("\nTesting format_daily_metrics:")
    # Profitable day
    profit_metrics = {
        "bankroll": 1250.0,
        "daily_profit": 75.0,
        "wins": 3,
        "losses": 1
    }
    formatted = formatter.format_daily_metrics(profit_metrics)
    print(f"  Profitable day: {formatted}")
    
    # Losing day
    loss_metrics = {
        "bankroll": 950.0,
        "daily_profit": -50.0,
        "wins": 1,
        "losses": 2
    }
    formatted = formatter.format_daily_metrics(loss_metrics)
    print(f"  Losing day: {formatted}")
    
    # Test format_startup_message
    print("\nTesting format_startup_message:")
    formatted = formatter.format_startup_message()
    print(f"  {formatted}")
    
    # Test format_generic_message
    print("\nTesting format_generic_message:")
    generic_messages = [
        "Agent initialization complete",
        "Found 3 betting opportunities",
        "Wallet balance is $1500.75"
    ]
    for message in generic_messages:
        formatted = formatter.format_generic_message(message)
        print(f"  Original: {message}")
        print(f"  Formatted: {formatted}")
        print()
    
    print("\nTest completed")

if __name__ == "__main__":
    main() 