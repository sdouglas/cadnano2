
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
        self.mousePress(sgi.getSliceHelixByCoord(3, 7), position=QPoint(14, 13), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.slicescene)
        self.mouseRelease(sgi.getSliceHelixByCoord(3, 7), position=QPoint(14, 13), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.slicescene)
        self.mousePress(sgi.getSliceHelixByCoord(3, 8), position=QPoint(9, 11), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.slicescene)
        self.mouseRelease(sgi.getSliceHelixByCoord(3, 8), position=QPoint(9, 11), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.slicescene)
        self.mousePress(sgi.getSliceHelixByCoord(4, 8), position=QPoint(13, 7), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.slicescene)
        self.mouseMove(sgi.getSliceHelixByCoord(4, 8), position=QPoint(13, 8), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.slicescene)
        self.mouseRelease(sgi.getSliceHelixByCoord(4, 8), position=QPoint(13, 8), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.slicescene)
        self.mousePress(sgi.getSliceHelixByCoord(4, 7), position=QPoint(20, 9), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.slicescene)
        self.mouseMove(sgi.getSliceHelixByCoord(4, 7), position=QPoint(18, 9), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.slicescene)
        self.mouseMove(sgi.getSliceHelixByCoord(4, 7), position=QPoint(17, 9), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.slicescene)
        self.mouseRelease(sgi.getSliceHelixByCoord(4, 7), position=QPoint(17, 9), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.slicescene)
        self.mousePress(sgi.getSliceHelixByCoord(4, 6), position=QPoint(15, 6), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.slicescene)
        self.mouseRelease(sgi.getSliceHelixByCoord(4, 6), position=QPoint(15, 6), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.slicescene)
        self.mousePress(sgi.getSliceHelixByCoord(3, 6), position=QPoint(8, 12), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.slicescene)
        self.mouseRelease(sgi.getSliceHelixByCoord(3, 6), position=QPoint(8, 12), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.slicescene)
        self.mousePress(sgi.getSliceHelixByCoord(3, 13), position=QPoint(10, 10), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.slicescene)
        self.mouseRelease(sgi.getSliceHelixByCoord(3, 13), position=QPoint(10, 10), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.slicescene)
        self.mousePress(sgi.getSliceHelixByCoord(3, 14), position=QPoint(8, 11), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.slicescene)
        self.mouseRelease(sgi.getSliceHelixByCoord(3, 14), position=QPoint(8, 11), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.slicescene)
        self.mousePress(sgi.getSliceHelixByCoord(4, 14), position=QPoint(14, 8), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.slicescene)
        self.mouseRelease(sgi.getSliceHelixByCoord(4, 14), position=QPoint(14, 8), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.slicescene)
        self.mousePress(sgi.getSliceHelixByCoord(4, 13), position=QPoint(21, 14), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.slicescene)
        self.mouseMove(sgi.getSliceHelixByCoord(4, 13), position=QPoint(19, 14), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.slicescene)
        self.mouseMove(sgi.getSliceHelixByCoord(4, 13), position=QPoint(18, 14), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.slicescene)
        self.mouseRelease(sgi.getSliceHelixByCoord(4, 13), position=QPoint(18, 14), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.slicescene)
        self.mousePress(sgi.getSliceHelixByCoord(4, 12), position=QPoint(19, 11), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.slicescene)
        self.mouseRelease(sgi.getSliceHelixByCoord(4, 12), position=QPoint(19, 11), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.slicescene)
        self.mousePress(sgi.getSliceHelixByCoord(3, 12), position=QPoint(7, 14), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.slicescene)
        self.mouseRelease(sgi.getSliceHelixByCoord(3, 12), position=QPoint(7, 14), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.slicescene)
        self.mousePress(sgi.getSliceHelixByCoord(6, 6), position=QPoint(22, 16), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.slicescene)
        self.mouseRelease(sgi.getSliceHelixByCoord(6, 6), position=QPoint(22, 16), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.slicescene)
        self.mousePress(sgi.getSliceHelixByCoord(6, 7), position=QPoint(10, 4), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.slicescene)
        self.mouseRelease(sgi.getSliceHelixByCoord(6, 7), position=QPoint(10, 4), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.slicescene)
        self.mousePress(sgi.getSliceHelixByCoord(7, 7), position=QPoint(14, 3), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.slicescene)
        self.mouseRelease(sgi.getSliceHelixByCoord(7, 7), position=QPoint(14, 3), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.slicescene)
        self.mousePress(sgi.getSliceHelixByCoord(7, 8), position=QPoint(13, 5), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.slicescene)
        self.mouseRelease(sgi.getSliceHelixByCoord(7, 8), position=QPoint(13, 5), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.slicescene)
        self.mousePress(sgi.getSliceHelixByCoord(7, 9), position=QPoint(23, 0), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.slicescene)
        self.mouseRelease(sgi.getSliceHelixByCoord(7, 9), position=QPoint(23, 0), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.slicescene)
        self.mousePress(sgi.getSliceHelixByCoord(7, 10), position=QPoint(20, 14), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.slicescene)
        self.mouseMove(sgi.getSliceHelixByCoord(7, 10), position=QPoint(21, 15), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.slicescene)
        self.mouseRelease(sgi.getSliceHelixByCoord(7, 10), position=QPoint(21, 15), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.slicescene)
        self.mousePress(sgi.getSliceHelixByCoord(7, 11), position=QPoint(14, 16), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.slicescene)
        self.mouseMove(sgi.getSliceHelixByCoord(7, 11), position=QPoint(14, 17), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.slicescene)
        self.mouseRelease(sgi.getSliceHelixByCoord(7, 11), position=QPoint(14, 17), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.slicescene)
        self.mousePress(sgi.getSliceHelixByCoord(7, 12), position=QPoint(14, 13), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.slicescene)
        self.mouseRelease(sgi.getSliceHelixByCoord(7, 12), position=QPoint(14, 13), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.slicescene)
        self.mousePress(sgi.getSliceHelixByCoord(7, 13), position=QPoint(12, 9), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.slicescene)
        self.mouseRelease(sgi.getSliceHelixByCoord(7, 13), position=QPoint(12, 9), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.slicescene)
        self.mousePress(sgi.getSliceHelixByCoord(6, 13), position=QPoint(15, 11), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.slicescene)
        self.mouseRelease(sgi.getSliceHelixByCoord(6, 13), position=QPoint(15, 11), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.slicescene)
        self.mousePress(sgi.getSliceHelixByCoord(6, 14), position=QPoint(17, 15), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.slicescene)
        self.mouseRelease(sgi.getSliceHelixByCoord(6, 14), position=QPoint(17, 15), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.slicescene)
        self.mousePress(ash, position=QPoint(15, 116), modifiers=Qt.AltModifier|Qt.ShiftModifier, qgraphicsscene=self.mainWindow.pathscene)
        self.mouseRelease(ash, position=QPoint(15, 116), modifiers=Qt.AltModifier|Qt.ShiftModifier, qgraphicsscene=self.mainWindow.pathscene)
        self.mousePress(phg.getPathHelix(0), position=QPoint(110, 28), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
        self.mouseMove(phg.getPathHelix(0), position=QPoint(114, 28), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
        self.mouseMove(phg.getPathHelix(0), position=QPoint(117, 28), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
        self.mouseMove(phg.getPathHelix(0), position=QPoint(121, 28), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
        self.mouseMove(phg.getPathHelix(0), position=QPoint(138, 31), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
        self.mouseMove(phg.getPathHelix(0), position=QPoint(142, 31), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
        self.mouseMove(phg.getPathHelix(0), position=QPoint(152, 35), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
        self.mouseMove(phg.getPathHelix(0), position=QPoint(155, 35), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
        self.mouseMove(phg.getPathHelix(0), position=QPoint(162, 35), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
        self.mouseMove(phg.getPathHelix(0), position=QPoint(176, 35), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
        self.mouseMove(phg.getPathHelix(0), position=QPoint(183, 35), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
        self.mouseMove(phg.getPathHelix(0), position=QPoint(183, 38), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
        self.mouseMove(phg.getPathHelix(0), position=QPoint(193, 38), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
        self.mouseMove(phg.getPathHelix(0), position=QPoint(204, 41), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
        self.mouseMove(phg.getPathHelix(0), position=QPoint(224, 45), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
        self.mouseMove(phg.getPathHelix(0), position=QPoint(249, 48), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
        self.mouseMove(phg.getPathHelix(0), position=QPoint(283, 48), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
        self.mouseMove(phg.getPathHelix(0), position=QPoint(321, 48), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
        self.mouseMove(phg.getPathHelix(0), position=QPoint(345, 52), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
        self.mouseMove(phg.getPathHelix(0), position=QPoint(404, 45), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
        self.mouseMove(phg.getPathHelix(0), position=QPoint(452, 41), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
        self.mouseMove(phg.getPathHelix(0), position=QPoint(494, 41), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
        self.mouseMove(phg.getPathHelix(0), position=QPoint(539, 41), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
        self.mouseMove(phg.getPathHelix(0), position=QPoint(580, 41), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
        self.mouseMove(phg.getPathHelix(0), position=QPoint(587, 41), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
        self.mouseMove(phg.getPathHelix(0), position=QPoint(590, 41), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
        self.mouseMove(phg.getPathHelix(0), position=QPoint(594, 41), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
        self.mouseMove(phg.getPathHelix(0), position=QPoint(608, 41), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
        self.mouseMove(phg.getPathHelix(0), position=QPoint(625, 45), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
        self.mouseMove(phg.getPathHelix(0), position=QPoint(632, 45), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
        self.mouseMove(phg.getPathHelix(0), position=QPoint(639, 45), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
        self.mouseMove(phg.getPathHelix(0), position=QPoint(642, 45), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
        self.mouseMove(phg.getPathHelix(0), position=QPoint(646, 45), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
        self.mouseMove(phg.getPathHelix(0), position=QPoint(649, 45), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
        self.mouseMove(phg.getPathHelix(0), position=QPoint(653, 45), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
        self.mouseMove(phg.getPathHelix(0), position=QPoint(656, 45), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
        self.mouseMove(phg.getPathHelix(0), position=QPoint(659, 45), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
        self.mouseMove(phg.getPathHelix(0), position=QPoint(663, 45), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
        self.mouseMove(phg.getPathHelix(0), position=QPoint(666, 52), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
        self.mouseMove(phg.getPathHelix(0), position=QPoint(670, 52), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
        self.mouseMove(phg.getPathHelix(0), position=QPoint(673, 52), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
        self.mouseMove(phg.getPathHelix(0), position=QPoint(677, 52), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
        self.mouseMove(phg.getPathHelix(0), position=QPoint(680, 52), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
        self.mouseMove(phg.getPathHelix(0), position=QPoint(684, 52), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
        self.mouseMove(phg.getPathHelix(0), position=QPoint(687, 52), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
        self.mouseMove(phg.getPathHelix(0), position=QPoint(691, 52), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
        self.mouseRelease(phg.getPathHelix(0), position=QPoint(691, 52), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
        self.mousePress(phg.getPathHelix(3), position=QPoint(691, 3), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
        self.mouseMove(phg.getPathHelix(3), position=QPoint(687, 3), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
        self.mouseMove(phg.getPathHelix(3), position=QPoint(684, 3), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
        self.mouseMove(phg.getPathHelix(3), position=QPoint(680, 3), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
        self.mouseMove(phg.getPathHelix(3), position=QPoint(673, 3), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
        self.mouseMove(phg.getPathHelix(3), position=QPoint(649, -1), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
        self.mouseMove(phg.getPathHelix(3), position=QPoint(604, -1), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
        self.mouseMove(phg.getPathHelix(3), position=QPoint(552, -1), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
        self.mouseMove(phg.getPathHelix(3), position=QPoint(504, -4), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
        self.mouseMove(phg.getPathHelix(3), position=QPoint(470, -4), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
        self.mouseMove(phg.getPathHelix(3), position=QPoint(442, -4), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
        self.mouseMove(phg.getPathHelix(3), position=QPoint(397, -8), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
        self.mouseMove(phg.getPathHelix(3), position=QPoint(328, -8), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
        self.mouseMove(phg.getPathHelix(3), position=QPoint(280, -8), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
        self.mouseMove(phg.getPathHelix(3), position=QPoint(252, -8), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
        self.mouseMove(phg.getPathHelix(3), position=QPoint(231, -8), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
        self.mouseMove(phg.getPathHelix(3), position=QPoint(221, -8), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
        self.mouseMove(phg.getPathHelix(3), position=QPoint(218, -8), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
        self.mouseMove(phg.getPathHelix(3), position=QPoint(211, -8), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
        self.mouseMove(phg.getPathHelix(3), position=QPoint(207, -4), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
        self.mouseMove(phg.getPathHelix(3), position=QPoint(204, -4), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
        self.mouseMove(phg.getPathHelix(3), position=QPoint(197, -1), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
        self.mouseMove(phg.getPathHelix(3), position=QPoint(186, -1), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
        self.mouseMove(phg.getPathHelix(3), position=QPoint(183, -1), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
        self.mouseMove(phg.getPathHelix(3), position=QPoint(183, 3), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
        self.mouseMove(phg.getPathHelix(3), position=QPoint(180, 3), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
        self.mouseMove(phg.getPathHelix(3), position=QPoint(173, 3), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
        self.mouseMove(phg.getPathHelix(3), position=QPoint(169, 3), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
        self.mouseMove(phg.getPathHelix(3), position=QPoint(166, 3), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
        self.mouseMove(phg.getPathHelix(3), position=QPoint(162, 3), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
        self.mouseMove(phg.getPathHelix(3), position=QPoint(159, 3), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
        self.mouseMove(phg.getPathHelix(3), position=QPoint(155, 3), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
        self.mouseMove(phg.getPathHelix(3), position=QPoint(148, 6), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
        self.mouseMove(phg.getPathHelix(3), position=QPoint(145, 6), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
        self.mouseMove(phg.getPathHelix(3), position=QPoint(138, 6), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
        self.mouseMove(phg.getPathHelix(3), position=QPoint(135, 10), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
        self.mouseMove(phg.getPathHelix(3), position=QPoint(131, 10), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
        self.mouseMove(phg.getPathHelix(3), position=QPoint(128, 10), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
        self.mouseMove(phg.getPathHelix(3), position=QPoint(124, 10), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
        self.mouseMove(phg.getPathHelix(3), position=QPoint(121, 10), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
        self.mouseMove(phg.getPathHelix(3), position=QPoint(114, 10), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
        self.mouseMove(phg.getPathHelix(3), position=QPoint(110, 10), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
        self.mouseMove(phg.getPathHelix(3), position=QPoint(107, 6), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
        self.mouseMove(phg.getPathHelix(3), position=QPoint(107, 3), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
        self.mouseRelease(phg.getPathHelix(3), position=QPoint(107, 3), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
        self.mousePress(phg.getPathHelix(5), position=QPoint(131, 13), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
        self.mouseMove(phg.getPathHelix(5), position=QPoint(135, 13), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
        self.mouseMove(phg.getPathHelix(5), position=QPoint(142, 13), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
        self.mouseMove(phg.getPathHelix(5), position=QPoint(152, 13), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
        self.mouseMove(phg.getPathHelix(5), position=QPoint(166, 13), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
        self.mouseMove(phg.getPathHelix(5), position=QPoint(214, 13), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
        self.mouseMove(phg.getPathHelix(5), position=QPoint(245, 13), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
        self.mouseMove(phg.getPathHelix(5), position=QPoint(283, 13), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
        self.mouseMove(phg.getPathHelix(5), position=QPoint(380, 13), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
        self.mouseMove(phg.getPathHelix(5), position=QPoint(439, 13), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
        self.mouseMove(phg.getPathHelix(5), position=QPoint(501, 9), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
        self.mouseMove(phg.getPathHelix(5), position=QPoint(601, 16), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
        self.mouseMove(phg.getPathHelix(5), position=QPoint(642, 16), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
        self.mouseMove(phg.getPathHelix(5), position=QPoint(656, 16), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
        self.mouseMove(phg.getPathHelix(5), position=QPoint(663, 16), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
        self.mouseMove(phg.getPathHelix(5), position=QPoint(666, 16), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
        self.mouseMove(phg.getPathHelix(5), position=QPoint(670, 16), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
        self.mouseMove(phg.getPathHelix(5), position=QPoint(670, 20), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
        self.mouseMove(phg.getPathHelix(5), position=QPoint(673, 20), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
        self.mouseMove(phg.getPathHelix(5), position=QPoint(677, 20), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
        self.mouseMove(phg.getPathHelix(5), position=QPoint(680, 20), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
        self.mouseMove(phg.getPathHelix(5), position=QPoint(687, 26), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
        self.mouseMove(phg.getPathHelix(5), position=QPoint(691, 26), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
        self.mouseMove(phg.getPathHelix(5), position=QPoint(694, 26), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
        self.mouseMove(phg.getPathHelix(5), position=QPoint(697, 26), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
        self.mouseRelease(phg.getPathHelix(5), position=QPoint(697, 26), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
        self.mousePress(phg.getPathHelix(7), position=QPoint(691, 12), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
        self.mouseMove(phg.getPathHelix(7), position=QPoint(673, 12), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
        self.mouseMove(phg.getPathHelix(7), position=QPoint(649, 12), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
        self.mouseMove(phg.getPathHelix(7), position=QPoint(632, 12), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
        self.mouseMove(phg.getPathHelix(7), position=QPoint(577, 19), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
        self.mouseMove(phg.getPathHelix(7), position=QPoint(542, 23), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
        self.mouseMove(phg.getPathHelix(7), position=QPoint(511, 26), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
        self.mouseMove(phg.getPathHelix(7), position=QPoint(452, 26), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
        self.mouseMove(phg.getPathHelix(7), position=QPoint(380, 26), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
        self.mouseMove(phg.getPathHelix(7), position=QPoint(331, 26), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
        self.mouseMove(phg.getPathHelix(7), position=QPoint(325, 26), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
        self.mouseMove(phg.getPathHelix(7), position=QPoint(314, 26), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
        self.mouseMove(phg.getPathHelix(7), position=QPoint(273, 26), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
        self.mouseMove(phg.getPathHelix(7), position=QPoint(238, 26), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
        self.mouseMove(phg.getPathHelix(7), position=QPoint(200, 26), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
        self.mouseMove(phg.getPathHelix(7), position=QPoint(183, 26), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
        self.mouseMove(phg.getPathHelix(7), position=QPoint(180, 26), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
        self.mouseMove(phg.getPathHelix(7), position=QPoint(176, 26), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
        self.mouseMove(phg.getPathHelix(7), position=QPoint(173, 26), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
        self.mouseMove(phg.getPathHelix(7), position=QPoint(169, 26), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
        self.mouseMove(phg.getPathHelix(7), position=QPoint(166, 26), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
        self.mouseMove(phg.getPathHelix(7), position=QPoint(162, 26), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
        self.mouseMove(phg.getPathHelix(7), position=QPoint(159, 26), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
        self.mouseMove(phg.getPathHelix(7), position=QPoint(155, 26), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
        self.mouseMove(phg.getPathHelix(7), position=QPoint(152, 26), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
        self.mouseMove(phg.getPathHelix(7), position=QPoint(152, 23), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
        self.mouseMove(phg.getPathHelix(7), position=QPoint(148, 23), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
        self.mouseMove(phg.getPathHelix(7), position=QPoint(145, 23), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
        self.mouseMove(phg.getPathHelix(7), position=QPoint(145, 16), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
        self.mouseMove(phg.getPathHelix(7), position=QPoint(142, 16), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
        self.mouseMove(phg.getPathHelix(7), position=QPoint(142, 12), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
        self.mouseMove(phg.getPathHelix(7), position=QPoint(142, 9), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
        self.mouseMove(phg.getPathHelix(7), position=QPoint(138, 9), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
        self.mouseMove(phg.getPathHelix(7), position=QPoint(138, 5), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
        self.mouseMove(phg.getPathHelix(7), position=QPoint(135, 5), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
        self.mouseMove(phg.getPathHelix(7), position=QPoint(135, 9), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
        self.mouseRelease(phg.getPathHelix(7), position=QPoint(135, 9), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)

        # Verify model for correctness
        refvh0 = """0 Scaffold: _,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,_\n0 Staple:   _,_ _,_ _,_ _,_ _,_ _,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_"""
        self.assertEqual(refvh0, repr(self.app.v[0]))
        refvh1 = """1 Scaffold: _,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,_\n1 Staple:   _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_"""
        self.assertEqual(refvh1, repr(self.app.v[1]))
        refvh2 = """2 Scaffold: _,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,_\n2 Staple:   _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_"""
        self.assertEqual(refvh2, repr(self.app.v[2]))
        refvh3 = """3 Scaffold: _,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,_\n3 Staple:   _,_ _,_ _,_ _,_ _,_ _,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_"""
        self.assertEqual(refvh3, repr(self.app.v[3]))
        refvh4 = """4 Scaffold: _,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,_\n4 Staple:   _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_"""
        self.assertEqual(refvh4, repr(self.app.v[4]))
        refvh5 = """5 Scaffold: _,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,_\n5 Staple:   _,_ _,_ _,_ _,_ _,_ _,_ _,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_"""
        self.assertEqual(refvh5, repr(self.app.v[5]))
        refvh6 = """6 Scaffold: _,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,_\n6 Staple:   _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_"""
        self.assertEqual(refvh6, repr(self.app.v[6]))
        refvh7 = """7 Scaffold: _,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,_\n7 Staple:   _,_ _,_ _,_ _,_ _,_ _,_ _,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_"""
        self.assertEqual(refvh7, repr(self.app.v[7]))
        refvh8 = """8 Scaffold: _,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,_\n8 Staple:   _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_"""
        self.assertEqual(refvh8, repr(self.app.v[8]))
        refvh9 = """9 Scaffold: _,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,_\n9 Staple:   _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_"""
        self.assertEqual(refvh9, repr(self.app.v[9]))
        refvh10 = """10Scaffold: _,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,_\n10Staple:   _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_"""
        self.assertEqual(refvh10, repr(self.app.v[10]))
        refvh11 = """11Scaffold: _,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,_\n11Staple:   _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_"""
        self.assertEqual(refvh11, repr(self.app.v[11]))
        refvh12 = """12Scaffold: _,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,_\n12Staple:   _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_"""
        self.assertEqual(refvh12, repr(self.app.v[12]))
        refvh13 = """13Scaffold: _,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,_\n13Staple:   _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_"""
        self.assertEqual(refvh13, repr(self.app.v[13]))
        refvh14 = """14Scaffold: _,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,_\n14Staple:   _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_"""
        self.assertEqual(refvh14, repr(self.app.v[14]))
        refvh15 = """15Scaffold: _,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,_\n15Staple:   _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_"""
        self.assertEqual(refvh15, repr(self.app.v[15]))
        refvh16 = """16Scaffold: _,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,_\n16Staple:   _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_"""
        self.assertEqual(refvh16, repr(self.app.v[16]))
        refvh17 = """17Scaffold: _,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,_\n17Staple:   _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_"""
        self.assertEqual(refvh17, repr(self.app.v[17]))
        refvh18 = """18Scaffold: _,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,_\n18Staple:   _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_"""
        self.assertEqual(refvh18, repr(self.app.v[18]))
        refvh19 = """19Scaffold: _,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,_\n19Staple:   _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_"""
        self.assertEqual(refvh19, repr(self.app.v[19]))
        refvh20 = """20Scaffold: _,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,_\n20Staple:   _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_"""
        self.assertEqual(refvh20, repr(self.app.v[20]))
        refvh21 = """21Scaffold: _,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,_\n21Staple:   _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_"""
        self.assertEqual(refvh21, repr(self.app.v[21]))
        refvh22 = """22Scaffold: _,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,_\n22Staple:   _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_"""
        self.assertEqual(refvh22, repr(self.app.v[22]))

        #self.debugHere()

if __name__ == '__main__':
    print "Running Last Recorded Test"
    test.cadnanoguitestcase.main()

