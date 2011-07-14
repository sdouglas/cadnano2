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
    partButton = self.mainWindow.topToolBar.widgetForAction(self.mainWindow.actionNewHoneycombPart)
    self.click(partButton)

    # Init refs
    sgi = self.documentController.sliceGraphicsItem
    phg = self.documentController.pathHelixGroup
    ash = self.documentController.pathHelixGroup.activeSliceHandle()

    # Playback user input
    self.mousePress(sgi.getSliceHelixByCoord(2, 8), position=QPoint(7, 11), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.slicescene)
    self.mouseRelease(sgi.getSliceHelixByCoord(2, 8), position=QPoint(7, 11), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.slicescene)
    self.mousePress(sgi.getSliceHelixByCoord(2, 9), position=QPoint(3, 7), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.slicescene)
    self.mouseRelease(sgi.getSliceHelixByCoord(2, 9), position=QPoint(3, 7), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.slicescene)
    self.mousePress(sgi.getSliceHelixByCoord(3, 9), position=QPoint(16, 12), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.slicescene)
    self.mouseMove(sgi.getSliceHelixByCoord(3, 9), position=QPoint(15, 12), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.slicescene)
    self.mouseRelease(sgi.getSliceHelixByCoord(3, 9), position=QPoint(15, 12), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.slicescene)
    self.mousePress(sgi.getSliceHelixByCoord(3, 8), position=QPoint(22, 6), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.slicescene)
    self.mouseRelease(sgi.getSliceHelixByCoord(3, 8), position=QPoint(22, 6), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.slicescene)
    self.mousePress(sgi.getSliceHelixByCoord(3, 7), position=QPoint(24, 8), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.slicescene)
    self.mouseRelease(sgi.getSliceHelixByCoord(3, 7), position=QPoint(24, 8), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.slicescene)
    self.mousePress(sgi.getSliceHelixByCoord(2, 7), position=QPoint(16, 19), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.slicescene)
    self.mouseRelease(sgi.getSliceHelixByCoord(2, 7), position=QPoint(16, 19), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.slicescene)
    self.mousePress(ash, position=QPoint(6, 118), modifiers=Qt.AltModifier|Qt.ShiftModifier, qgraphicsscene=self.mainWindow.pathscene)
    self.mouseRelease(ash, position=QPoint(6, 118), modifiers=Qt.AltModifier|Qt.ShiftModifier, qgraphicsscene=self.mainWindow.pathscene)

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