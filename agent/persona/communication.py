"""
Communication module for the NBA Betting Agent.

This module handles formatting messages according to Billy's persona
for different communication contexts.
"""

import logging
from typing import Dict, Any, List, Optional

from agent.persona.billy import BillyPersona

logger = logging.getLogger(__name__)

class CommunicationManager:
    """
    Manager for agent communications using Billy's persona.
    
    This class handles formatting messages for different contexts
    and ensures consistent communication style.
    """
    
    def __init__(self):
        """Initialize the communication manager"""
        self.persona = BillyPersona()
        logger.info("Communication Manager initialized")
    
    def format_betting_opportunity(self, opportunity: Dict[str, Any]) -> str:
        """
        Format a betting opportunity message.
        
        Args:
            opportunity: Dictionary containing betting opportunity data
            
        Returns:
            Formatted message
        """
        return self.persona.format_betting_opportunity(opportunity)
    
    def format_wallet_status(self, wallet_info: Dict[str, Any]) -> str:
        """
        Format wallet status information.
        
        Args:
            wallet_info: Dictionary containing wallet information
            
        Returns:
            Formatted message
        """
        return self.persona.format_wallet_status(wallet_info)
    
    def format_research_results(self, research_data: Dict[str, Any]) -> str:
        """
        Format research results.
        
        Args:
            research_data: Dictionary containing research data
            
        Returns:
            Formatted message
        """
        return self.persona.format_research_results(research_data)
    
    def format_error_message(self, error: str) -> str:
        """
        Format an error message.
        
        Args:
            error: Error message
            
        Returns:
            Formatted message
        """
        return self.persona.format_error_message(error)
    
    def format_daily_summary(self) -> str:
        """
        Format a daily summary message.
        
        Returns:
            Formatted message
        """
        return self.persona.create_daily_summary()
    
    def format_message(self, message: str, context: str = "") -> str:
        """
        Format a generic message based on context.
        
        Args:
            message: Message to format
            context: Context of the message
            
        Returns:
            Formatted message
        """
        style = self.persona.get_response_style(context)
        return self.persona.format_message(message, style)
    
    def format_betting_advice(self, advice: Dict[str, Any]) -> str:
        """
        Format betting advice.
        
        Args:
            advice: Dictionary containing betting advice
            
        Returns:
            Formatted message
        """
        # For betting advice, we prioritize accuracy over humor
        team = advice.get("team", "")
        expected_value = advice.get("expected_value", 0)
        confidence = advice.get("confidence", 0)
        odds = advice.get("odds", 0)
        book = advice.get("book", "")
        
        message = f"Betting Advice: {team} at {odds} odds ({book})"
        message += f"\nExpected Value: {expected_value:.2f}%"
        message += f"\nConfidence: {confidence:.2f}"
        
        # This is one case where we don't use Billy's lowercase style
        return message
    
    def format_opportunity_summary(self, opportunities: List[Dict[str, Any]]) -> str:
        """
        Format a summary of betting opportunities.
        
        Args:
            opportunities: List of betting opportunities
            
        Returns:
            Formatted message
        """
        count = len(opportunities)
        
        if count == 0:
            base_message = "no actionable edges found today. sometimes the best bet is no bet."
        elif count == 1:
            base_message = "found 1 actionable edge today. quality over quantity."
        else:
            base_message = f"found {count} actionable edges today. time to feast."
        
        return self.persona.format_message(base_message)
    
    def format_notification(self, notification_type: str, data: Dict[str, Any]) -> str:
        """
        Format a notification message.
        
        Args:
            notification_type: Type of notification
            data: Dictionary containing notification data
            
        Returns:
            Formatted message
        """
        if notification_type == "new_opportunity":
            return self.format_betting_opportunity(data)
        elif notification_type == "wallet_update":
            return self.format_wallet_status(data)
        elif notification_type == "research_complete":
            return self.format_research_results(data)
        elif notification_type == "error":
            return self.format_error_message(data.get("message", "unknown error"))
        elif notification_type == "daily_summary":
            return self.format_daily_summary()
        else:
            # Generic notification
            message = data.get("message", "")
            return self.format_message(message) 