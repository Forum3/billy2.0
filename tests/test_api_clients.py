#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import logging
from pprint import pprint
from datetime import datetime

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import the API clients
from agent.api.sportstensor_client import SportsTensorClient
from agent.api.polymarket_client import PolymarketClient

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

def test_sportstensor():
    """Test the SportsTensor API client"""
    print("\n=== Testing SportsTensor API Client ===")
    
    # Replace with your actual API key
    api_key = "your_sportstensor_api_key_here"
    
    # Create client
    client = SportsTensorClient(api_key=api_key)
    
    # Get NBA predictions
    predictions = client.get_nba_predictions()
    print(f"Retrieved {len(predictions)} NBA predictions")
    
    # Display sample predictions
    if predictions:
        print("\nSample Prediction:")
        pprint(predictions[0])
    
    # Get model performance
    performance = client.get_model_performance()
    print("\nModel Performance:")
    pprint(performance)

def test_polymarket():
    """Test the Polymarket API client"""
    print("\n=== Testing Polymarket API Client ===")
    
    # Create client (API key optional for public endpoints)
    client = PolymarketClient()
    
    # Get NBA markets
    markets = client.get_nba_markets()
    print(f"Retrieved {len(markets)} NBA markets")
    
    # Display sample market
    if markets:
        print("\nSample Market:")
        sample_market = markets[0]
        pprint({
            "id": sample_market.get("id"),
            "title": sample_market.get("title"),
            "description": sample_market.get("description"),
            "slug": sample_market.get("slug")
        })
        
        # Extract start time
        description = sample_market.get("description", "")
        start_time = client.extract_start_time(description)
        if start_time:
            print(f"\nExtracted Start Time: {start_time.isoformat()}")
        
        # Get market odds if market ID is available
        market_id = sample_market.get("id")
        if market_id:
            odds = client.get_market_odds(market_id)
            print("\nMarket Odds:")
            pprint(odds)
    
    # Test slug construction
    home_team = "Los Angeles Lakers"
    away_team = "Golden State Warriors"
    game_date = datetime.now()
    slug = client.construct_nba_slug(home_team, away_team, game_date)
    print(f"\nConstructed Slug: {slug}")
    
    # Get market by slug
    market = client.get_market_by_slug(slug)
    if market:
        print(f"Found market for slug: {slug}")
        print(f"Title: {market.get('title')}")
    else:
        print(f"No market found for slug: {slug}")

def main():
    """Main function to run tests"""
    print("Testing NBA Betting Agent API Clients")
    
    # Test SportsTensor client
    try:
        test_sportstensor()
    except Exception as e:
        print(f"Error testing SportsTensor client: {str(e)}")
    
    # Test Polymarket client
    try:
        test_polymarket()
    except Exception as e:
        print(f"Error testing Polymarket client: {str(e)}")

if __name__ == "__main__":
    main() 