"""
Security utilities for indoxRouter.
This module contains functions for enhancing API security.
"""

import re
import logging
import time
from typing import Dict, Any, Optional, List, Tuple
import ipaddress
from fastapi import Request

from app.core.config import settings
from app.db.database import update_api_key_last_used

logger = logging.getLogger(__name__)

# IP allowlist and blocklist
IP_ALLOWLIST = set()
IP_BLOCKLIST = set()

# Suspicious activity tracking
FAILED_LOGIN_ATTEMPTS = {}
SUSPICIOUS_ACTIVITY = {}


def load_ip_lists():
    """Load IP allow and block lists from settings."""
    global IP_ALLOWLIST, IP_BLOCKLIST

    # Clear existing lists
    IP_ALLOWLIST = set()
    IP_BLOCKLIST = set()

    # Check if IP filtering is enabled
    if not settings.ENABLE_IP_FILTERING:
        logger.info("IP filtering is disabled")
        return

    # Load allowlist
    if hasattr(settings, "IP_ALLOWLIST") and settings.IP_ALLOWLIST:
        try:
            IP_ALLOWLIST = set(settings.IP_ALLOWLIST)
            logger.info(f"Loaded {len(IP_ALLOWLIST)} IP addresses in allowlist")
        except Exception as e:
            logger.error(f"Error loading IP allowlist: {e}")
    else:
        logger.info(
            "IP allowlist is empty, all IPs will be allowed unless in blocklist"
        )

    # Load blocklist
    if hasattr(settings, "IP_BLOCKLIST") and settings.IP_BLOCKLIST:
        try:
            IP_BLOCKLIST = set(settings.IP_BLOCKLIST)
            logger.info(f"Loaded {len(IP_BLOCKLIST)} IP addresses in blocklist")
        except Exception as e:
            logger.error(f"Error loading IP blocklist: {e}")
    else:
        logger.info("IP blocklist is empty, no IPs will be blocked by default")


def is_ip_allowed(ip_address: str) -> bool:
    """
    Check if an IP address is allowed based on allow/block lists.

    Args:
        ip_address: The IP address to check.

    Returns:
        True if allowed, False if blocked.
    """
    # If allowlist is empty, allow all non-blocked IPs
    if not IP_ALLOWLIST:
        return ip_address not in IP_BLOCKLIST

    # If allowlist is set, only allow IPs in the list
    return ip_address in IP_ALLOWLIST and ip_address not in IP_BLOCKLIST


def validate_api_key_format(api_key: str) -> bool:
    """
    Validate the format of an API key.

    Args:
        api_key: The API key to validate.

    Returns:
        True if valid format, False otherwise.
    """
    # Accept both formats: inr- prefix and indox_r_ prefix
    pattern = r"^(inr-[a-zA-Z0-9]{32}|indox_r_[a-zA-Z0-9_-]+)$"
    return bool(re.match(pattern, api_key))


def track_api_key_usage(api_key_id: int, user_id: int, endpoint: str) -> None:
    """
    Track API key usage.

    Args:
        api_key_id: The API key ID.
        user_id: The user ID.
        endpoint: The endpoint being accessed.
    """
    if not api_key_id:
        return

    try:
        # Update last used timestamp for the API key
        update_api_key_last_used(api_key_id)
    except Exception as e:
        logger.error(f"Error updating API key usage: {e}")


def track_failed_login(ip_address: str, username: Optional[str] = None) -> None:
    """
    Track failed login attempts.

    Args:
        ip_address: The IP address of the request.
        username: The username that failed login.
    """
    current_time = time.time()

    # Track by IP
    if ip_address not in FAILED_LOGIN_ATTEMPTS:
        FAILED_LOGIN_ATTEMPTS[ip_address] = []

    # Add current attempt
    FAILED_LOGIN_ATTEMPTS[ip_address].append(current_time)

    # Clean up old attempts (older than 1 hour)
    FAILED_LOGIN_ATTEMPTS[ip_address] = [
        t
        for t in FAILED_LOGIN_ATTEMPTS[ip_address]
        if current_time - t < 3600  # 1 hour
    ]

    # If too many attempts, add to suspicious activity
    if len(FAILED_LOGIN_ATTEMPTS[ip_address]) >= 5:  # 5 attempts in 1 hour
        SUSPICIOUS_ACTIVITY[ip_address] = {
            "type": "failed_login",
            "count": len(FAILED_LOGIN_ATTEMPTS[ip_address]),
            "last_attempt": current_time,
            "username": username,
        }
        logger.warning(
            f"Suspicious activity detected: Multiple failed logins from {ip_address}"
        )


def is_suspicious(ip_address: str) -> bool:
    """
    Check if an IP address is suspicious.

    Args:
        ip_address: The IP address to check.

    Returns:
        True if suspicious, False otherwise.
    """
    if ip_address in SUSPICIOUS_ACTIVITY:
        # Clean up old activity (older than 24 hours)
        current_time = time.time()
        if (
            current_time - SUSPICIOUS_ACTIVITY[ip_address]["last_attempt"] > 86400
        ):  # 24 hours
            del SUSPICIOUS_ACTIVITY[ip_address]
            return False

        return True

    return False


def get_client_ip(request: Request) -> str:
    """
    Get the client IP address from a request.

    Args:
        request: The FastAPI request object.

    Returns:
        The client IP address.
    """
    # Try different headers
    forwarded_for = request.headers.get("X-Forwarded-For")
    if forwarded_for:
        # Get the first IP in the chain
        return forwarded_for.split(",")[0].strip()

    # Fall back to request client
    return request.client.host if request.client else "unknown"


# Initialize IP lists
load_ip_lists()
