#!/usr/bin/env python
"""
Test runner script for indoxRouter client tests.
This script provides options to run unit tests, integration tests, or both.

Usage:
    python run_tests.py [--unit] [--integration] [--all] [--verbose]

Options:
    --unit          Run only unit tests
    --integration   Run only integration tests
    --all           Run all tests (default)
    --verbose       Show more detailed test output
"""

import os
import sys
import unittest
import argparse
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Ensure the client package is in the path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))


def run_tests(test_type="all", verbose=False):
    """Run tests based on the specified type."""
    test_dir = Path(__file__).parent / "tests"

    # Create test loader
    loader = unittest.TestLoader()

    # Set up test suite
    suite = unittest.TestSuite()

    # Add tests to suite based on test_type
    if test_type in ["unit", "all"]:
        unit_dir = test_dir / "unit"
        if unit_dir.exists():
            unit_tests = loader.discover(str(unit_dir), pattern="test_*.py")
            suite.addTests(unit_tests)
            logger.info(f"Added unit tests from {unit_dir}")
        else:
            logger.warning(f"Unit test directory {unit_dir} not found")

    if test_type in ["integration", "all"]:
        # Check if required environment variables are set
        if not os.environ.get("INDOX_ROUTER_API_KEY"):
            logger.error(
                "Integration tests require INDOX_ROUTER_API_KEY environment variable. "
                "Please set it before running integration tests."
            )
            if test_type == "integration":
                return 1
        else:
            integration_dir = test_dir / "integration"
            if integration_dir.exists():
                integration_tests = loader.discover(
                    str(integration_dir), pattern="test_*.py"
                )
                suite.addTests(integration_tests)
                logger.info(f"Added integration tests from {integration_dir}")
            else:
                logger.warning(
                    f"Integration test directory {integration_dir} not found"
                )

    # Run the tests
    verbosity = 2 if verbose else 1
    runner = unittest.TextTestRunner(verbosity=verbosity)
    result = runner.run(suite)

    # Return exit code based on test results
    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Run indoxRouter client tests")

    # Add test type options
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--unit", action="store_true", help="Run only unit tests")
    group.add_argument(
        "--integration", action="store_true", help="Run only integration tests"
    )
    group.add_argument("--all", action="store_true", help="Run all tests")

    # Add other options
    parser.add_argument(
        "--verbose", action="store_true", help="Show more detailed test output"
    )

    args = parser.parse_args()

    # Determine test type
    if args.unit:
        test_type = "unit"
    elif args.integration:
        test_type = "integration"
    else:
        test_type = "all"

    # Run tests and exit with appropriate code
    sys.exit(run_tests(test_type, args.verbose))
