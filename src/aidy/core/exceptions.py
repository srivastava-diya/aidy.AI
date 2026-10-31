"""Domain exceptions for aidy.AI multi-agent orchestration and tools."""


class AidyException(Exception):
    """Base exception for all aidy.AI domain errors."""
    pass


class ConfigurationError(AidyException):
    """Raised when environment or provider configuration is invalid or missing."""
    pass


class SecurityViolationError(AidyException):
    """Raised when an unsafe URL, SSRF vector, or prompt injection pattern is detected."""
    pass


class WebSearchError(AidyException):
    """Raised when web search querying fails or rate limits are exceeded."""
    pass


class WebRetrievalError(AidyException):
    """Raised when HTTP webpage fetching or content parsing fails."""
    pass


class VerificationError(AidyException):
    """Raised when fact-checking or claim cross-referencing encounters an unrecoverable failure."""
    pass


class BudgetExceededError(AidyException):
    """Raised when token usage or iteration limits exceed the configured safety budget."""
    pass
