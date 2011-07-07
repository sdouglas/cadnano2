
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

        # Init buttons
        actionPathInsertButton = self.mainWindow.rightToolBar.widgetForAction(self.mainWindow.actionPathInsert)
        actionPathEraseButton = self.mainWindow.rightToolBar.widgetForAction(self.mainWindow.actionPathErase)

        # Playback user input
        self.mousePress(sgi.getSliceHelixByCoord(0, 6), position=QPoint(23, 14), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.slicescene)
        self.mouseRelease(sgi.getSliceHelixByCoord(0, 6), position=QPoint(23, 14), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.slicescene)
        self.mousePress(sgi.getSliceHelixByCoord(0, 7), position=QPoint(27, 16), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.slicescene)
        self.mouseRelease(sgi.getSliceHelixByCoord(0, 7), position=QPoint(27, 16), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.slicescene)
        self.mousePress(phg.getPathHelix(0), position=QPoint(452, 14), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
        self.mouseMove(phg.getPathHelix(0), position=QPoint(454, 14), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
        self.mouseMove(phg.getPathHelix(0), position=QPoint(456, 14), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
        self.mouseMove(phg.getPathHelix(0), position=QPoint(461, 14), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
        self.mouseMove(phg.getPathHelix(0), position=QPoint(470, 14), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
        self.mouseMove(phg.getPathHelix(0), position=QPoint(484, 14), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
        self.mouseMove(phg.getPathHelix(0), position=QPoint(498, 14), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
        self.mouseMove(phg.getPathHelix(0), position=QPoint(512, 14), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
        self.mouseMove(phg.getPathHelix(0), position=QPoint(529, 14), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
        self.mouseMove(phg.getPathHelix(0), position=QPoint(561, 16), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
        self.mouseMove(phg.getPathHelix(0), position=QPoint(582, 16), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
        self.mouseMove(phg.getPathHelix(0), position=QPoint(594, 16), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
        self.mouseMove(phg.getPathHelix(0), position=QPoint(598, 16), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
        self.mouseMove(phg.getPathHelix(0), position=QPoint(601, 16), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
        self.mouseRelease(phg.getPathHelix(0), position=QPoint(601, 16), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
        self.mousePress(phg.getPathHelix(1), position=QPoint(445, 26), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
        self.mouseMove(phg.getPathHelix(1), position=QPoint(447, 26), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
        self.mouseMove(phg.getPathHelix(1), position=QPoint(452, 26), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
        self.mouseMove(phg.getPathHelix(1), position=QPoint(454, 26), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
        self.mouseMove(phg.getPathHelix(1), position=QPoint(461, 26), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
        self.mouseMove(phg.getPathHelix(1), position=QPoint(468, 26), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
        self.mouseMove(phg.getPathHelix(1), position=QPoint(473, 26), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
        self.mouseMove(phg.getPathHelix(1), position=QPoint(480, 26), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
        self.mouseMove(phg.getPathHelix(1), position=QPoint(487, 26), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
        self.mouseMove(phg.getPathHelix(1), position=QPoint(494, 26), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
        self.mouseMove(phg.getPathHelix(1), position=QPoint(501, 26), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
        self.mouseMove(phg.getPathHelix(1), position=QPoint(508, 26), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
        self.mouseMove(phg.getPathHelix(1), position=QPoint(515, 26), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
        self.mouseMove(phg.getPathHelix(1), position=QPoint(522, 29), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
        self.mouseMove(phg.getPathHelix(1), position=QPoint(526, 29), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
        self.mouseMove(phg.getPathHelix(1), position=QPoint(533, 29), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
        self.mouseMove(phg.getPathHelix(1), position=QPoint(538, 29), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
        self.mouseMove(phg.getPathHelix(1), position=QPoint(545, 29), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
        self.mouseMove(phg.getPathHelix(1), position=QPoint(554, 29), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
        self.mouseMove(phg.getPathHelix(1), position=QPoint(559, 29), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
        self.mouseMove(phg.getPathHelix(1), position=QPoint(566, 29), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
        self.mouseMove(phg.getPathHelix(1), position=QPoint(568, 29), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
        self.mouseMove(phg.getPathHelix(1), position=QPoint(577, 29), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
        self.mouseMove(phg.getPathHelix(1), position=QPoint(589, 29), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
        self.mouseMove(phg.getPathHelix(1), position=QPoint(596, 29), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
        self.mouseMove(phg.getPathHelix(1), position=QPoint(608, 29), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
        self.mouseMove(phg.getPathHelix(1), position=QPoint(612, 29), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
        self.mouseMove(phg.getPathHelix(1), position=QPoint(615, 29), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
        self.mouseRelease(phg.getPathHelix(1), position=QPoint(615, 29), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
        self.mousePress(phg.getPathHelix(0), position=QPoint(470, 30), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
        self.mouseMove(phg.getPathHelix(0), position=QPoint(473, 30), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
        self.mouseMove(phg.getPathHelix(0), position=QPoint(482, 30), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
        self.mouseMove(phg.getPathHelix(0), position=QPoint(491, 30), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
        self.mouseMove(phg.getPathHelix(0), position=QPoint(505, 30), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
        self.mouseMove(phg.getPathHelix(0), position=QPoint(517, 33), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
        self.mouseMove(phg.getPathHelix(0), position=QPoint(526, 33), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
        self.mouseMove(phg.getPathHelix(0), position=QPoint(538, 33), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
        self.mouseMove(phg.getPathHelix(0), position=QPoint(552, 33), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
        self.mouseMove(phg.getPathHelix(0), position=QPoint(564, 33), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
        self.mouseMove(phg.getPathHelix(0), position=QPoint(582, 33), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
        self.mouseMove(phg.getPathHelix(0), position=QPoint(594, 33), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
        self.mouseMove(phg.getPathHelix(0), position=QPoint(596, 33), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
        self.mouseMove(phg.getPathHelix(0), position=QPoint(601, 33), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
        self.mouseMove(phg.getPathHelix(0), position=QPoint(603, 33), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
        self.mouseMove(phg.getPathHelix(0), position=QPoint(608, 33), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
        self.mouseMove(phg.getPathHelix(0), position=QPoint(612, 33), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
        self.mouseMove(phg.getPathHelix(0), position=QPoint(617, 33), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
        self.mouseMove(phg.getPathHelix(0), position=QPoint(622, 33), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
        self.mouseMove(phg.getPathHelix(0), position=QPoint(631, 33), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
        self.mouseMove(phg.getPathHelix(0), position=QPoint(638, 33), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
        self.mouseMove(phg.getPathHelix(0), position=QPoint(643, 33), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
        self.mouseMove(phg.getPathHelix(0), position=QPoint(647, 33), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
        self.mouseMove(phg.getPathHelix(0), position=QPoint(652, 33), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
        self.mouseMove(phg.getPathHelix(0), position=QPoint(657, 33), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
        self.mouseMove(phg.getPathHelix(0), position=QPoint(659, 33), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
        self.mouseRelease(phg.getPathHelix(0), position=QPoint(659, 33), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
        self.click(actionPathEraseButton)
        self.mousePress(phg.getPathHelix(0), position=QPoint(543, 9), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
        self.mouseRelease(phg.getPathHelix(0), position=QPoint(543, 9), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
        self.click(actionPathInsertButton)
        self.mousePress(phg.getPathHelix(1), position=QPoint(524, 22), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
        self.mouseRelease(phg.getPathHelix(1), position=QPoint(524, 22), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)

        self.debugHere()


        # Verify model for correctness
        refvh0 = """0 Scaffold: _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_\n0 Staple:   _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,> <,> <,> <,> <,> <,> <,> <,> <,> <,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_"""
        self.assertEqual(refvh0, repr(self.app.v[0]))
        refvh1 = """1 Scaffold: _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_\n1 Staple:   _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_"""
        self.assertEqual(refvh1, repr(self.app.v[1]))


if __name__ == '__main__':
    print "Running Last Recorded Test"
    test.cadnanoguitestcase.main()

