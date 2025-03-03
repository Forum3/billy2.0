#!/bin/bash
# Run script for NBA Betting Agent

# Display help message
function show_help {
    echo "NBA Betting Agent Runner"
    echo "Usage: ./run.sh [options]"
    echo ""
    echo "Options:"
    echo "  --test       Run in test mode (no actual bets placed)"
    echo "  --sim        Run in simulation mode (with historical data)"
    echo "  --live       Run in live mode (with actual betting)"
    echo "  --help       Display this help message"
    echo ""
    echo "Examples:"
    echo "  ./run.sh --test     # Run in test mode"
    echo "  ./run.sh --sim      # Run in simulation mode"
    echo "  ./run.sh --live     # Run in live mode (CAUTION: places real bets!)"
}

# Check for help flag
if [[ "$1" == "--help" || "$1" == "-h" ]]; then
    show_help
    exit 0
fi

# Set default mode to test if no arguments provided
if [[ $# -eq 0 ]]; then
    echo "No mode specified, defaulting to test mode"
    echo "Use --help for more options"
    python main.py --test
    exit 0
fi

# Process arguments
case "$1" in
    --test)
        echo "Starting NBA Betting Agent in TEST mode"
        python main.py --test
        ;;
    --sim)
        echo "Starting NBA Betting Agent in SIMULATION mode"
        python main.py --sim
        ;;
    --live)
        echo "WARNING: You are about to run the agent in LIVE mode"
        echo "This will place REAL bets with REAL money"
        read -p "Are you sure you want to continue? (y/N): " confirm
        if [[ "$confirm" == "y" || "$confirm" == "Y" ]]; then
            echo "Starting NBA Betting Agent in LIVE mode"
            python main.py --live
        else
            echo "Live mode cancelled"
            exit 1
        fi
        ;;
    *)
        echo "Unknown option: $1"
        show_help
        exit 1
        ;;
esac 