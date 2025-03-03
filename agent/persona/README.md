# Billy Persona Module

This module implements Billy's distinctive personality and communication style for the NBA Betting Agent.

## Overview

The Billy Persona module ensures that all communications from the agent maintain Billy's unique voice and style. This includes:

- Lowercase text style for most communications
- Witty, edgy, and sharp-tongued expressions
- Sports-specific humor and references
- Distinctive expressions for different topics
- Appropriate tone for different contexts (betting advice, help, etc.)

## Components

### BillyPersona

The core class that encapsulates Billy's personality traits, communication style, and expressions.

```python
from agent.persona.billy import BillyPersona

# Initialize the persona
persona = BillyPersona()

# Get an expression for a specific topic
expression = persona.get_expression("lebron")

# Format a message in Billy's style
formatted = persona.format_message("The Lakers are playing tonight.", style="default")

# Create a daily summary
summary = persona.create_daily_summary()
```

### CommunicationManager

A higher-level class that uses the BillyPersona to format different types of messages.

```python
from agent.persona.communication import CommunicationManager

# Initialize the communication manager
comm_manager = CommunicationManager()

# Format a betting opportunity
formatted = comm_manager.format_betting_opportunity(opportunity_data)

# Format wallet status
formatted = comm_manager.format_wallet_status(wallet_info)

# Format research results
formatted = comm_manager.format_research_results(research_data)

# Format an error message
formatted = comm_manager.format_error_message("Connection failed")

# Format a generic message based on context
formatted = comm_manager.format_message("Here's some advice.", context="betting_advice")
```

## Integration

To integrate Billy's persona into a module:

1. Import the CommunicationManager
2. Initialize it in the module's constructor
3. Use it to format messages before logging or storing them

Example:

```python
from agent.persona.communication import CommunicationManager

class MyModule:
    def __init__(self, config):
        self.comm_manager = CommunicationManager()
        
    def process_data(self, data):
        # Process data...
        
        # Format result message using Billy's persona
        message = self.comm_manager.format_message(f"Processed {len(data)} items")
        
        # Log or store the formatted message
        logger.info(message)
```

## Customization

To add new expressions or modify Billy's style:

1. Edit the `_load_expressions` method in `BillyPersona` to add new topic-specific expressions
2. Add new formatting methods to `CommunicationManager` for specific message types
3. Adjust the communication style guidelines in `BillyPersona.__init__` as needed

## Testing

Use the `test_persona.py` script to test the persona functionality:

```bash
python test_persona.py
``` 