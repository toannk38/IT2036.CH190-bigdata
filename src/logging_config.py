"""
Centralized logging configuration for Vietnam Stock AI Backend.
Provides structured logging with JSON format support.
"""

import logging
import sys
import json
import traceback
from datetime import datetime
from typing import Optional, Dict, Any
from src.config import config


class JSONFormatter(logging.Formatter):
    """
    Custom JSON formatter for structured logging.
    Outputs logs in JSON format with timestamp, level, component, message, and context.
    """
    
    def format(self, record: logging.LogRecord) -> str:
        """
        Format log record as JSON.
        
        Args:
            record: Log record to format
            
        Returns:
            JSON-formatted log string
        """
        log_data = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "component": record.name,
            "message": record.getMessage(),
        }
        
        # Add context if available
        if hasattr(record, 'context') and record.context:
            log_data["context"] = record.context
        
        # Add exception info if available
        if record.exc_info:
            log_data["context"] = log_data.get("context", {})
            log_data["context"]["error"] = str(record.exc_info[1])
            log_data["context"]["stack_trace"] = "".join(
                traceback.format_exception(*record.exc_info)
            )
        
        return json.dumps(log_data)


def setup_logging(component_name: str, use_json: bool = True) -> logging.Logger:
    """
    Setup structured logging for a component.
    
    Args:
        component_name: Name of the component (e.g., 'price_collector', 'api_service')
        use_json: Whether to use JSON format (default: True)
    
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
    
    # Create formatter based on configuration
    if use_json:
        formatter = JSONFormatter()
    else:
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
    Provides methods for logging at different levels with contextual information.
    """
    
    def __init__(self, component_name: str, use_json: bool = True):
        """
        Initialize structured logger.
        
        Args:
            component_name: Name of the component
            use_json: Whether to use JSON format
        """
        self.logger = setup_logging(component_name, use_json)
        self.component_name = component_name
        self.use_json = use_json
    
    def _log_with_context(self, level: int, message: str, context: Optional[Dict[str, Any]] = None, exc_info: bool = False):
        """
        Internal method to log with context.
        
        Args:
            level: Logging level
            message: Log message
            context: Additional context information
            exc_info: Whether to include exception info
        """
        if self.use_json:
            # For JSON format, attach context to the record
            extra = {'context': context} if context else {}
            self.logger.log(level, message, exc_info=exc_info, extra=extra)
        else:
            # For text format, append context to message
            if context:
                context_str = ' | '.join([f"{k}={v}" for k, v in context.items()])
                message = f"{message} | {context_str}"
            self.logger.log(level, message, exc_info=exc_info)
    
    def debug(self, message: str, context: Optional[Dict[str, Any]] = None):
        """
        Log debug message.
        
        Args:
            message: Log message
            context: Additional context information
        """
        self._log_with_context(logging.DEBUG, message, context)
    
    def info(self, message: str, context: Optional[Dict[str, Any]] = None):
        """
        Log info message.
        
        Args:
            message: Log message
            context: Additional context information
        """
        self._log_with_context(logging.INFO, message, context)
    
    def warning(self, message: str, context: Optional[Dict[str, Any]] = None):
        """
        Log warning message.
        
        Args:
            message: Log message
            context: Additional context information
        """
        self._log_with_context(logging.WARNING, message, context)
    
    def error(self, message: str, context: Optional[Dict[str, Any]] = None, exc_info: bool = False):
        """
        Log error message.
        
        Args:
            message: Log message
            context: Additional context information
            exc_info: Whether to include exception info
        """
        self._log_with_context(logging.ERROR, message, context, exc_info)
    
    def critical(self, message: str, context: Optional[Dict[str, Any]] = None, exc_info: bool = False):
        """
        Log critical message.
        
        Args:
            message: Log message
            context: Additional context information
            exc_info: Whether to include exception info
        """
        self._log_with_context(logging.CRITICAL, message, context, exc_info)


def get_logger(component_name: str, use_json: bool = True) -> StructuredLogger:
    """
    Get a structured logger instance for a component.
    
    Args:
        component_name: Name of the component
        use_json: Whether to use JSON format (default: True)
        
    Returns:
        StructuredLogger instance
    """
    return StructuredLogger(component_name, use_json)
