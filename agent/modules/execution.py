#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Execution module for the NBA Betting Agent.

This module is responsible for executing betting decisions by interacting
with sportsbook APIs or providing instructions for manual execution.
"""

import logging
import time
import json
import requests
from typing import Dict, List, Any, Optional
from datetime import datetime
from agent.utils.response_formatter import BillyResponseFormatter

logger = logging.getLogger(__name__)

class PolymarketAPI:
    """Client for interacting with the Polymarket API"""
    
    def __init__(self, api_key: str, base_url: str = "https://api.polymarket.com"):
        """
        Initialize the Polymarket API client.
        
        Args:
            api_key: API key for authenticating with Polymarket
            base_url: Base URL for the Polymarket API
        """
        self.api_key = api_key
        self.base_url = base_url
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        logger.info("Polymarket API client initialized")
    
    def get_markets(self, category: str = "NBA") -> List[Dict[str, Any]]:
        """
        Get available markets in a category.
        
        Args:
            category: Market category to filter by
            
        Returns:
            List of available markets
        """
        try:
            url = f"{self.base_url}/markets"
            params = {"category": category}
            
            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            
            return response.json().get("markets", [])
            
        except Exception as e:
            logger.error(f"Error getting markets: {str(e)}")
            return []
    
    def get_market_details(self, market_id: str) -> Dict[str, Any]:
        """
        Get details for a specific market.
        
        Args:
            market_id: ID of the market to retrieve
            
        Returns:
            Market details
        """
        try:
            url = f"{self.base_url}/markets/{market_id}"
            
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            
            return response.json()
            
        except Exception as e:
            logger.error(f"Error getting market details: {str(e)}")
            return {}
    
    def place_bet(self, market_id: str, outcome: str, amount: float) -> Dict[str, Any]:
        """
        Place a bet on a market.
        
        Args:
            market_id: ID of the market to bet on
            outcome: Outcome to bet on (e.g., "YES" or "NO")
            amount: Amount to bet in USD
            
        Returns:
            Bet details including bet ID and odds
        """
        try:
            url = f"{self.base_url}/bets"
            
            data = {
                "market_id": market_id,
                "outcome": outcome,
                "amount": amount
            }
            
            response = requests.post(url, headers=self.headers, json=data)
            response.raise_for_status()
            
            result = response.json()
            logger.info(f"Successfully placed bet on {market_id}: {outcome} for ${amount}")
            
            return {
                "bet_id": result.get("bet_id"),
                "market_id": market_id,
                "outcome": outcome,
                "amount": amount,
                "odds": result.get("odds", 1.95),  # Default to 1.95 if not provided
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error placing bet: {str(e)}")
            raise Exception(f"Failed to place bet: {str(e)}")
    
    def get_bet_status(self, bet_id: str) -> Dict[str, Any]:
        """
        Get the status of a bet.
        
        Args:
            bet_id: ID of the bet to check
            
        Returns:
            Bet status details
        """
        try:
            url = f"{self.base_url}/bets/{bet_id}"
            
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            
            return response.json()
            
        except Exception as e:
            logger.error(f"Error getting bet status: {str(e)}")
            return {"status": "unknown", "error": str(e)}

class ExecutionModule:
    """Module for executing NBA betting actions on Polymarket"""
    
    def __init__(self, memory_client, config):
        self.memory = memory_client
        self.config = config
        self.logger = logging.getLogger("nba_agent.execution")
        self.polymarket_api = PolymarketAPI(
            api_key=config["polymarket"]["api_key"],
            base_url=config["polymarket"]["base_url"]
        )
        
        # Store reference to controller for accessing persona
        self.controller = None
        
        self.logger.info("Execution module initialized")
    
    def set_controller(self, controller):
        """
        Set the controller reference for accessing persona.
        
        Args:
            controller: The agent controller instance
        """
        self.controller = controller
    
    def format_bet_summary(self, results: Dict[str, Any]) -> str:
        """
        Format bet summary in Billy's style.
        
        Args:
            results: Dictionary containing execution results
            
        Returns:
            Formatted bet summary
        """
        if self.controller and hasattr(self.controller, 'persona'):
            formatter = BillyResponseFormatter(self.controller.persona)
            
            if results.get("bets_placed", 0) > 0:
                # Format bet placement details
                bet_data = {
                    "count": results.get("bets_placed", 0),
                    "amount": results.get("total_amount", 0),
                    "details": results.get("bet_details", [])
                }
                
                # Create a message about the bets placed
                message = f"Placed {bet_data['count']} bets totaling ${bet_data['amount']:.2f}"
                return formatter.format_generic_message(message, "execution")
            else:
                return formatter.format_generic_message("no bets placed. waiting for better spots.", "execution")
        else:
            # Fallback if controller or persona not available
            if results.get("bets_placed", 0) > 0:
                return f"Placed {results['bets_placed']} bets totaling ${results['total_amount']:.2f}"
            else:
                return "No bets placed. Waiting for better spots."
    
    def execute_betting_actions(self, betting_decisions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Execute betting actions based on reasoning outcomes"""
        self.logger.info(f"Executing betting actions for {len(betting_decisions)} decisions")
        
        execution_results = {
            "bets_placed": 0,
            "total_amount": 0,
            "bet_details": [],
            "timestamp": datetime.now().isoformat()
        }
        
        try:
            for decision in betting_decisions:
                decision_content = decision.get("content", "")
                metadata = decision.get("metadata", {})
                
                # Skip if this isn't an actual betting decision
                if metadata.get("decision") != "bet":
                    continue
                
                game_id = metadata.get("game_id")
                team = metadata.get("team")
                expected_value = metadata.get("expected_value", 0)
                
                # Get bet size from the decision metadata or recalculate
                bet_size = self._calculate_bet_size(expected_value)
                
                # Skip if bet size is too small
                if bet_size < self.config["betting"]["min_bet"]:
                    self.logger.info(f"Skipping bet for game {game_id}: bet size {bet_size} below minimum")
                    continue
                
                # Check if we're in test mode
                if self.config["agent"]["test_mode"]:
                    self.logger.info(f"TEST MODE: Would place bet of ${bet_size} on {team} for game {game_id}")
                    bet_result = {
                        "success": True,
                        "bet_id": f"test-{game_id}-{int(time.time())}",
                        "amount": bet_size,
                        "team": team,
                        "odds": 1.95,  # Placeholder
                        "timestamp": datetime.now().isoformat()
                    }
                else:
                    # Place actual bet on Polymarket
                    bet_result = self.place_bet(game_id, team, bet_size)
                
                # Record bet details regardless of test mode
                if bet_result["success"]:
                    execution_results["bets_placed"] += 1
                    execution_results["total_amount"] += bet_result["amount"]
                    execution_results["bet_details"].append(bet_result)
                    
                    # Record the bet in memory
                    self.record_bet(game_id, team, bet_result)
            
            # Format and log summary in Billy's style
            summary = self.format_bet_summary(execution_results)
            self.logger.info(summary)
            
            # Add summary to execution results
            execution_results["summary"] = summary
            
            return execution_results
            
        except Exception as e:
            self.logger.error(f"Error executing betting actions: {str(e)}")
            raise
    
    def place_bet(self, game_id: str, team: str, amount: float) -> Dict[str, Any]:
        """Place a bet on Polymarket"""
        self.logger.info(f"Placing bet of ${amount:.2f} on {team} for game {game_id}")
        
        try:
            # Get market ID for this game
            market_id = self._get_market_id_for_game(game_id)
            
            # Place bet through Polymarket API
            result = self.polymarket_api.place_bet(
                market_id=market_id,
                outcome=self._team_to_outcome(team),
                amount=amount
            )
            
            return {
                "success": True,
                "bet_id": result["bet_id"],
                "amount": amount,
                "team": team,
                "odds": result["odds"],
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error placing bet: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "game_id": game_id,
                "team": team,
                "amount": amount,
                "timestamp": datetime.now().isoformat()
            }
    
    def record_bet(self, game_id: str, team: str, bet_result: Dict[str, Any]) -> None:
        """Record bet details in memory"""
        self.memory.add({
            "content": f"Placed bet of ${bet_result['amount']:.2f} on {team} for game {game_id}",
            "metadata": {
                "type": "bet_record",
                "game_id": game_id,
                "team": team,
                "bet_id": bet_result["bet_id"],
                "amount": bet_result["amount"],
                "odds": bet_result["odds"],
                "timestamp": bet_result["timestamp"],
                "status": "placed"
            }
        })
    
    def monitor_outcomes(self) -> None:
        """Monitor outcomes of placed bets"""
        self.logger.info("Monitoring bet outcomes")
        
        try:
            # Get all open bets from memory
            open_bets = self.memory.search({
                "query": "bets with status of placed",
                "metadata_filter": {
                    "type": "bet_record",
                    "status": "placed"
                }
            })
            
            for bet in open_bets:
                metadata = bet.get("metadata", {})
                bet_id = metadata.get("bet_id")
                game_id = metadata.get("game_id")
                
                # Check if the game has completed
                game_status = self._check_game_status(game_id)
                
                if game_status == "completed":
                    # Get game result
                    game_result = self._get_game_result(game_id)
                    
                    # Determine if bet won
                    bet_team = metadata.get("team")
                    bet_won = (bet_team == "home" and game_result["home_team_won"]) or \
                              (bet_team == "away" and not game_result["home_team_won"])
                    
                    # Update bet status in memory
                    self.memory.add({
                        "content": f"Bet {bet_id} for game {game_id} has {('won' if bet_won else 'lost')}",
                        "metadata": {
                            "type": "bet_record",
                            "bet_id": bet_id,
                            "game_id": game_id,
                            "status": "settled",
                            "outcome": "won" if bet_won else "lost",
                            "profit": metadata.get("amount") * (metadata.get("odds") - 1) if bet_won else -metadata.get("amount"),
                            "settlement_time": datetime.now().isoformat()
                        }
                    })
                    
                    # Record outcome for learning
                    self.update_strategy(game_id, bet_team, bet_won)
        
        except Exception as e:
            self.logger.error(f"Error monitoring bet outcomes: {str(e)}")
    
    def update_strategy(self, game_id: str, team: str, bet_won: bool) -> None:
        """Update betting strategy based on bet outcomes"""
        self.logger.info(f"Updating strategy based on outcome of game {game_id}")
        
        try:
            # Retrieve original betting decision from memory
            betting_decision = self.memory.search({
                "query": f"betting decision for game {game_id}",
                "metadata_filter": {
                    "type": "betting_decision",
                    "game_id": game_id
                },
                "limit": 1
            })
            
            if not betting_decision:
                self.logger.warning(f"Could not find original betting decision for game {game_id}")
                return
            
            decision = betting_decision[0]
            metadata = decision.get("metadata", {})
            
            # Record outcome and learning points
            self.memory.add({
                "content": f"Strategy update for game {game_id}: Bet on {team} {'won' if bet_won else 'lost'}",
                "metadata": {
                    "type": "strategy_update",
                    "game_id": game_id,
                    "bet_team": team,
                    "outcome": "won" if bet_won else "lost",
                    "original_confidence": metadata.get("confidence"),
                    "original_ev": metadata.get("expected_value"),
                    "learning_points": self._extract_learning_points(decision, bet_won),
                    "timestamp": datetime.now().isoformat()
                }
            })
            
        except Exception as e:
            self.logger.error(f"Error updating strategy: {str(e)}")
    
    def _calculate_bet_size(self, expected_value: float) -> float:
        """Calculate optimal bet size based on expected value"""
        # Use Kelly criterion with fraction to be conservative
        max_kelly_fraction = self.config["betting"]["max_kelly_fraction"]
        bankroll = self.config["betting"]["bankroll"]
        
        # Simple Kelly implementation
        kelly_percentage = expected_value / 100  # Convert EV percentage to decimal
        conservative_kelly = kelly_percentage * max_kelly_fraction
        
        # Calculate bet size
        bet_size = conservative_kelly * bankroll
        
        # Apply minimum and maximum bet constraints
        min_bet = self.config["betting"]["min_bet"]
        max_bet = self.config["betting"]["max_bet"]
        
        return max(min_bet, min(bet_size, max_bet))
    
    def _get_market_id_for_game(self, game_id: str) -> str:
        """Get Polymarket market ID for a given game"""
        # In a real implementation, this would query Polymarket's API
        # or use a mapping from game IDs to market IDs
        
        # For now, return a placeholder
        return f"polymarket-{game_id}"
    
    def _team_to_outcome(self, team: str) -> str:
        """Convert team (home/away) to Polymarket outcome string"""
        if team == "home":
            return "YES"  # Assuming YES = home team wins
        else:
            return "NO"  # Assuming NO = away team wins
    
    def _check_game_status(self, game_id: str) -> str:
        """Check if a game has completed"""
        # In a real implementation, this would query a sports data API
        
        # For testing, randomly return completed or in_progress
        import random
        return random.choice(["completed", "in_progress"])
    
    def _get_game_result(self, game_id: str) -> Dict[str, Any]:
        """Get the result of a completed game"""
        # In a real implementation, this would query a sports data API
        
        # For testing, randomly determine winner
        import random
        home_team_won = random.choice([True, False])
        
        return {
            "game_id": game_id,
            "home_team_won": home_team_won,
            "home_score": 110 if home_team_won else 98,
            "away_score": 98 if home_team_won else 110
        }
    
    def _extract_learning_points(self, decision: Dict[str, Any], bet_won: bool) -> List[str]:
        """Extract learning points from bet outcome"""
        # In a sophisticated implementation, this would analyze the original
        # decision reasoning against the actual outcome to identify learnings
        
        if bet_won:
            return ["Successful prediction validates our model",
                    "Continue monitoring similar patterns"]
        else:
            return ["Investigate factors that weren't properly weighted",
                    "Review model assumptions for this game type"]
    
    # Legacy method for backward compatibility
    def run(self, betting_decisions: Dict[str, Any]) -> Dict[str, Any]:
        """
        Run the execution module (legacy method).
        
        Args:
            betting_decisions: Dictionary containing betting decisions
            
        Returns:
            Dictionary containing execution results
        """
        self.logger.info("Running execution module (legacy method)")
        
        # Convert legacy betting decisions to new format
        decisions_list = []
        for rec in betting_decisions.get('betting_recommendations', []):
            decisions_list.append({
                "content": f"Betting recommendation: {rec.get('bet_type')} on {rec.get('bet_target')}",
                "metadata": {
                    "type": "betting_decision",
                    "decision": "bet",
                    "game_id": rec.get('game_id', f"unknown-{int(time.time())}"),
                    "team": rec.get('bet_target', "unknown"),
                    "confidence": rec.get('confidence', 0.7),
                    "expected_value": rec.get('edge', 0.05)
                }
            })
        
        # Execute betting actions
        results = self.execute_betting_actions(decisions_list)
        
        # Format for backward compatibility
        legacy_results = {
            "bets_placed": results.get("bets_placed", 0),
            "total_amount": results.get("total_amount", 0.0),
            "summary": results.get("summary", ""),
            "timestamp": results.get("timestamp", datetime.now().isoformat())
        }
        
        return legacy_results 