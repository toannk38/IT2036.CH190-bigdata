"""
Property-based tests for error handling and logging.
"""

import json
import logging
import time
from io import StringIO
from datetime import datetime
from unittest.mock import Mock, patch
from hypothesis import given, strategies as st, settings
from src.logging_config import get_logger, StructuredLogger, JSONFormatter
from src.error_handling import (
    retry_with_exponential_backoff,
    CircuitBreaker,
    CircuitBreakerError,
    DeadLetterQueue
)


# Property 38: Error logging completeness
@given(
    component_name=st.text(min_size=1, max_size=50, alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd'), min_codepoint=65)),
    error_message=st.text(min_size=1, max_size=200),
    context_dict=st.dictionaries(
        keys=st.text(min_size=1, max_size=20, alphabet=st.characters(whitelist_categories=('Lu', 'Ll'), min_codepoint=65)),
        values=st.one_of(st.text(max_size=50), st.integers(), st.floats(allow_nan=False, allow_infinity=False)),
        max_size=5
    )
)
@settings(max_examples=100)
def test_error_logging_completeness(component_name, error_message, context_dict):
    """
    **Feature: vietnam-stock-ai-backend, Property 38: Error logging completeness**
    
    For any error encountered by any component, the error log should include 
    timestamp, component name, error message, and stack trace.
    
    **Validates: Requirements 13.1**
    """
    # Create a string buffer to capture log output
    log_stream = StringIO()
    handler = logging.StreamHandler(log_stream)
    handler.setFormatter(JSONFormatter())
    
    # Create logger with JSON format
    logger = StructuredLogger(component_name, use_json=True)
    logger.logger.handlers.clear()
    logger.logger.addHandler(handler)
    logger.logger.setLevel(logging.ERROR)
    
    # Simulate an error with exception info
    try:
        raise ValueError("Test error for logging")
    except ValueError:
        logger.error(error_message, context=context_dict, exc_info=True)
    
    # Get the logged output
    log_output = log_stream.getvalue()
    
    # Parse JSON log
    log_data = json.loads(log_output.strip())
    
    # Verify all required fields are present
    assert "timestamp" in log_data, "Log must include timestamp"
    assert "component" in log_data, "Log must include component name"
    assert "message" in log_data, "Log must include error message"
    assert "level" in log_data, "Log must include log level"
    
    # Verify component name matches
    assert log_data["component"] == component_name, "Component name must match"
    
    # Verify message matches
    assert log_data["message"] == error_message, "Error message must match"
    
    # Verify level is ERROR
    assert log_data["level"] == "ERROR", "Log level must be ERROR"
    
    # Verify timestamp format (ISO 8601)
    timestamp_str = log_data["timestamp"]
    assert timestamp_str.endswith("Z"), "Timestamp must be in UTC (end with Z)"
    # Verify it can be parsed
    datetime.fromisoformat(timestamp_str.replace("Z", "+00:00"))
    
    # Verify context is included
    if context_dict:
        assert "context" in log_data, "Log must include context when provided"
        for key in context_dict:
            assert key in log_data["context"], f"Context must include key {key}"
    
    # Verify stack trace is included when exc_info=True
    assert "context" in log_data, "Log must include context for exception"
    assert "stack_trace" in log_data["context"], "Log must include stack trace"
    assert "ValueError" in log_data["context"]["stack_trace"], "Stack trace must contain exception type"


# Additional test for non-exception errors
@given(
    component_name=st.text(min_size=1, max_size=50, alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd'), min_codepoint=65)),
    error_message=st.text(min_size=1, max_size=200)
)
@settings(max_examples=100)
def test_error_logging_without_exception(component_name, error_message):
    """
    Test that error logging works correctly even without exception info.
    """
    # Create a string buffer to capture log output
    log_stream = StringIO()
    handler = logging.StreamHandler(log_stream)
    handler.setFormatter(JSONFormatter())
    
    # Create logger with JSON format
    logger = StructuredLogger(component_name, use_json=True)
    logger.logger.handlers.clear()
    logger.logger.addHandler(handler)
    logger.logger.setLevel(logging.ERROR)
    
    # Log error without exception
    logger.error(error_message)
    
    # Get the logged output
    log_output = log_stream.getvalue()
    
    # Parse JSON log
    log_data = json.loads(log_output.strip())
    
    # Verify required fields
    assert "timestamp" in log_data
    assert "component" in log_data
    assert "message" in log_data
    assert "level" in log_data
    assert log_data["component"] == component_name
    assert log_data["message"] == error_message
    assert log_data["level"] == "ERROR"



# Property 31: Database retry with exponential backoff
@given(
    max_retries=st.integers(min_value=1, max_value=5),
    base_delay=st.floats(min_value=0.01, max_value=2.0),
    failure_count=st.integers(min_value=1, max_value=5)
)
@settings(max_examples=100, deadline=None)
def test_database_retry_exponential_backoff(max_retries, base_delay, failure_count):
    """
    **Feature: vietnam-stock-ai-backend, Property 31: Database retry with exponential backoff**
    
    For any failed database operation, retry attempts should occur with 
    exponentially increasing delays (e.g., 1s, 2s, 4s, 8s).
    
    **Validates: Requirements 9.5**
    """
    # Track call times to verify exponential backoff
    call_times = []
    attempt_count = [0]
    
    @retry_with_exponential_backoff(
        max_retries=max_retries,
        base_delay=base_delay,
        exceptions=(ValueError,)
    )
    def failing_database_operation():
        """Simulated database operation that fails."""
        call_times.append(time.time())
        attempt_count[0] += 1
        
        # Fail for the specified number of times, then succeed
        if attempt_count[0] <= failure_count:
            raise ValueError(f"Database connection failed (attempt {attempt_count[0]})")
        return "success"
    
    # Test case 1: Operation succeeds within retry limit
    if failure_count <= max_retries:
        result = failing_database_operation()
        assert result == "success", "Operation should eventually succeed"
        
        # Verify number of attempts
        assert len(call_times) == failure_count + 1, \
            f"Should have {failure_count + 1} attempts (failures + success)"
        
        # Verify exponential backoff delays
        if len(call_times) > 1:
            for i in range(1, len(call_times)):
                actual_delay = call_times[i] - call_times[i-1]
                expected_delay = base_delay * (2 ** (i-1))
                
                # Allow some tolerance for timing (±20%)
                min_delay = expected_delay * 0.8
                max_delay = expected_delay * 1.2
                
                assert min_delay <= actual_delay <= max_delay, \
                    f"Delay between attempt {i-1} and {i} should be ~{expected_delay}s, got {actual_delay}s"
    
    # Test case 2: Operation fails beyond retry limit
    else:
        # Reset for new test
        call_times.clear()
        attempt_count[0] = 0
        
        try:
            failing_database_operation()
            assert False, "Should have raised ValueError after max retries"
        except ValueError as e:
            # Verify it failed after max_retries + 1 attempts (initial + retries)
            assert len(call_times) == max_retries + 1, \
                f"Should have {max_retries + 1} attempts before giving up"
            
            # Verify exponential backoff was applied
            if len(call_times) > 1:
                for i in range(1, len(call_times)):
                    actual_delay = call_times[i] - call_times[i-1]
                    expected_delay = base_delay * (2 ** (i-1))
                    
                    # Allow some tolerance for timing (±20%)
                    min_delay = expected_delay * 0.8
                    max_delay = expected_delay * 1.2
                    
                    assert min_delay <= actual_delay <= max_delay, \
                        f"Delay between attempt {i-1} and {i} should be ~{expected_delay}s, got {actual_delay}s"


@given(
    max_retries=st.integers(min_value=2, max_value=5),
    base_delay=st.floats(min_value=0.01, max_value=1.0)
)
@settings(max_examples=50, deadline=None)
def test_retry_respects_max_delay(max_retries, base_delay):
    """
    Test that retry decorator respects max_delay parameter.
    """
    max_delay = 5.0
    call_times = []
    
    @retry_with_exponential_backoff(
        max_retries=max_retries,
        base_delay=base_delay,
        max_delay=max_delay,
        exceptions=(ValueError,)
    )
    def failing_operation():
        call_times.append(time.time())
        raise ValueError("Always fails")
    
    try:
        failing_operation()
    except ValueError:
        pass
    
    # Verify delays don't exceed max_delay
    if len(call_times) > 1:
        for i in range(1, len(call_times)):
            actual_delay = call_times[i] - call_times[i-1]
            # Allow small tolerance for timing
            assert actual_delay <= max_delay * 1.2, \
                f"Delay should not exceed max_delay ({max_delay}s), got {actual_delay}s"
