#!/usr/bin/env python3
"""
Run all tests for the IndoxRouter application.
"""

import os
import sys
import logging
import pytest
from pathlib import Path

# Add the parent directory to sys.path
sys.path.append(str(Path(__file__).parent.parent))

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def main():
    """Run all tests."""
    try:
        # Get the tests directory
        tests_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "tests")

        # Run the tests
        logger.info("Running tests...")
        result = pytest.main(
            [
                tests_dir,
                "--cov=indoxRouter",
                "--cov-report=term",
                "--cov-report=html",
                "-v",
            ]
        )

        # Check the result
        if result == 0:
            logger.info("All tests passed!")
        else:
            logger.error("Some tests failed.")
            sys.exit(1)
    except Exception as e:
        logger.error(f"Error running tests: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
