# NBA Betting Agent System Architecture

```mermaid
graph TD
    %% Main Components
    User[User/Operator] --> |Runs| Main[Main Entry Point]
    Main --> |Initializes| Controller[Agent Controller]
    
    %% Configuration
    Config[Configuration] --> |Provides settings to| Controller
    Config --> |Loaded by| Main
    
    %% Core Modules
    Controller --> |Orchestrates| Research[Research Module]
    Controller --> |Orchestrates| Reasoning[Reasoning Module]
    Controller --> |Orchestrates| RiskMgmt[Risk Management Module]
    Controller --> |Orchestrates| Execution[Execution Module]
    
    %% Memory System
    Mem0[Mem0 Memory System] --> |Provides data to| Research
    Mem0 --> |Provides data to| Reasoning
    Mem0 --> |Provides data to| RiskMgmt
    Mem0 --> |Provides data to| Execution
    Research --> |Stores results in| Mem0
    Reasoning --> |Stores decisions in| Mem0
    RiskMgmt --> |Stores risk assessments in| Mem0
    Execution --> |Stores outcomes in| Mem0
    
    %% External Systems
    SportsAPI[Sports Data API] --> |Provides data to| Research
    NewsAPI[News API] --> |Provides data to| Research
    Polymarket[Polymarket API] --> |Receives bets from| Execution
    
    %% State Flow
    Controller --> |Manages state| AgentState{Agent State}
    AgentState --> |RESEARCHING| Research
    AgentState --> |REASONING| Reasoning
    AgentState --> |RISK_ASSESSMENT| RiskMgmt
    AgentState --> |EXECUTING| Execution
    AgentState --> |IDLE| Controller
    
    %% Data Flow
    Research --> |Provides research data| Reasoning
    Reasoning --> |Provides betting decisions| RiskMgmt
    RiskMgmt --> |Provides validated decisions| Execution
    Execution --> |Updates strategy based on outcomes| Reasoning
    Execution --> |Updates bankroll| RiskMgmt
    
    %% Subcomponents
    subgraph "Research Module"
        ResearchQueue[Research Queue]
        InjuryReports[Injury Reports]
        TeamStats[Team Statistics]
        LineMovements[Line Movements]
        NewsAnalysis[News Analysis]
    end
    
    subgraph "Reasoning Module"
        BeliefUpdating[Belief Updating]
        ProbabilityCalculation[Probability Calculation]
        MarketComparison[Market Comparison]
        EVCalculation[Expected Value Calculation]
        BettingDecision[Betting Decision]
    end
    
    subgraph "Risk Management Module"
        MaxBetSize[Maximum Bet Size Limits]
        DailyLossLimits[Daily Loss Limits]
        EdgeThresholds[Required Edge Thresholds]
        BetFrequency[Bet Frequency Limits]
        KellyFraction[Kelly Fraction Control]
        BankrollTracking[Bankroll Tracking]
    end
    
    subgraph "Execution Module"
        BetPlacement[Bet Placement]
        BetRecording[Bet Recording]
        OutcomeMonitoring[Outcome Monitoring]
        StrategyUpdating[Strategy Updating]
    end
    
    %% Running Modes
    RunModes{Running Modes} --> |Test Mode| Controller
    RunModes --> |Simulation Mode| Controller
    RunModes --> |Live Mode| Controller
    
    %% Styling
    classDef module fill:#f9f,stroke:#333,stroke-width:2px;
    classDef external fill:#bbf,stroke:#33f,stroke-width:2px;
    classDef memory fill:#bfb,stroke:#3f3,stroke-width:2px;
    classDef state fill:#fbb,stroke:#f33,stroke-width:2px;
    classDef risk fill:#ffb,stroke:#f90,stroke-width:2px;
    
    class Research,Reasoning,Execution module;
    class RiskMgmt risk;
    class SportsAPI,NewsAPI,Polymarket external;
    class Mem0 memory;
    class AgentState,RunModes state;
```

## System Workflow

1. **Initialization**:
   - User starts the agent via the main entry point
   - Configuration is loaded from settings
   - Agent Controller initializes with the specified mode (test, simulation, or live)
   - Memory client connects to Mem0

2. **Research Phase**:
   - Controller transitions to RESEARCHING state
   - Research Module gathers data from external APIs
   - Data includes team statistics, injury reports, betting odds, and news
   - Research results are stored in Mem0 memory

3. **Reasoning Phase**:
   - Controller transitions to REASONING state
   - Reasoning Module retrieves research data from memory
   - Beliefs are updated based on new information
   - Win probabilities are calculated and compared to market odds
   - Expected value is calculated for potential bets
   - Betting decisions are made and stored in memory

4. **Risk Assessment Phase**:
   - Controller transitions to RISK_ASSESSMENT state
   - Risk Management Module retrieves betting decisions from memory
   - Decisions are validated against risk parameters:
     - Maximum bet size limits
     - Daily loss limits
     - Required edge thresholds
     - Bet frequency limits
     - Kelly criterion adjustments
   - Validated decisions are stored in memory with risk assessment notes
   - Risk metrics are updated and stored

5. **Execution Phase**:
   - Controller transitions to EXECUTING state
   - Execution Module retrieves validated betting decisions from memory
   - In test mode: simulates bet placement
   - In live mode: places actual bets via Polymarket API
   - Bet details are recorded in memory
   - Bankroll is updated in the Risk Management Module

6. **Monitoring Phase**:
   - Execution Module monitors bet outcomes
   - Results are recorded and used to update strategies
   - Bankroll and risk metrics are updated based on outcomes
   - Performance metrics are calculated

7. **Idle Phase**:
   - Controller transitions to IDLE state
   - Waits for the next research interval
   - Cycle repeats

The system uses a state machine approach to manage the workflow, with the Agent Controller orchestrating the transitions between states and coordinating the modules. The Risk Management Module serves as a critical safety layer between the Reasoning and Execution modules, ensuring that all betting decisions adhere to predefined risk parameters before execution. 