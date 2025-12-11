"""
Unit tests for error handling utilities.
Tests retry logic, circuit breaker, and logging functionality.
"""

import json
import time
import logging
from io import StringIO
from unittest.mock import Mock, MagicMock
import pytest
from src.error_handling import (
    retry_with_exponential_backoff,
    CircuitBreaker,
    CircuitBreakerState,
    CircuitBreakerError,
    DeadLetterQueue
)
from src.logging_config import StructuredLogger, JSONFormatter


class TestRetryWithExponentialBackoff:
    """Test retry decorator with different failure scenarios."""
    
    def test_retry_succeeds_on_first_attempt(self):
        """Test that function succeeds without retries."""
        call_count = [0]
        
        @retry_with_exponential_backoff(max_retries=3, base_delay=0.01)
        def successful_function():
            call_count[0] += 1
            return "success"
        
        result = successful_function()
        assert result == "success"
        assert call_count[0] == 1
    
    def test_retry_succeeds_after_failures(self):
        """Test that function succeeds after some failures."""
        call_count = [0]
        
        @retry_with_exponential_backoff(max_retries=3, base_delay=0.01)
        def eventually_successful():
            call_count[0] += 1
            if call_count[0] < 3:
                raise ValueError("Temporary failure")
            return "success"
        
        result = eventually_successful()
        assert result == "success"
        assert call_count[0] == 3
    
    def test_retry_fails_after_max_retries(self):
        """Test that function raises exception after max retries."""
        call_count = [0]
        
        @retry_with_exponential_backoff(max_retries=2, base_delay=0.01)
        def always_fails():
            call_count[0] += 1
            raise ValueError("Always fails")
        
        with pytest.raises(ValueError, match="Always fails"):
            always_fails()
        
        # Should be called 3 times: initial + 2 retries
        assert call_count[0] == 3
    
    def test_retry_with_specific_exceptions(self):
        """Test that retry only catches specified exceptions."""
        call_count = [0]
        
        @retry_with_exponential_backoff(
            max_retries=3,
            base_delay=0.01,
            exceptions=(ValueError,)
        )
        def raises_different_exception():
            call_count[0] += 1
            if call_count[0] == 1:
                raise TypeError("Not retryable")
            return "success"
        
        # Should raise TypeError immediately without retrying
        with pytest.raises(TypeError, match="Not retryable"):
            raises_different_exception()
        
        assert call_count[0] == 1
    
    def test_retry_exponential_backoff_timing(self):
        """Test that delays follow exponential backoff pattern."""
        call_times = []
        
        @retry_with_exponential_backoff(max_retries=3, base_delay=0.1)
        def failing_function():
            call_times.append(time.time())
            if len(call_times) < 3:
                raise ValueError("Fail")
            return "success"
        
        result = failing_function()
        assert result == "success"
        
        # Verify exponential delays (with tolerance)
        delay1 = call_times[1] - call_times[0]
        delay2 = call_times[2] - call_times[1]
        
        # First delay should be ~0.1s, second ~0.2s
        assert 0.08 <= delay1 <= 0.15
        assert 0.15 <= delay2 <= 0.30


