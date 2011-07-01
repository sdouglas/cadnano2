
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
    partButton = self.mainWindow.topToolBar.widgetForAction(self.mainWindow.actionNewSquarePart)
        self.click(partButton)

    # Init refs
    sgi = self.documentController.sliceGraphicsItem
    phg = self.documentController.pathHelixGroup
    ash = self.documentController.pathHelixGroup.activeSliceHandle()

    # Playback user input
    self.mousePress(sgi.getSliceHelixByCoord(0, 0), position=QPoint(19, 13), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.slicescene)
    self.mouseMove(sgi.getSliceHelixByCoord(0, 0), position=QPoint(19, 14), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.slicescene)
    self.mouseRelease(sgi.getSliceHelixByCoord(0, 0), position=QPoint(19, 14), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.slicescene)
    self.mousePress(phg.getPathHelix(0), position=QPoint(630, 10), modifiers=Qt.AltModifier, qgraphicsscene=self.mainWindow.pathscene)
    self.mouseRelease(phg.getPathHelix(0), position=QPoint(630, 10), modifiers=Qt.AltModifier, qgraphicsscene=self.mainWindow.pathscene)
    self.mousePress(phg.getPathHelix(0), position=QPoint(889, 27), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
    self.mouseMove(phg.getPathHelix(0), position=QPoint(889, 30), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
    self.mouseMove(phg.getPathHelix(0), position=QPoint(873, 30), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
    self.mouseMove(phg.getPathHelix(0), position=QPoint(856, 30), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
    self.mouseMove(phg.getPathHelix(0), position=QPoint(829, 34), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
    self.mouseMove(phg.getPathHelix(0), position=QPoint(765, 37), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
    self.mouseMove(phg.getPathHelix(0), position=QPoint(714, 37), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
    self.mouseMove(phg.getPathHelix(0), position=QPoint(664, 37), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
    self.mouseMove(phg.getPathHelix(0), position=QPoint(630, 34), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
    self.mouseMove(phg.getPathHelix(0), position=QPoint(600, 30), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
    self.mouseMove(phg.getPathHelix(0), position=QPoint(576, 27), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
    self.mouseMove(phg.getPathHelix(0), position=QPoint(539, 24), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
    self.mouseMove(phg.getPathHelix(0), position=QPoint(495, 24), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
    self.mouseMove(phg.getPathHelix(0), position=QPoint(458, 24), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
    self.mouseMove(phg.getPathHelix(0), position=QPoint(431, 24), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
    self.mouseMove(phg.getPathHelix(0), position=QPoint(411, 24), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
    self.mouseMove(phg.getPathHelix(0), position=QPoint(394, 24), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
    self.mouseRelease(phg.getPathHelix(0), position=QPoint(394, 24), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)

    # Verify model for correctness
    refvh0 = """0 Scaffold: _,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_\n0 Staple:   _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_"""
    self.assertEqual(refvh0, repr(self.app.v[0]))

    #self.debugHere()
