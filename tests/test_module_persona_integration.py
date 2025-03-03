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
from agent.modules.research import ResearchModule
from agent.modules.reasoning import ReasoningModule
from agent.modules.execution import ExecutionModule
from agent.modules.risk_management import RiskManagementModule
from agent.persona.billy import BillyPersona
from agent.utils.response_formatter import BillyResponseFormatter

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

def test_research_module():
    """Test the ResearchModule's integration with Billy's persona"""
    print("\n=== Testing ResearchModule Persona Integration ===")
    
    # Get configuration
    config = get_config()
    
    # Create controller
    controller = AgentController(config)
    
    # Test generate_research_summary
    research_results = [
        {
            "game_id": "game1",
            "home_team": "Los Angeles Lakers",
            "away_team": "Golden State Warriors",
            "odds_data": {"markets": [{"bet_type": "moneyline", "odds": -110}]},
            "injury_data": {"home_team_injuries": [{"player": "LeBron James", "status": "Questionable"}]},
            "team_stats": {"home_team_stats": {"wins": 15, "losses": 10}}
        },
        {
            "game_id": "game2",
            "home_team": "Boston Celtics",
            "away_team": "Philadelphia 76ers",
            "odds_data": {"markets": [{"bet_type": "moneyline", "odds": -120}]},
            "injury_data": {"away_team_injuries": [{"player": "Joel Embiid", "status": "Out"}]},
            "team_stats": {"home_team_stats": {"wins": 18, "losses": 7}}
        }
    ]
    
    summary = controller.research_module.generate_research_summary(research_results)
    print(f"Research Summary: {summary}")

def test_reasoning_module():
    """Test the ReasoningModule's integration with Billy's persona"""
    print("\n=== Testing ReasoningModule Persona Integration ===")
    
    # Get configuration
    config = get_config()
    
    # Create controller
    controller = AgentController(config)
    
    # Test format_betting_decision with a positive decision
    positive_decision = {
        "game_id": "game1",
        "home_team": "Los Angeles Lakers",
        "away_team": "Golden State Warriors",
        "should_bet": True,
        "team": "Los Angeles Lakers",
        "expected_value": 7.5,  # 7.5% edge
        "bet_size": 50.0,
        "odds": -110,
        "book": "DraftKings",
        "reasoning": "Home team has 7.5% edge, which exceeds our 2.0% threshold."
    }
    
    formatted = controller.reasoning_module.format_betting_decision(positive_decision)
    print(f"Positive Decision: {formatted}")
    
    # Test format_betting_decision with a negative decision
    negative_decision = {
        "game_id": "game2",
        "home_team": "Boston Celtics",
        "away_team": "Philadelphia 76ers",
        "should_bet": False,
        "team": None,
        "expected_value": 1.5,  # 1.5% edge, below threshold
        "bet_size": 0.0,
        "odds": None,
        "book": None,
        "reasoning": "No bet has sufficient edge. Best option is 1.5%, below our 2.0% threshold"
    }
    
    formatted = controller.reasoning_module.format_betting_decision(negative_decision)
    print(f"Negative Decision: {formatted}")

def test_execution_module():
    """Test the ExecutionModule's integration with Billy's persona"""
    print("\n=== Testing ExecutionModule Persona Integration ===")
    
    # Get configuration
    config = get_config()
    
    # Create controller
    controller = AgentController(config)
    
    # Test format_bet_summary with bets placed
    execution_results = {
        "bets_placed": 2,
        "total_amount": 125.0,
        "bet_details": [
            {
                "bet_id": "test-game1-123456789",
                "amount": 75.0,
                "team": "Los Angeles Lakers",
                "odds": -110,
                "timestamp": "2023-05-01T15:30:00"
            },
            {
                "bet_id": "test-game2-123456790",
                "amount": 50.0,
                "team": "Boston Celtics",
                "odds": -120,
                "timestamp": "2023-05-01T15:31:00"
            }
        ],
        "timestamp": "2023-05-01T15:31:00"
    }
    
    formatted = controller.execution_module.format_bet_summary(execution_results)
    print(f"Execution Results (with bets): {formatted}")
    
    # Test format_bet_summary with no bets placed
    no_bets_results = {
        "bets_placed": 0,
        "total_amount": 0.0,
        "bet_details": [],
        "timestamp": "2023-05-01T15:31:00"
    }
    
    formatted = controller.execution_module.format_bet_summary(no_bets_results)
    print(f"Execution Results (no bets): {formatted}")

def test_risk_management_module():
    """Test the RiskManagementModule's integration with Billy's persona"""
    print("\n=== Testing RiskManagementModule Persona Integration ===")
    
    # Get configuration
    config = get_config()
    
    # Create controller
    controller = AgentController(config)
    
    # Test format_risk_assessment with an approved bet
    approved_decision = {
        "game_id": "game1",
        "team": "Los Angeles Lakers",
        "should_bet": True,
        "original_bet_size": 75.0,
        "bet_size": 75.0,
        "expected_value": 7.5,
        "risk_management_note": "Bet approved"
    }
    
    formatted = controller.risk_management_module.format_risk_assessment(approved_decision)
    print(f"Approved Bet: {formatted}")
    
    # Test format_risk_assessment with an adjusted bet
    adjusted_decision = {
        "game_id": "game2",
        "team": "Boston Celtics",
        "should_bet": True,
        "original_bet_size": 150.0,
        "bet_size": 100.0,
        "expected_value": 6.5,
        "risk_management_note": "Bet size adjusted from $150.00 to $100.00"
    }
    
    formatted = controller.risk_management_module.format_risk_assessment(adjusted_decision)
    print(f"Adjusted Bet: {formatted}")
    
    # Test format_risk_assessment with a rejected bet
    rejected_decision = {
        "game_id": "game3",
        "team": "Philadelphia 76ers",
        "should_bet": False,
        "original_bet_size": 50.0,
        "bet_size": 0.0,
        "expected_value": 1.5,
        "risk_management_note": "Expected value 1.50% below threshold 2.0%"
    }
    
    formatted = controller.risk_management_module.format_risk_assessment(rejected_decision)
    print(f"Rejected Bet: {formatted}")

def main():
    """Main function to run all tests"""
    print("Testing Module Persona Integration")
    
    # Load environment variables
    load_dotenv()
    
    # Run tests
    test_research_module()
    test_reasoning_module()
    test_execution_module()
    test_risk_management_module()
    
    print("\nAll tests completed")

if __name__ == "__main__":
    main() 