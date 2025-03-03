#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Wake Up Module for the NBA Betting Agent.

This module implements the "wake up" functionality that integrates SportsTensor
predictions with Polymarket odds to identify initial betting edges.
"""

import logging
import time
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta

from agent.api.sportstensor_client import SportsTensorClient
from agent.api.polymarket_client import PolymarketClient
from agent.memory.short_term import ShortTermMemory
from agent.utils.wallet_utils import WalletManager
from agent.persona.communication import CommunicationManager

logger = logging.getLogger(__name__)

class WakeUpModule:
    """
    Wake Up Module for the NBA Betting Agent.
    
    This module identifies initial betting edges by comparing SportsTensor
    model predictions with Polymarket odds.
    """
    
    def __init__(self, memory, config: Dict[str, Any]):
        """
        Initialize the Wake Up Module.
        
        Args:
            memory: Memory client for storing and retrieving information
            config: Configuration dictionary
        """
        self.memory = memory
        self.config = config
        self.short_term = ShortTermMemory()
        
        # Initialize API clients
        self.sportstensor_client = SportsTensorClient(
            api_key=config.get("sportstensor", {}).get("api_key", ""),
            base_url=config.get("sportstensor", {}).get("base_url", "https://mm-api.sportstensor.com")
        )
        
        self.polymarket_client = PolymarketClient(
            api_key=config.get("polymarket", {}).get("api_key"),
            base_url=config.get("polymarket", {}).get("base_url", "https://gamma-api.polymarket.com")
        )
        
        # Initialize wallet manager
        self.wallet_manager = WalletManager(config)
        
        # Initialize communication manager
        self.comm_manager = CommunicationManager()
        
        # Edge threshold for identifying opportunities
        self.edge_threshold = config.get("risk_management", {}).get("min_edge_threshold", 0.05)
        
        logger.info("Wake Up Module initialized")
    
    def check_wallet_balance(self) -> Dict[str, Any]:
        """
        Check wallet balance to ensure sufficient funds for betting.
        
        Returns:
            Dictionary containing wallet status information
        """
        logger.info("Checking wallet balance")
        
        # Get wallet information
        wallet_info = self.wallet_manager.get_wallet_info()
        
        # Check if balance is sufficient
        min_balance = self.config.get("wallet", {}).get("min_balance_alert", 50)
        
        if wallet_info["status"] == "success":
            balance = wallet_info["balance_usdc"]
            is_sufficient = balance >= min_balance
            
            wallet_status = {
                "status": "success",
                "balance": balance,
                "is_sufficient": is_sufficient,
                "min_balance": min_balance,
                "address": wallet_info["address"],
                "network": wallet_info["network"]
            }
            
            if not is_sufficient:
                logger.warning(f"Wallet balance (${balance:.2f}) is below minimum threshold (${min_balance:.2f})")
                
                # Format message using Billy's persona
                message = self.comm_manager.format_wallet_status(wallet_info)
                
                # Store alert in memory
                self.memory.add({
                    "content": message,
                    "metadata": {
                        "type": "wallet_alert",
                        "balance": balance,
                        "min_balance": min_balance,
                        "timestamp": datetime.now().isoformat()
                    }
                })
            else:
                logger.info(f"Wallet balance is sufficient: ${balance:.2f}")
        else:
            wallet_status = {
                "status": "error",
                "error": wallet_info["error"],
                "is_sufficient": False
            }
            logger.error(f"Error checking wallet balance: {wallet_info['error']}")
        
        return wallet_status
    
    def scan_for_opportunities(self) -> List[Dict[str, Any]]:
        """
        Scan for betting opportunities by comparing model predictions with market odds.
        
        Returns:
            List of opportunities with edge information
        """
        logger.info("Scanning for betting opportunities")
        
        # Get SportsTensor predictions
        predictions = self.sportstensor_client.get_nba_predictions()
        logger.info(f"Retrieved {len(predictions)} predictions from SportsTensor")
        
        # Get Polymarket NBA markets
        markets = self.polymarket_client.get_nba_markets()
        logger.info(f"Retrieved {len(markets)} markets from Polymarket")
        
        # Match predictions with markets and calculate edges
        opportunities = self._calculate_edges(predictions, markets)
        
        # Filter opportunities by edge threshold
        filtered_opportunities = [
            opp for opp in opportunities 
            if opp.get("edge", 0) >= self.edge_threshold
        ]
        
        logger.info(f"Identified {len(filtered_opportunities)} opportunities with edge >= {self.edge_threshold}")
        
        # Store opportunities in memory
        self._store_opportunities(filtered_opportunities)
        
        return filtered_opportunities
    
    def _calculate_edges(self, predictions: List[Dict[str, Any]], 
                        markets: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Calculate edges between model predictions and market odds.
        
        Args:
            predictions: List of game predictions from SportsTensor
            markets: List of markets from Polymarket
            
        Returns:
            List of opportunities with edge calculations
        """
        opportunities = []
        
        for prediction in predictions:
            # Extract prediction details
            game_id = prediction.get("game_id")
            home_team = prediction.get("home_team")
            away_team = prediction.get("away_team")
            home_win_prob = prediction.get("home_win_probability")
            away_win_prob = prediction.get("away_win_probability")
            
            if not all([game_id, home_team, away_team, home_win_prob, away_win_prob]):
                logger.warning(f"Incomplete prediction data for game {game_id}")
                continue
            
            # Find matching market
            market = self._find_matching_market(home_team, away_team, markets)
            
            if not market:
                logger.warning(f"No matching market found for {away_team} @ {home_team}")
                continue
            
            # Get market odds
            market_id = market.get("id")
            market_odds = self.polymarket_client.get_market_odds(market_id)
            
            if not market_odds:
                logger.warning(f"No odds found for market {market_id}")
                continue
            
            # Calculate edges
            home_market_prob = market_odds.get(home_team, 0)
            away_market_prob = market_odds.get(away_team, 0)
            
            home_edge = home_win_prob - home_market_prob
            away_edge = away_win_prob - away_market_prob
            
            # Determine best opportunity
            if abs(home_edge) > abs(away_edge):
                edge = home_edge
                team = home_team
                model_prob = home_win_prob
                market_prob = home_market_prob
            else:
                edge = away_edge
                team = away_team
                model_prob = away_win_prob
                market_prob = away_market_prob
            
            # Create opportunity object
            opportunity = {
                "game_id": game_id,
                "home_team": home_team,
                "away_team": away_team,
                "team": team,
                "model_probability": model_prob,
                "market_probability": market_prob,
                "edge": edge,
                "market_id": market_id,
                "timestamp": datetime.now().isoformat(),
                "source": "wakeup_module"
            }
            
            opportunities.append(opportunity)
            
            # Format message using Billy's persona
            message = self.comm_manager.format_betting_opportunity(opportunity)
            logger.info(f"Found opportunity: {message}")
        
        return opportunities
    
    def _find_matching_market(self, home_team: str, away_team: str, 
                             markets: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """
        Find a matching market for the given teams.
        
        Args:
            home_team: Home team name
            away_team: Away team name
            markets: List of markets from Polymarket
            
        Returns:
            Matching market or None if not found
        """
        # Try to find by title first (most reliable)
        for market in markets:
            title = market.get("title", "")
            if home_team in title and away_team in title:
                return market
        
        # Try to find by slug
        slug = self.polymarket_client.construct_nba_slug(home_team, away_team)
        for market in markets:
            if market.get("slug") == slug:
                return market
        
        # Try to find by description
        for market in markets:
            description = market.get("description", "")
            if home_team in description and away_team in description:
                return market
        
        return None
    
    def _store_opportunities(self, opportunities: List[Dict[str, Any]]) -> None:
        """
        Store opportunities in memory for further processing.
        
        Args:
            opportunities: List of opportunities with edge calculations
        """
        if not opportunities:
            return
        
        # Store in short-term memory
        self.short_term.update_context("betting_opportunities", opportunities)
        
        # Format summary message using Billy's persona
        summary = self.comm_manager.format_opportunity_summary(opportunities)
        
        # Store summary in memory
        self.memory.add({
            "content": summary,
            "metadata": {
                "type": "opportunity_summary",
                "count": len(opportunities),
                "timestamp": datetime.now().isoformat()
            }
        })
        
        # Store each opportunity in memory
        for opportunity in opportunities:
            # Format message using Billy's persona
            message = self.comm_manager.format_betting_opportunity(opportunity)
            
            self.memory.add({
                "content": message,
                "metadata": {
                    "type": "betting_opportunity",
                    "game_id": opportunity["game_id"],
                    "home_team": opportunity["home_team"],
                    "away_team": opportunity["away_team"],
                    "team": opportunity["team"],
                    "edge": opportunity["edge"],
                    "timestamp": opportunity["timestamp"]
                }
            })
    
    def run(self) -> Dict[str, Any]:
        """
        Run the Wake Up Module.
        
        Returns:
            Dictionary containing the results of the wake-up scan
        """
        logger.info("Running Wake Up Module")
        
        try:
            # Create daily summary
            daily_summary = self.comm_manager.format_daily_summary()
            logger.info(f"Daily Summary: {daily_summary}")
            
            # Store daily summary in memory
            self.memory.add({
                "content": daily_summary,
                "metadata": {
                    "type": "daily_summary",
                    "timestamp": datetime.now().isoformat()
                }
            })
            
            # Check wallet balance first
            wallet_status = self.check_wallet_balance()
            
            # Only proceed with opportunity scanning if wallet balance is sufficient
            if wallet_status["status"] == "error" or not wallet_status["is_sufficient"]:
                error_message = "Insufficient wallet balance for betting operations"
                formatted_message = self.comm_manager.format_error_message(error_message)
                
                logger.warning(formatted_message)
                
                return {
                    "opportunities_found": 0,
                    "opportunities": [],
                    "wallet_status": wallet_status,
                    "timestamp": datetime.now().isoformat(),
                    "status": "warning",
                    "message": formatted_message
                }
            
            # Scan for opportunities
            opportunities = self.scan_for_opportunities()
            
            # Format research results message
            research_message = self.comm_manager.format_research_results(opportunities)
            
            # Prepare results
            results = {
                "opportunities_found": len(opportunities),
                "opportunities": opportunities,
                "wallet_status": wallet_status,
                "timestamp": datetime.now().isoformat(),
                "status": "success",
                "message": research_message
            }
            
            logger.info(f"Wake Up Module completed: {research_message}")
            return results
            
        except Exception as e:
            error_message = str(e)
            formatted_message = self.comm_manager.format_error_message(error_message)
            
            logger.error(f"Error in Wake Up Module: {error_message}", exc_info=True)
            
            return {
                "opportunities_found": 0,
                "opportunities": [],
                "wallet_status": {"status": "error", "error": error_message},
                "timestamp": datetime.now().isoformat(),
                "status": "error",
                "message": formatted_message,
                "error": error_message
            } 