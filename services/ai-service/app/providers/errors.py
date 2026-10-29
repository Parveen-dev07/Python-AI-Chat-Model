class AIProviderError(RuntimeError):
    """Raised when the configured AI provider fails to complete a request."""


class AIProviderTimeoutError(AIProviderError):
    """Raised when the AI provider does not respond in time."""
