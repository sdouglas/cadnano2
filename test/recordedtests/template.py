# The MIT License
#
# Copyright (c) 2011 Wyss Institute at Harvard University
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#
# http://www.opensource.org/licenses/mit-license.php

"""
template.py

Created by Shawn Douglas on 2011-06-28.
"""

from test.cadnanoguitestcase import CadnanoGuiTestCase


class RecordedTests(CadnanoGuiTestCase):
    """
    Functional tests are end-to-end tests that simulate user interaction
    with the interface and verify that the final outputs (e.g. staple
    sequences) are correct.

    Run these tests by calling "python -m test.functionaltests" from cadnano2
    root directory.
    """
    def setUp(self):
        """
        The setUp method is called before running any test. It is used
        to set the general conditions for the tests to run correctly.
        """
        CadnanoGuiTestCase.setUp(self)
        # Add extra initialization here

    def tearDown(self):
        """
        The tearDown method is called at the end of running each test,
        generally used to clean up any objects created in setUp
        """
        CadnanoGuiTestCase.tearDown(self)
        # Add functional-test-specific cleanup here

    def testMethod(self):
        """Gets overrided in runall.py"""
        pass

    def testMethod1(self):
        """Gets overrided in runall.py"""
        pass

