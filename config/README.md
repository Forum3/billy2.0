# NBA Betting Agent Configuration

This directory contains configuration settings for the NBA Betting Agent.

## Configuration Structure

The configuration is organized into the following sections:

### Agent Settings
```python
"agent": {
    "name": "NBA Betting Agent",
    "version": "0.1.0",
    "loop_interval": 60,  # seconds between main loop iterations
    "research_interval": 3600,  # seconds between research cycles
    "test_mode": True,  # Set to False for actual betting
}
```

### Memory Settings (Mem0)
```python
"mem0": {
    "api_key": "your_mem0_api_key_here",  # Replace with actual API key
    "agent_id": "nba_betting_agent",
    "base_url": "https://api.mem0.ai"
}
```

### Betting Parameters
```python
"betting": {
    "bankroll": 1000,  # Starting bankroll in USD
    "min_bet": 10,  # Minimum bet amount
    "max_bet": 100,  # Maximum bet amount
    "min_ev_threshold": 2.0,  # Minimum expected value percentage to place a bet
    "max_kelly_fraction": 0.25,  # Conservative fraction of Kelly criterion
    "daily_loss_limit": 100,  # Maximum allowed daily loss
    "daily_bet_limit": 5,  # Maximum number of bets per day
}
```

### Polymarket API Settings
```python
"polymarket": {
    "api_key": "your_polymarket_api_key_here",  # Replace with actual API key
    "base_url": "https://api.polymarket.com"
}
```

### Sports Data API Settings
```python
"sports_data": {
    "api_key": "your_sports_data_api_key_here",  # Replace with actual API key
    "base_url": "https://api.sportsdata.io/v3/nba"
}
```

### News API Settings
```python
"news_api": {
    "api_key": "your_news_api_key_here",  # Replace with actual API key
    "base_url": "https://newsapi.org/v2"
}
```

### Logging Settings
```python
"logging": {
    "level": "INFO",
    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    "file": "logs/nba_agent.log"
}
```

## Using the Configuration

### Loading Configuration

```python
from config.settings import get_config

# Get the default configuration
config = get_config()

# Access specific sections
agent_config = config['agent']
betting_config = config['betting']
```

### Custom Configuration File

You can create a custom configuration file in JSON format and load it:

```python
from config.settings import load_settings

# Load custom configuration
config = load_settings('path/to/custom_config.json')
```

### Environment Variables

You can override configuration values using environment variables:

```bash
# Set environment variables
export NBA_AGENT_BETTING__BANKROLL=5000
export NBA_AGENT_AGENT__TEST_MODE=false
export NBA_AGENT_POLYMARKET__API_KEY=your_actual_api_key
```

Environment variables should be prefixed with `NBA_AGENT_` and use double underscores (`__`) for nested keys.

### Saving Configuration

You can save the configuration to a file:

```python
from config.settings import save_settings

# Save configuration
save_settings(config, 'path/to/save_config.json')
```

## Example Usage

See the `examples/config_usage.py` file for a complete example of how to use the configuration settings.

## Legacy Configuration

The configuration still includes legacy settings for backward compatibility:

```python
"data_sources": { ... },
"min_edge_threshold": 0.05,
"confidence_threshold": 0.65,
"execution_mode": "manual",
"bankroll_fraction": 0.02,
"preferred_sportsbook": "Polymarket",
"vector_store": { ... },
"data_dir": "data",
"models_dir": "data/models",
"historical_dir": "data/historical",
"bet_history_file": "data/bet_history.json"
```

These settings are maintained for backward compatibility but may be deprecated in future versions. 