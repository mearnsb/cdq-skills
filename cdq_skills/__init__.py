"""CDQ Skills - Collibra Data Quality API client and skills."""

__version__ = "1.0.0"

from .client import main
from .auth import get_config, get_headers, get_token, test_connection

__all__ = ["main", "get_config", "get_headers", "get_token", "test_connection"]
