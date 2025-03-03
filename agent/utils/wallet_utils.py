#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Wallet utilities for the NBA Betting Agent.

This module provides functions to interact with blockchain wallets
and check balances for betting operations.
"""

import os
import logging
from typing import Dict, Any, Optional
from web3 import Web3
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

# USDC.e contract address on Polygon
USDC_ADDRESS = "0x2791Bca1f2de4661ED88A30C99A7a9449Aa84174"

# USDC.e ABI (minimal for balance checking)
USDC_ABI = [
    {
        "constant": True,
        "inputs": [{"name": "account", "type": "address"}],
        "name": "balanceOf",
        "outputs": [{"name": "", "type": "uint256"}],
        "type": "function"
    }
]

class WalletManager:
    """
    Manager for blockchain wallet operations.
    
    This class provides functionality to check wallet balances
    and perform other wallet-related operations.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the wallet manager.
        
        Args:
            config: Configuration dictionary containing wallet settings
        """
        self.config = config
        self.wallet_config = config.get("wallet", {})
        
        # Load environment variables
        load_dotenv()
        
        # Initialize Web3 connection
        self.rpc_url = self.wallet_config.get("rpc_url") or os.getenv("RPC_URL")
        if not self.rpc_url:
            logger.warning("No RPC URL provided for wallet operations")
            self.web3 = None
        else:
            try:
                self.web3 = Web3(Web3.HTTPProvider(self.rpc_url))
                logger.info(f"Web3 connection initialized: {self.web3.is_connected()}")
            except Exception as e:
                logger.error(f"Error initializing Web3 connection: {str(e)}")
                self.web3 = None
        
        # Get wallet address
        self.private_key = self.wallet_config.get("private_key") or os.getenv("PK")
        self.wallet_address = None
        
        if self.private_key and self.web3:
            try:
                account = self.web3.eth.account.from_key(self.private_key)
                self.wallet_address = account.address
                logger.info(f"Wallet address initialized: {self.wallet_address[:6]}...{self.wallet_address[-4:]}")
            except Exception as e:
                logger.error(f"Error initializing wallet address: {str(e)}")
    
    def get_usdc_balance(self) -> float:
        """
        Get the USDC.e balance of the wallet.
        
        Returns:
            Balance in USDC.e (float)
        """
        if not self.web3 or not self.wallet_address:
            logger.warning("Web3 or wallet address not initialized")
            return 0.0
        
        try:
            # Initialize USDC.e contract
            usdc_contract = self.web3.eth.contract(
                address=self.web3.to_checksum_address(USDC_ADDRESS),
                abi=USDC_ABI
            )
            
            # Get balance
            balance = usdc_contract.functions.balanceOf(self.wallet_address).call()
            
            # USDC.e has 6 decimals
            balance_in_usdc = balance / 1e6
            
            logger.info(f"Current wallet USDC.e balance: ${balance_in_usdc:,.2f}")
            return balance_in_usdc
            
        except Exception as e:
            logger.error(f"Error getting USDC.e balance: {str(e)}")
            return 0.0
    
    def get_wallet_info(self) -> Dict[str, Any]:
        """
        Get comprehensive wallet information.
        
        Returns:
            Dictionary containing wallet information
        """
        if not self.web3 or not self.wallet_address:
            return {
                "status": "error",
                "error": "Web3 or wallet address not initialized",
                "balance_usdc": 0.0,
                "address": None,
                "network": None
            }
        
        try:
            # Get USDC.e balance
            usdc_balance = self.get_usdc_balance()
            
            # Get network information
            chain_id = self.web3.eth.chain_id
            network = "Polygon" if chain_id == 137 else f"Unknown ({chain_id})"
            
            # Get native token (MATIC) balance
            matic_balance = self.web3.eth.get_balance(self.wallet_address) / 1e18
            
            return {
                "status": "success",
                "address": self.wallet_address,
                "balance_usdc": usdc_balance,
                "balance_matic": matic_balance,
                "network": network,
                "chain_id": chain_id
            }
            
        except Exception as e:
            logger.error(f"Error getting wallet info: {str(e)}")
            return {
                "status": "error",
                "error": str(e),
                "balance_usdc": 0.0,
                "address": self.wallet_address,
                "network": None
            } 