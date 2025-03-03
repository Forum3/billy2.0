# NBA Betting Agent

An intelligent agent for NBA betting research, analysis, and execution.

## Overview

The NBA Betting Agent is an automated system that researches NBA games, analyzes betting opportunities, and executes bets on Polymarket. The agent uses a modular architecture with four main components:

1. **Research Module**: Gathers data on upcoming NBA games, including team statistics, player performance, injury reports, and betting odds.
2. **Reasoning Module**: Analyzes research data to identify betting opportunities with positive expected value.
3. **Risk Management Module**: Enforces betting limits and thresholds to ensure responsible betting behavior.
4. **Execution Module**: Places bets on Polymarket based on reasoning outcomes and manages the betting portfolio.

The agent uses the Mem0 memory system to store and retrieve information throughout the betting process.

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/nba-betting-agent.git
   cd nba-betting-agent
   ```

2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Set up API keys:
   - Create accounts and obtain API keys for:
     - Mem0 (memory system)
     - Polymarket (betting platform)
     - Sports Data API (NBA data)
     - News API (NBA news)
   - Update the configuration with your API keys (see Configuration section)

## Configuration

The agent uses a hierarchical configuration system with the following priority:

1. Command-line arguments
2. Environment variables
3. Configuration file
4. Default settings

### Configuration File

The default configuration is defined in `config/settings.py`. You can create a custom configuration file in JSON format:

```json
{
  "agent": {
    "test_mode": true,
    "loop_interval": 60,
    "research_interval": 3600
  },
  "betting": {
    "bankroll": 1000,
    "min_bet": 10,
    "max_bet": 100
  },
  "risk_management": {
    "daily_bet_limit": 5,
    "daily_loss_limit": 100,
    "min_edge_threshold": 0.05,
    "kelly_fraction": 0.5
  }
}
```

### Environment Variables

You can override configuration values using environment variables:

```bash
export NBA_AGENT_BETTING__BANKROLL=5000
export NBA_AGENT_AGENT__TEST_MODE=false
export NBA_AGENT_POLYMARKET__API_KEY=your_actual_api_key
export NBA_AGENT_RISK_MANAGEMENT__DAILY_LOSS_LIMIT=200
```

Environment variables should be prefixed with `NBA_AGENT_` and use double underscores (`__`) for nested keys.

## Running the Agent

### Using the Run Script

The easiest way to run the agent is using the provided shell script:

```bash
# Make the script executable (first time only)
chmod +x run.sh

# Run in test mode (default, no actual bets placed)
./run.sh --test

# Run in simulation mode (with historical data)
./run.sh --sim

# Run in live mode (CAUTION: places real bets!)
./run.sh --live

# Show help
./run.sh --help
```

### Using Python Directly

You can also run the agent directly with Python:

```bash
# Run in test mode
python main.py --test

# Run in simulation mode
python main.py --sim

# Run in live mode (CAUTION: places real bets!)
python main.py --live

# Run with a custom configuration file
python main.py --test --config path/to/config.json
```

### Test Mode

By default, the agent runs in test mode, which simulates betting without actually placing bets. To enable real betting:

```bash
./run.sh --live
```

**WARNING**: Only use live mode when you are ready to place real bets with real money.

## Architecture

The agent is organized into the following components:

### Modules

- **Research Module** (`agent/modules/research.py`): Gathers data on upcoming NBA games.
- **Reasoning Module** (`agent/modules/reasoning.py`): Analyzes research data to identify betting opportunities.
- **Risk Management Module** (`agent/modules/risk_management.py`): Enforces betting limits and thresholds to ensure responsible betting.
- **Execution Module** (`agent/modules/execution.py`): Places bets on Polymarket and manages the betting portfolio.

### Memory

- **Mem0 Client** (`agent/memory/mem0_client.py`): Client for interacting with the Mem0 memory system.

### Configuration

- **Settings** (`config/settings.py`): Configuration management system.

### Controller

- **Agent Controller** (`agent/controller.py`): Orchestrates the agent's operations and decision-making process.

## Risk Management

The Risk Management module provides several safeguards to ensure responsible betting:

### Betting Limits

- **Maximum Bet Size**: Caps the size of individual bets based on bankroll percentage.
- **Daily Bet Limit**: Restricts the number of bets placed in a 24-hour period.
- **Daily Loss Limit**: Stops betting if losses exceed a specified amount in a 24-hour period.

### Betting Thresholds

- **Minimum Edge Threshold**: Only places bets with an expected value above a specified threshold.
- **Kelly Criterion**: Adjusts bet sizes based on the Kelly criterion, with a configurable fraction.

### Bankroll Management

- **Bankroll Tracking**: Monitors the current bankroll and adjusts bet sizes accordingly.
- **Bet Frequency Control**: Prevents overtrading by limiting the frequency of bets.

## Development

### Adding a New Module

1. Create a new module file in the `agent/modules` directory.
2. Implement the module class with the required methods.
3. Update the agent class in `agent/agent.py` to use the new module.

### Extending Configuration

1. Add new configuration parameters to the `DEFAULT_CONFIG` dictionary in `config/settings.py`.
2. Update the relevant modules to use the new configuration parameters.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- [Mem0](https://mem0.ai) for providing the memory management system.
- [Polymarket](https://polymarket.com) for the betting platform.
- [Sports Data API](https://sportsdata.io) for NBA data.
- [News API](https://newsapi.org) for NBA news. 