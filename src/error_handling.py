"""
Error handling utilities for Vietnam Stock AI Backend.
Provides retry logic, circuit breaker, and dead letter queue handling.
"""

import time
import functools
from typing import Callable, Any, Optional, Type, Tuple
from datetime import datetime, timedelta
from enum import Enum
from src.logging_config import get_logger

logger = get_logger("error_handling")


class CircuitBreakerState(Enum):
    """Circuit breaker states."""
    CLOSED = "CLOSED"  # Normal operation
    OPEN = "OPEN"  # Failing, reject requests
    HALF_OPEN = "HALF_OPEN"  # Testing if service recovered


class CircuitBreakerError(Exception):
    """Raised when circuit breaker is open."""
    pass


class CircuitBreaker:
    """
    Circuit breaker pattern implementation to prevent cascading failures.
    Used for external API calls and LLM service calls.
    """
    
    def __init__(self, failure_threshold: int = 5, timeout: int = 60, name: str = "default"):
        """
        Initialize circuit breaker.
        
        Args:
            failure_threshold: Number of failures before opening circuit
            timeout: Seconds to wait before attempting recovery (HALF_OPEN)
            name: Name of the circuit breaker for logging
        """
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.name = name
        self.failure_count = 0
        self.last_failure_time: Optional[datetime] = None
        self.state = CircuitBreakerState.CLOSED
        self.success_count = 0
    
    def call(self, func: Callable, *args, **kwargs) -> Any:
        """
        Execute function with circuit breaker protection.
        
        Args:
            func: Function to execute
            *args: Positional arguments for function
            **kwargs: Keyword arguments for function
            
        Returns:
            Function result
            
        Raises:
            CircuitBreakerError: If circuit is open
        """
        if self.state == CircuitBreakerState.OPEN:
            if self._should_attempt_reset():
                self.state = CircuitBreakerState.HALF_OPEN
                logger.info(f"Circuit breaker {self.name} entering HALF_OPEN state")
            else:
                logger.warning(
                    f"Circuit breaker {self.name} is OPEN",
                    context={"failure_count": self.failure_count}
                )
                raise CircuitBreakerError(f"Circuit breaker {self.name} is OPEN")
        
        try:
            result = func(*args, **kwargs)
            self._on_success()
            return result
        except Exception as e:
            self._on_failure()
            raise
    
    def _should_attempt_reset(self) -> bool:
        """Check if enough time has passed to attempt reset."""
        if self.last_failure_time is None:
            return True
        return datetime.now() - self.last_failure_time > timedelta(seconds=self.timeout)
    
    def _on_success(self):
        """Handle successful call."""
        if self.state == CircuitBreakerState.HALF_OPEN:
            self.success_count += 1
            if self.success_count >= 2:  # Require 2 successes to close
                self.state = CircuitBreakerState.CLOSED
                self.failure_count = 0
                self.success_count = 0
                logger.info(f"Circuit breaker {self.name} closed after recovery")
        else:
            self.failure_count = 0
    
    def _on_failure(self):
        """Handle failed call."""
        self.failure_count += 1
        self.last_failure_time = datetime.now()
        self.success_count = 0
        
        if self.failure_count >= self.failure_threshold:
            self.state = CircuitBreakerState.OPEN
            logger.error(
                f"Circuit breaker {self.name} opened",
                context={
                    "failure_count": self.failure_count,
                    "threshold": self.failure_threshold
                }
            )


def retry_with_exponential_backoff(
    max_retries: int = 5,
    base_delay: float = 1.0,
    max_delay: float = 60.0,
    exceptions: Tuple[Type[Exception], ...] = (Exception,)
):
    """
    Decorator for retrying function with exponential backoff.
    
    Args:
        max_retries: Maximum number of retry attempts
        base_delay: Initial delay in seconds
        max_delay: Maximum delay in seconds
        exceptions: Tuple of exception types to catch and retry
        
    Returns:
        Decorated function
        
    Example:
        @retry_with_exponential_backoff(max_retries=3, base_delay=1.0)
        def fetch_data():
            # ... code that might fail
            pass
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            last_exception = None
            
            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    
                    if attempt == max_retries:
                        logger.error(
                            f"Function {func.__name__} failed after {max_retries} retries",
                            context={
                                "function": func.__name__,
                                "attempts": attempt + 1,
                                "error": str(e)
                            },
                            exc_info=True
                        )
                        raise
                    
                    # Calculate delay with exponential backoff
                    delay = min(base_delay * (2 ** attempt), max_delay)
                    
                    logger.warning(
                        f"Function {func.__name__} failed, retrying",
                        context={
                            "function": func.__name__,
                            "attempt": attempt + 1,
                            "max_retries": max_retries,
                            "delay": delay,
                            "error": str(e)
                        }
                    )
                    
                    time.sleep(delay)
            
            # This should never be reached, but just in case
            if last_exception:
                raise last_exception
        
        return wrapper
    return decorator


class DeadLetterQueue:
    """
    Dead letter queue handler for Kafka messages that fail processing.
    """
    
    # Mapping of main topics to their DLQ topics
    DLQ_TOPICS = {
        'stock_prices_raw': 'stock_prices_dlq',
        'stock_news_raw': 'stock_news_dlq'
    }
    
    def __init__(self, kafka_producer):
        """
        Initialize dead letter queue handler.
        
        Args:
            kafka_producer: Kafka producer instance
        """
        self.producer = kafka_producer
    
    def send_to_dlq(self, original_topic: str, message: dict, error: Exception):
        """
        Send failed message to dead letter queue.
        
        Args:
            original_topic: Original Kafka topic
            message: Message that failed processing
            error: Exception that caused the failure
        """
        dlq_topic = self.DLQ_TOPICS.get(original_topic)
        
        if not dlq_topic:
            logger.error(
                f"No DLQ topic configured for {original_topic}",
                context={"original_topic": original_topic}
            )
            return
        
        # Enrich message with error information
        dlq_message = {
            "original_topic": original_topic,
            "original_message": message,
            "error": str(error),
            "error_type": type(error).__name__,
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }
        
        try:
            self.producer.send(dlq_topic, value=dlq_message)
            logger.info(
                f"Message sent to DLQ",
                context={
                    "original_topic": original_topic,
                    "dlq_topic": dlq_topic,
                    "error": str(error)
                }
            )
        except Exception as e:
            logger.error(
                f"Failed to send message to DLQ",
                context={
                    "original_topic": original_topic,
                    "dlq_topic": dlq_topic,
                    "error": str(e)
                },
                exc_info=True
            )
    
    @classmethod
    def get_dlq_topic(cls, original_topic: str) -> Optional[str]:
        """
        Get DLQ topic name for an original topic.
        
        Args:
            original_topic: Original Kafka topic
            
        Returns:
            DLQ topic name or None if not configured
        """
        return cls.DLQ_TOPICS.get(original_topic)
