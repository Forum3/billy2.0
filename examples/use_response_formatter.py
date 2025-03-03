#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Example demonstrating how to use the BillyResponseFormatter.

This script shows how to integrate the BillyResponseFormatter into
a module to ensure all outputs maintain Billy's distinctive style.
"""

import os
import sys
import logging
from datetime import datetime

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import the necessary modules
from agent.persona.billy import BillyPersona
from agent.utils.response_formatter import BillyResponseFormatter

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

class ExampleModule:
    """Example module that uses the BillyResponseFormatter"""
    
    def __init__(self):
        """Initialize the example module"""
        self.logger = logging.getLogger("example_module")
        
        # Initialize Billy's persona
        self.persona = BillyPersona()
        
        # Initialize the response formatter
        self.formatter = BillyResponseFormatter(self.persona)
        
        self.logger.info("Example module initialized")
    
    def process_betting_data(self, game_data):
        """
        Process betting data and return formatted responses.
        
        Args:
            game_data: Dictionary containing game and betting data
            
        Returns:
            Dictionary containing formatted responses
        """
        self.logger.info(f"Processing betting data for {game_data['home_team']} vs {game_data['away_team']}")
        
        # Simulate analyzing the game
        analysis_result = self._analyze_game(game_data)
        
        # Format the results using the response formatter
        formatted_responses = {
            "market_data": self.formatter.format_market_data({
                "away_team": game_data["away_team"],
                "home_team": game_data["home_team"],
                "spread": game_data["spread"],
                "total": game_data["total"],
                "moneyline": game_data["moneyline"],
                "start_time": game_data["start_time"]
            }),
            
            "edge_analysis": self.formatter.format_edge_analysis({
                "away_team": game_data["away_team"],
                "home_team": game_data["home_team"],
                "bet_team": analysis_result["bet_team"],
                "edge": analysis_result["edge"]
            }),
            
            "betting_advice": self.formatter.format_betting_advice({
                "game": f"{game_data['away_team']} vs {game_data['home_team']}",
                "bet_type": analysis_result["bet_type"],
                "odds": analysis_result["odds"],
                "analysis": analysis_result["analysis"]
            })
        }
        
        # Log the formatted responses
        for key, response in formatted_responses.items():
            self.logger.info(f"{key.upper()}: {response}")
        
        return formatted_responses
    
    def _analyze_game(self, game_data):
        """
        Simulate analyzing a game to find betting edges.
        
        Args:
            game_data: Dictionary containing game data
            
        Returns:
            Dictionary containing analysis results
        """
        # In a real implementation, this would use sophisticated models
        # For this example, we'll use a simple heuristic
        
        # Simulate finding an edge on the home team
        if "favorite" in game_data and game_data["favorite"] == "home":
            return {
                "bet_team": game_data["home_team"],
                "edge": 0.07,  # 7% edge
                "bet_type": "Moneyline",
                "odds": game_data["home_moneyline"],
                "analysis": f"{game_data['home_team']} has a strong home record and {game_data['away_team']} is on a back-to-back. Our model gives {game_data['home_team']} a 58% chance to win, compared to the market's 51%, creating a 7% edge."
            }
        else:
            return {
                "bet_team": game_data["away_team"],
                "edge": 0.05,  # 5% edge
                "bet_type": "Spread",
                "odds": game_data["away_spread_odds"],
                "analysis": f"{game_data['away_team']} has been undervalued by the market recently. Our model gives them a 55% chance to cover, compared to the market's 50%, creating a 5% edge."
            }
    
    def handle_error(self, error_message):
        """
        Handle an error and return a formatted error message.
        
        Args:
            error_message: Error message
            
        Returns:
            Formatted error message
        """
        self.logger.error(f"Error occurred: {error_message}")
        
        # Format the error message using the response formatter
        formatted_error = self.formatter.format_error_message(error_message)
        
        self.logger.info(f"Formatted error: {formatted_error}")
        return formatted_error
    
    def generate_daily_report(self, metrics):
        """
        Generate a daily report with formatted metrics.
        
        Args:
            metrics: Dictionary containing daily metrics
            
        Returns:
            Formatted daily report
        """
        self.logger.info("Generating daily report")
        
        # Format the daily metrics using the response formatter
        formatted_metrics = self.formatter.format_daily_metrics(metrics)
        
        # Format the startup message
        startup_message = self.formatter.format_startup_message()
        
        # Combine into a daily report
        daily_report = f"{startup_message}\n\n{formatted_metrics}"
        
        self.logger.info(f"Daily report: {daily_report}")
        return daily_report

def main():
    """Main function to demonstrate the BillyResponseFormatter"""
    print("Demonstrating BillyResponseFormatter Integration")
    
    # Create an instance of the example module
    module = ExampleModule()
    
    # Example game data
    game_data = {
        "away_team": "Golden State Warriors",
        "home_team": "Los Angeles Lakers",
        "favorite": "home",
        "spread": "Lakers -3.5",
        "total": "Over/Under 224.5",
        "moneyline": "Lakers -160, Warriors +140",
        "home_moneyline": "-160",
        "away_moneyline": "+140",
        "home_spread_odds": "-110",
        "away_spread_odds": "-110",
        "start_time": "7:30 PM ET"
    }
    
    # Process betting data
    print("\nProcessing betting data:")
    responses = module.process_betting_data(game_data)
    
    # Display formatted responses
    print("\nFormatted Responses:")
    for key, response in responses.items():
        print(f"\n{key.upper()}:")
        print(f"  {response}")
    
    # Handle an error
    print("\nHandling an error:")
    error_message = "Connection timeout when fetching odds data from API"
    formatted_error = module.handle_error(error_message)
    print(f"  {formatted_error}")
    
    # Generate a daily report
    print("\nGenerating daily report:")
    metrics = {
        "bankroll": 1250.0,
        "daily_profit": 75.0,
        "wins": 3,
        "losses": 1
    }
    daily_report = module.generate_daily_report(metrics)
    print(f"  {daily_report}")
    
    print("\nDemonstration completed")

if __name__ == "__main__":
    main() 