#!/usr/bin/env python
"""
Main test runner script for the entire IndoxRouter application.
This script provides options to run tests for the client, server, or both.

Usage:
    python run_all_tests.py [--client] [--server] [--all] [--unit] [--integration] [--verbose]

Options:
    --client        Run only client tests
    --server        Run only server tests
    --all           Run all tests (default)
    --unit          Run only unit tests
    --integration   Run only integration tests
    --verbose       Show more detailed test output
"""

import os
import sys
import subprocess
import argparse
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def run_client_tests(test_type="all", verbose=False):
    """Run client tests."""
    client_dir = Path(__file__).parent / "indoxRouter_client"
    run_tests_script = client_dir / "run_tests.py"

    if not run_tests_script.exists():
        logger.error(f"Client test runner script not found at {run_tests_script}")
        return 1

    # Build command
    cmd = [sys.executable, str(run_tests_script)]
    if test_type == "unit":
        cmd.append("--unit")
    elif test_type == "integration":
        cmd.append("--integration")
    else:
        cmd.append("--all")
    if verbose:
        cmd.append("--verbose")

    logger.info(f"Running client tests with command: {' '.join(cmd)}")

    # Run tests
    result = subprocess.run(cmd, cwd=str(client_dir))
    return result.returncode


def run_server_tests(test_type="all", verbose=False):
    """Run server tests."""
    server_dir = Path(__file__).parent / "indoxRouter_server"
    run_tests_script = server_dir / "run_tests.py"

    if not run_tests_script.exists():
        logger.error(f"Server test runner script not found at {run_tests_script}")
        return 1

    # Build command
    cmd = [sys.executable, str(run_tests_script)]
    if test_type == "unit":
        cmd.append("--unit")
    elif test_type == "integration":
        cmd.append("--integration")
    else:
        cmd.append("--all")
    if verbose:
        cmd.append("--verbose")

    logger.info(f"Running server tests with command: {' '.join(cmd)}")

    # Run tests
    result = subprocess.run(cmd, cwd=str(server_dir))
    return result.returncode


def run_all_tests(component="all", test_type="all", verbose=False):
    """Run all specified tests."""
    exit_code = 0

    if component in ["client", "all"]:
        logger.info("Running client tests...")
        client_result = run_client_tests(test_type, verbose)
        if client_result != 0:
            exit_code = client_result
        logger.info(f"Client tests {'passed' if client_result == 0 else 'failed'}")

    if component in ["server", "all"]:
        logger.info("Running server tests...")
        server_result = run_server_tests(test_type, verbose)
        if server_result != 0:
            exit_code = server_result
        logger.info(f"Server tests {'passed' if server_result == 0 else 'failed'}")

    return exit_code


if __name__ == "__main__":
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Run IndoxRouter tests")

    # Add component options
    component_group = parser.add_mutually_exclusive_group()
    component_group.add_argument(
        "--client", action="store_true", help="Run only client tests"
    )
    component_group.add_argument(
        "--server", action="store_true", help="Run only server tests"
    )
    component_group.add_argument("--all", action="store_true", help="Run all tests")

    # Add test type options
    test_type_group = parser.add_mutually_exclusive_group()
    test_type_group.add_argument(
        "--unit", action="store_true", help="Run only unit tests"
    )
    test_type_group.add_argument(
        "--integration", action="store_true", help="Run only integration tests"
    )

    # Add other options
    parser.add_argument(
        "--verbose", action="store_true", help="Show more detailed test output"
    )

    args = parser.parse_args()

    # Determine component
    if args.client:
        component = "client"
    elif args.server:
        component = "server"
    else:
        component = "all"

    # Determine test type
    if args.unit:
        test_type = "unit"
    elif args.integration:
        test_type = "integration"
    else:
        test_type = "all"

    # Run tests and exit with appropriate code
    sys.exit(run_all_tests(component, test_type, args.verbose))