class TestCircuitBreaker:
    """Test circuit breaker state transitions."""
    
    def test_circuit_breaker_closed_state(self):
        """Test circuit breaker in CLOSED state allows calls."""
        cb = CircuitBreaker(failure_threshold=3, timeout=1, name="test")
        
        def successful_call():
            return "success"
        
        result = cb.call(successful_call)
        assert result == "success"
        assert cb.state == CircuitBreakerState.CLOSED
        assert cb.failure_count == 0
    
    def test_circuit_breaker_opens_after_threshold(self):
        """Test circuit breaker opens after failure threshold."""
        cb = CircuitBreaker(failure_threshold=3, timeout=1, name="test")
        
        def failing_call():
            raise ValueError("Failure")
        
        # Fail 3 times to reach threshold
        for i in range(3):
            with pytest.raises(ValueError):
                cb.call(failing_call)
        
        # Circuit should now be OPEN
        assert cb.state == CircuitBreakerState.OPEN
        assert cb.failure_count == 3
        
        # Next call should raise CircuitBreakerError
        with pytest.raises(CircuitBreakerError):
            cb.call(failing_call)
    
    def test_circuit_breaker_half_open_after_timeout(self):
        """Test circuit breaker enters HALF_OPEN after timeout."""
        cb = CircuitBreaker(failure_threshold=2, timeout=0.1, name="test")
        
        def failing_call():
            raise ValueError("Failure")
        
        # Open the circuit
        for i in range(2):
            with pytest.raises(ValueError):
                cb.call(failing_call)
        
        assert cb.state == CircuitBreakerState.OPEN
        
        # Wait for timeout
        time.sleep(0.15)
        
        # Next call should enter HALF_OPEN
        with pytest.raises(ValueError):
            cb.call(failing_call)
        
        # State should have been HALF_OPEN during the call
        # but back to OPEN after failure
        assert cb.state == CircuitBreakerState.OPEN
    
    def test_circuit_breaker_closes_after_success_in_half_open(self):
        """Test circuit breaker closes after successful calls in HALF_OPEN."""
        cb = CircuitBreaker(failure_threshold=2, timeout=0.1, name="test")
        
        def failing_call():
            raise ValueError("Failure")
        
        def successful_call():
            return "success"
        
        # Open the circuit
        for i in range(2):
            with pytest.raises(ValueError):
                cb.call(failing_call)
        
        assert cb.state == CircuitBreakerState.OPEN
        
        # Wait for timeout
        time.sleep(0.15)
        
        # Successful calls should close the circuit
        # Need 2 successes to close
        result1 = cb.call(successful_call)
        assert result1 == "success"
        
        result2 = cb.call(successful_call)
        assert result2 == "success"
        
        assert cb.state == CircuitBreakerState.CLOSED
        assert cb.failure_count == 0
    
    def test_circuit_breaker_resets_failure_count_on_success(self):
        """Test that failure count resets on successful call."""
        cb = CircuitBreaker(failure_threshold=3, timeout=1, name="test")
        
        def failing_call():
            raise ValueError("Failure")
        
        def successful_call():
            return "success"
        
        # Fail once
        with pytest.raises(ValueError):
            cb.call(failing_call)
        
        assert cb.failure_count == 1
        
        # Succeed
        cb.call(successful_call)
        
        # Failure count should reset
        assert cb.failure_count == 0
        assert cb.state == CircuitBreakerState.CLOSED


class TestDeadLetterQueue:
    """Test dead letter queue handling."""
    
    def test_send_to_dlq_with_valid_topic(self):
        """Test sending message to DLQ for valid topic."""
        mock_producer = Mock()
        dlq = DeadLetterQueue(mock_producer)
        
        original_topic = "stock_prices_raw"
        message = {"symbol": "VNM", "price": 85000}
        error = ValueError("Processing failed")
        
        dlq.send_to_dlq(original_topic, message, error)
        
        # Verify producer was called
        mock_producer.send.assert_called_once()
        
        # Verify DLQ topic
        call_args = mock_producer.send.call_args
        assert call_args[0][0] == "stock_prices_dlq"
        
        # Verify message structure
        dlq_message = call_args[1]["value"]
        assert dlq_message["original_topic"] == original_topic
        assert dlq_message["original_message"] == message
        assert "Processing failed" in dlq_message["error"]
        assert dlq_message["error_type"] == "ValueError"
        assert "timestamp" in dlq_message
    
    def test_send_to_dlq_with_invalid_topic(self):
        """Test sending message to DLQ for topic without DLQ configured."""
        mock_producer = Mock()
        dlq = DeadLetterQueue(mock_producer)
        
        original_topic = "unknown_topic"
        message = {"data": "test"}
        error = ValueError("Error")
        
        # Should not raise exception, just log error
        dlq.send_to_dlq(original_topic, message, error)
        
        # Producer should not be called
        mock_producer.send.assert_not_called()
    
    def test_get_dlq_topic(self):
        """Test getting DLQ topic name."""
        assert DeadLetterQueue.get_dlq_topic("stock_prices_raw") == "stock_prices_dlq"
        assert DeadLetterQueue.get_dlq_topic("stock_news_raw") == "stock_news_dlq"
        assert DeadLetterQueue.get_dlq_topic("unknown_topic") is None


