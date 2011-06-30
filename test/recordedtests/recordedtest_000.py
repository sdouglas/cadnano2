
from template import RecordedTests

def testMethod(self):
        # Create part
        partButton = self.mainWindow.topToolBar.widgetForAction(self.mainWindow.actionNewHoneycombPart)
        self.click(partButton)
        # Init SliceHelix refs
        sliceGraphicsItem = self.documentController.sliceGraphicsItem
        sgi = self.documentController.sliceGraphicsItem
        sh_0_0 = sgi.getSliceHelixByCoord(0, 0)
        sh_0_1 = sgi.getSliceHelixByCoord(0, 1)
        sh_0_2 = sgi.getSliceHelixByCoord(0, 2)

        # Init PathHelix refs
        pathHelixGroup = self.documentController.pathHelixGroup
        phg = self.documentController.pathHelixGroup
        ph0 = phg.getPathHelix(0)
        ph1 = phg.getPathHelix(1)

        # Playback user input
        self.mousePress(sh_0_0, position=QPoint(22, 12), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
        self.mouseRelease(sh_0_0, position=QPoint(22, 12), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
        self.mousePress(sh_0_1, position=QPoint(25, 24), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
        self.mouseRelease(sh_0_1, position=QPoint(25, 24), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
        self.mousePress(ph0, position=QPoint(128, 12), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
        self.mouseMove(ph0, position=QPoint(130, 12), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
        self.mouseMove(ph0, position=QPoint(133, 12), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
        self.mouseMove(ph0, position=QPoint(140, 12), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
        self.mouseMove(ph0, position=QPoint(147, 9), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
        self.mouseMove(ph0, position=QPoint(158, 7), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
        self.mouseMove(ph0, position=QPoint(170, 5), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
        self.mouseMove(ph0, position=QPoint(182, 5), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
        self.mouseMove(ph0, position=QPoint(193, 5), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
        self.mouseMove(ph0, position=QPoint(198, 5), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
        self.mouseMove(ph0, position=QPoint(200, 5), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
        self.mouseMove(ph0, position=QPoint(205, 5), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
        self.mouseMove(ph0, position=QPoint(210, 5), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
        self.mouseMove(ph0, position=QPoint(212, 5), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
        self.mouseMove(ph0, position=QPoint(214, 5), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
        self.mouseRelease(ph0, position=QPoint(214, 5), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
        self.mousePress(ph1, position=QPoint(191, 1), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
        self.mouseMove(ph1, position=QPoint(193, 1), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
        self.mouseMove(ph1, position=QPoint(196, 1), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
        self.mouseMove(ph1, position=QPoint(198, 3), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
        self.mouseMove(ph1, position=QPoint(200, 3), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
        self.mouseMove(ph1, position=QPoint(207, 3), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
        self.mouseMove(ph1, position=QPoint(214, 3), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
        self.mouseMove(ph1, position=QPoint(224, 3), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
        self.mouseMove(ph1, position=QPoint(235, 3), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
        self.mouseMove(ph1, position=QPoint(242, 3), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
        self.mouseMove(ph1, position=QPoint(249, 3), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
        self.mouseMove(ph1, position=QPoint(251, 3), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
        self.mouseMove(ph1, position=QPoint(256, 3), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
        self.mouseMove(ph1, position=QPoint(258, 3), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
        self.mouseRelease(ph1, position=QPoint(258, 3), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
        self.mousePress(sh_0_2, position=QPoint(29, 5), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)
        self.mouseRelease(sh_0_2, position=QPoint(29, 5), modifiers=Qt.NoModifier, qgraphicsscene=self.mainWindow.pathscene)

        # Verify model for correctness
        refvh0 = """0 Scaffold: _,_ _,_ _,_ _,_ _,_ _,_ _,> <,> <,> <,> <,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,> <,> <,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_\n0 Staple:   _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_"""
        self.assertEqual(refvh0, repr(self.app.v[0]))
        refvh1 = """1 Scaffold: _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,> <,> <,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_\n1 Staple:   _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,> <,> <,> <,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_"""
        self.assertEqual(refvh1, repr(self.app.v[1]))
        refvh2 = """2 Scaffold: _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,> <,> <,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_\n2 Staple:   _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_"""
        self.assertEqual(refvh2, repr(self.app.v[2]))

        self.debugHere()
