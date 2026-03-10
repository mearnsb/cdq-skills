"""Shared authentication module for CDQ API.

Handles authentication for Collibra Data Quality API calls.
"""

import os
import time
from pathlib import Path
from typing import Optional

import requests
from dotenv import load_dotenv

# Suppress SSL warnings for self-signed certs
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Load .env from project root
_env_path = Path(__file__).parent.parent / ".env"
load_dotenv(_env_path)

# Token cache (simple in-memory cache)
_token_cache: dict = {"token": None, "expires_at": 0}


def get_env_var(name: str, required: bool = True) -> Optional[str]:
    """Get environment variable with optional validation."""
    value = os.getenv(name)
    if required and not value:
        raise ValueError(f"Required environment variable {name} is not set")
    return value


def get_config() -> dict:
    """Get all CDQ configuration from environment."""
    verify_ssl = get_env_var("DQ_VERIFY_SSL", required=False)
    return {
        "url": get_env_var("DQ_URL"),
        "username": get_env_var("DQ_USERNAME"),
        "password": get_env_var("DQ_PASSWORD"),
        "iss": get_env_var("DQ_ISS"),
        "cxn": get_env_var("DQ_CXN", required=False) or "BIGQUERY",
        "verify_ssl": verify_ssl.lower() not in ("false", "0", "no") if verify_ssl else True,
    }


def get_token(force_refresh: bool = False) -> str:
    """Get authentication token with caching.

    Args:
        force_refresh: Force token refresh even if cached token is valid

    Returns:
        Bearer token string
    """
    # Check cache (tokens valid for ~1 hour, refresh 5 min early)
    if not force_refresh and _token_cache["token"]:
        if time.time() < _token_cache["expires_at"] - 300:
            return _token_cache["token"]

    config = get_config()

    # Authenticate via /auth/signin
    auth_url = f"{config['url']}/auth/signin"
    payload = {
        "username": config["username"],
        "password": config["password"],
        "iss": config["iss"],
    }

    response = requests.post(
        auth_url,
        json=payload,
        headers={"Content-Type": "application/json"},
        verify=config["verify_ssl"]
    )
    response.raise_for_status()

    data = response.json()
    token = data.get("token")

    if not token:
        raise ValueError(f"No token in auth response: {data}")

    # Cache token (assume 1 hour expiry)
    _token_cache["token"] = token
    _token_cache["expires_at"] = time.time() + 3600

    return token


def get_headers() -> dict:
    """Get authorization headers for API requests."""
    token = get_token()
    return {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "Accept": "application/json",
    }


def test_connection() -> dict:
    """Test connection to CDQ API.

    Returns:
        dict with connection status and details
    """
    config = get_config()

    try:
        token = get_token()
        return {
            "success": True,
            "url": config["url"],
            "username": config["username"],
        }
    except Exception as e:
        return {
            "success": False,
            "url": config["url"],
            "error": str(e),
        }


if __name__ == "__main__":
    result = test_connection()
    print(result)