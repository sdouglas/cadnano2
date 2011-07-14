
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
import time

def testMethod(self):
    # Create part
    partButton = self.mainWindow.topToolBar.widgetForAction(self.mainWindow.actionNewHoneycombPart)
    self.click(partButton)

    # Init refs
    sgi = self.documentController.sliceGraphicsItem
    phg = self.documentController.pathHelixGroup
    ash = self.documentController.pathHelixGroup.activeSliceHandle()

    # Playback user input
    self.mousePress(sgi.getSliceHelixByCoord(1, 3), position=QPoint(12, 23), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.slicescene)
    self.mouseMove(sgi.getSliceHelixByCoord(1, 3), position=QPoint(14, 26), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.slicescene)
    self.mouseRelease(sgi.getSliceHelixByCoord(1, 3), position=QPoint(14, 26), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.slicescene)
    self.mousePress(phg.getPathHelix(0), position=QPoint(105, 0), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
    self.mouseMove(phg.getPathHelix(0), position=QPoint(107, 0), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
    self.mouseMove(phg.getPathHelix(0), position=QPoint(109, 0), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
    self.mouseMove(phg.getPathHelix(0), position=QPoint(119, 0), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
    self.mouseMove(phg.getPathHelix(0), position=QPoint(133, 0), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
    self.mouseMove(phg.getPathHelix(0), position=QPoint(156, 2), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
    self.mouseMove(phg.getPathHelix(0), position=QPoint(212, 2), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
    self.mouseMove(phg.getPathHelix(0), position=QPoint(261, 2), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
    self.mouseMove(phg.getPathHelix(0), position=QPoint(275, 2), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
    self.mouseMove(phg.getPathHelix(0), position=QPoint(277, 2), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
    self.mouseMove(phg.getPathHelix(0), position=QPoint(279, 2), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
    self.mouseRelease(phg.getPathHelix(0), position=QPoint(279, 2), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
    self.mousePress(phg.getPathHelix(0), position=QPoint(545, 0), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
    self.mouseMove(phg.getPathHelix(0), position=QPoint(547, 0), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
    self.mouseMove(phg.getPathHelix(0), position=QPoint(552, 0), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
    self.mouseMove(phg.getPathHelix(0), position=QPoint(561, 0), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
    self.mouseMove(phg.getPathHelix(0), position=QPoint(575, 5), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
    self.mouseMove(phg.getPathHelix(0), position=QPoint(589, 12), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
    self.mouseMove(phg.getPathHelix(0), position=QPoint(608, 12), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
    self.mouseMove(phg.getPathHelix(0), position=QPoint(645, 14), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
    self.mouseMove(phg.getPathHelix(0), position=QPoint(682, 7), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
    self.mouseMove(phg.getPathHelix(0), position=QPoint(717, 2), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
    self.mouseMove(phg.getPathHelix(0), position=QPoint(759, 2), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
    self.mouseMove(phg.getPathHelix(0), position=QPoint(785, 5), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
    self.mouseMove(phg.getPathHelix(0), position=QPoint(789, 5), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
    self.mouseRelease(phg.getPathHelix(0), position=QPoint(789, 5), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
    self.mousePress(phg.getPathHelix(0), position=QPoint(196, 23), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
    self.mouseMove(phg.getPathHelix(0), position=QPoint(198, 23), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
    self.mouseMove(phg.getPathHelix(0), position=QPoint(212, 23), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
    self.mouseMove(phg.getPathHelix(0), position=QPoint(242, 28), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
    self.mouseMove(phg.getPathHelix(0), position=QPoint(305, 30), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
    self.mouseMove(phg.getPathHelix(0), position=QPoint(366, 30), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
    self.mouseMove(phg.getPathHelix(0), position=QPoint(419, 26), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
    self.mouseMove(phg.getPathHelix(0), position=QPoint(466, 23), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
    self.mouseMove(phg.getPathHelix(0), position=QPoint(498, 23), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
    self.mouseMove(phg.getPathHelix(0), position=QPoint(531, 30), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
    self.mouseMove(phg.getPathHelix(0), position=QPoint(552, 30), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
    self.mouseMove(phg.getPathHelix(0), position=QPoint(575, 30), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
    self.mouseMove(phg.getPathHelix(0), position=QPoint(608, 26), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
    self.mouseMove(phg.getPathHelix(0), position=QPoint(633, 23), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
    self.mouseMove(phg.getPathHelix(0), position=QPoint(652, 19), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
    self.mouseMove(phg.getPathHelix(0), position=QPoint(673, 19), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
    self.mouseMove(phg.getPathHelix(0), position=QPoint(689, 21), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
    self.mouseMove(phg.getPathHelix(0), position=QPoint(694, 21), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
    self.mouseMove(phg.getPathHelix(0), position=QPoint(696, 23), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
    self.mouseMove(phg.getPathHelix(0), position=QPoint(699, 23), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
    self.mouseMove(phg.getPathHelix(0), position=QPoint(703, 23), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
    self.mouseMove(phg.getPathHelix(0), position=QPoint(708, 23), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
    self.mouseMove(phg.getPathHelix(0), position=QPoint(713, 23), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
    self.mouseMove(phg.getPathHelix(0), position=QPoint(715, 23), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
    self.mouseMove(phg.getPathHelix(0), position=QPoint(717, 23), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
    self.mouseMove(phg.getPathHelix(0), position=QPoint(722, 23), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
    self.mouseMove(phg.getPathHelix(0), position=QPoint(731, 23), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
    self.mouseMove(phg.getPathHelix(0), position=QPoint(740, 23), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
    self.mouseMove(phg.getPathHelix(0), position=QPoint(747, 23), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
    self.mouseRelease(phg.getPathHelix(0), position=QPoint(747, 23), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
    self.mousePress(phg.getPathHelix(0), position=QPoint(268, 9), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
    self.mouseMove(phg.getPathHelix(0), position=QPoint(270, 9), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
    self.mouseMove(phg.getPathHelix(0), position=QPoint(272, 9), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
    self.mouseMove(phg.getPathHelix(0), position=QPoint(272, 12), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
    self.mouseMove(phg.getPathHelix(0), position=QPoint(277, 12), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
    self.mouseMove(phg.getPathHelix(0), position=QPoint(293, 14), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
    self.mouseMove(phg.getPathHelix(0), position=QPoint(312, 14), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
    self.mouseMove(phg.getPathHelix(0), position=QPoint(345, 16), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
    self.mouseMove(phg.getPathHelix(0), position=QPoint(363, 16), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
    self.mouseMove(phg.getPathHelix(0), position=QPoint(366, 16), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
    self.mouseMove(phg.getPathHelix(0), position=QPoint(368, 16), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
    self.mouseMove(phg.getPathHelix(0), position=QPoint(370, 16), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
    self.mouseMove(phg.getPathHelix(0), position=QPoint(373, 16), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
    self.mouseMove(phg.getPathHelix(0), position=QPoint(375, 16), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
    self.mouseMove(phg.getPathHelix(0), position=QPoint(377, 16), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
    self.mouseMove(phg.getPathHelix(0), position=QPoint(380, 16), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
    self.mouseMove(phg.getPathHelix(0), position=QPoint(382, 16), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
    self.mouseMove(phg.getPathHelix(0), position=QPoint(384, 16), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
    self.mouseMove(phg.getPathHelix(0), position=QPoint(389, 16), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
    self.mouseMove(phg.getPathHelix(0), position=QPoint(394, 16), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
    self.mouseMove(phg.getPathHelix(0), position=QPoint(396, 16), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
    self.mouseMove(phg.getPathHelix(0), position=QPoint(398, 16), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
    self.mouseMove(phg.getPathHelix(0), position=QPoint(401, 16), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
    self.mouseRelease(phg.getPathHelix(0), position=QPoint(401, 16), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
    self.mousePress(phg.getPathHelix(0), position=QPoint(747, 33), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
    self.mouseMove(phg.getPathHelix(0), position=QPoint(745, 33), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
    self.mouseMove(phg.getPathHelix(0), position=QPoint(736, 30), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
    self.mouseMove(phg.getPathHelix(0), position=QPoint(720, 30), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
    self.mouseMove(phg.getPathHelix(0), position=QPoint(696, 33), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
    self.mouseMove(phg.getPathHelix(0), position=QPoint(652, 30), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
    self.mouseMove(phg.getPathHelix(0), position=QPoint(605, 21), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
    self.mouseMove(phg.getPathHelix(0), position=QPoint(587, 19), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
    self.mouseMove(phg.getPathHelix(0), position=QPoint(564, 19), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
    self.mouseMove(phg.getPathHelix(0), position=QPoint(540, 19), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
    self.mouseMove(phg.getPathHelix(0), position=QPoint(519, 26), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
    self.mouseMove(phg.getPathHelix(0), position=QPoint(501, 28), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
    self.mouseMove(phg.getPathHelix(0), position=QPoint(489, 28), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
    self.mouseMove(phg.getPathHelix(0), position=QPoint(473, 28), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
    self.mouseMove(phg.getPathHelix(0), position=QPoint(449, 28), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
    self.mouseMove(phg.getPathHelix(0), position=QPoint(428, 28), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
    self.mouseMove(phg.getPathHelix(0), position=QPoint(419, 30), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
    self.mouseMove(phg.getPathHelix(0), position=QPoint(410, 33), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
    self.mouseMove(phg.getPathHelix(0), position=QPoint(408, 33), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
    self.mouseMove(phg.getPathHelix(0), position=QPoint(405, 33), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
    self.mouseMove(phg.getPathHelix(0), position=QPoint(403, 35), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
    self.mouseMove(phg.getPathHelix(0), position=QPoint(401, 35), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
    self.mouseMove(phg.getPathHelix(0), position=QPoint(398, 35), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
    self.mouseMove(phg.getPathHelix(0), position=QPoint(396, 35), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
    self.mouseMove(phg.getPathHelix(0), position=QPoint(391, 35), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
    self.mouseMove(phg.getPathHelix(0), position=QPoint(384, 35), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
    self.mouseMove(phg.getPathHelix(0), position=QPoint(375, 35), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
    self.mouseMove(phg.getPathHelix(0), position=QPoint(361, 35), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
    self.mouseMove(phg.getPathHelix(0), position=QPoint(354, 35), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
    self.mouseMove(phg.getPathHelix(0), position=QPoint(347, 35), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
    self.mouseMove(phg.getPathHelix(0), position=QPoint(340, 35), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
    self.mouseMove(phg.getPathHelix(0), position=QPoint(338, 35), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
    self.mouseMove(phg.getPathHelix(0), position=QPoint(333, 35), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
    self.mouseMove(phg.getPathHelix(0), position=QPoint(331, 35), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
    self.mouseMove(phg.getPathHelix(0), position=QPoint(328, 33), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
    self.mouseMove(phg.getPathHelix(0), position=QPoint(324, 33), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
    self.mouseMove(phg.getPathHelix(0), position=QPoint(317, 33), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
    self.mouseRelease(phg.getPathHelix(0), position=QPoint(317, 33), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)

    # Verify model for correctness
    refvh0 = """0 Scaffold: _,_ _,_ _,_ _,_ _,_ _,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,_ _,> <,> <,_ _,_ _,_ _,_ _,_ _,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,_ _,_ _,_\n0 Staple:   _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,> <,> <,> <,> <,> <,> <,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_"""
    self.assertEqual(refvh0, repr(self.app.v[0]))

    #self.debugHere()
