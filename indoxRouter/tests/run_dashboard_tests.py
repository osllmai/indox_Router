#!/usr/bin/env python3
"""
Run the dashboard tests.

This script runs the tests for the IndoxRouter dashboard.
"""

import os
import sys
import unittest

# Add the parent directory to the path to import from indoxRouter
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tests.test_dashboard import TestDashboard


def run_tests():
    """Run the dashboard tests."""
    # Create a test suite
    suite = unittest.TestSuite()

    # Add the dashboard tests
    suite.addTest(unittest.makeSuite(TestDashboard))

    # Run the tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # Return the result
    return result.wasSuccessful()


if __name__ == "__main__":
    # Run the tests
    success = run_tests()

    # Exit with the appropriate code
    sys.exit(0 if success else 1)
