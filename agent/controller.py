"""
Controller module for the NBA Betting Agent.
This module orchestrates the agent's operations and decision-making process.
"""

import os
import time
import logging
from enum import Enum, auto
from typing import Dict, Any, List
from datetime import datetime

from agent.modules.research import ResearchModule
from agent.modules.reasoning import ReasoningModule
from agent.modules.execution import ExecutionModule
from agent.modules.risk_management import RiskManagementModule
from agent.memory.mem0_client import Mem0Client
from agent.memory.mem0_official import Mem0OfficialClient
from agent.persona.communication import CommunicationManager
from agent.persona.billy import BillyPersona

class AgentState(Enum):
    INITIALIZING = auto()
    RESEARCHING = auto()
    REASONING = auto()
    RISK_ASSESSMENT = auto()
    EXECUTING = auto()
    IDLE = auto()
    ERROR = auto()

class AgentController:
    """
    Main controller for the NBA betting agent.
    
    This class orchestrates the agent's operations, including research,
    reasoning, and execution of betting strategies.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the agent controller.
        
        Args:
            config: Configuration settings for the agent
        """
        self.config = config
        self.logger = self._setup_logger()
        self.logger.info("Initializing NBA Betting Agent")
        
        # Initialize Mem0 client for memory management
        if config['mem0'].get('use_official_client', False):
            self.logger.info("Using official Mem0 client")
            try:
                self.memory = Mem0OfficialClient(
                    api_key=config['mem0']['api_key'],
                    agent_id=config['mem0']['agent_id'],
                    base_url=config['mem0'].get('base_url', "https://api.mem0.ai"),
                    cache_ttl=config['mem0'].get('cache_ttl', 300)
                )
            except Exception as e:
                self.logger.error(f"Failed to initialize official Mem0 client: {str(e)}")
                self.logger.info("Falling back to custom Mem0 client")
                self.memory = Mem0Client(
                    api_key=config['mem0']['api_key'],
                    agent_id=config['mem0']['agent_id'],
                    base_url=config['mem0'].get('base_url', "https://api.mem0.ai"),
                    cache_ttl=config['mem0'].get('cache_ttl', 300)
                )
        else:
            self.logger.info("Using custom Mem0 client")
            self.memory = Mem0Client(
                api_key=config["mem0"]["api_key"],
                agent_id=config["mem0"]["agent_id"],
                base_url=config['mem0'].get('base_url', "https://api.mem0.ai"),
                cache_ttl=config['mem0'].get('cache_ttl', 300)
            )
        
        # Initialize Billy's persona
        self.persona = BillyPersona()
        self.comm_manager = CommunicationManager()
        self.logger.info("Billy's persona loaded")
        
        # Store persona in memory
        self.memory.add({
            "content": "Billy's persona traits and style",
            "metadata": {
                "type": "persona_config",
                "traits": self.persona.traits,
                "style": self.persona.communication_style,
                "rules": self.persona.interaction_rules,
                "timestamp": datetime.now().isoformat()
            }
        })
        
        # Initialize modules
        self.research_module = ResearchModule(self.memory, config)
        self.reasoning_module = ReasoningModule(self.memory, config)
        self.risk_management_module = RiskManagementModule(self.memory, config)
        self.execution_module = ExecutionModule(self.memory, config)
        
        # Set controller reference in each module
        self.research_module.set_controller(self)
        self.reasoning_module.set_controller(self)
        self.risk_management_module.set_controller(self)
        self.execution_module.set_controller(self)
        
        # Set initial state
        self.state = AgentState.INITIALIZING
        self.current_tasks = []
        self.is_running = False
        
    def _setup_logger(self):
        """Set up and configure the logger."""
        logger = logging.getLogger("nba_agent")
        logger.setLevel(logging.INFO)
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        return logger
        
    def start(self):
        """Start the agent's main execution loop"""
        self.is_running = True
        self.state = AgentState.INITIALIZING
        
        try:
            # Initialize with base model predictions
            self._initialize()
            
            # Main agent loop
            while self.is_running:
                self._process_current_state()
                time.sleep(self.config["agent"]["loop_interval"])
                
        except Exception as e:
            self.logger.error(f"Error in agent execution: {str(e)}")
            self.state = AgentState.ERROR
            raise
        finally:
            self.logger.info("Agent execution stopped")
    
    def stop(self):
        """Stop the agent execution gracefully"""
        self.logger.info("Stopping agent execution")
        self.is_running = False
    
    def _initialize(self):
        """Initialize the agent with base model predictions and setup"""
        self.logger.info("Initializing agent with Billy's persona")
        
        # Create a Billy-style initialization message
        init_message = self.comm_manager.format_daily_summary()
        
        # Store initialization context in memory
        self.memory.add({
            "content": init_message,
            "metadata": {
                "type": "system_event",
                "event": "initialization",
                "timestamp": datetime.now().isoformat(),
                "persona": "billy"
            }
        })
        
        # Initialize research queue
        self.research_module.initialize_research_queue()
        
        self.state = AgentState.RESEARCHING
        self.logger.info(f"Agent initialized: {init_message}")
    
    def _process_current_state(self):
        """Process the current state of the agent"""
        if self.state == AgentState.RESEARCHING:
            self._handle_research_state()
        elif self.state == AgentState.REASONING:
            self._handle_reasoning_state()
        elif self.state == AgentState.RISK_ASSESSMENT:
            self._handle_risk_assessment_state()
        elif self.state == AgentState.EXECUTING:
            self._handle_execution_state()
        elif self.state == AgentState.IDLE:
            self._handle_idle_state()
        elif self.state == AgentState.ERROR:
            self._handle_error_state()
    
    def _handle_research_state(self):
        """Handle the research state"""
        self.logger.info("Performing research tasks")
        
        try:
            # Execute research tasks
            research_results = self.research_module.execute_research_tasks()
            
            # Format research results message
            research_message = self.comm_manager.format_research_results(research_results)
            self.logger.info(research_message)
            
            # Store research results in memory
            for result in research_results:
                self.memory.add({
                    "content": f"Research finding: {result['summary']}",
                    "metadata": {
                        "type": "research_result",
                        "source": result["source"],
                        "timestamp": result["timestamp"]
                    }
                })
            
            # Store summary in Billy's style
            self.memory.add({
                "content": research_message,
                "metadata": {
                    "type": "research_summary",
                    "count": len(research_results),
                    "timestamp": datetime.now().isoformat(),
                    "persona": "billy"
                }
            })
            
            # Transition to reasoning state
            self.state = AgentState.REASONING
            
        except Exception as e:
            error_message = str(e)
            formatted_error = self.comm_manager.format_error_message(error_message)
            self.logger.error(f"Error during research: {formatted_error}")
            self.state = AgentState.ERROR
    
    def _handle_reasoning_state(self):
        """Handle the reasoning state"""
        self.logger.info("Performing reasoning tasks")
        
        try:
            # Retrieve relevant research from memory
            research_data = self.memory.search({
                "query": "recent NBA team statistics and injury reports",
                "metadata_filter": {"type": "research_result"}
            })
            
            # Execute reasoning based on research data
            reasoning_results = self.reasoning_module.execute_reasoning_tasks(research_data)
            
            # Format reasoning results message
            opportunities_count = len(reasoning_results.get("actionable_bets", []))
            reasoning_message = self.comm_manager.format_opportunity_summary(
                reasoning_results.get("actionable_bets", [])
            )
            self.logger.info(reasoning_message)
            
            # Store reasoning results in memory
            self.memory.add({
                "content": reasoning_message,
                "metadata": {
                    "type": "reasoning_result",
                    "confidence": reasoning_results["confidence"],
                    "expected_value": reasoning_results["expected_value"],
                    "actionable_bets": opportunities_count,
                    "timestamp": datetime.now().isoformat(),
                    "persona": "billy"
                }
            })
            
            # Store each betting decision separately
            for decision in reasoning_results.get("actionable_bets", []):
                # Format decision in Billy's style
                decision_message = self.comm_manager.format_betting_opportunity({
                    "home_team": decision.get("home_team", ""),
                    "away_team": decision.get("away_team", ""),
                    "team": decision.get("team", ""),
                    "edge": decision.get("expected_value", 0) / 100,  # Convert to decimal
                    "model_probability": decision.get("confidence", 0),
                    "market_probability": 0  # Not available in this context
                })
                
                self.memory.add({
                    "content": decision_message,
                    "metadata": {
                        "type": "betting_decision",
                        "game_id": decision.get("game_id"),
                        "team": decision.get("team"),
                        "expected_value": decision.get("expected_value"),
                        "bet_size": decision.get("bet_size"),
                        "confidence": decision.get("confidence"),
                        "persona": "billy"
                    }
                })
            
            # Transition to risk assessment state if there are actionable bets
            if reasoning_results["actionable_bets"]:
                self.state = AgentState.RISK_ASSESSMENT
            else:
                self.state = AgentState.IDLE
                
        except Exception as e:
            error_message = str(e)
            formatted_error = self.comm_manager.format_error_message(error_message)
            self.logger.error(f"Error during reasoning: {formatted_error}")
            self.state = AgentState.ERROR
    
    def _handle_risk_assessment_state(self):
        """Handle the risk assessment state"""
        self.logger.info("Performing risk assessment")
        
        try:
            # Retrieve betting decisions from memory
            betting_decisions = self.memory.search({
                "query": "current betting decisions",
                "metadata_filter": {"type": "betting_decision"}
            })
            
            # Extract the actual decision objects
            decisions = []
            for item in betting_decisions:
                metadata = item.get("metadata", {})
                decisions.append({
                    "game_id": metadata.get("game_id"),
                    "team": metadata.get("team"),
                    "expected_value": metadata.get("expected_value"),
                    "bet_size": metadata.get("bet_size"),
                    "confidence": metadata.get("confidence"),
                    "should_bet": True,
                    "summary": item.get("content", "")
                })
            
            # Apply risk management rules
            validated_decisions = self.risk_management_module.validate_betting_decisions(decisions)
            
            # Store risk assessment results in memory
            for decision in validated_decisions:
                risk_note = decision.get("risk_management_note", "Passed risk assessment")
                
                # Format risk assessment message in Billy's style
                if decision.get("should_bet", False):
                    risk_message = self.comm_manager.format_message(
                        f"Bet on {decision.get('team')} passed risk assessment. " +
                        f"Adjusted size: ${decision.get('bet_size', 0):.2f}."
                    )
                else:
                    risk_message = self.comm_manager.format_message(
                        f"Bet on {decision.get('team')} rejected by risk management: {risk_note}"
                    )
                
                self.memory.add({
                    "content": risk_message,
                    "metadata": {
                        "type": "risk_assessment",
                        "game_id": decision.get("game_id"),
                        "team": decision.get("team"),
                        "should_bet": decision.get("should_bet", False),
                        "original_bet_size": decision.get("original_bet_size", decision.get("bet_size")),
                        "adjusted_bet_size": decision.get("bet_size"),
                        "timestamp": datetime.now().isoformat(),
                        "persona": "billy"
                    }
                })
            
            # Get risk metrics
            risk_metrics = self.risk_management_module.get_risk_metrics()
            
            # Format risk metrics message in Billy's style
            metrics_message = self.comm_manager.format_message(
                f"Bankroll: ${risk_metrics['bankroll']:.2f}. " +
                f"Daily bets: {risk_metrics['daily_metrics']['bets_placed']}/{risk_metrics['limits']['daily_bet_limit']}. " +
                f"Daily P&L: ${risk_metrics['daily_metrics'].get('net_profit', 0):.2f}."
            )
            
            # Store risk metrics in memory
            self.memory.add({
                "content": metrics_message,
                "metadata": {
                    "type": "risk_metrics",
                    "bankroll": risk_metrics["bankroll"],
                    "daily_metrics": risk_metrics["daily_metrics"],
                    "limits": risk_metrics["limits"],
                    "timestamp": datetime.now().isoformat(),
                    "persona": "billy"
                }
            })
            
            # Filter to only include decisions that passed risk assessment
            actionable_decisions = [d for d in validated_decisions if d.get("should_bet", False)]
            
            # Log summary in Billy's style
            summary_message = self.comm_manager.format_message(
                f"{len(actionable_decisions)} of {len(decisions)} bets passed risk assessment."
            )
            self.logger.info(summary_message)
            
            # Transition to execution state if there are still actionable bets
            if actionable_decisions:
                self.state = AgentState.EXECUTING
            else:
                self.logger.info(self.comm_manager.format_message("No bets passed risk assessment."))
                self.state = AgentState.IDLE
                
        except Exception as e:
            error_message = str(e)
            formatted_error = self.comm_manager.format_error_message(error_message)
            self.logger.error(f"Error during risk assessment: {formatted_error}")
            self.state = AgentState.ERROR
    
    def _handle_execution_state(self):
        """Handle the execution state"""
        self.logger.info("Performing execution tasks")
        
        try:
            # Retrieve betting decisions that passed risk assessment
            risk_assessments = self.memory.search({
                "query": "betting decisions that passed risk assessment",
                "metadata_filter": {
                    "type": "risk_assessment",
                    "should_bet": True
                }
            })
            
            # Extract game IDs and teams
            approved_bets = []
            for assessment in risk_assessments:
                metadata = assessment.get("metadata", {})
                game_id = metadata.get("game_id")
                team = metadata.get("team")
                
                # Find the original betting decision
                betting_decisions = self.memory.search({
                    "query": f"betting decision for game {game_id}",
                    "metadata_filter": {
                        "type": "betting_decision",
                        "game_id": game_id,
                        "team": team
                    },
                    "limit": 1
                })
                
                if betting_decisions:
                    decision_metadata = betting_decisions[0].get("metadata", {})
                    approved_bets.append({
                        "game_id": game_id,
                        "team": team,
                        "expected_value": decision_metadata.get("expected_value"),
                        "bet_size": metadata.get("adjusted_bet_size"),
                        "confidence": decision_metadata.get("confidence"),
                        "should_bet": True
                    })
            
            # Execute betting actions
            if approved_bets:
                execution_results = self.execution_module.execute_betting_actions(approved_bets)
                
                # Format execution results message in Billy's style
                execution_message = self.comm_manager.format_message(
                    f"Placed {execution_results['bets_placed']} bets totaling ${execution_results['total_amount']:.2f}. " +
                    f"Books about to feel the pain."
                )
                
                # Store execution results in memory
                self.memory.add({
                    "content": execution_message,
                    "metadata": {
                        "type": "execution_result",
                        "bets_placed": execution_results["bets_placed"],
                        "total_amount": execution_results["total_amount"],
                        "timestamp": datetime.now().isoformat(),
                        "persona": "billy"
                    }
                })
                
                # Log execution results
                self.logger.info(execution_message)
                
                # Update bankroll for each bet
                for bet in execution_results.get("bets", []):
                    # For now, we don't know the outcome, so we just record the bet
                    # The outcome will be updated later when we monitor results
                    self.risk_management_module.update_bankroll(
                        amount=bet.get("amount", 0),
                        is_win=False  # Initially record as a loss, will be updated when we know the outcome
                    )
            else:
                self.logger.info(self.comm_manager.format_message("No bets to execute. Books got lucky today."))
            
            # Transition to idle state
            self.state = AgentState.IDLE
            
        except Exception as e:
            error_message = str(e)
            formatted_error = self.comm_manager.format_error_message(error_message)
            self.logger.error(f"Error during execution: {formatted_error}")
            self.state = AgentState.ERROR
    
    def _handle_idle_state(self):
        """Handle the idle state"""
        self.logger.info(self.comm_manager.format_message("Agent in idle state, checking for new tasks"))
        
        # Check if it's time to research again
        current_time = time.time()
        last_research_time = self.research_module.get_last_research_time()
        
        if (current_time - last_research_time) > self.config["agent"]["research_interval"]:
            self.state = AgentState.RESEARCHING
            self.logger.info(self.comm_manager.format_message("Time for new research. Let's find some edges."))
        
        # Check for bet outcomes to monitor
        try:
            # Monitor bet outcomes
            self.execution_module.monitor_outcomes()
            
            # Get updated risk metrics
            risk_metrics = self.risk_management_module.get_risk_metrics()
            
            # Format metrics message in Billy's style
            metrics_message = self.comm_manager.format_message(
                f"Current bankroll: ${risk_metrics['bankroll']:.2f}. " +
                f"Today's P&L: ${risk_metrics['daily_metrics'].get('net_profit', 0):.2f}. " +
                f"Books in shambles."
            )
            
            # Log current bankroll and metrics
            self.logger.info(metrics_message)
            
        except Exception as e:
            error_message = str(e)
            formatted_error = self.comm_manager.format_error_message(error_message)
            self.logger.error(f"Error monitoring outcomes: {formatted_error}")
    
    def _handle_error_state(self):
        """Handle the error state"""
        error_message = self.comm_manager.format_error_message("Agent in error state, attempting recovery")
        self.logger.error(error_message)
        
        # Log error to memory
        self.memory.add({
            "content": error_message,
            "metadata": {
                "type": "system_event",
                "event": "error_recovery",
                "timestamp": datetime.now().isoformat(),
                "persona": "billy"
            }
        })
        
        # Simple recovery: reset to idle and try again later
        self.state = AgentState.IDLE
    
    def run(self):
        """
        Run the agent (legacy method for backward compatibility).
        
        This method starts the agent's execution loop.
        """
        self.logger.info("Starting agent using legacy run method")
        self.start()

    def format_response(self, message: str, context: str = "") -> str:
        """
        Format a response using Billy's persona.
        
        Args:
            message: The message to format
            context: Optional context for the message
            
        Returns:
            Formatted message in Billy's style
        """
        return self.comm_manager.format_message(message, context) 