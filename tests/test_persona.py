#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import logging
from pprint import pprint

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import the persona and communication modules
from agent.persona.billy import BillyPersona
from agent.persona.communication import CommunicationManager

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

def test_persona():
    """Test the Billy persona functionality"""
    print("\n=== Testing Billy Persona ===")
    
    # Initialize the persona
    persona = BillyPersona()
    
    # Test getting expressions for different topics
    topics = ["lebron", "warriors", "betting", "dfs", "random topic"]
    
    print("\nTesting expressions for different topics:")
    for topic in topics:
        expression = persona.get_expression(topic)
        print(f"  Topic: {topic}")
        print(f"  Expression: {expression}")
        print()
    
    # Test message formatting for different styles
    messages = [
        "The Lakers are playing the Warriors tonight.",
        "Here's some betting advice for the game.",
        "Let me explain how the Kelly criterion works."
    ]
    
    styles = ["default", "betting_advice", "helpful"]
    
    print("\nTesting message formatting for different styles:")
    for message in messages:
        for style in styles:
            formatted = persona.format_message(message, style)
            print(f"  Original: {message}")
            print(f"  Style: {style}")
            print(f"  Formatted: {formatted}")
            print()
    
    # Test daily summary
    print("\nTesting daily summary:")
    summary = persona.create_daily_summary()
    print(f"  {summary}")

def test_communication():
    """Test the communication manager functionality"""
    print("\n=== Testing Communication Manager ===")
    
    # Initialize the communication manager
    comm_manager = CommunicationManager()
    
    # Test formatting a betting opportunity
    opportunity = {
        "home_team": "Los Angeles Lakers",
        "away_team": "Golden State Warriors",
        "team": "Los Angeles Lakers",
        "edge": 0.08,  # 8% edge
        "model_probability": 0.65,
        "market_probability": 0.57
    }
    
    print("\nTesting betting opportunity formatting:")
    formatted = comm_manager.format_betting_opportunity(opportunity)
    print(f"  {formatted}")
    
    # Test formatting wallet status
    wallet_info = {
        "status": "success",
        "address": "0x1234567890abcdef1234567890abcdef12345678",
        "balance_usdc": 1500.75,
        "balance_matic": 0.25,
        "network": "Polygon",
        "chain_id": 137
    }
    
    print("\nTesting wallet status formatting:")
    formatted = comm_manager.format_wallet_status(wallet_info)
    print(f"  {formatted}")
    
    # Test formatting research results
    research_data = [
        {"game_id": "1", "home_team": "Lakers", "away_team": "Warriors"},
        {"game_id": "2", "home_team": "Celtics", "away_team": "76ers"},
        {"game_id": "3", "home_team": "Bucks", "away_team": "Heat"}
    ]
    
    print("\nTesting research results formatting:")
    formatted = comm_manager.format_research_results(research_data)
    print(f"  {formatted}")
    
    # Test formatting error message
    error = "Failed to connect to the API"
    
    print("\nTesting error message formatting:")
    formatted = comm_manager.format_error_message(error)
    print(f"  {formatted}")
    
    # Test formatting betting advice
    advice = {
        "team": "Los Angeles Lakers",
        "expected_value": 8.5,
        "confidence": 0.75,
        "odds": -110,
        "book": "DraftKings"
    }
    
    print("\nTesting betting advice formatting:")
    formatted = comm_manager.format_betting_advice(advice)
    print(f"  {formatted}")
    
    # Test formatting opportunity summary
    opportunities = [opportunity, opportunity, opportunity]
    
    print("\nTesting opportunity summary formatting:")
    formatted = comm_manager.format_opportunity_summary(opportunities)
    print(f"  {formatted}")
    
    # Test formatting notification
    print("\nTesting notification formatting:")
    notification_types = ["new_opportunity", "wallet_update", "research_complete", "error", "daily_summary"]
    
    for notification_type in notification_types:
        if notification_type == "new_opportunity":
            data = opportunity
        elif notification_type == "wallet_update":
            data = wallet_info
        elif notification_type == "research_complete":
            data = research_data
        elif notification_type == "error":
            data = {"message": error}
        else:
            data = {}
        
        formatted = comm_manager.format_notification(notification_type, data)
        print(f"  Type: {notification_type}")
        print(f"  Formatted: {formatted}")
        print()

def main():
    """Main function to run tests"""
    print("Testing Billy Persona and Communication Manager")
    
    # Test persona functionality
    test_persona()
    
    # Test communication manager functionality
    test_communication()
    
    print("\nTest completed")

if __name__ == "__main__":
    main() 