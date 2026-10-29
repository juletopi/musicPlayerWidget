"""
Custom exceptions for the music widget application.

Provides specific exception types for better error handling and user feedback.
"""

from __future__ import annotations


class MusicWidgetError(Exception):
    """Base exception for all music widget errors."""

    def __init__(self, message: str, status_code: int = 500, code: str = "unknown"):
        self.message = message
        self.status_code = status_code
        # Stable identifier used for translations, headers and /health/auth
        self.code = code
        super().__init__(self.message)


class ConfigurationError(MusicWidgetError):
    """Raised when required configuration is missing or invalid."""

    def __init__(self, message: str, code: str = "unknown"):
        super().__init__(message, status_code=500, code=code)


class ServiceNotConfiguredError(ConfigurationError):
    """Raised when no music service is configured."""

    def __init__(self):
        super().__init__(
            "No music service configured. "
            "Set SPOTIFY_* or LAST_FM_* environment variables.",
            code="not_configured",
        )


class AuthenticationError(MusicWidgetError):
    """Raised when authentication with a music service fails."""

    def __init__(self, service: str, details: str = "", code: str = "auth_failed"):
        message = f"Authentication failed with {service}"
        if details:
            message += f": {details}"
        super().__init__(message, status_code=401, code=code)


class APIError(MusicWidgetError):
    """Raised when an API request fails."""

    def __init__(self, service: str, status_code: int, details: str = "", code: str = "api_error"):
        message = f"{service} API error (HTTP {status_code})"
        if details:
            message += f": {details}"
        super().__init__(message, status_code=502, code=code)


class NoTracksError(MusicWidgetError):
    """Raised when no tracks are available from the service."""

    def __init__(self, service: str):
        super().__init__(
            f"No tracks available from {service}",
            status_code=204,
            code="no_tracks",
        )


class ImageProcessingError(MusicWidgetError):
    """Raised when image loading or processing fails."""

    def __init__(self, details: str = ""):
        message = "Failed to process album art"
        if details:
            message += f": {details}"
        super().__init__(message, status_code=500)


class InvalidParameterError(MusicWidgetError):
    """Raised when a request parameter is invalid."""

    def __init__(self, param_name: str, details: str = ""):
        message = f"Invalid parameter: {param_name}"
        if details:
            message += f" - {details}"
        super().__init__(message, status_code=400)
