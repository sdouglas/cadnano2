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
functionaltests.py

Created by Shawn Douglas on 2011-06-28.
"""

import sys
sys.path.insert(0, '.')

import time
from PyQt4.QtCore import *
from PyQt4.QtGui import *
import test.cadnanoguitestcase
from test.cadnanoguitestcase import CadnanoGuiTestCase
from cadnano import app as getAppInstance
from model.enum import StrandType
from model.virtualhelix import VirtualHelix


class FunctionalTests(CadnanoGuiTestCase):
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
        # Add your initialization here
        # self.app gives you a pointer to the application object
        getAppInstance().dontAskAndJustDiscardUnsavedChanges = True
        getAppInstance().initGui()

    def tearDown(self):
        """
        The tearDown method is called at the end of running each test,
        generally used to clean up any objects created in setUp
        """
        CadnanoGuiTestCase.tearDown(self)
        # Add your clean up here

    def testFunction1(self):
        # Create a new Honeycomb part
        newHoneycombPartButton = self.mainWindow.topToolBar.widgetForAction(\
                                       self.mainWindow.actionNewHoneycombPart)
        self.click(newHoneycombPartButton)

        sliceGraphicsItem = self.mainWindow.sliceroot.childItems()[0]
        print sliceGraphicsItem
        # Get the SliceHelix
        slicehelix1 = sliceGraphicsItem.getSliceHelixByCoord(0, 0)
        print slicehelix1, slicehelix1.isEnabled()
        self.click(slicehelix1, qgraphicsscene=self.mainWindow.slicescene)

        # time.sleep(5)  # Sleep for 1 second
        self.debugHere()  # Stop simulation and give control to user


if __name__ == '__main__':
    print "Running Functional Tests"
    test.cadnanoguitestcase.main()
