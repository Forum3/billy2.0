#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
NBA Betting Agent main module.

This module implements the main agent loop and coordinates the various modules
for research, reasoning, and execution.
"""

import logging
import time
import sys
import os
from datetime import datetime

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import configuration
from config.settings import get_config

# Import modules
from agent.modules.research import ResearchModule
from agent.modules.reasoning import ReasoningModule
from agent.modules.execution import ExecutionModule

# Import memory clients
from agent.memory.mem0_client import Mem0Client
# Import the official client wrapper
from agent.memory.mem0_official import Mem0OfficialClient

class NBABettingAgent:
    """
    NBA Betting Agent main class.
    
    This class coordinates the research, reasoning, and execution modules
    to implement the full betting agent functionality.
    """
    
    def __init__(self, config_file=None):
        """
        Initialize the NBA Betting Agent.
        
        Args:
            config_file: Optional path to a configuration file
        """
        # Load configuration
        self.config = get_config()
        
        # Set up logging
        self._setup_logging()
        
        # Initialize memory client
        # Check if we should use the official client
        if self.config['mem0'].get('use_official_client', False):
            self.logger.info("Using official Mem0 client")
            try:
                self.memory = Mem0OfficialClient(
                    api_key=self.config['mem0']['api_key'],
                    agent_id=self.config['mem0']['agent_id'],
                    base_url=self.config['mem0']['base_url'],
                    cache_ttl=self.config['mem0'].get('cache_ttl', 300)
                )
            except Exception as e:
                self.logger.error(f"Failed to initialize official Mem0 client: {str(e)}")
                self.logger.info("Falling back to custom Mem0 client")
                self.memory = Mem0Client(
                    api_key=self.config['mem0']['api_key'],
                    agent_id=self.config['mem0']['agent_id'],
                    base_url=self.config['mem0']['base_url'],
                    cache_ttl=self.config['mem0'].get('cache_ttl', 300)
                )
        else:
            self.logger.info("Using custom Mem0 client")
            self.memory = Mem0Client(
                api_key=self.config['mem0']['api_key'],
                agent_id=self.config['mem0']['agent_id'],
                base_url=self.config['mem0']['base_url'],
                cache_ttl=self.config['mem0'].get('cache_ttl', 300)
            )
        
        # Initialize modules
        self.research_module = ResearchModule(self.memory, self.config)
        self.reasoning_module = ReasoningModule(self.memory, self.config)
        self.execution_module = ExecutionModule(self.memory, self.config)
        
        self.logger.info("NBA Betting Agent initialized")
    
    def _setup_logging(self):
        """Set up logging for the agent."""
        log_config = self.config['logging']
        
        # Create log directory if it doesn't exist
        log_dir = os.path.dirname(log_config['file'])
        if not os.path.exists(log_dir):
            os.makedirs(log_dir, exist_ok=True)
        
        # Configure logging
        logging.basicConfig(
            level=getattr(logging, log_config['level']),
            format=log_config['format'],
            handlers=[
                logging.FileHandler(log_config['file']),
                logging.StreamHandler()
            ]
        )
        
        self.logger = logging.getLogger("nba_agent")
    
    def run(self):
        """
        Run the main agent loop.
        
        This method implements the main loop of the agent, coordinating
        the research, reasoning, and execution modules.
        """
        self.logger.info("Starting NBA Betting Agent")
        
        try:
            # Initialize the last injury report time
            self.last_injury_report_time = time.time()
            
            while True:
                self.logger.info("Starting agent cycle")
                cycle_start = datetime.now()
                
                # Check if injury reports should be refreshed
                if self._should_refresh_injury_reports():
                    self.logger.info("Refreshing NBA injury reports")
                    try:
                        injury_data = self.research_module.fetch_injury_reports()
                        self.logger.info(f"Injury reports refreshed: data for {len(injury_data)} teams")
                        self.last_injury_report_time = time.time()
                    except Exception as e:
                        self.logger.error(f"Error refreshing injury reports: {str(e)}")
                
                # Check if research is needed
                if self._should_run_research():
                    self.logger.info("Running research module")
                    research_results = self.research_module.execute_research_tasks()
                    self.logger.info(f"Research completed: {len(research_results)} games researched")
                
                # Run reasoning on available research data
                self.logger.info("Running reasoning module")
                reasoning_results = self.reasoning_module.execute_reasoning_tasks()
                self.logger.info(f"Reasoning completed: {len(reasoning_results)} betting decisions made")
                
                # Execute betting decisions
                if reasoning_results:
                    self.logger.info("Running execution module")
                    execution_results = self.execution_module.execute_betting_actions(reasoning_results)
                    self.logger.info(f"Execution completed: {execution_results['bets_placed']} bets placed")
                
                # Monitor bet outcomes
                self.execution_module.monitor_outcomes()
                
                # Calculate cycle duration
                cycle_duration = (datetime.now() - cycle_start).total_seconds()
                self.logger.info(f"Agent cycle completed in {cycle_duration:.2f} seconds")
                
                # Sleep until next cycle
                sleep_time = max(1, self.config['agent']['loop_interval'] - cycle_duration)
                self.logger.info(f"Sleeping for {sleep_time:.2f} seconds")
                time.sleep(sleep_time)
                
        except KeyboardInterrupt:
            self.logger.info("Agent stopped by user")
        except Exception as e:
            self.logger.error(f"Error in agent loop: {str(e)}", exc_info=True)
            raise
    
    def _should_refresh_injury_reports(self):
        """
        Determine if injury reports should be refreshed in this cycle.
        
        Returns:
            Boolean indicating whether injury reports should be refreshed
        """
        # Skip if Firecrawl is not enabled
        if not self.config.get('firecrawl', {}).get('enabled', False):
            return False
            
        # Get the refresh interval from config (default to 2 hours)
        refresh_interval = self.config.get('firecrawl', {}).get('refresh_interval', 7200)
        
        # Calculate time since last refresh
        now = time.time()
        time_since_last = now - getattr(self, 'last_injury_report_time', 0)
        
        # Refresh if enough time has passed
        return time_since_last >= refresh_interval
    
    def _should_run_research(self):
        """
        Determine if research should be run in this cycle.
        
        Returns:
            Boolean indicating whether research should be run
        """
        # Get the last research time from memory
        last_research_time = self.research_module.get_last_research_time()
        
        # If no previous research, run it
        if not last_research_time:
            return True
        
        # Calculate time since last research
        now = datetime.now()
        last_time = datetime.fromisoformat(last_research_time)
        time_since_last = (now - last_time).total_seconds()
        
        # Run research if enough time has passed
        return time_since_last >= self.config['agent']['research_interval']

def main():
    """Main entry point for the NBA Betting Agent."""
    agent = NBABettingAgent()
    agent.run()

if __name__ == "__main__":
    main() 