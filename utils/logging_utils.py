#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Logging utilities for the NBA Betting Agent.

This module provides functions to set up and configure logging for the agent.
"""

import os
import logging
import logging.handlers
from datetime import datetime
from typing import Optional, Dict, Any

def setup_logging(log_level: str = "INFO", 
                  log_file: Optional[str] = None,
                  log_to_console: bool = True) -> None:
    """
    Set up logging configuration for the application.
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Optional path to log file
        log_to_console: Whether to log to console
    """
    # Convert string log level to logging constant
    numeric_level = getattr(logging, log_level.upper(), logging.INFO)
    
    # Create logs directory if it doesn't exist
    if log_file:
        os.makedirs(os.path.dirname(log_file), exist_ok=True)
    
    # Basic configuration
    root_logger = logging.getLogger()
    root_logger.setLevel(numeric_level)
    
    # Clear existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Add file handler if log_file is specified
    if log_file:
        file_handler = logging.handlers.RotatingFileHandler(
            log_file,
            maxBytes=10 * 1024 * 1024,  # 10 MB
            backupCount=5
        )
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)
    
    # Add console handler if log_to_console is True
    if log_to_console:
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        root_logger.addHandler(console_handler)
    
    # Suppress overly verbose logs from libraries
    logging.getLogger('requests').setLevel(logging.WARNING)
    logging.getLogger('urllib3').setLevel(logging.WARNING)
    
    logging.info(f"Logging initialized at level: {log_level}")

def get_logger(name: str) -> logging.Logger:
    """
    Get a logger with the specified name.
    
    Args:
        name: Name of the logger
        
    Returns:
        Logger instance
    """
    return logging.getLogger(name)

def log_execution_time(logger: logging.Logger, start_time: datetime, 
                       operation: str, additional_info: Optional[Dict[str, Any]] = None) -> None:
    """
    Log the execution time of an operation.
    
    Args:
        logger: Logger instance
        start_time: Start time of the operation
        operation: Description of the operation
        additional_info: Optional additional information to log
    """
    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()
    
    log_message = f"{operation} completed in {duration:.2f} seconds"
    
    if additional_info:
        log_message += f" | Additional info: {additional_info}"
    
    logger.info(log_message)

def log_error_with_context(logger: logging.Logger, error: Exception, 
                          context: Dict[str, Any], operation: str) -> None:
    """
    Log an error with contextual information.
    
    Args:
        logger: Logger instance
        error: Exception that occurred
        context: Dictionary containing contextual information
        operation: Description of the operation that failed
    """
    error_message = f"Error during {operation}: {str(error)}"
    logger.error(f"{error_message} | Context: {context}", exc_info=True) 