class TestLoggingFormat:
    """Test logging output format."""
    
    def test_json_formatter_basic(self):
        """Test JSON formatter with basic log record."""
        formatter = JSONFormatter()
        
        # Create a log record
        record = logging.LogRecord(
            name="test_component",
            level=logging.ERROR,
            pathname="test.py",
            lineno=10,
            msg="Test error message",
            args=(),
            exc_info=None
        )
        
        # Format the record
        formatted = formatter.format(record)
        
        # Parse JSON
        log_data = json.loads(formatted)
        
        # Verify structure
        assert log_data["level"] == "ERROR"
        assert log_data["component"] == "test_component"
        assert log_data["message"] == "Test error message"
        assert "timestamp" in log_data
        assert log_data["timestamp"].endswith("Z")
    
    def test_json_formatter_with_context(self):
        """Test JSON formatter with context."""
        formatter = JSONFormatter()
        
        # Create a log record with context
        record = logging.LogRecord(
            name="test_component",
            level=logging.INFO,
            pathname="test.py",
            lineno=10,
            msg="Test message",
            args=(),
            exc_info=None
        )
        record.context = {"symbol": "VNM", "price": 85000}
        
        # Format the record
        formatted = formatter.format(record)
        
        # Parse JSON
        log_data = json.loads(formatted)
        
        # Verify context is included
        assert "context" in log_data
        assert log_data["context"]["symbol"] == "VNM"
        assert log_data["context"]["price"] == 85000
    
    def test_json_formatter_with_exception(self):
        """Test JSON formatter with exception info."""
        formatter = JSONFormatter()
        
        # Create exception
        try:
            raise ValueError("Test exception")
        except ValueError:
            exc_info = True
            
            # Create a log record with exception
            record = logging.LogRecord(
                name="test_component",
                level=logging.ERROR,
                pathname="test.py",
                lineno=10,
                msg="Error occurred",
                args=(),
                exc_info=True
            )
            
            # Manually set exc_info
            import sys
            record.exc_info = sys.exc_info()
            
            # Format the record
            formatted = formatter.format(record)
            
            # Parse JSON
            log_data = json.loads(formatted)
            
            # Verify exception info is included
            assert "context" in log_data
            assert "error" in log_data["context"]
            assert "stack_trace" in log_data["context"]
            assert "ValueError" in log_data["context"]["stack_trace"]
            assert "Test exception" in log_data["context"]["error"]
    
    def test_structured_logger_methods(self):
        """Test all StructuredLogger methods."""
        log_stream = StringIO()
        handler = logging.StreamHandler(log_stream)
        handler.setFormatter(JSONFormatter())
        
        logger = StructuredLogger("test_component", use_json=True)
        logger.logger.handlers.clear()
        logger.logger.addHandler(handler)
        logger.logger.setLevel(logging.DEBUG)
        
        # Test each log level
        logger.debug("Debug message", context={"level": "debug"})
        logger.info("Info message", context={"level": "info"})
        logger.warning("Warning message", context={"level": "warning"})
        logger.error("Error message", context={"level": "error"})
        logger.critical("Critical message", context={"level": "critical"})
        
        # Get all log output
        log_output = log_stream.getvalue()
        log_lines = [line for line in log_output.strip().split('\n') if line]
        
        # Verify we have 5 log entries
        assert len(log_lines) == 5
        
        # Verify each log level
        levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        for i, line in enumerate(log_lines):
            log_data = json.loads(line)
            assert log_data["level"] == levels[i]
            assert log_data["component"] == "test_component"
