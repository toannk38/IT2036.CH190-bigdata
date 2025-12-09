"""
Centralized logging configuration for Vietnam Stock AI Backend.
"""

import logging
import sys
from datetime import datetime
from src.config import config


def setup_logging(component_name: str) -> logging.Logger:
    """
    Setup structured logging for a component.
    
    Args:
        component_name: Name of the component (e.g., 'price_collector', 'api_service')
    
    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(component_name)
    logger.setLevel(getattr(logging, config.LOG_LEVEL.upper(), logging.INFO))
    
    # Remove existing handlers
    logger.handlers.clear()
    
    # Create console handler
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(getattr(logging, config.LOG_LEVEL.upper(), logging.INFO))
    
    # Create formatter with structured format
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    handler.setFormatter(formatter)
    
    # Add handler to logger
    logger.addHandler(handler)
    
    return logger


class StructuredLogger:
    """
    Wrapper for structured logging with context.
    """
    
    def __init__(self, component_name: str):
        self.logger = setup_logging(component_name)
        self.component_name = component_name
    
    def _format_message(self, message: str, context: dict = None) -> str:
        """Format message with context."""
        if context:
            context_str = ' | '.join([f"{k}={v}" for k, v in context.items()])
            return f"{message} | {context_str}"
        return message
    
    def debug(self, message: str, context: dict = None):
        """Log debug message."""
        self.logger.debug(self._format_message(message, context))
    
    def info(self, message: str, context: dict = None):
        """Log info message."""
        self.logger.info(self._format_message(message, context))
    
    def warning(self, message: str, context: dict = None):
        """Log warning message."""
        self.logger.warning(self._format_message(message, context))
    
    def error(self, message: str, context: dict = None, exc_info: bool = False):
        """Log error message."""
        self.logger.error(self._format_message(message, context), exc_info=exc_info)
    
    def critical(self, message: str, context: dict = None, exc_info: bool = False):
        """Log critical message."""
        self.logger.critical(self._format_message(message, context), exc_info=exc_info)


def get_logger(component_name: str) -> StructuredLogger:
    """
    Get a structured logger instance for a component.
    
    Args:
        component_name: Name of the component
        
    Returns:
        StructuredLogger instance
    """
    return StructuredLogger(component_name)
