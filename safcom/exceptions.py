class SafcomError(Exception):
    """Base exception for all safcom errors."""
    pass

class AuthError(SafcomError):
    """Raised when M-Pesa authentication fails."""
    pass

class APIError(SafcomError):
    """Raised when the M-Pesa API returns an error response."""
    def __init__(self, message: str, response_code: str | None = None):
        self.response_code = response_code
        super().__init__(f"[{response_code}] {message}" if response_code else message)

class ValidationError(SafcomError):
    """Raised when input validation fails."""
    pass
