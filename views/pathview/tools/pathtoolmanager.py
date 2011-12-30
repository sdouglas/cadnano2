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

import os
from cadnano import app
from selecttool import SelectTool
from penciltool import PencilTool
from breaktool import BreakTool
from erasetool import EraseTool
from insertiontool import InsertionTool
from skiptool import SkipTool
from painttool import PaintTool
from addseqtool import AddSeqTool
import util

# import Qt stuff into the module namespace with PySide, PyQt4 independence
util.qtWrapImport('QtCore', globals(), ['QObject', 'pyqtSignal'])
util.qtWrapImport('QtGui', globals(), [ 'QActionGroup'])


class PathToolManager(QObject):
    """
    Manages the interactions between Path widgets / UI elements and the model.
    """
    def __init__(self, win):
        super(PathToolManager, self).__init__()
        self.window = win
        self._activeTool = None
        self._activePart = None
        self.selectTool = SelectTool(self)
        self.pencilTool = PencilTool(self)
        self.breakTool = BreakTool(self)
        self.eraseTool = EraseTool(self)
        self.insertionTool = InsertionTool(self)
        self.skipTool = SkipTool(self)
        self.paintTool = PaintTool(self) # (self, win.pathGraphicsView.toolbar)
        self.addSeqTool = AddSeqTool(self)

        def installTool(toolName, window):
            toolWidget = getattr(window, 'actionPath' + toolName)
            lToolName = toolName[0].lower() + toolName[1:]
            tool = getattr(self, lToolName + 'Tool')
            tool.actionName = 'actionPath' + toolName

            def clickHandler(self):
                toolWidget.setChecked(True)
                self.setActiveTool(tool)
                if hasattr(tool, 'widgetClicked'):
                    tool.widgetClicked()
            selectToolMethodName = 'choose' + toolName + 'Tool'
            setattr(self.__class__, selectToolMethodName, clickHandler)
            handler = getattr(self, selectToolMethodName)
            toolWidget.triggered.connect(handler)
            return toolWidget

        tools = ('Select', 'Pencil', 'Break', 'Erase', 'Insertion', 'Skip', 'Paint', 'AddSeq')
        ag = QActionGroup(win)
        # Call installTool on every tool
        map((lambda toolName: ag.addAction(installTool(toolName, win))), tools)
        ag.setExclusive(True)
        # Select the preferred Startup tool
        startupToolName = app().prefs.getStartupToolName()
        getattr(self, 'choose' + startupToolName + 'Tool')()

    ### SIGNALS ###
    activeToolChangedSignal = pyqtSignal(str)

    ### SLOTS ###

    ### METHODS ###
    def activePart(self):
        return self._activePart

    def setActivePart(self, part):
        self._activePart = part

    def activeTool(self):
        return self._activeTool

    def setActiveTool(self, newActiveTool):
        if newActiveTool == self._activeTool:
            return
        if self.lastLocation():
            newActiveTool.updateLocation(*self.lastLocation())
        if self._activeTool:
            self._activeTool.setActive(False)
        if str(newActiveTool) == "selectTool":
            self.window.activateSelection(True)
        elif str(newActiveTool) == "paintTool":
            self.window.activateSelection(True)
        else:
            self.window.activateSelection(False)
        self._activeTool = newActiveTool
        self._activeTool.setActive(True)
        self.activeToolChangedSignal.emit(self._activeTool.actionName)

    def isSelectToolActive(self):
        if self.activeTool() == self.selectTool:
            return True
        return False

    def lastLocation(self):
        """(PathHelix, posInScene) or None, depending on where
        the mouse is (basically, pathHelix and position of
        the last event seen by the active tool)"""
        if self._activeTool == None:
            return None
        return self._activeTool.lastLocation()
# end class
