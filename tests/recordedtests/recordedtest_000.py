
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
    """Recorded test 000: click-drag +6 helices, alt+shift+click activeslicehandle"""
    # Create part
    partButton = self.mainWindow.topToolBar.widgetForAction(self.mainWindow.actionNewHoneycombPart)
    self.click(partButton)

    # Init refs
    sgi = self.documentController.sliceGraphicsItem
    phg = self.documentController.pathHelixGroup
    ash = self.documentController.pathHelixGroup.activeSliceHandle()

    # Init buttons

    # Playback user input
    self.mousePress(sgi.getSliceHelixByCoord(5, 13), position=QPoint(10, 9), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.slicescene)
    self.mouseMove(sgi.getSliceHelixByCoord(5, 13), position=QPoint(11, 9), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.slicescene)
    self.mouseMove(sgi.getSliceHelixByCoord(5, 13), position=QPoint(15, 9), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.slicescene)
    self.mouseMove(sgi.getSliceHelixByCoord(5, 13), position=QPoint(18, 9), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.slicescene)
    self.mouseMove(sgi.getSliceHelixByCoord(5, 13), position=QPoint(22, 9), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.slicescene)
    self.mouseMove(sgi.getSliceHelixByCoord(5, 13), position=QPoint(25, 9), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.slicescene)
    self.mouseMove(sgi.getSliceHelixByCoord(5, 13), position=QPoint(27, 9), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.slicescene)
    self.mouseMove(sgi.getSliceHelixByCoord(5, 13), position=QPoint(28, 11), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.slicescene)
    self.mouseMove(sgi.getSliceHelixByCoord(5, 13), position=QPoint(30, 14), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.slicescene)
    self.mouseMove(sgi.getSliceHelixByCoord(5, 13), position=QPoint(32, 16), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.slicescene)
    self.mouseMove(sgi.getSliceHelixByCoord(5, 13), position=QPoint(33, 16), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.slicescene)
    self.mouseMove(sgi.getSliceHelixByCoord(5, 13), position=QPoint(35, 19), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.slicescene)
    self.mouseMove(sgi.getSliceHelixByCoord(5, 13), position=QPoint(37, 21), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.slicescene)
    self.mouseMove(sgi.getSliceHelixByCoord(5, 13), position=QPoint(37, 23), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.slicescene)
    self.mouseMove(sgi.getSliceHelixByCoord(5, 13), position=QPoint(37, 25), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.slicescene)
    self.mouseMove(sgi.getSliceHelixByCoord(5, 13), position=QPoint(37, 26), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.slicescene)
    self.mouseMove(sgi.getSliceHelixByCoord(5, 13), position=QPoint(37, 30), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.slicescene)
    self.mouseMove(sgi.getSliceHelixByCoord(5, 13), position=QPoint(35, 33), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.slicescene)
    self.mouseMove(sgi.getSliceHelixByCoord(5, 13), position=QPoint(35, 36), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.slicescene)
    self.mouseMove(sgi.getSliceHelixByCoord(5, 13), position=QPoint(35, 40), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.slicescene)
    self.mouseMove(sgi.getSliceHelixByCoord(5, 13), position=QPoint(33, 43), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.slicescene)
    self.mouseMove(sgi.getSliceHelixByCoord(5, 13), position=QPoint(33, 45), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.slicescene)
    self.mouseMove(sgi.getSliceHelixByCoord(5, 13), position=QPoint(33, 47), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.slicescene)
    self.mouseMove(sgi.getSliceHelixByCoord(5, 13), position=QPoint(33, 50), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.slicescene)
    self.mouseMove(sgi.getSliceHelixByCoord(5, 13), position=QPoint(33, 53), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.slicescene)
    self.mouseMove(sgi.getSliceHelixByCoord(5, 13), position=QPoint(33, 57), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.slicescene)
    self.mouseMove(sgi.getSliceHelixByCoord(5, 13), position=QPoint(33, 60), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.slicescene)
    self.mouseMove(sgi.getSliceHelixByCoord(5, 13), position=QPoint(33, 63), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.slicescene)
    self.mouseMove(sgi.getSliceHelixByCoord(5, 13), position=QPoint(33, 65), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.slicescene)
    self.mouseMove(sgi.getSliceHelixByCoord(5, 13), position=QPoint(33, 67), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.slicescene)
    self.mouseMove(sgi.getSliceHelixByCoord(5, 13), position=QPoint(33, 68), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.slicescene)
    self.mouseMove(sgi.getSliceHelixByCoord(5, 13), position=QPoint(30, 70), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.slicescene)
    self.mouseMove(sgi.getSliceHelixByCoord(5, 13), position=QPoint(28, 70), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.slicescene)
    self.mouseMove(sgi.getSliceHelixByCoord(5, 13), position=QPoint(27, 72), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.slicescene)
    self.mouseMove(sgi.getSliceHelixByCoord(5, 13), position=QPoint(23, 72), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.slicescene)
    self.mouseMove(sgi.getSliceHelixByCoord(5, 13), position=QPoint(20, 74), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.slicescene)
    self.mouseMove(sgi.getSliceHelixByCoord(5, 13), position=QPoint(18, 75), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.slicescene)
    self.mouseMove(sgi.getSliceHelixByCoord(5, 13), position=QPoint(17, 77), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.slicescene)
    self.mouseMove(sgi.getSliceHelixByCoord(5, 13), position=QPoint(13, 77), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.slicescene)
    self.mouseMove(sgi.getSliceHelixByCoord(5, 13), position=QPoint(11, 80), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.slicescene)
    self.mouseMove(sgi.getSliceHelixByCoord(5, 13), position=QPoint(10, 80), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.slicescene)
    self.mouseMove(sgi.getSliceHelixByCoord(5, 13), position=QPoint(8, 80), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.slicescene)
    self.mouseMove(sgi.getSliceHelixByCoord(5, 13), position=QPoint(8, 84), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.slicescene)
    self.mouseMove(sgi.getSliceHelixByCoord(5, 13), position=QPoint(6, 84), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.slicescene)
    self.mouseMove(sgi.getSliceHelixByCoord(5, 13), position=QPoint(5, 84), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.slicescene)
    self.mouseMove(sgi.getSliceHelixByCoord(5, 13), position=QPoint(3, 84), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.slicescene)
    self.mouseMove(sgi.getSliceHelixByCoord(5, 13), position=QPoint(0, 80), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.slicescene)
    self.mouseMove(sgi.getSliceHelixByCoord(5, 13), position=QPoint(-3, 75), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.slicescene)
    self.mouseMove(sgi.getSliceHelixByCoord(5, 13), position=QPoint(-3, 74), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.slicescene)
    self.mouseMove(sgi.getSliceHelixByCoord(5, 13), position=QPoint(-6, 72), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.slicescene)
    self.mouseMove(sgi.getSliceHelixByCoord(5, 13), position=QPoint(-6, 70), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.slicescene)
    self.mouseMove(sgi.getSliceHelixByCoord(5, 13), position=QPoint(-8, 68), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.slicescene)
    self.mouseMove(sgi.getSliceHelixByCoord(5, 13), position=QPoint(-9, 67), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.slicescene)
    self.mouseMove(sgi.getSliceHelixByCoord(5, 13), position=QPoint(-11, 65), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.slicescene)
    self.mouseMove(sgi.getSliceHelixByCoord(5, 13), position=QPoint(-13, 62), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.slicescene)
    self.mouseMove(sgi.getSliceHelixByCoord(5, 13), position=QPoint(-15, 60), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.slicescene)
    self.mouseMove(sgi.getSliceHelixByCoord(5, 13), position=QPoint(-16, 57), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.slicescene)
    self.mouseMove(sgi.getSliceHelixByCoord(5, 13), position=QPoint(-18, 53), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.slicescene)
    self.mouseMove(sgi.getSliceHelixByCoord(5, 13), position=QPoint(-18, 52), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.slicescene)
    self.mouseMove(sgi.getSliceHelixByCoord(5, 13), position=QPoint(-18, 50), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.slicescene)
    self.mouseMove(sgi.getSliceHelixByCoord(5, 13), position=QPoint(-18, 48), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.slicescene)
    self.mouseMove(sgi.getSliceHelixByCoord(5, 13), position=QPoint(-18, 47), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.slicescene)
    self.mouseMove(sgi.getSliceHelixByCoord(5, 13), position=QPoint(-18, 45), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.slicescene)
    self.mouseMove(sgi.getSliceHelixByCoord(5, 13), position=QPoint(-18, 43), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.slicescene)
    self.mouseMove(sgi.getSliceHelixByCoord(5, 13), position=QPoint(-18, 41), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.slicescene)
    self.mouseMove(sgi.getSliceHelixByCoord(5, 13), position=QPoint(-16, 38), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.slicescene)
    self.mouseMove(sgi.getSliceHelixByCoord(5, 13), position=QPoint(-13, 35), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.slicescene)
    self.mouseMove(sgi.getSliceHelixByCoord(5, 13), position=QPoint(-9, 30), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.slicescene)
    self.mouseMove(sgi.getSliceHelixByCoord(5, 13), position=QPoint(-6, 26), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.slicescene)
    self.mouseMove(sgi.getSliceHelixByCoord(5, 13), position=QPoint(-4, 25), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.slicescene)
    self.mouseMove(sgi.getSliceHelixByCoord(5, 13), position=QPoint(-3, 21), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.slicescene)
    self.mouseRelease(sgi.getSliceHelixByCoord(5, 13), position=QPoint(-3, 21), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.slicescene)
    self.mousePress(ash, position=QPoint(9, 120), modifiers=Qt.AltModifier|Qt.ShiftModifier, qgraphicsscene=self.mainWindow.pathscene)
    self.mouseRelease(ash, position=QPoint(9, 120), modifiers=Qt.AltModifier|Qt.ShiftModifier, qgraphicsscene=self.mainWindow.pathscene)

    # Verify model for correctness
    refvh0 = """0 Scaffold: _,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,_\n0 Staple:   _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_"""
    self.assertEqual(refvh0, repr(self.app.v[0]))
    refvh1 = """1 Scaffold: _,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,_\n1 Staple:   _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_"""
    self.assertEqual(refvh1, repr(self.app.v[1]))
    refvh2 = """2 Scaffold: _,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,_\n2 Staple:   _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_"""
    self.assertEqual(refvh2, repr(self.app.v[2]))
    refvh3 = """3 Scaffold: _,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,_\n3 Staple:   _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_"""
    self.assertEqual(refvh3, repr(self.app.v[3]))
    refvh4 = """4 Scaffold: _,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,_\n4 Staple:   _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_"""
    self.assertEqual(refvh4, repr(self.app.v[4]))
    refvh5 = """5 Scaffold: _,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,_\n5 Staple:   _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_"""
    self.assertEqual(refvh5, repr(self.app.v[5]))

    #self.debugHere()
