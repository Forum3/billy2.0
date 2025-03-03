#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import logging
from pprint import pprint

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import the BetstampClient
from agent.api.betstamp_client import BetstampClient

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

def main():
    # Create client with your API key
    client = BetstampClient(api_key="7KQ6RWNVA8HAUS5TOW5EYN12GOR5BGRLNA06F5G9DDHN0A9RJBJ89GL8G1QF6DFV")
    
    # Get NBA market data for moneyline, spread, and total from DraftKings and True Line
    markets = client.get_markets(
        league="NBA",
        book_ids=[200, 999],
        bet_types=["moneyline", "spread", "total"],
        periods=["FT"]
    )
    
    # Get basic stats and print
    market_count = len(markets.get("markets", []))
    print(f"Retrieved {market_count} markets")
    
    # Get the first few markets as examples
    sample_markets = markets.get("markets", [])[:5]
    print("\nSample Markets:")
    for market in sample_markets:
        print(f"Type: {market.get('bet_type')}, Side: {market.get('side')}, Odds: {market.get('odds')}")
    
    # Get fixtures (games)
    fixtures = client.get_fixtures(league="NBA")
    fixture_count = len(fixtures.get("fixtures", []))
    print(f"\nRetrieved {fixture_count} fixtures")
    
    # Get the first few fixtures as examples
    sample_fixtures = fixtures.get("fixtures", [])[:3]
    print("\nSample Fixtures:")
    for fixture in sample_fixtures:
        print(f"{fixture.get('away_abbr')} @ {fixture.get('home_abbr')} on {fixture.get('date')}")
    
    # Get teams data
    teams = client.get_teams(league="NBA")
    team_count = len(teams.get("teams", {}))
    print(f"\nRetrieved {team_count} teams")
    
    # Get players data
    players = client.get_players(league="NBA")
    player_count = len(players.get("players", {}))
    print(f"\nRetrieved {player_count} players")

if __name__ == "__main__":
    main() 