#!/usr/bin/env python
"""Project unit testing library.

.. packageauthor: zimmed <zimmed@zimmed.io>

Exposes:
    :class TestCase -- The class that all tests must inherit from.
    :callable main -- The main procedure when script is run from the CLI.
    :package core -- Test package
    :package game -- Test package
"""

import unittest
import json


class TestCase(unittest.TestCase):
    """Base test case."""

    def assertHasAttribute(self, obj, attr_name, msg=None):
        """Assert object has attribute.

        :param obj: mixed -- The object to test.
        :param attr_name: str -- The name of the attribute to find.

        :raise AssertionError if object does not contain the attribute specified.
        """
        if not msg:
            msg = "Object has no attribute: `" + attr_name + "`."
        self.assertTrue(hasattr(obj, attr_name), msg)

    def assertHasAttributes(self, obj, attr_names, msg=None):
        """Assert object has multiple attributes.

        :param obj: mixed -- The object to test.
        :param attr_names: list -- The names of the attributes to find.

        :raise AssertionError if object does not contain any of the specified
            attributes.
        """
        for attr_name in attr_names:
            self.assertHasAttribute(obj, attr_name, msg)

    def assertIsJsonReady(self, obj, msg=None):
        """Assert object is JSON ready.

        :param obj: mixed -- The object to test.

        :raise AssertionError if object does not dump to JSON without error.
        """
        if not msg:
            msg = "Object is not JSON-ready."
        try:
            json.dumps(obj)
        except (TypeError, ValueError):
            raise AssertionError(msg)


def main():
    unittest.main()

if __name__ == "__main__":
    main()

# ----------------------------------------------------------------------------
__version__ = 0.2
__license__ = "MIT"
__credits__ = ["zimmed"]
# ----------------------------------------------------------------------------
