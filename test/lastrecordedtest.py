
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
        partButton = self.mainWindow.topToolBar.widgetForAction(self.mainWindow.actionNewSquarePart)
        self.click(partButton)

        # Init refs
        sgi = self.documentController.sliceGraphicsItem
        phg = self.documentController.pathHelixGroup
        ash = self.documentController.pathHelixGroup.activeSliceHandle()

        # Playback user input
        self.mousePress(sgi.getSliceHelixByCoord(0, 3), position=QPoint(20, 10), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.slicescene)
        self.mouseRelease(sgi.getSliceHelixByCoord(0, 3), position=QPoint(20, 10), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.slicescene)
        self.mousePress(sgi.getSliceHelixByCoord(0, 2), position=QPoint(26, 14), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.slicescene)
        self.mouseRelease(sgi.getSliceHelixByCoord(0, 2), position=QPoint(26, 14), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.slicescene)
        self.mousePress(sgi.getSliceHelixByCoord(1, 2), position=QPoint(11, 10), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.slicescene)
        self.mouseMove(sgi.getSliceHelixByCoord(1, 2), position=QPoint(11, 11), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.slicescene)
        self.mouseMove(sgi.getSliceHelixByCoord(1, 2), position=QPoint(13, 11), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.slicescene)
        self.mouseRelease(sgi.getSliceHelixByCoord(1, 2), position=QPoint(13, 11), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.slicescene)
        self.mousePress(sgi.getSliceHelixByCoord(1, 3), position=QPoint(11, 13), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.slicescene)
        self.mouseRelease(sgi.getSliceHelixByCoord(1, 3), position=QPoint(11, 13), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.slicescene)
        self.mousePress(phg.getPathHelix(0), position=QPoint(61, 30), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
        self.mouseMove(phg.getPathHelix(0), position=QPoint(64, 30), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
        self.mouseMove(phg.getPathHelix(0), position=QPoint(81, 37), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
        self.mouseMove(phg.getPathHelix(0), position=QPoint(108, 44), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
        self.mouseMove(phg.getPathHelix(0), position=QPoint(138, 51), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
        self.mouseMove(phg.getPathHelix(0), position=QPoint(179, 47), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
        self.mouseMove(phg.getPathHelix(0), position=QPoint(243, 44), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
        self.mouseMove(phg.getPathHelix(0), position=QPoint(340, 37), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
        self.mouseMove(phg.getPathHelix(0), position=QPoint(398, 37), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
        self.mouseMove(phg.getPathHelix(0), position=QPoint(421, 37), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
        self.mouseMove(phg.getPathHelix(0), position=QPoint(478, 37), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
        self.mouseMove(phg.getPathHelix(0), position=QPoint(576, 24), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
        self.mouseMove(phg.getPathHelix(0), position=QPoint(613, 24), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
        self.mouseMove(phg.getPathHelix(0), position=QPoint(627, 24), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
        self.mouseRelease(phg.getPathHelix(0), position=QPoint(627, 24), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
        self.mousePress(phg.getPathHelix(0), position=QPoint(1108, 3), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
        self.mouseMove(phg.getPathHelix(0), position=QPoint(1102, 3), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
        self.mouseMove(phg.getPathHelix(0), position=QPoint(1091, 3), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
        self.mouseMove(phg.getPathHelix(0), position=QPoint(1048, 7), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
        self.mouseMove(phg.getPathHelix(0), position=QPoint(987, 20), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
        self.mouseMove(phg.getPathHelix(0), position=QPoint(933, 27), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
        self.mouseMove(phg.getPathHelix(0), position=QPoint(889, 30), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
        self.mouseMove(phg.getPathHelix(0), position=QPoint(852, 30), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
        self.mouseMove(phg.getPathHelix(0), position=QPoint(846, 30), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
        self.mouseMove(phg.getPathHelix(0), position=QPoint(839, 30), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
        self.mouseMove(phg.getPathHelix(0), position=QPoint(829, 30), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
        self.mouseMove(phg.getPathHelix(0), position=QPoint(819, 30), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
        self.mouseMove(phg.getPathHelix(0), position=QPoint(809, 30), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
        self.mouseMove(phg.getPathHelix(0), position=QPoint(805, 30), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
        self.mouseMove(phg.getPathHelix(0), position=QPoint(802, 30), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
        self.mouseMove(phg.getPathHelix(0), position=QPoint(798, 30), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
        self.mouseMove(phg.getPathHelix(0), position=QPoint(795, 30), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
        self.mouseMove(phg.getPathHelix(0), position=QPoint(792, 30), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
        self.mouseMove(phg.getPathHelix(0), position=QPoint(782, 30), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
        self.mouseMove(phg.getPathHelix(0), position=QPoint(775, 27), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
        self.mouseMove(phg.getPathHelix(0), position=QPoint(755, 27), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
        self.mouseMove(phg.getPathHelix(0), position=QPoint(741, 27), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
        self.mouseRelease(phg.getPathHelix(0), position=QPoint(741, 27), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
        self.mousePress(phg.getPathHelix(1), position=QPoint(677, 28), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
        self.mouseMove(phg.getPathHelix(1), position=QPoint(677, 31), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
        self.mouseMove(phg.getPathHelix(1), position=QPoint(684, 35), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
        self.mouseMove(phg.getPathHelix(1), position=QPoint(711, 45), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
        self.mouseMove(phg.getPathHelix(1), position=QPoint(738, 45), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
        self.mouseMove(phg.getPathHelix(1), position=QPoint(768, 48), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
        self.mouseMove(phg.getPathHelix(1), position=QPoint(798, 48), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
        self.mouseMove(phg.getPathHelix(1), position=QPoint(876, 48), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
        self.mouseMove(phg.getPathHelix(1), position=QPoint(963, 48), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
        self.mouseMove(phg.getPathHelix(1), position=QPoint(990, 45), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
        self.mouseMove(phg.getPathHelix(1), position=QPoint(1054, 35), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
        self.mouseMove(phg.getPathHelix(1), position=QPoint(1081, 35), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
        self.mouseMove(phg.getPathHelix(1), position=QPoint(1108, 35), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
        self.mouseMove(phg.getPathHelix(1), position=QPoint(1125, 35), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
        self.mouseRelease(phg.getPathHelix(1), position=QPoint(1125, 35), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
        self.mousePress(phg.getPathHelix(2), position=QPoint(613, 25), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
        self.mouseMove(phg.getPathHelix(2), position=QPoint(610, 25), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
        self.mouseMove(phg.getPathHelix(2), position=QPoint(606, 25), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
        self.mouseMove(phg.getPathHelix(2), position=QPoint(600, 25), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
        self.mouseMove(phg.getPathHelix(2), position=QPoint(566, 32), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
        self.mouseMove(phg.getPathHelix(2), position=QPoint(492, 39), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
        self.mouseMove(phg.getPathHelix(2), position=QPoint(418, 25), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
        self.mouseMove(phg.getPathHelix(2), position=QPoint(398, 25), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
        self.mouseMove(phg.getPathHelix(2), position=QPoint(377, 22), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
        self.mouseMove(phg.getPathHelix(2), position=QPoint(300, 15), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
        self.mouseMove(phg.getPathHelix(2), position=QPoint(185, 12), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
        self.mouseMove(phg.getPathHelix(2), position=QPoint(121, 9), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
        self.mouseRelease(phg.getPathHelix(2), position=QPoint(121, 9), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
        self.mousePress(phg.getPathHelix(3), position=QPoint(438, 10), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
        self.mouseMove(phg.getPathHelix(3), position=QPoint(445, 10), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
        self.mouseMove(phg.getPathHelix(3), position=QPoint(478, 13), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
        self.mouseMove(phg.getPathHelix(3), position=QPoint(573, 16), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
        self.mouseMove(phg.getPathHelix(3), position=QPoint(687, 26), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
        self.mouseMove(phg.getPathHelix(3), position=QPoint(755, 23), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
        self.mouseMove(phg.getPathHelix(3), position=QPoint(788, 23), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
        self.mouseMove(phg.getPathHelix(3), position=QPoint(862, 20), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
        self.mouseMove(phg.getPathHelix(3), position=QPoint(923, 10), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
        self.mouseMove(phg.getPathHelix(3), position=QPoint(967, 6), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
        self.mouseMove(phg.getPathHelix(3), position=QPoint(974, 3), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
        self.mouseRelease(phg.getPathHelix(3), position=QPoint(974, 3), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
        self.mousePress(phg.getPathHelix(3), position=QPoint(974, 6), modifiers=Qt.AltModifier, qgraphicsscene=self.mainWindow.pathscene)
        self.mouseRelease(phg.getPathHelix(3), position=QPoint(974, 6), modifiers=Qt.AltModifier, qgraphicsscene=self.mainWindow.pathscene)
        self.mousePress(phg.getPathHelix(2), position=QPoint(613, 29), modifiers=Qt.AltModifier, qgraphicsscene=self.mainWindow.pathscene)
        self.mouseRelease(phg.getPathHelix(2), position=QPoint(613, 29), modifiers=Qt.AltModifier, qgraphicsscene=self.mainWindow.pathscene)
        self.mousePress(phg.getPathHelix(1), position=QPoint(633, 28), modifiers=Qt.AltModifier, qgraphicsscene=self.mainWindow.pathscene)
        self.mouseRelease(phg.getPathHelix(1), position=QPoint(633, 28), modifiers=Qt.AltModifier, qgraphicsscene=self.mainWindow.pathscene)
        self.mousePress(phg.getPathHelix(2), position=QPoint(637, 15), modifiers=Qt.AltModifier, qgraphicsscene=self.mainWindow.pathscene)
        self.mouseRelease(phg.getPathHelix(2), position=QPoint(637, 15), modifiers=Qt.AltModifier, qgraphicsscene=self.mainWindow.pathscene)
        self.mousePress(phg.getPathHelix(3), position=QPoint(674, 26), modifiers=Qt.AltModifier, qgraphicsscene=self.mainWindow.pathscene)
        self.mouseRelease(phg.getPathHelix(3), position=QPoint(674, 26), modifiers=Qt.AltModifier, qgraphicsscene=self.mainWindow.pathscene)
        self.mousePress(phg.getPathHelix(1), position=QPoint(1125, 28), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
        self.mouseMove(phg.getPathHelix(1), position=QPoint(1122, 28), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
        self.mouseMove(phg.getPathHelix(1), position=QPoint(1118, 28), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
        self.mouseMove(phg.getPathHelix(1), position=QPoint(1088, 28), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
        self.mouseMove(phg.getPathHelix(1), position=QPoint(1001, 35), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
        self.mouseMove(phg.getPathHelix(1), position=QPoint(923, 35), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
        self.mouseMove(phg.getPathHelix(1), position=QPoint(903, 38), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
        self.mouseMove(phg.getPathHelix(1), position=QPoint(899, 38), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
        self.mouseMove(phg.getPathHelix(1), position=QPoint(859, 38), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
        self.mouseMove(phg.getPathHelix(1), position=QPoint(809, 41), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
        self.mouseMove(phg.getPathHelix(1), position=QPoint(768, 38), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
        self.mouseMove(phg.getPathHelix(1), position=QPoint(718, 28), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
        self.mouseMove(phg.getPathHelix(1), position=QPoint(674, 28), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
        self.mouseMove(phg.getPathHelix(1), position=QPoint(657, 28), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
        self.mouseMove(phg.getPathHelix(1), position=QPoint(610, 25), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
        self.mouseMove(phg.getPathHelix(1), position=QPoint(576, 25), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
        self.mouseMove(phg.getPathHelix(1), position=QPoint(573, 25), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
        self.mouseMove(phg.getPathHelix(1), position=QPoint(566, 25), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
        self.mouseMove(phg.getPathHelix(1), position=QPoint(563, 25), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
        self.mouseMove(phg.getPathHelix(1), position=QPoint(556, 25), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
        self.mouseMove(phg.getPathHelix(1), position=QPoint(512, 18), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
        self.mouseMove(phg.getPathHelix(1), position=QPoint(441, 18), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
        self.mouseMove(phg.getPathHelix(1), position=QPoint(428, 18), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
        self.mouseMove(phg.getPathHelix(1), position=QPoint(398, 18), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
        self.mouseMove(phg.getPathHelix(1), position=QPoint(344, 18), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
        self.mouseMove(phg.getPathHelix(1), position=QPoint(300, 18), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
        self.mouseMove(phg.getPathHelix(1), position=QPoint(283, 18), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
        self.mouseMove(phg.getPathHelix(1), position=QPoint(276, 18), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
        self.mouseMove(phg.getPathHelix(1), position=QPoint(256, 18), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
        self.mouseMove(phg.getPathHelix(1), position=QPoint(249, 18), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
        self.mouseRelease(phg.getPathHelix(1), position=QPoint(249, 18), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
        self.mousePress(phg.getPathHelix(1), position=QPoint(246, 8), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
        self.mouseMove(phg.getPathHelix(1), position=QPoint(249, 8), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
        self.mouseMove(phg.getPathHelix(1), position=QPoint(266, 8), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
        self.mouseMove(phg.getPathHelix(1), position=QPoint(327, 18), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
        self.mouseMove(phg.getPathHelix(1), position=QPoint(431, 25), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
        self.mouseMove(phg.getPathHelix(1), position=QPoint(519, 28), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
        self.mouseMove(phg.getPathHelix(1), position=QPoint(620, 14), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
        self.mouseMove(phg.getPathHelix(1), position=QPoint(734, 4), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
        self.mouseMove(phg.getPathHelix(1), position=QPoint(842, -2), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
        self.mouseMove(phg.getPathHelix(1), position=QPoint(933, -16), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
        self.mouseMove(phg.getPathHelix(1), position=QPoint(987, -19), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
        self.mouseMove(phg.getPathHelix(1), position=QPoint(1054, -19), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
        self.mouseMove(phg.getPathHelix(1), position=QPoint(1078, -13), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
        self.mouseMove(phg.getPathHelix(1), position=QPoint(1091, -13), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
        self.mouseMove(phg.getPathHelix(1), position=QPoint(1132, -6), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
        self.mouseMove(phg.getPathHelix(1), position=QPoint(1139, 1), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
        self.mouseMove(phg.getPathHelix(1), position=QPoint(1142, 1), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
        self.mouseRelease(phg.getPathHelix(1), position=QPoint(1142, 1), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)

        # Verify model for correctness
        refvh0 = """0 Scaffold: _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,> <,> <,_ _,_ _,_ _,_ _,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_\n0 Staple:   _,_ _,_ _,_ _,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_"""
        self.assertEqual(refvh0, repr(self.app.v[0]))
        refvh1 = """1 Scaffold: _,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_\n1 Staple:   _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,_ _,_ _,_ _,_ _,_ _,_ _,_"""
        self.assertEqual(refvh1, repr(self.app.v[1]))
        refvh2 = """2 Scaffold: _,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_\n2 Staple:   _,_ _,_ _,_ _,_ _,_ _,_ _,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,_"""
        self.assertEqual(refvh2, repr(self.app.v[2]))
        refvh3 = """3 Scaffold: _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,_\n3 Staple:   _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,_"""
        self.assertEqual(refvh3, repr(self.app.v[3]))

        #self.debugHere()

if __name__ == '__main__':
    print "Running Last Recorded Test"
    test.cadnanoguitestcase.main()

