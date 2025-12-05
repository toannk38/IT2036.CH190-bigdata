class ConsumerError(Exception):
    """Base exception for consumer-related errors"""
    pass

class MongoDBConnectionError(ConsumerError):
    """Raised when MongoDB connection fails"""
    pass

class BatchProcessingError(ConsumerError):
    """Raised when batch processing fails"""
    pass

class DataValidationError(ConsumerError):
    """Raised when data validation fails"""
    pass

class RateLimitExceededError(ConsumerError):
    """Raised when rate limit is exceeded"""
    pass