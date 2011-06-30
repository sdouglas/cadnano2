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
from cadnano import app
from model.enum import LatticeType
import util

util.qtWrapImport('QtCore', globals(), ['Qt', 'QPoint', 'QPointF',\
                                        'QEvent', 'pyqtSlot'])


class TestRecorder(object):
    """
    TestRecorded can be used to auto-generate functional tests based on
    user input.

    It is currently set up for specific workflow, which assumes the first
    step is creating a part, followed by mousePress, mouseMove, and
    mouseRelease events in the slice and path views.
    """
    def __init__(self):
        self.ops = []  # user operations
        self.sh = {}  # slicehelix dict
        self.ph = {}  # pathhelix dict
        self.seenActiveSliceHandle = False
        self.latticeType = None

    def sliceSceneEvent(self, event, coord):
        target = "sh_%d_%d" % (coord[0], coord[1])
        op = self.getOp(target, event)
        if op:
            if not coord in self.sh:
                self.sh[coord] = True  # save to later Init SliceHelix refs
            self.ops.append(op)

    def pathSceneEvent(self, event, num):
        target = "ph%s" % num
        op = self.getOp(target, event)
        if op:
            if not num in self.ph:
                self.ph[num] = True  # save to later Init PathHelix refs
            self.ops.append(op)

    def ashSceneEvent(self, event):
        if not self.seenActiveSliceHandle:
            self.seenActiveSliceHandle = True
            str = """\n        # Set up ActiveSliceHandle\n        activeSliceHandle = self.documentController.pathHelixGroup.activeSliceHandle()\n"""
            self.ops.append(str)
        op = self.getOp("activeSliceHandle", event)
        if op:
            self.ops.append(op)

    def getOp(self, target, event):
        """Convert the  for getOp"""
        type = None
        if event.type() == QEvent.GraphicsSceneMousePress:
            type = "mousePress"
        if event.type() == QEvent.GraphicsSceneMouseMove:
            type = "mouseMove"
        if event.type() == QEvent.GraphicsSceneMouseRelease:
            type = "mouseRelease"
        if type:  # did we recognize the event type?
            s = """        self.%s(%s, position=QPoint(%d, %d), modifiers=%s, qgraphicsscene=self.mainWindow.pathscene)\n""" \
                                % (type, target,\
                                   event.pos().toPoint().x(),\
                                   event.pos().toPoint().y(),\
                                   self.getModifierString(event))
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

    def createPart(self):
        if self.latticeType == LatticeType.Honeycomb:
            ret = """        partButton = self.mainWindow.topToolBar.widgetForAction(self.mainWindow.actionNewHoneycombPart)
        self.click(partButton)\n"""
        else:
            ret = """        partButton = self.mainWindow.topToolBar.widgetForAction(self.mainWindow.actionNewSquarePart)
        self.click(partButton)\n"""
        return ret

    def createSliceHelixRefs(self):
        s = "        sgi = self.documentController.sliceGraphicsItem\n"
        for coord in sorted(self.sh.keys()):
            s = s + "        sh_%d_%d = sgi.getSliceHelixByCoord(%d, %d)\n" % (coord[0], coord[1], coord[0], coord[1])
        return s

    def createPathHelixRefs(self):
        s = "        phg = self.documentController.pathHelixGroup\n"
        for num in sorted(self.ph.keys()):
            s = s + "        ph%d = phg.getPathHelix(%d)\n" % (num, num)
        return s

    def createUserInput(self):
        return "".join(self.ops)

    def checkAgainstModel(self):
        s = ""
        for num in app().v.keys():
            r = "\\n".join(repr(app().v[num]).split("\n"))
            s = s + "        refvh%d = \"\"\"%s\"\"\"\n" % (num, r)
            s = s + "        self.assertEqual(refvh%d, repr(self.app.v[%d]))\n" % (num, num)
        return s

    def generateTest(self):
        """docstring for printTest"""
        if self.latticeType == None:
            return # nothing to record

        # build the new test string
        newtest = self.testTemplate % (self.createPart(),\
                                       self.createSliceHelixRefs(),\
                                       self.createPathHelixRefs(),\
                                       self.createUserInput(),\
                                       self.checkAgainstModel())
        # write to the next file
        oldtests = os.listdir("test/recordedtests")
        name = "test/recordedtests/recordedtest_%03d.py" % (len(oldtests)-2)  # ignore init and template
        f = open(name, 'w')
        f.write(newtest)
        f.close()

    testTemplate = """
from template import RecordedTests

    def testMethod(self):
        # Create part
%s
        # Init SliceHelix refs
        sliceGraphicsItem = self.documentController.sliceGraphicsItem
%s
        # Init PathHelix refs
        pathHelixGroup = self.documentController.pathHelixGroup
%s
        # Playback user input
%s
        # Verify model for correctness
%s
        self.debugHere()
"""
