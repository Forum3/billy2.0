#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import logging
from pprint import pprint
from dotenv import load_dotenv

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import configuration and modules
from config.settings import get_config
from agent.modules.wakeup import WakeUpModule
from agent.memory.mem0_client import Mem0Client
from agent.memory.mem0_official import Mem0OfficialClient

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

def main():
    """Test the WakeUp module"""
    print("Testing WakeUp Module for NBA Betting Agent")
    
    # Load environment variables
    load_dotenv()
    
    # Get configuration
    config = get_config()
    
    # Update API keys if needed (replace with your actual keys)
    config["sportstensor"]["api_key"] = "hPW29W7OuyU3-qt5qdW6JIOi09PVB3THV7lSkwKhghQ"
    
    # Check if private key is set in environment
    if not os.getenv("PK"):
        print("\nWARNING: Private key (PK) not set in environment variables.")
        print("Wallet balance checking will be skipped.")
        print("You can create a .env file in the project root with the following content:")
        print("PK=your_private_key_here")
        print("RPC_URL=https://polygon-rpc.com")
    
    # Initialize memory client
    if config['mem0'].get('use_official_client', False):
        print("Using official Mem0 client")
        try:
            memory = Mem0OfficialClient(
                api_key=config['mem0']['api_key'],
                agent_id=config['mem0']['agent_id'],
                base_url=config['mem0'].get('base_url', "https://api.mem0.ai"),
                cache_ttl=config['mem0'].get('cache_ttl', 300)
            )
        except Exception as e:
            print(f"Failed to initialize official Mem0 client: {str(e)}")
            print("Falling back to custom Mem0 client")
            memory = Mem0Client(
                api_key=config['mem0']['api_key'],
                agent_id=config['mem0']['agent_id'],
                base_url=config['mem0'].get('base_url', "https://api.mem0.ai"),
                cache_ttl=config['mem0'].get('cache_ttl', 300)
            )
    else:
        print("Using custom Mem0 client")
        memory = Mem0Client(
            api_key=config["mem0"]["api_key"],
            agent_id=config["mem0"]["agent_id"],
            base_url=config['mem0'].get('base_url', "https://api.mem0.ai"),
            cache_ttl=config['mem0'].get('cache_ttl', 300)
        )
    
    # Initialize WakeUp module
    wakeup_module = WakeUpModule(memory, config)
    
    # Run the module
    print("\nRunning WakeUp module to scan for betting opportunities...")
    results = wakeup_module.run()
    
    # Display results
    print(f"\nWakeUp module completed with status: {results['status']}")
    
    # Display Billy's message
    if "message" in results:
        print(f"\nBilly says: \"{results['message']}\"")
    
    # Display wallet status
    wallet_status = results.get("wallet_status", {})
    if wallet_status.get("status") == "success":
        print(f"\nWallet Status:")
        print(f"  Address: {wallet_status.get('address', 'N/A')}")
        print(f"  Network: {wallet_status.get('network', 'N/A')}")
        print(f"  Balance: ${wallet_status.get('balance', 0):,.2f}")
        print(f"  Sufficient for betting: {'Yes' if wallet_status.get('is_sufficient', False) else 'No'}")
        
        if not wallet_status.get("is_sufficient", False):
            print(f"  Minimum required: ${wallet_status.get('min_balance', 0):,.2f}")
    elif wallet_status.get("status") == "error":
        print(f"\nError checking wallet: {wallet_status.get('error', 'Unknown error')}")
    
    # Display opportunities
    print(f"\nFound {results['opportunities_found']} betting opportunities")
    
    if results["opportunities_found"] > 0:
        print("\nBetting Opportunities:")
        for i, opp in enumerate(results["opportunities"], 1):
            print(f"\nOpportunity {i}:")
            print(f"  Game: {opp['away_team']} @ {opp['home_team']}")
            print(f"  Team: {opp['team']}")
            print(f"  Model Probability: {opp['model_probability']:.2%}")
            print(f"  Market Probability: {opp['market_probability']:.2%}")
            print(f"  Edge: {opp['edge']:.2%}")
    
    # Display memory entries
    print("\nMemory Entries:")
    entries = memory.search({
        "query": "recent entries",
        "limit": 5
    })
    
    for entry in entries:
        print(f"\n  Content: {entry.get('content')}")
        print(f"  Type: {entry.get('metadata', {}).get('type', 'unknown')}")
        print(f"  Timestamp: {entry.get('metadata', {}).get('timestamp', 'unknown')}")
    
    print("\nTest completed")

if __name__ == "__main__":
    main() 