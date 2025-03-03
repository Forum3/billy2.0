#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Base module for the NBA Betting Agent.

This module provides a base class for all agent modules.
"""

import logging
from typing import Dict, Any

class BaseModule:
    """Base class for all agent modules"""
    
    def __init__(self, memory, config: Dict[str, Any]):
        """
        Initialize the base module.
        
        Args:
            memory: Memory client for storing and retrieving information
            config: Configuration dictionary
        """
        self.memory = memory
        self.config = config
        self.logger = logging.getLogger(f"nba_agent.{self.__class__.__name__.lower()}")
        
    def run(self) -> Dict[str, Any]:
        """
        Run the module.
        
        This method should be implemented by subclasses.
        
        Returns:
            Dictionary containing the results of running the module
        """
        raise NotImplementedError("Subclasses must implement the run method") 