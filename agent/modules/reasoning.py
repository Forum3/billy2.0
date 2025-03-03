#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Reasoning module for the NBA Betting Agent.

This module is responsible for analyzing data and making betting decisions
based on the research data collected.
"""

import logging
from typing import Dict, List, Any
import json
from datetime import datetime
from agent.utils.response_formatter import BillyResponseFormatter

class ReasoningModule:
    """Module for reasoning about NBA betting decisions"""
    
    def __init__(self, memory_client, config):
        self.memory = memory_client
        self.config = config
        self.logger = logging.getLogger("nba_agent.reasoning")
        
        # Store reference to controller for accessing persona
        self.controller = None
        
        self.logger.info("Reasoning module initialized")
    
    def set_controller(self, controller):
        """
        Set the controller reference for accessing persona.
        
        Args:
            controller: The agent controller instance
        """
        self.controller = controller
    
    def format_betting_decision(self, decision: Dict[str, Any]) -> str:
        """
        Format a betting decision in Billy's style.
        
        Args:
            decision: The betting decision to format
            
        Returns:
            Formatted betting decision
        """
        if self.controller and hasattr(self.controller, 'persona'):
            formatter = BillyResponseFormatter(self.controller.persona)
            
            if decision.get("should_bet", False):
                # Format as edge analysis
                edge_data = {
                    "home_team": decision.get("home_team", ""),
                    "away_team": decision.get("away_team", ""),
                    "bet_team": decision.get("team", ""),
                    "edge": decision.get("expected_value", 0) / 100  # Convert to decimal
                }
                return formatter.format_edge_analysis(edge_data)
            else:
                # Format as generic message
                message = f"No edge found for {decision.get('away_team', '')} @ {decision.get('home_team', '')}"
                return formatter.format_generic_message(message, "reasoning")
        else:
            # Fallback if controller or persona not available
            if decision.get("should_bet", False):
                return f"Found edge on {decision.get('team', '')} with {decision.get('expected_value', 0):.2f}% value"
            else:
                return f"No edge found for {decision.get('away_team', '')} @ {decision.get('home_team', '')}"
    
    def execute_reasoning_tasks(self, research_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Execute reasoning tasks based on research data"""
        self.logger.info("Executing reasoning tasks")
        
        try:
            # Process each game that has completed research
            betting_decisions = []
            
            for game_research in research_data:
                # Extract game information from memory
                game_id = game_research.get("metadata", {}).get("game_id")
                home_team = game_research.get("metadata", {}).get("home_team")
                away_team = game_research.get("metadata", {}).get("away_team")
                
                self.logger.info(f"Reasoning about game: {away_team} @ {home_team}")
                
                # Extract odds data from research
                odds_data = game_research.get("odds_data", {})
                
                # Perform reasoning steps
                updated_beliefs = self.update_beliefs(game_research)
                probabilities = self.calculate_probabilities(updated_beliefs)
                market_comparison = self.compare_to_market_odds(probabilities, game_id, odds_data)
                ev_calculation = self.calculate_expected_value(market_comparison)
                betting_decision = self.make_betting_decision(ev_calculation)
                
                # If decision meets threshold, add to betting decisions
                if betting_decision["should_bet"]:
                    betting_decisions.append(betting_decision)
                    
                    # Store detailed decision reasoning in memory
                    self.memory.add({
                        "content": f"Betting decision for {away_team} @ {home_team}: {betting_decision['summary']}",
                        "metadata": {
                            "type": "betting_decision",
                            "game_id": game_id,
                            "decision": "bet",
                            "team": betting_decision["team"],
                            "confidence": betting_decision["confidence"],
                            "expected_value": betting_decision["expected_value"],
                            "reasoning": betting_decision["reasoning"]
                        }
                    })
                else:
                    # Store decision to skip betting
                    self.memory.add({
                        "content": f"Decision to skip betting on {away_team} @ {home_team}: {betting_decision['summary']}",
                        "metadata": {
                            "type": "betting_decision",
                            "game_id": game_id,
                            "decision": "skip",
                            "reasoning": betting_decision["reasoning"]
                        }
                    })
            
            # Compile overall reasoning results
            result = {
                "actionable_bets": betting_decisions,
                "total_games_analyzed": len(research_data),
                "total_betting_opportunities": len(betting_decisions),
                "timestamp": datetime.now().isoformat(),
                "summary": f"Found {len(betting_decisions)} actionable betting opportunities from {len(research_data)} games",
                "confidence": self._calculate_overall_confidence(betting_decisions),
                "expected_value": self._calculate_overall_ev(betting_decisions)
            }
            
            self.logger.info(f"Reasoning completed: {result['summary']}")
            return result
            
        except Exception as e:
            self.logger.error(f"Error executing reasoning tasks: {str(e)}")
            raise
    
    def update_beliefs(self, game_research: Dict[str, Any]) -> Dict[str, Any]:
        """Update beliefs based on new research data"""
        # In a real implementation, this would use Bayesian updating
        # to incorporate new information into existing beliefs
        
        # Extract the content from the research data
        content = game_research.get("content", "")
        
        # For now, return a simple representation of updated beliefs
        return {
            "game_id": game_research.get("metadata", {}).get("game_id", "unknown"),
            "home_team_strength": 0.55,  # Placeholder value
            "away_team_strength": 0.45,  # Placeholder value
            "key_factors": [
                "Home team has key player returning from injury",
                "Away team on second night of back-to-back"
            ]
        }
    
    def calculate_probabilities(self, updated_beliefs: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate win probabilities based on updated beliefs"""
        # In a real implementation, this would use statistical models
        
        # For demonstration, use simple values from updated beliefs
        home_strength = updated_beliefs.get("home_team_strength", 0.5)
        away_strength = updated_beliefs.get("away_team_strength", 0.5)
        
        # Normalize to ensure probabilities sum to 1
        total = home_strength + away_strength
        home_prob = home_strength / total
        away_prob = away_strength / total
        
        return {
            "game_id": updated_beliefs.get("game_id"),
            "home_win_probability": home_prob,
            "away_win_probability": away_prob,
            "confidence": 0.75  # Placeholder for model confidence
        }
    
    def compare_to_market_odds(self, probabilities: Dict[str, Any], game_id: str, odds_data: Dict[str, Any] = None) -> Dict[str, Any]:
        """Compare calculated probabilities with current market odds"""
        try:
            # Extract our calculated probabilities
            home_prob = probabilities.get("home_win_probability", 0.5)
            away_prob = probabilities.get("away_win_probability", 0.5)
            confidence = probabilities.get("confidence", 0.7)
            
            # If no odds data provided, use placeholder values
            if not odds_data:
                self.logger.warning(f"No odds data provided for game {game_id}, using placeholder values")
                market_odds = {
                    "home_implied_probability": 0.52,
                    "away_implied_probability": 0.48
                }
                
                home_edge = home_prob - market_odds["home_implied_probability"]
                away_edge = away_prob - market_odds["away_implied_probability"]
                
                return {
                    "game_id": game_id,
                    "calculated_probabilities": probabilities,
                    "market_odds": market_odds,
                    "home_edge": home_edge,
                    "away_edge": away_edge
                }
            
            # Extract market odds - focus on DraftKings and True Line
            dk_home_ml = odds_data.get("odds", {}).get("moneyline", {}).get("home", {}).get("dk")
            dk_away_ml = odds_data.get("odds", {}).get("moneyline", {}).get("away", {}).get("dk")
            true_home_ml = odds_data.get("odds", {}).get("moneyline", {}).get("home", {}).get("true_line")
            true_away_ml = odds_data.get("odds", {}).get("moneyline", {}).get("away", {}).get("true_line")
            
            # Calculate implied probabilities from odds
            dk_home_implied = self._odds_to_probability(dk_home_ml) if dk_home_ml else 0.5
            dk_away_implied = self._odds_to_probability(dk_away_ml) if dk_away_ml else 0.5
            true_home_implied = self._odds_to_probability(true_home_ml) if true_home_ml else 0.5
            true_away_implied = self._odds_to_probability(true_away_ml) if true_away_ml else 0.5
            
            # Calculate edges for each book
            dk_home_edge = home_prob - dk_home_implied
            dk_away_edge = away_prob - dk_away_implied
            true_home_edge = home_prob - true_home_implied
            true_away_edge = away_prob - true_away_implied
            
            # Find best available odds (highest edge)
            best_home_edge = max(dk_home_edge, true_home_edge)
            best_away_edge = max(dk_away_edge, true_away_edge)
            
            # Determine which book offers the best odds
            best_home_book = "DraftKings" if dk_home_edge >= true_home_edge else "True Line"
            best_away_book = "DraftKings" if dk_away_edge >= true_away_edge else "True Line"
            
            return {
                "game_id": game_id,
                "calculated_probabilities": probabilities,
                "market_odds": {
                    "draftkings": {
                        "home_implied_probability": dk_home_implied,
                        "away_implied_probability": dk_away_implied,
                        "home_moneyline": dk_home_ml,
                        "away_moneyline": dk_away_ml
                    },
                    "true_line": {
                        "home_implied_probability": true_home_implied,
                        "away_implied_probability": true_away_implied,
                        "home_moneyline": true_home_ml,
                        "away_moneyline": true_away_ml
                    }
                },
                "best_odds": {
                    "home": {
                        "book": best_home_book,
                        "edge": best_home_edge,
                        "odds": dk_home_ml if best_home_book == "DraftKings" else true_home_ml
                    },
                    "away": {
                        "book": best_away_book,
                        "edge": best_away_edge,
                        "odds": dk_away_ml if best_away_book == "DraftKings" else true_away_ml
                    }
                },
                "home_edge": best_home_edge,
                "away_edge": best_away_edge
            }
        except Exception as e:
            self.logger.error(f"Error comparing to market odds: {str(e)}")
            # Return fallback data
            market_odds = {
                "home_implied_probability": 0.52,
                "away_implied_probability": 0.48
            }
            
            home_edge = probabilities.get("home_win_probability", 0.5) - market_odds["home_implied_probability"]
            away_edge = probabilities.get("away_win_probability", 0.5) - market_odds["away_implied_probability"]
            
            return {
                "game_id": game_id,
                "calculated_probabilities": probabilities,
                "market_odds": market_odds,
                "home_edge": home_edge,
                "away_edge": away_edge,
                "best_odds": {}
            }
    
    def calculate_expected_value(self, market_comparison: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate expected value of potential bets"""
        # Get the edges from the market comparison
        home_edge = market_comparison.get("home_edge", 0)
        away_edge = market_comparison.get("away_edge", 0)
        
        # Calculate expected value as a percentage
        home_ev = home_edge * 100  # Simple EV in percentage points
        away_ev = away_edge * 100
        
        # Get the best odds for Kelly calculation
        best_home_odds = market_comparison.get("best_odds", {}).get("home", {}).get("odds")
        best_away_odds = market_comparison.get("best_odds", {}).get("away", {}).get("odds")
        
        # Get implied probabilities for Kelly calculation
        if "draftkings" in market_comparison.get("market_odds", {}):
            home_implied_prob = market_comparison["market_odds"]["draftkings"].get("home_implied_probability", 0.5)
            away_implied_prob = market_comparison["market_odds"]["draftkings"].get("away_implied_probability", 0.5)
        else:
            # Fallback to simple market odds if detailed structure not available
            home_implied_prob = market_comparison.get("market_odds", {}).get("home_implied_probability", 0.5)
            away_implied_prob = market_comparison.get("market_odds", {}).get("away_implied_probability", 0.5)
        
        # Determine optimal bet size using Kelly criterion
        home_kelly = max(0, home_edge / (1/home_implied_prob - 1)) if home_implied_prob > 0 else 0
        away_kelly = max(0, away_edge / (1/away_implied_prob - 1)) if away_implied_prob > 0 else 0
        
        # Include the best book information in the result
        best_home_book = market_comparison.get("best_odds", {}).get("home", {}).get("book", "Unknown")
        best_away_book = market_comparison.get("best_odds", {}).get("away", {}).get("book", "Unknown")
        
        return {
            "game_id": market_comparison["game_id"],
            "home_expected_value": home_ev,
            "away_expected_value": away_ev,
            "home_kelly": home_kelly,
            "away_kelly": away_kelly,
            "best_home_book": best_home_book,
            "best_away_book": best_away_book,
            "best_home_odds": best_home_odds,
            "best_away_odds": best_away_odds
        }
    
    def make_betting_decision(self, ev_calculation: Dict[str, Any]) -> Dict[str, Any]:
        """Make final betting decision based on expected value"""
        min_ev_threshold = self.config.get("betting", {}).get("min_ev_threshold", 2.0)
        
        # Determine if either bet meets our threshold
        home_ev = ev_calculation["home_expected_value"]
        away_ev = ev_calculation["away_expected_value"]
        
        if home_ev > away_ev and home_ev > min_ev_threshold:
            should_bet = True
            team = "home"
            ev = home_ev
            kelly = ev_calculation["home_kelly"]
            book = ev_calculation.get("best_home_book", "Unknown")
            odds = ev_calculation.get("best_home_odds")
            reasoning = f"Home team has {home_ev:.2f}% edge, which exceeds our {min_ev_threshold}% threshold. Best odds at {book}."
        elif away_ev > home_ev and away_ev > min_ev_threshold:
            should_bet = True
            team = "away"
            ev = away_ev
            kelly = ev_calculation["away_kelly"]
            book = ev_calculation.get("best_away_book", "Unknown")
            odds = ev_calculation.get("best_away_odds")
            reasoning = f"Away team has {away_ev:.2f}% edge, which exceeds our {min_ev_threshold}% threshold. Best odds at {book}."
        else:
            should_bet = False
            team = None
            ev = max(home_ev, away_ev)
            kelly = 0
            book = None
            odds = None
            reasoning = f"No bet has sufficient edge. Best option is {max(home_ev, away_ev):.2f}%, below our {min_ev_threshold}% threshold"
        
        # Apply bankroll management
        max_kelly_fraction = self.config.get("betting", {}).get("max_kelly_fraction", 0.5)
        bankroll = self.config.get("betting", {}).get("bankroll", 1000)
        
        if should_bet:
            bet_size = min(kelly, max_kelly_fraction) * bankroll
            # Ensure bet size is within limits
            min_bet = self.config.get("betting", {}).get("min_bet", 10)
            max_bet = self.config.get("betting", {}).get("max_bet", 100)
            bet_size = max(min_bet, min(bet_size, max_bet))
        else:
            bet_size = 0
        
        # Create the decision dictionary
        decision = {
            "game_id": ev_calculation["game_id"],
            "should_bet": should_bet,
            "team": team,
            "expected_value": ev,
            "bet_size": bet_size,
            "reasoning": reasoning,
            "confidence": 0.7 if should_bet else 0.5,  # Placeholder
            "summary": f"{'Bet' if should_bet else 'Skip'} with EV: {ev:.2f}%, size: ${bet_size:.2f}",
            "book": book,
            "odds": odds
        }
        
        # Format the decision in Billy's style and log it
        formatted_decision = self.format_betting_decision(decision)
        self.logger.info(f"Betting decision: {formatted_decision}")
        
        return decision
    
    def _calculate_overall_confidence(self, betting_decisions: List[Dict[str, Any]]) -> float:
        """Calculate overall confidence across all betting decisions"""
        if not betting_decisions:
            return 0.0
            
        total_confidence = sum(decision.get("confidence", 0) for decision in betting_decisions)
        return total_confidence / len(betting_decisions)
    
    def _calculate_overall_ev(self, betting_decisions: List[Dict[str, Any]]) -> float:
        """Calculate overall expected value across all betting decisions"""
        if not betting_decisions:
            return 0.0
            
        total_ev = sum(decision.get("expected_value", 0) for decision in betting_decisions)
        return total_ev / len(betting_decisions)
    
    def _odds_to_probability(self, odds: float) -> float:
        """
        Convert moneyline odds to implied probability.
        
        Args:
            odds: Moneyline odds
            
        Returns:
            Implied probability (0-1)
        """
        if not odds:
            return 0.5
            
        if odds > 0:  # Positive odds (e.g., +150)
            return 100 / (odds + 100)
        else:  # Negative odds (e.g., -150)
            return abs(odds) / (abs(odds) + 100)
    
    # Legacy method for backward compatibility
    def run(self) -> Dict[str, Any]:
        """
        Run the reasoning module (legacy method).
        
        Returns:
            Dictionary containing reasoning results
        """
        self.logger.info("Running reasoning module (legacy method)")
        
        # Retrieve research data from memory
        research_data = self.memory.search({
            "query": "recent NBA research data",
            "metadata_filter": {"type": "game_research"},
            "limit": 20
        })
        
        # Execute reasoning tasks
        results = self.execute_reasoning_tasks(research_data)
        
        # Format for backward compatibility
        legacy_results = {
            "betting_recommendations": results.get("actionable_bets", []),
            "analysis_summary": results.get("summary", ""),
            "timestamp": results.get("timestamp", datetime.now().isoformat())
        }
        
        return legacy_results 