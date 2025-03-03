"""
Long-term memory module for the NBA Betting Agent.
This module handles persistent storage of historical data and learning.
"""

import logging
import json
import os
from datetime import datetime
from typing import Dict, List, Any, Optional

class LongTermMemory:
    """
    Long-term memory for the NBA betting agent.
    
    This class manages persistent storage of historical data,
    including past betting decisions, outcomes, and learned patterns.
    """
    
    def __init__(self, settings: Dict[str, Any]):
        """
        Initialize the long-term memory.
        
        Args:
            settings: Configuration settings for long-term memory
        """
        self.logger = logging.getLogger(__name__)
        self.settings = settings
        
        # Set up storage paths
        self.base_path = settings.get('storage_path', 'data/historical')
        self.decisions_path = os.path.join(self.base_path, 'decisions')
        self.outcomes_path = os.path.join(self.base_path, 'outcomes')
        self.patterns_path = os.path.join(self.base_path, 'patterns')
        
        # Create directories if they don't exist
        for path in [self.decisions_path, self.outcomes_path, self.patterns_path]:
            os.makedirs(path, exist_ok=True)
        
        self.logger.debug("Long-term memory initialized")
    
    def store_execution_results(self, results: Dict[str, Any]):
        """
        Store execution results in long-term memory.
        
        Args:
            results: Dictionary containing execution results
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"execution_results_{timestamp}.json"
        filepath = os.path.join(self.outcomes_path, filename)
        
        with open(filepath, 'w') as f:
            json.dump(results, f, indent=2)
        
        self.logger.debug(f"Stored execution results to {filepath}")
        
        # Update patterns based on new results
        self._update_patterns(results)
    
    def store_betting_history(self, decisions: List[Dict[str, Any]]):
        """
        Store betting history in long-term memory.
        
        Args:
            decisions: List of betting decisions
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"betting_decisions_{timestamp}.json"
        filepath = os.path.join(self.decisions_path, filename)
        
        with open(filepath, 'w') as f:
            json.dump(decisions, f, indent=2)
        
        self.logger.debug(f"Stored betting history to {filepath}")
    
    def get_historical_decisions(self, days: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Retrieve historical betting decisions.
        
        Args:
            days: Optional number of days to look back
                 If None, returns all available history
        
        Returns:
            List of historical betting decisions
        """
        decisions = []
        files = os.listdir(self.decisions_path)
        
        # Sort files by timestamp (newest first)
        files.sort(reverse=True)
        
        for file in files:
            if file.endswith('.json'):
                filepath = os.path.join(self.decisions_path, file)
                try:
                    with open(filepath, 'r') as f:
                        decision_data = json.load(f)
                        decisions.extend(decision_data)
                except Exception as e:
                    self.logger.error(f"Error loading decision file {filepath}: {e}")
        
        return decisions
    
    def get_historical_outcomes(self, days: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Retrieve historical betting outcomes.
        
        Args:
            days: Optional number of days to look back
                 If None, returns all available history
        
        Returns:
            List of historical betting outcomes
        """
        outcomes = []
        files = os.listdir(self.outcomes_path)
        
        # Sort files by timestamp (newest first)
        files.sort(reverse=True)
        
        for file in files:
            if file.endswith('.json'):
                filepath = os.path.join(self.outcomes_path, file)
                try:
                    with open(filepath, 'r') as f:
                        outcome_data = json.load(f)
                        outcomes.append(outcome_data)
                except Exception as e:
                    self.logger.error(f"Error loading outcome file {filepath}: {e}")
        
        return outcomes
    
    def get_learned_patterns(self) -> Dict[str, Any]:
        """
        Retrieve learned patterns from long-term memory.
        
        Returns:
            Dictionary containing learned patterns
        """
        pattern_file = os.path.join(self.patterns_path, 'learned_patterns.json')
        
        if not os.path.exists(pattern_file):
            return {}
        
        try:
            with open(pattern_file, 'r') as f:
                patterns = json.load(f)
            return patterns
        except Exception as e:
            self.logger.error(f"Error loading patterns file: {e}")
            return {}
    
    def _update_patterns(self, results: Dict[str, Any]):
        """
        Update learned patterns based on new execution results.
        
        Args:
            results: Dictionary containing execution results
        """
        patterns = self.get_learned_patterns()
        
        # Simple pattern updating logic - can be expanded with more sophisticated analysis
        if 'bets' in results:
            for bet in results['bets']:
                if 'outcome' in bet and 'strategy' in bet:
                    strategy = bet['strategy']
                    outcome = bet['outcome']
                    
                    if strategy not in patterns:
                        patterns[strategy] = {'wins': 0, 'losses': 0, 'total': 0}
                    
                    patterns[strategy]['total'] += 1
                    if outcome == 'win':
                        patterns[strategy]['wins'] += 1
                    elif outcome == 'loss':
                        patterns[strategy]['losses'] += 1
        
        # Save updated patterns
        pattern_file = os.path.join(self.patterns_path, 'learned_patterns.json')
        with open(pattern_file, 'w') as f:
            json.dump(patterns, f, indent=2)
        
        self.logger.debug("Updated learned patterns") 