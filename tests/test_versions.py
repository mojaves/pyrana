#!/usr/bin/python

import pyrana
import unittest

class TestCommonData(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        pyrana.setup()

    def test_PlatformCPy3x(self):
        class MockPlat:
            def python_implementation(self):
                return 'CPython'
 
            def python_version_tuple(self):
                return ('3', '2')

        pyrana._enforce_platform(MockPlat())
        assert(True)

    def test_PlatformCPy31(self):
        class MockPlat:
            def python_implementation(self):
                return 'CPython'
 
            def python_version_tuple(self):
                return ('3', '1')
        
        with self.assertRaises(RuntimeError):
            pyrana._enforce_platform(MockPlat())

    def test_PlatformCPy2x(self):
        class MockPlat:
            def python_implementation(self):
                return 'CPython'
 
            def python_version_tuple(self):
                return ('2', '7')
        
        with self.assertRaises(RuntimeError):
            pyrana._enforce_platform(MockPlat())
