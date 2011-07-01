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

def testMethod(self):
    # Create part
    partButton = self.mainWindow.topToolBar.widgetForAction(self.mainWindow.actionNewHoneycombPart)
    self.click(partButton)

    # Init refs
    sgi = self.documentController.sliceGraphicsItem
    phg = self.documentController.pathHelixGroup
    ash = self.documentController.pathHelixGroup.activeSliceHandle()

    # Playback user input
    self.mousePress(sgi.getSliceHelixByCoord(0, 0), position=QPoint(22, 10), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.slicescene)
    self.mouseRelease(sgi.getSliceHelixByCoord(0, 0), position=QPoint(22, 10), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.slicescene)
    self.mousePress(sgi.getSliceHelixByCoord(0, 1), position=QPoint(15, 16), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.slicescene)
    self.mouseRelease(sgi.getSliceHelixByCoord(0, 1), position=QPoint(15, 16), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.slicescene)
    self.mousePress(phg.getPathHelix(0), position=QPoint(412, 9), modifiers=Qt.AltModifier, qgraphicsscene=self.mainWindow.pathscene)
    self.mouseRelease(phg.getPathHelix(0), position=QPoint(412, 9), modifiers=Qt.AltModifier, qgraphicsscene=self.mainWindow.pathscene)
    self.mousePress(phg.getPathHelix(1), position=QPoint(454, 24), modifiers=Qt.AltModifier, qgraphicsscene=self.mainWindow.pathscene)
    self.mouseRelease(phg.getPathHelix(1), position=QPoint(454, 24), modifiers=Qt.AltModifier, qgraphicsscene=self.mainWindow.pathscene)

    # Verify model for correctness
    refvh0 = """0 Scaffold: _,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_\n0 Staple:   _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_"""
    self.assertEqual(refvh0, repr(self.app.v[0]))
    refvh1 = """1 Scaffold: _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,_\n1 Staple:   _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_"""
    self.assertEqual(refvh1, repr(self.app.v[1]))

    # self.debugHere()
