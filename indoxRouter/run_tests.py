#!/usr/bin/env python
"""
Test runner script for indoxRouter client tests.
This script uses pytest to run unit tests, integration tests, or both.

Usage:
    python run_tests.py [--unit] [--integration] [--all] [--coverage] [--verbose] [--server URL]

Options:
    --unit          Run only unit tests
    --integration   Run only integration tests
    --all           Run all tests (default)
    --coverage      Generate test coverage report
    --verbose       Show more detailed test output
    --server URL    Specify server URL for integration tests
"""

import os
import sys
import argparse
import subprocess
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def run_tests(test_type="all", coverage=False, verbose=False, server_url=None):
    """Run tests using pytest based on the specified type."""
    # Get the base directory of the package
    base_dir = Path(__file__).parent
    tests_dir = base_dir / "tests"

    # Build pytest command
    pytest_cmd = ["pytest"]

    # Add test type specific arguments
    if test_type == "unit":
        pytest_cmd.append(str(tests_dir / "unit"))
        logger.info("Running unit tests")
    elif test_type == "integration":
        # Check if required environment variables are set for integration tests
        if not os.environ.get("INDOX_ROUTER_API_KEY"):
            logger.error(
                "Integration tests require INDOX_ROUTER_API_KEY environment variable. "
                "Please set it before running integration tests."
            )
            return 1

        # Set server URL if provided
        if server_url:
            logger.info(f"Using server URL: {server_url}")
            os.environ["INDOX_ROUTER_BASE_URL"] = server_url

        # Enable live tests
        os.environ["RUN_LIVE_TESTS"] = "1"

        pytest_cmd.append(str(tests_dir / "integration"))
        logger.info("Running integration tests")
    else:  # all tests
        pytest_cmd.append(str(tests_dir))
        logger.info("Running all tests")

        # Set server URL for integration tests if provided
        if server_url:
            logger.info(f"Using server URL: {server_url}")
            os.environ["INDOX_ROUTER_BASE_URL"] = server_url
            os.environ["RUN_LIVE_TESTS"] = "1"

    # Add coverage if requested
    if coverage:
        pytest_cmd.extend(
            [
                "--cov=indoxRouter",
                "--cov-report=term",
                "--cov-report=html:coverage_html",
            ]
        )
        logger.info("Generating coverage report")

    # Add verbosity if requested
    if verbose:
        pytest_cmd.append("-v")

    # Run pytest and capture the return code
    logger.info(f"Running command: {' '.join(pytest_cmd)}")
    try:
        result = subprocess.run(pytest_cmd, check=False)
        return result.returncode
    except Exception as e:
        logger.error(f"Error running tests: {e}")
        return 1


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
        "--coverage", action="store_true", help="Generate test coverage report"
    )
    parser.add_argument(
        "--verbose", action="store_true", help="Show more detailed test output"
    )
    parser.add_argument(
        "--server",
        metavar="URL",
        help="Specify server URL for integration tests (e.g., http://91.107.253.133:8000)",
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
    sys.exit(run_tests(test_type, args.coverage, args.verbose, args.server))
