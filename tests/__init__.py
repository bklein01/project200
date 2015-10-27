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

    def assertHasAttribute(self, obj, attr_name):
        """Assert object has attribute.

        :param obj: mixed -- The object to test.
        :param attr_name: str -- The name of the attribute to find.

        :raise AssertionError if object does not contain the attribute specified.
        """
        if not hasattr(obj, attr_name):
            raise AssertionError("Object has no attribute: `" + attr_name + "`.")

    def assertHasAttributes(self, obj, attr_names):
        """Assert object has multiple attributes.

        :param obj: mixed -- The object to test.
        :param attr_names: list -- The names of the attributes to find.

        :raise AssertionError if object does not contain any of the specified
            attributes.
        """
        for attr_name in attr_names:
            self.assertHasAttribute(obj, attr_name)

    def assertIsJsonReady(self, obj):
        """Assert object is JSON ready.

        :param obj: mixed -- The object to test.

        :raise AssertionError if object does not dump to JSON without error.
        """
        try:
            json.dumps(obj)
        except Exception as e:
            raise AssertionError("Object not JSON-ready: " + str(e))


def main():
    unittest.main()

if __name__ == "main":
    main()

# ----------------------------------------------------------------------------
__version__ = 0.1
__license__ = "MIT"
__credits__ = ["zimmed"]
# ----------------------------------------------------------------------------
