#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Risk Management module for the NBA Betting Agent.

This module is responsible for enforcing betting limits, loss limits,
and other risk management controls to ensure responsible betting behavior.
"""

import logging
from typing import Dict, List, Any
from datetime import datetime, timedelta

from agent.persona.communication import CommunicationManager
from agent.utils.response_formatter import BillyResponseFormatter

class RiskManagementModule:
    """Module for managing betting risk and enforcing safety limits"""
    
    def __init__(self, memory_client, config):
        """
        Initialize the risk management module.
        
        Args:
            memory_client: Client for accessing the memory system
            config: Configuration settings
        """
        self.memory = memory_client
        self.config = config
        self.logger = logging.getLogger("nba_agent.risk_management")
        
        # Initialize communication manager for Billy's persona
        self.comm_manager = CommunicationManager()
        
        # Store reference to controller for accessing persona
        self.controller = None
        
        # Extract risk management settings from config
        self.betting_config = config.get("betting", {})
        self.bankroll = self.betting_config.get("bankroll", 1000)
        self.min_bet = self.betting_config.get("min_bet", 10)
        self.max_bet = self.betting_config.get("max_bet", 100)
        self.min_ev_threshold = self.betting_config.get("min_ev_threshold", 2.0)
        self.max_kelly_fraction = self.betting_config.get("max_kelly_fraction", 0.25)
        self.daily_loss_limit = self.betting_config.get("daily_loss_limit", 100)
        self.daily_bet_limit = self.betting_config.get("daily_bet_limit", 5)
        
        self.logger.info("Risk Management module initialized")
        self.logger.info(f"Bankroll: ${self.bankroll}, Daily loss limit: ${self.daily_loss_limit}")
    
    def set_controller(self, controller):
        """
        Set the controller reference for accessing persona.
        
        Args:
            controller: The agent controller instance
        """
        self.controller = controller
    
    def format_risk_assessment(self, decision: Dict[str, Any]) -> str:
        """
        Format a risk assessment in Billy's style.
        
        Args:
            decision: The betting decision with risk assessment
            
        Returns:
            Formatted risk assessment
        """
        if self.controller and hasattr(self.controller, 'persona'):
            formatter = BillyResponseFormatter(self.controller.persona)
            
            team = decision.get("team", "unknown")
            should_bet = decision.get("should_bet", False)
            
            if should_bet:
                # Format approved bet
                original_size = decision.get("original_bet_size", 0)
                adjusted_size = decision.get("bet_size", 0)
                
                if original_size != adjusted_size:
                    message = f"adjusted bet size on {team} from ${original_size:.2f} to ${adjusted_size:.2f}. risk management 101."
                else:
                    message = f"approved ${adjusted_size:.2f} bet on {team}. risk parameters satisfied."
            else:
                # Format rejected bet
                risk_note = decision.get("risk_management_note", "Failed risk assessment")
                message = f"rejected bet on {team}. {risk_note}. discipline keeps the bankroll growing."
            
            return formatter.format_generic_message(message, "risk_management")
        else:
            # Fallback if controller or persona not available
            if decision.get("should_bet", False):
                return f"Bet on {decision.get('team', 'unknown')} approved with size ${decision.get('bet_size', 0):.2f}"
            else:
                return f"Bet on {decision.get('team', 'unknown')} rejected: {decision.get('risk_management_note', 'Failed risk assessment')}"
    
    def validate_betting_decision(self, decision: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate a betting decision against risk management rules.
        
        Args:
            decision: The betting decision to validate
            
        Returns:
            Updated decision with risk management applied
        """
        game_id = decision.get('game_id', 'unknown')
        team = decision.get('team', 'unknown')
        self.logger.info(f"Validating betting decision for game {game_id}")
        
        # Start with the original decision
        validated_decision = decision.copy()
        
        # Check if we should bet at all
        if not decision.get("should_bet", False):
            return validated_decision
        
        # Store original bet size for reference
        validated_decision["original_bet_size"] = decision.get("bet_size", 0)
        
        # Check expected value threshold
        expected_value = decision.get("expected_value", 0)
        if expected_value < self.min_ev_threshold:
            validated_decision["should_bet"] = False
            validated_decision["risk_management_note"] = f"Expected value {expected_value:.2f}% below threshold {self.min_ev_threshold}%"
            
            # Format message using Billy's persona
            message = self.comm_manager.format_message(
                f"rejecting bet on {team} - {expected_value:.2f}% edge below my {self.min_ev_threshold}% threshold. standards matter."
            )
            self.logger.info(message)
            return validated_decision
        
        # Check bet size limits
        original_bet_size = decision.get("bet_size", 0)
        adjusted_bet_size = max(self.min_bet, min(original_bet_size, self.max_bet))
        
        if adjusted_bet_size != original_bet_size:
            validated_decision["bet_size"] = adjusted_bet_size
            validated_decision["risk_management_note"] = f"Bet size adjusted from ${original_bet_size:.2f} to ${adjusted_bet_size:.2f}"
            
            # Format message using Billy's persona
            message = self.comm_manager.format_message(
                f"adjusting bet size on {team} from ${original_bet_size:.2f} to ${adjusted_bet_size:.2f}. risk management 101."
            )
            self.logger.info(message)
        
        # Check daily betting limits
        if not self._check_daily_bet_limit():
            validated_decision["should_bet"] = False
            validated_decision["risk_management_note"] = f"Daily bet limit of {self.daily_bet_limit} reached"
            
            # Format message using Billy's persona
            message = self.comm_manager.format_message(
                f"hit daily bet limit of {self.daily_bet_limit}. discipline keeps the bankroll growing."
            )
            self.logger.info(message)
            return validated_decision
        
        # Check daily loss limits
        if not self._check_daily_loss_limit():
            validated_decision["should_bet"] = False
            validated_decision["risk_management_note"] = f"Daily loss limit of ${self.daily_loss_limit} reached"
            
            # Format message using Billy's persona
            message = self.comm_manager.format_message(
                f"hit daily loss limit of ${self.daily_loss_limit}. taking a breather. back tomorrow to destroy the books."
            )
            self.logger.info(message)
            return validated_decision
        
        # Format risk assessment in Billy's style and log it
        formatted_assessment = self.format_risk_assessment(validated_decision)
        self.logger.info(formatted_assessment)
        
        return validated_decision
    
    def validate_betting_decisions(self, decisions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Validate multiple betting decisions against risk management rules.
        
        Args:
            decisions: List of betting decisions to validate
            
        Returns:
            List of updated decisions with risk management applied
        """
        validated_decisions = []
        
        # First pass: validate each decision individually
        for decision in decisions:
            validated_decision = self.validate_betting_decision(decision)
            validated_decisions.append(validated_decision)
        
        # Second pass: apply portfolio-level constraints
        validated_decisions = self._apply_portfolio_constraints(validated_decisions)
        
        return validated_decisions
    
    def _check_daily_bet_limit(self) -> bool:
        """
        Check if the daily bet limit has been reached.
        
        Returns:
            Boolean indicating if more bets can be placed today
        """
        today = datetime.now().date()
        today_start = datetime.combine(today, datetime.min.time()).isoformat()
        today_end = datetime.combine(today, datetime.max.time()).isoformat()
        
        # Query memory for bets placed today
        bets_today = self.memory.search({
            "query": "bets placed today",
            "metadata_filter": {
                "type": "bet_placed",
                "timestamp": {"$gte": today_start, "$lte": today_end}
            }
        })
        
        return len(bets_today) < self.daily_bet_limit
    
    def _check_daily_loss_limit(self) -> bool:
        """
        Check if the daily loss limit has been reached.
        
        Returns:
            Boolean indicating if more losses can be sustained today
        """
        today = datetime.now().date()
        today_start = datetime.combine(today, datetime.min.time()).isoformat()
        today_end = datetime.combine(today, datetime.max.time()).isoformat()
        
        # Query memory for bet results today
        bet_results = self.memory.search({
            "query": "bet results today",
            "metadata_filter": {
                "type": "bet_result",
                "timestamp": {"$gte": today_start, "$lte": today_end}
            }
        })
        
        # Calculate total losses today
        total_loss = 0
        for result in bet_results:
            metadata = result.get("metadata", {})
            if not metadata.get("won", False):
                total_loss += metadata.get("amount", 0)
        
        return total_loss < self.daily_loss_limit
    
    def _apply_portfolio_constraints(self, decisions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Apply portfolio-level constraints to a set of betting decisions.
        
        Args:
            decisions: List of betting decisions
            
        Returns:
            Updated list of decisions with portfolio constraints applied
        """
        # Filter to only include decisions that passed individual validation
        active_decisions = [d for d in decisions if d.get("should_bet", False)]
        
        if not active_decisions:
            return decisions
        
        # Calculate total bet amount
        total_bet_amount = sum(d.get("bet_size", 0) for d in active_decisions)
        
        # Check if total exceeds daily limit
        max_daily_bet_amount = self.bankroll * 0.1  # 10% of bankroll per day
        
        if total_bet_amount > max_daily_bet_amount:
            # Scale down all bets proportionally
            scaling_factor = max_daily_bet_amount / total_bet_amount
            
            for decision in active_decisions:
                original_size = decision.get("bet_size", 0)
                adjusted_size = original_size * scaling_factor
                decision["bet_size"] = adjusted_size
                decision["risk_management_note"] = f"Bet size scaled down from ${original_size:.2f} to ${adjusted_size:.2f} due to portfolio constraints"
                self.logger.info(f"Portfolio adjustment: Bet size scaled to ${adjusted_size:.2f}")
        
        # Update the original decisions list
        for i, decision in enumerate(decisions):
            if decision.get("should_bet", False):
                # Find the corresponding updated decision
                for updated in active_decisions:
                    if updated.get("game_id") == decision.get("game_id") and updated.get("team") == decision.get("team"):
                        decisions[i] = updated
                        break
        
        return decisions
    
    def update_bankroll(self, amount: float, is_win: bool) -> None:
        """
        Update the bankroll based on bet results.
        
        Args:
            amount: Amount won or lost
            is_win: Whether the bet was won
        """
        if is_win:
            self.bankroll += amount
            self.logger.info(f"Bankroll increased by ${amount:.2f} to ${self.bankroll:.2f}")
        else:
            self.bankroll -= amount
            self.logger.info(f"Bankroll decreased by ${amount:.2f} to ${self.bankroll:.2f}")
        
        # Update bankroll in config
        self.betting_config["bankroll"] = self.bankroll
        
        # Create wallet info for formatting
        wallet_info = {
            "balance_usdc": self.bankroll,
            "change": amount if is_win else -amount,
            "is_win": is_win
        }
        
        # Format message using Billy's persona
        content = self.comm_manager.format_wallet_status(wallet_info)
        
        # Store bankroll update in memory
        self.memory.add({
            "content": content,
            "metadata": {
                "type": "bankroll_update",
                "previous_value": self.bankroll - (amount if is_win else -amount),
                "new_value": self.bankroll,
                "change": amount if is_win else -amount,
                "timestamp": datetime.now().isoformat(),
                "persona": "billy"
            }
        })
    
    def get_risk_metrics(self) -> Dict[str, Any]:
        """
        Get current risk management metrics.
        
        Returns:
            Dictionary containing risk metrics
        """
        # Calculate metrics
        today = datetime.now().date()
        today_start = datetime.combine(today, datetime.min.time()).isoformat()
        today_end = datetime.combine(today, datetime.max.time()).isoformat()
        
        # Query memory for bets placed today
        bets_today = self.memory.search({
            "query": "bets placed today",
            "metadata_filter": {
                "type": "bet_placed",
                "timestamp": {"$gte": today_start, "$lte": today_end}
            }
        })
        
        # Query memory for bet results today
        bet_results = self.memory.search({
            "query": "bet results today",
            "metadata_filter": {
                "type": "bet_result",
                "timestamp": {"$gte": today_start, "$lte": today_end}
            }
        })
        
        # Calculate metrics
        total_bets_today = len(bets_today)
        total_bet_amount_today = sum(b.get("metadata", {}).get("amount", 0) for b in bets_today)
        
        wins_today = sum(1 for r in bet_results if r.get("metadata", {}).get("won", False))
        losses_today = sum(1 for r in bet_results if not r.get("metadata", {}).get("won", False))
        
        total_won_today = sum(r.get("metadata", {}).get("amount", 0) for r in bet_results if r.get("metadata", {}).get("won", False))
        total_lost_today = sum(r.get("metadata", {}).get("amount", 0) for r in bet_results if not r.get("metadata", {}).get("won", False))
        
        # Calculate remaining limits
        remaining_bet_limit = self.daily_bet_limit - total_bets_today
        remaining_loss_limit = self.daily_loss_limit - total_lost_today
        
        return {
            "bankroll": self.bankroll,
            "daily_metrics": {
                "bets_placed": total_bets_today,
                "total_bet_amount": total_bet_amount_today,
                "wins": wins_today,
                "losses": losses_today,
                "amount_won": total_won_today,
                "amount_lost": total_lost_today,
                "net_profit": total_won_today - total_lost_today
            },
            "limits": {
                "min_bet": self.min_bet,
                "max_bet": self.max_bet,
                "daily_bet_limit": self.daily_bet_limit,
                "daily_loss_limit": self.daily_loss_limit,
                "remaining_bet_limit": remaining_bet_limit,
                "remaining_loss_limit": remaining_loss_limit
            },
            "thresholds": {
                "min_ev_threshold": self.min_ev_threshold,
                "max_kelly_fraction": self.max_kelly_fraction
            },
            "timestamp": datetime.now().isoformat()
        } 