"""
Short-term memory module for the NBA Betting Agent.
This module handles temporary storage of data during agent operation.
"""

import logging
from typing import Dict, List, Any, Optional

class ShortTermMemory:
    """
    Short-term memory for the NBA betting agent.
    
    This class manages temporary storage of data during the agent's
    operation cycle, including research results and betting decisions.
    """
    
    def __init__(self):
        """Initialize the short-term memory."""
        self.logger = logging.getLogger(__name__)
        self.research_results = {}
        self.betting_decisions = []
        self.current_context = {}
        self.logger.debug("Short-term memory initialized")
    
    def store_research_results(self, results: Dict[str, Any]):
        """
        Store research results in short-term memory.
        
        Args:
            results: Dictionary containing research results
        """
        self.research_results = results
        self.logger.debug(f"Stored research results: {len(results)} items")
    
    def get_research_results(self) -> Dict[str, Any]:
        """
        Retrieve research results from short-term memory.
        
        Returns:
            Dictionary containing research results
        """
        return self.research_results
    
    def store_betting_decisions(self, decisions: List[Dict[str, Any]]):
        """
        Store betting decisions in short-term memory.
        
        Args:
            decisions: List of betting decisions
        """
        self.betting_decisions = decisions
        self.logger.debug(f"Stored betting decisions: {len(decisions)} items")
    
    def get_betting_decisions(self) -> List[Dict[str, Any]]:
        """
        Retrieve betting decisions from short-term memory.
        
        Returns:
            List of betting decisions
        """
        return self.betting_decisions
    
    def update_context(self, key: str, value: Any):
        """
        Update the current context with a key-value pair.
        
        Args:
            key: Context key
            value: Context value
        """
        self.current_context[key] = value
        self.logger.debug(f"Updated context: {key}")
    
    def get_context(self, key: Optional[str] = None) -> Any:
        """
        Retrieve context information.
        
        Args:
            key: Optional key to retrieve specific context
                 If None, returns the entire context
        
        Returns:
            Context value or entire context dictionary
        """
        if key is not None:
            return self.current_context.get(key)
        return self.current_context
    
    def clear(self):
        """Clear all short-term memory."""
        self.research_results = {}
        self.betting_decisions = []
        self.current_context = {}
        self.logger.debug("Short-term memory cleared")
        
    def get_pending_games(self) -> List[Dict[str, Any]]:
        """
        Retrieve pending games that need research.
        
        Returns:
            List of pending games with their metadata
        """
        # In a real implementation, this would query a database or API
        # For now, we'll return games from the current context if available
        pending_games = self.current_context.get("pending_games", [])
        self.logger.debug(f"Retrieved {len(pending_games)} pending games")
        return pending_games
    
    def update_game_research_status(self, game_id: str, status: str, 
                                   timestamp: str, message: str):
        """
        Update the research status of a game.
        
        Args:
            game_id: Unique identifier for the game
            status: New research status (e.g., 'completed', 'failed')
            timestamp: ISO format timestamp of the update
            message: Status message
        """
        # Update the game status in the current context
        pending_games = self.current_context.get("pending_games", [])
        
        for game in pending_games:
            if game.get("metadata", {}).get("game_id") == game_id:
                game["metadata"]["research_status"] = status
                game["metadata"]["last_updated"] = timestamp
                game["metadata"]["status_message"] = message
                break
                
        # Update the context with the modified games list
        self.current_context["pending_games"] = pending_games
        self.logger.debug(f"Updated research status for game {game_id} to {status}") 