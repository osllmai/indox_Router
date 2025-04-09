"""
Patch for bcrypt to fix compatibility with passlib.
This file adds the missing __about__ attribute to bcrypt module.
"""

import sys
import logging
from importlib.metadata import version

logger = logging.getLogger(__name__)


def patch_bcrypt():
    """
    Patch bcrypt to work with passlib.

    Newer versions of bcrypt removed the __about__ attribute that passlib looks for.
    This patch adds it back as a mock object.
    """
    try:
        import bcrypt

        if not hasattr(bcrypt, "__about__"):
            # Create a mock __about__ module
            class AboutModule:
                __version__ = version("bcrypt")

            # Add the mock to bcrypt
            bcrypt.__about__ = AboutModule()
            logger.info(
                f"Patched bcrypt module with version {bcrypt.__about__.__version__}"
            )
        return True
    except Exception as e:
        logger.error(f"Failed to patch bcrypt: {e}")
        return False
