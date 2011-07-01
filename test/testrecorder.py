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
recorder.py

Created by Shawn on 2011-06-30.
"""

import os
import glob
from cadnano import app
from model.enum import LatticeType
import util

util.qtWrapImport('QtCore', globals(), ['Qt', 'QPoint', 'QPointF',\
                                        'QEvent', 'pyqtSlot'])


class TestRecorder(object):
    """
    TestRecorder can be used to auto-generate functional tests based on
    user input.

    It is currently set up for specific workflow, which assumes the first
    step is creating a part, followed by mousePress, mouseMove, and
    mouseRelease events in the slice and path views.
    
    INSTRUCTIONS:
    To record a new test, call "python main.py -r" from the cadnano2
    root directory. The resulting test will be saved in two places:
    
    1. In test/recordedtests/ as recordedtest_nnn.py for running by hudson
    2. In test/lastrecordedtest.py for command line testing.
    """
    def __init__(self):
        self.ops = []  # user operations
        self.sh = {}  # slicehelix dict
        self.ph = {}  # pathhelix dict
        self.seenActiveSliceHandle = False
        self.latticeType = None

    def sliceSceneEvent(self, event, coord):
        target = "sgi.getSliceHelixByCoord(%d, %d)" % (coord[0], coord[1])
        op = self.getOp(target, event, "slicescene")
        if op:
            self.ops.append(op)

    def pathSceneEvent(self, event, num):
        target = "phg.getPathHelix(%s)" % num
        op = self.getOp(target, event, "pathscene")
        if op:
            self.ops.append(op)

    def ashSceneEvent(self, event):
        op = self.getOp("ash", event, "pathscene")
        if op:
            self.ops.append(op)

    def getOp(self, target, event, scene):
        """Convert the event info into a string adding to the ops list."""
        type = None
        if event.type() == QEvent.GraphicsSceneMousePress:
            type = "mousePress"
        if event.type() == QEvent.GraphicsSceneMouseMove:
            type = "mouseMove"
        if event.type() == QEvent.GraphicsSceneMouseRelease:
            type = "mouseRelease"
        if type:  # did we recognize the event type?
            s = """self.%s(%s, position=QPoint(%d, %d), modifiers=%s, qgraphicsscene=self.mainWindow.%s)\n""" \
                                % (type, target,\
                                   event.pos().toPoint().x(),\
                                   event.pos().toPoint().y(),\
                                   self.getModifierString(event),\
                                   scene)
            return s
        else:
            return None

    def getModifierString(self, event):
        mods = []
        if (event.modifiers() & Qt.AltModifier):
            mods.append("Qt.AltModifier")
        if (event.modifiers() & Qt.ShiftModifier):
            mods.append("Qt.ShiftModifier")
        if len(mods) > 0:
            modifiers = '|'.join(mods)
        else:
            modifiers = "Qt.NoModifier"
        return modifiers

    def setPart(self, latticeType):
        self.latticeType = latticeType

    def createPart(self, indent):
        if self.latticeType == LatticeType.Honeycomb:
            ret = indent + "partButton = self.mainWindow.topToolBar.widgetForAction(self.mainWindow.actionNewHoneycombPart)\n" + indent + "self.click(partButton)\n"
        else:
            ret = indent + "partButton = self.mainWindow.topToolBar.widgetForAction(self.mainWindow.actionNewSquarePart)\n" + indent + "self.click(partButton)\n"
        return ret

    def createUserInput(self, indent):
        return indent + indent.join(self.ops)

    def checkAgainstModel(self, indent):
        s = ""
        for num in app().v.keys():
            r = "\\n".join(repr(app().v[num]).split("\n"))
            s = s + indent + "refvh%d = \"\"\"%s\"\"\"\n" % (num, r)
            s = s + indent + "self.assertEqual(refvh%d, repr(self.app.v[%d]))\n" % (num, num)
        return s

    def generateTest(self):
        """docstring for printTest"""
        if self.latticeType == None:
            return # nothing to record

        # build the new test string
        indent = "".join(" " for i in range(4))
        newtest = self.testTemplate % (self.createPart(indent),\
                                       self.createUserInput(indent),\
                                       self.checkAgainstModel(indent))
        # write to the next file
        # oldtests = glob.glob("test/recordedtests/recordedtest_*.py")  # get all the recorded tests
        # name = "test/recordedtests/recordedtest_%03d.py" % len(oldtests)
        # f = open(name, 'w')
        # f.write(newtest)
        # f.close()

        indent2 = "".join(" " for i in range(8))
        newtest2 = self.testTemplate2 % (self.createPart(indent2),\
                                       self.createUserInput(indent2),\
                                       self.checkAgainstModel(indent2))
        name = "test/lastrecordedtest.py"
        f = open(name, 'w')
        f.write(newtest2)
        f.close()

    testTemplate = """
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

from PyQt4.QtCore import Qt, QPoint


def testMethod(self):
    # Create part
%s
    # Init refs
    sgi = self.documentController.sliceGraphicsItem
    phg = self.documentController.pathHelixGroup
    ash = self.documentController.pathHelixGroup.activeSliceHandle()

    # Playback user input
%s
    # Verify model for correctness
%s
    #self.debugHere()
"""

    testTemplate2 = """
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


import sys
from PyQt4.QtCore import *
from PyQt4.QtGui import *
import test.cadnanoguitestcase
from test.cadnanoguitestcase import CadnanoGuiTestCase

sys.path.insert(0, '.')


class LastRecordedTest(CadnanoGuiTestCase):
    \"\"\"
    Run this test by calling "python -m test.lastrecordedtest" from the 
    cadnano2 root directory.
    \"\"\"
    def setUp(self):
        CadnanoGuiTestCase.setUp(self)

    def tearDown(self):
        CadnanoGuiTestCase.tearDown(self)

    def testMethod(self):
        # Create part
%s
        # Init refs
        sgi = self.documentController.sliceGraphicsItem
        phg = self.documentController.pathHelixGroup
        ash = self.documentController.pathHelixGroup.activeSliceHandle()

        # Playback user input
%s
        # Verify model for correctness
%s
        #self.debugHere()

if __name__ == '__main__':
    print "Running Last Recorded Test"
    test.cadnanoguitestcase.main()

"""