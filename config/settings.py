#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Configuration settings for the NBA Betting Agent.

This module provides functions to load and manage configuration settings
for the agent from various sources (environment variables, config files, etc.)
"""

import os
import json
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

# Default configuration
DEFAULT_CONFIG = {
    # Agent settings
    "agent": {
        "name": "NBA Betting Agent",
        "version": "0.1.0",
        "loop_interval": 60,  # seconds between main loop iterations
        "research_interval": 3600,  # seconds between research cycles
        "test_mode": True,  # Set to False for actual betting
    },
    
    # Memory settings (Mem0)
    "mem0": {
        "api_key": "m0-T4igXztudPWn8RgRATwUkxzpNKFBNIzuZUnAUUbW",  # Updated API key
        "agent_id": "nba_betting_agent",
        "base_url": "https://api.mem0.ai",
        "use_official_client": True,  # Flag to use the official Mem0 client
        "cache_ttl": 300  # Cache time-to-live in seconds (5 minutes)
    },
    
    # LLM settings
    "llm": {
        "provider": "anthropic",
        "api_key": "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",
        "model": "claude-3-7-sonnet-20250219",
        "temperature": 0.7,
        "max_tokens": 4096
    },
    
    # Persona settings
    "persona": {
        "name": "Billy",
        "style": "lowercase",
        "use_witty_responses": True,
        "profanity_level": "moderate",  # none, mild, moderate, heavy
        "fourth_wall_breaking": True,
        "confidence_level": "high"      # moderate, high, extreme
    },
    
    # Betting parameters
    "betting": {
        "bankroll": 1000,  # Starting bankroll in USD
        "min_bet": 10,  # Minimum bet amount
        "max_bet": 100,  # Maximum bet amount
        "min_ev_threshold": 2.0,  # Minimum expected value percentage to place a bet
        "max_kelly_fraction": 0.25,  # Conservative fraction of Kelly criterion
    },
    
    # Risk Management parameters
    "risk_management": {
        "daily_loss_limit": 100,  # Maximum allowed daily loss
        "daily_bet_limit": 5,  # Maximum number of bets per day
        "min_edge_threshold": 0.05,  # Minimum edge required (5%)
        "max_bet_size_pct": 0.02,  # Maximum bet size as percentage of bankroll
        "kelly_fraction": 0.5,  # Kelly criterion fraction (conservative)
        "bet_frequency_limit": 3,  # Maximum bets per hour
        "portfolio_concentration_limit": 0.3,  # Maximum exposure to a single team/market
        "required_confidence": 0.65,  # Minimum confidence level required
        "enable_bankroll_tracking": True,  # Track bankroll changes
        "enable_risk_limits": True,  # Enable risk management limits
    },
    
    # Betstamp API settings
    "betstamp": {
        "api_key": "7KQ6RWNVA8HAUS5TOW5EYN12GOR5BGRLNA06F5G9DDHN0A9RJBJ89GL8G1QF6DFV",  # Replace with actual API key
        "base_url": "https://api.pro.betstamp.com/api",
        "book_ids": [200, 999],  # Default book IDs to use (200 = Pinnacle, 999 = Consensus)
        "bet_types": ["moneyline", "spread", "total"],  # Default bet types to fetch
        "periods": ["FT"],  # Default periods to fetch (FT = full time)
        "timedelta": 24,  # Default hours window for games
    },
    
    # SportsTensor API settings
    "sportstensor": {
        "api_key": "hPW29W7OuyU3-qt5qdW6JIOi09PVB3THV7lSkwKhghQ",  # SportsTensor API key
        "base_url": "https://mm-api.sportstensor.com",
        "model_version": "v1.0",  # Model version to use
        "confidence_threshold": 0.6,  # Minimum confidence threshold for predictions
    },
    
    # Firecrawl settings
    "firecrawl": {
        "api_key": "fc-974d0c4fea5244eca58e9b81642fc722",
        "injury_sources": [
            "https://www.rotowire.com/basketball/nba-injuries.php",
            "https://www.cbssports.com/nba/injuries/",
            "https://www.espn.com/nba/injuries"
        ],
        "refresh_interval": 7200,  # seconds between injury report refreshes (2 hours)
        "enabled": True
    },
    
    # Anthropic API settings (for Claude - used with Firecrawl)
    "anthropic": {
        "api_key": "",  # Add your Anthropic API key here
        "enabled": False  # Will be set to True if API key is provided
    },
    
    # Polymarket API settings
    "polymarket": {
        "api_key": "your_polymarket_api_key_here",  # Replace with actual API key
        "base_url": "https://gamma-api.polymarket.com"
    },
    
    # Wallet settings
    "wallet": {
        "private_key": "",  # Set via environment variable PK for security
        "rpc_url": "https://polygon-rpc.com",  # Polygon RPC URL
        "usdc_address": "0x2791Bca1f2de4661ED88A30C99A7a9449Aa84174",  # USDC.e on Polygon
        "min_balance_alert": 50,  # Minimum balance to trigger alert (in USDC)
        "enable_auto_funding": False,  # Whether to enable auto-funding from a funding source
    },
    
    # Sports data API settings
    "sports_data": {
        "api_key": "your_sports_data_api_key_here",  # Replace with actual API key
        "base_url": "https://api.sportsdata.io/v3/nba"
    },
    
    # News API settings
    "news_api": {
        "api_key": "your_news_api_key_here",  # Replace with actual API key
        "base_url": "https://newsapi.org/v2"
    },
    
    # Logging settings
    "logging": {
        "level": "INFO",
        "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        "file": "logs/nba_agent.log"
    },
    
    # Legacy settings (for backward compatibility)
    "data_sources": {
        "nba_api": {
            "enabled": True,
            "rate_limit": 1.0  # requests per second
        },
        "odds_api": {
            "enabled": True,
            "api_key": "",
            "rate_limit": 1.0
        }
    },
    "min_edge_threshold": 0.05,  # 5% minimum edge
    "confidence_threshold": 0.65,  # 65% confidence
    "execution_mode": "manual",  # 'auto' or 'manual'
    "bankroll_fraction": 0.02,  # 2% of bankroll per bet
    "preferred_sportsbook": "Polymarket",
    "vector_store": {
        "type": "local",  # 'local' or 'pinecone'
        "path": "data/vector_store",
        "dimensions": 1536
    },
    "data_dir": "data",
    "models_dir": "data/models",
    "historical_dir": "data/historical",
    "bet_history_file": "data/bet_history.json"
}

def load_settings(config_file: Optional[str] = None) -> Dict[str, Any]:
    """
    Load configuration settings from various sources.
    
    Priority order:
    1. Environment variables
    2. Config file (if provided)
    3. Default configuration
    
    Args:
        config_file: Optional path to a JSON configuration file
        
    Returns:
        Dictionary containing merged configuration settings
    """
    # Start with default configuration
    config = DEFAULT_CONFIG.copy()
    
    # Load from config file if provided
    if config_file and os.path.exists(config_file):
        try:
            with open(config_file, 'r') as f:
                file_config = json.load(f)
                _deep_update(config, file_config)
            logger.info(f"Loaded configuration from {config_file}")
        except Exception as e:
            logger.error(f"Error loading config file {config_file}: {e}")
    
    # Override with environment variables
    _update_from_env(config)
    
    # Ensure required directories exist
    _ensure_directories(config)
    
    return config

def _deep_update(target: Dict[str, Any], source: Dict[str, Any]) -> None:
    """
    Recursively update a nested dictionary.
    
    Args:
        target: Target dictionary to update
        source: Source dictionary with new values
    """
    for key, value in source.items():
        if key in target and isinstance(target[key], dict) and isinstance(value, dict):
            _deep_update(target[key], value)
        else:
            target[key] = value

def _update_from_env(config: Dict[str, Any]) -> None:
    """
    Update configuration from environment variables.
    
    Environment variables should be prefixed with NBA_AGENT_
    For nested keys, use double underscore as separator
    
    Examples:
    NBA_AGENT_LOGGING__LEVEL=DEBUG
    NBA_AGENT_BETTING__BANKROLL=2000
    NBA_AGENT_POLYMARKET__API_KEY=your_api_key
    
    Args:
        config: Configuration dictionary to update
    """
    prefix = "NBA_AGENT_"
    
    for key, value in os.environ.items():
        if key.startswith(prefix):
            config_key = key[len(prefix):].lower()
            
            # Handle nested keys
            if "__" in config_key:
                parts = config_key.split("__")
                current = config
                
                # Navigate to the nested dictionary
                for part in parts[:-1]:
                    if part not in current:
                        current[part] = {}
                    current = current[part]
                
                # Set the value
                current[parts[-1]] = _parse_env_value(value)
            else:
                config[config_key] = _parse_env_value(value)

def _parse_env_value(value: str) -> Any:
    """
    Parse environment variable value to appropriate type.
    
    Args:
        value: String value from environment variable
        
    Returns:
        Parsed value (bool, int, float, or string)
    """
    # Boolean values
    if value.lower() in ('true', 'yes', '1'):
        return True
    if value.lower() in ('false', 'no', '0'):
        return False
    
    # Try numeric values
    try:
        if '.' in value:
            return float(value)
        return int(value)
    except ValueError:
        # Return as string if not numeric
        return value

def _ensure_directories(config: Dict[str, Any]) -> None:
    """
    Ensure that required directories exist.
    
    Args:
        config: Configuration dictionary
    """
    directories = [
        config.get('data_dir', 'data'),
        config.get('models_dir', 'data/models'),
        config.get('historical_dir', 'data/historical'),
        os.path.dirname(config.get('bet_history_file', 'data/bet_history.json')),
        os.path.dirname(config.get('logging', {}).get('file', 'logs/nba_agent.log')),
    ]
    
    if config.get('vector_store', {}).get('type') == 'local':
        directories.append(config.get('vector_store', {}).get('path', 'data/vector_store'))
    
    for directory in directories:
        if directory and not os.path.exists(directory):
            try:
                os.makedirs(directory, exist_ok=True)
                logger.debug(f"Created directory: {directory}")
            except Exception as e:
                logger.error(f"Error creating directory {directory}: {e}")

def save_settings(config: Dict[str, Any], config_file: str) -> bool:
    """
    Save configuration settings to a file.
    
    Args:
        config: Configuration dictionary to save
        config_file: Path to save the configuration file
        
    Returns:
        Boolean indicating success or failure
    """
    try:
        os.makedirs(os.path.dirname(config_file), exist_ok=True)
        with open(config_file, 'w') as f:
            json.dump(config, f, indent=2)
        logger.info(f"Saved configuration to {config_file}")
        return True
    except Exception as e:
        logger.error(f"Error saving config to {config_file}: {e}")
        return False

# Convenience function to get the full configuration
def get_config() -> Dict[str, Any]:
    """
    Get the full configuration with default settings.
    
    Returns:
        Dictionary containing the full configuration
    """
    return load_settings() 