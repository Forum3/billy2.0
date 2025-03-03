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
from agent.utils.wallet_utils import WalletManager

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

def main():
    """Test the wallet functionality"""
    print("Testing Wallet Functionality for NBA Betting Agent")
    
    # Load environment variables
    load_dotenv()
    
    # Get configuration
    config = get_config()
    
    # Check if private key is set in environment
    if not os.getenv("PK"):
        print("\nWARNING: Private key (PK) not set in environment variables.")
        print("Please set the PK environment variable with your wallet's private key.")
        print("You can create a .env file in the project root with the following content:")
        print("PK=your_private_key_here")
        print("RPC_URL=https://polygon-rpc.com")
        return
    
    # Initialize wallet manager
    wallet_manager = WalletManager(config)
    
    # Get wallet information
    print("\nRetrieving wallet information...")
    wallet_info = wallet_manager.get_wallet_info()
    
    # Display wallet information
    if wallet_info["status"] == "success":
        print("\nWallet Information:")
        print(f"  Address: {wallet_info['address']}")
        print(f"  Network: {wallet_info['network']} (Chain ID: {wallet_info['chain_id']})")
        print(f"  USDC.e Balance: ${wallet_info['balance_usdc']:,.2f}")
        print(f"  MATIC Balance: {wallet_info['balance_matic']:,.6f}")
        
        # Check if balance is sufficient for betting
        min_balance = config["wallet"]["min_balance_alert"]
        if wallet_info["balance_usdc"] < min_balance:
            print(f"\nWARNING: USDC.e balance (${wallet_info['balance_usdc']:,.2f}) is below the minimum alert threshold (${min_balance:,.2f}).")
            print("Consider funding your wallet before placing bets.")
        else:
            print(f"\nBalance is sufficient for betting operations.")
    else:
        print(f"\nError retrieving wallet information: {wallet_info['error']}")
    
    print("\nTest completed")

if __name__ == "__main__":
    main() 