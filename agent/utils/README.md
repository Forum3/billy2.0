# NBA Betting Agent Utilities

This directory contains utility modules for the NBA Betting Agent.

## BillyResponseFormatter

The `BillyResponseFormatter` ensures all outputs from any module maintain Billy's distinctive style. It provides a centralized way to format different types of responses according to Billy's persona.

### Usage

```python
from agent.persona.billy import BillyPersona
from agent.utils.response_formatter import BillyResponseFormatter

# Initialize Billy's persona
persona = BillyPersona()

# Initialize the response formatter
formatter = BillyResponseFormatter(persona)

# Format different types of responses
betting_advice = formatter.format_betting_advice(betting_data)
market_data = formatter.format_market_data(market_data)
edge_analysis = formatter.format_edge_analysis(edge_data)
research_summary = formatter.format_research_summary(research_data)
error_message = formatter.format_error_message(error)
bet_placement = formatter.format_bet_placement(bet_data)
bet_outcome = formatter.format_bet_outcome(outcome_data)
daily_metrics = formatter.format_daily_metrics(metrics)
startup_message = formatter.format_startup_message()
generic_message = formatter.format_generic_message(message)
```

### Available Formatting Methods

- **format_betting_advice**: Formats betting advice with accurate data presentation
- **format_market_data**: Formats market data in a clean, factual way
- **format_edge_analysis**: Formats edge analysis with Billy's flair
- **format_research_summary**: Formats research summary with Billy's style
- **format_error_message**: Formats error messages with Billy's style
- **format_bet_placement**: Formats bet placement confirmation with Billy's style
- **format_bet_outcome**: Formats bet outcome with Billy's style
- **format_daily_metrics**: Formats daily metrics with Billy's style
- **format_startup_message**: Formats startup message with Billy's style
- **format_generic_message**: Formats a generic message with Billy's style

### Integration Example

See `examples/use_response_formatter.py` for a complete example of how to integrate the `BillyResponseFormatter` into a module.

## WalletManager

The `WalletManager` provides functionality to interact with blockchain wallets and check balances for betting operations.

### Usage

```python
from agent.utils import WalletManager

# Initialize wallet manager
wallet_manager = WalletManager(config)

# Get wallet information
wallet_info = wallet_manager.get_wallet_info()

# Get USDC balance
usdc_balance = wallet_manager.get_usdc_balance()
``` 