class VnstockError(Exception):
    """Base exception for vnstock wrapper"""
    pass

class RateLimitError(VnstockError):
    """Raised when rate limit is exceeded"""
    pass

class DataNotFoundError(VnstockError):
    """Raised when requested data is not found"""
    pass
