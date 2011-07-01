
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
    """
    Run this test by calling "python -m test.lastrecordedtest" from the 
    cadnano2 root directory.
    """
    def setUp(self):
        CadnanoGuiTestCase.setUp(self)

    def tearDown(self):
        CadnanoGuiTestCase.tearDown(self)

    def testMethod(self):
        # Create part
        partButton = self.mainWindow.topToolBar.widgetForAction(self.mainWindow.actionNewHoneycombPart)
        self.click(partButton)

        # Init refs
        sgi = self.documentController.sliceGraphicsItem
        phg = self.documentController.pathHelixGroup
        ash = self.documentController.pathHelixGroup.activeSliceHandle()

        # Playback user input
        self.mousePress(sgi.getSliceHelixByCoord(0, 0), position=QPoint(18, 5), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.slicescene)
        self.mouseMove(sgi.getSliceHelixByCoord(0, 0), position=QPoint(18, 9), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.slicescene)
        self.mouseRelease(sgi.getSliceHelixByCoord(0, 0), position=QPoint(18, 9), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.slicescene)
        self.mousePress(sgi.getSliceHelixByCoord(0, 1), position=QPoint(11, 10), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.slicescene)
        self.mouseMove(sgi.getSliceHelixByCoord(0, 1), position=QPoint(11, 12), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.slicescene)
        self.mouseMove(sgi.getSliceHelixByCoord(0, 1), position=QPoint(11, 15), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.slicescene)
        self.mouseRelease(sgi.getSliceHelixByCoord(0, 1), position=QPoint(11, 15), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.slicescene)
        self.mousePress(ash, position=QPoint(8, 118), modifiers=Qt.AltModifier|Qt.ShiftModifier, qgraphicsscene=self.mainWindow.pathscene)
        self.mouseRelease(ash, position=QPoint(8, 118), modifiers=Qt.AltModifier|Qt.ShiftModifier, qgraphicsscene=self.mainWindow.pathscene)
        self.mousePress(phg.getPathHelix(0), position=QPoint(470, 14), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
        self.mouseRelease(phg.getPathHelix(0), position=QPoint(470, 14), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)

        self.debugHere()
        # Verify model for correctness
        refvh0 = """0 Scaffold: _,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,1:22 1:23,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,_\n0 Staple:   _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_"""
        self.assertEqual(refvh0, repr(self.app.v[0]))
        refvh1 = """1 Scaffold: _,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,0:22 0:23,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,_\n1 Staple:   _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_"""
        self.assertEqual(refvh1, repr(self.app.v[1]))


if __name__ == '__main__':
    print "Running Last Recorded Test"
    test.cadnanoguitestcase.main()

