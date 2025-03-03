#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Response formatter for the NBA Betting Agent.

This module ensures all responses maintain Billy's distinctive style.
"""

import logging
import re
from typing import Dict, Any, List, Optional
from datetime import datetime

class BillyResponseFormatter:
    """Formats responses according to Billy's persona"""
    
    def __init__(self, persona):
        """
        Initialize the response formatter.
        
        Args:
            persona: Billy's persona object
        """
        self.persona = persona
        self.logger = logging.getLogger("nba_agent.formatter")
        self.logger.info("Response formatter initialized")
    
    def format_betting_advice(self, data: Dict[str, Any]) -> str:
        """
        Format betting advice in Billy's style.
        
        Args:
            data: Betting advice data
            
        Returns:
            Formatted betting advice
        """
        # For betting advice, we want accuracy over humor
        # and maintain proper formatting of odds and data
        
        game = data.get("game", "")
        bet_type = data.get("bet_type", "")
        odds = data.get("odds", "")
        analysis = data.get("analysis", "")
        
        response = f"Betting Advice: {game} {bet_type} {odds}\n\n{analysis}"
        
        # Use persona to format but specify betting_advice style
        return self.persona.format_message(response, "betting_advice")
    
    def format_market_data(self, data: Dict[str, Any]) -> str:
        """
        Format market data in a clean, factual way.
        
        Args:
            data: Market data
            
        Returns:
            Formatted market data
        """
        # For market data, we want clean presentation without humor
        
        formatted_lines = []
        
        # Format game header
        if "away_team" in data and "home_team" in data:
            formatted_lines.append(f"{data['away_team']} @ {data['home_team']}")
        
        # Format odds
        if "spread" in data:
            formatted_lines.append(f"Spread: {data['spread']}")
        if "total" in data:
            formatted_lines.append(f"Total: {data['total']}")
        if "moneyline" in data:
            formatted_lines.append(f"Moneyline: {data['moneyline']}")
        
        # Format other data
        if "start_time" in data:
            formatted_lines.append(f"Start Time: {data['start_time']}")
            
        response = "\n".join(formatted_lines)
        
        # Use persona to format but specify betting_advice style to keep it clean
        return self.persona.format_message(response, "betting_advice")
    
    def format_edge_analysis(self, data: Dict[str, Any]) -> str:
        """
        Format edge analysis with Billy's flair.
        
        Args:
            data: Edge analysis data
            
        Returns:
            Formatted edge analysis
        """
        game = f"{data.get('away_team', '')} @ {data.get('home_team', '')}"
        bet_team = data.get('bet_team', '')
        edge = data.get('edge', 0)
        
        # For edge analysis, we can add some Billy flair
        response = f"Found edge on {bet_team} with {edge:.2f}% value"
        
        if edge > 0.1:  # Strong edge
            response += f". books literally shaking watching this spot."
        elif edge > 0.05:  # Moderate edge
            response += f". solid spot that markets haven't figured out yet."
        
        # Use default style for more Billy personality
        return self.persona.format_message(response, "default")
    
    def format_research_summary(self, data: List[Dict[str, Any]]) -> str:
        """
        Format research summary with Billy's style.
        
        Args:
            data: Research summary data
            
        Returns:
            Formatted research summary
        """
        if not data:
            return self.persona.format_message("no edges found today. books getting lucky for once.")
        
        # Count how many edges found
        edge_count = len(data)
        
        # Select base message
        if edge_count > 3:
            base = f"found {edge_count} edges today. books about to get cooked."
        elif edge_count > 0:
            base = f"found {edge_count} solid spots for today. time to make the books pay."
        else:
            base = "markets looking efficient today. saving powder for tomorrow."
        
        # Use default style for Billy's personality
        return self.persona.format_message(base, "default")
    
    def format_error_message(self, error: str, context: str = "") -> str:
        """
        Format error messages with Billy's style.
        
        Args:
            error: Error message
            context: Optional context about the error
            
        Returns:
            Formatted error message
        """
        # Base error message
        base_message = "hit a small glitch in the matrix."
        
        # Add context if provided
        if context:
            base_message += f" {context}."
        
        # Add Billy's flair based on error type
        if "connection" in error.lower() or "timeout" in error.lower():
            base_message += " books probably trying to block us. not happening."
        elif "api" in error.lower():
            base_message += " api acting up. temporary setback, we move."
        elif "memory" in error.lower():
            base_message += " memory hiccup. back to regularly scheduled profit shortly."
        else:
            base_message += " minor technical difficulty. back to regularly scheduled profit shortly."
        
        return self.persona.format_message(base_message)
    
    def format_bet_placement(self, bet_data: Dict[str, Any]) -> str:
        """
        Format bet placement confirmation with Billy's style.
        
        Args:
            bet_data: Bet placement data
            
        Returns:
            Formatted bet placement confirmation
        """
        team = bet_data.get("team", "")
        amount = bet_data.get("amount", 0)
        odds = bet_data.get("odds", "")
        book = bet_data.get("book", "")
        
        base_message = f"just placed ${amount:.2f} on {team} at {odds} odds"
        
        if book:
            base_message += f" with {book}"
        
        # Add Billy's flair
        if amount > 100:
            base_message += ". big bet energy. books about to feel the pain."
        elif amount > 50:
            base_message += ". solid position. books sweating."
        else:
            base_message += ". calculated play. slow build to generational wealth."
        
        return self.persona.format_message(base_message)
    
    def format_bet_outcome(self, outcome_data: Dict[str, Any]) -> str:
        """
        Format bet outcome with Billy's style.
        
        Args:
            outcome_data: Bet outcome data
            
        Returns:
            Formatted bet outcome
        """
        team = outcome_data.get("team", "")
        amount = outcome_data.get("amount", 0)
        profit = outcome_data.get("profit", 0)
        won = outcome_data.get("won", False)
        
        if won:
            base_message = f"just cashed ${profit:.2f} on {team} bet"
            
            # Add Billy's flair for wins
            if profit > 200:
                base_message += ". massive win. books in absolute shambles."
            elif profit > 100:
                base_message += ". solid win. books crying."
            else:
                base_message += ". another day, another win. pure mathematics."
        else:
            base_message = f"took an L on {team} bet. ${amount:.2f} down"
            
            # Add Billy's flair for losses
            base_message += ". temporary setback. variance happens. back stronger tomorrow."
        
        return self.persona.format_message(base_message)
    
    def format_daily_metrics(self, metrics: Dict[str, Any]) -> str:
        """
        Format daily metrics with Billy's style.
        
        Args:
            metrics: Daily metrics data
            
        Returns:
            Formatted daily metrics
        """
        bankroll = metrics.get("bankroll", 0)
        daily_profit = metrics.get("daily_profit", 0)
        wins = metrics.get("wins", 0)
        losses = metrics.get("losses", 0)
        
        # Create base message with bankroll and profit
        base_message = f"current bankroll: ${bankroll:.2f}. "
        
        if daily_profit > 0:
            base_message += f"today's profit: +${daily_profit:.2f}. "
            
            # Add Billy's flair for profitable days
            if wins > 0 and losses == 0:
                base_message += f"perfect {wins}-0 day. books in absolute shambles."
            elif wins > losses:
                base_message += f"{wins}-{losses} record today. books feeling the pressure."
            else:
                base_message += f"grinding out profit despite variance. pure skill."
        else:
            base_message += f"today's p&l: ${daily_profit:.2f}. "
            
            # Add Billy's flair for losing days
            base_message += f"variance happens. back tomorrow to collect what's ours."
        
        return self.persona.format_message(base_message)
    
    def format_startup_message(self) -> str:
        """
        Format startup message with Billy's style.
        
        Returns:
            Formatted startup message
        """
        # Get current day number (arbitrary starting point)
        day_number = (datetime.now() - datetime(2023, 1, 1)).days
        
        startup_options = [
            f"day {day_number} of being an elite ai bettor: still more profitable than your stock broker.",
            "books hoping i take a day off. not happening.",
            f"another day of breaking offshore limits (day {day_number}).",
            "what's better than making books cry? doing it every single day."
        ]
        
        # Use random choice from persona's daily summary
        return self.persona.create_daily_summary()
    
    def format_generic_message(self, message: str, context: str = "") -> str:
        """
        Format a generic message with Billy's style.
        
        Args:
            message: Message to format
            context: Optional context for the message
            
        Returns:
            Formatted message
        """
        # Simply use persona's format_message method
        return self.persona.format_message(message, context) 