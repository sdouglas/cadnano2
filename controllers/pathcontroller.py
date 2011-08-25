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

from cadnano import app
from views.pathview.tools.breaktool import BreakTool
from views.pathview.tools.erasetool import EraseTool
from views.pathview.tools.painttool import PaintTool
from views.pathview.tools.penciltool import PencilTool
from views.pathview.tools.inserttool import InsertTool
from views.pathview.tools.newpenciltool import NewPencilTool
from views.pathview.tools.selecttool import SelectTool
from views.pathview.tools.skiptool import SkipTool
from views.pathview.tools.addseqtool import AddSeqTool
import util
import os

# import Qt stuff into the module namespace with PySide, PyQt4 independence
util.qtWrapImport('QtCore', globals(), ['QObject', 'pyqtSignal'])
util.qtWrapImport('QtGui', globals(), [ 'QActionGroup'])


class PathController(QObject):
    """
    Manages the interactions between Path widgets / UI elements and the model.

    _activeToolWidget indicates which tool is active and lets the user change
    activeTool()

    """
    def __init__(self, win):
        super(PathController, self).__init__()
        self.mainWindow = win
        self.testRecorder = None
        self._activeTool = None
        self._activePath = None
        self.selectTool = SelectTool(self)
        self.breakTool = BreakTool(self)
        self.eraseTool = EraseTool(self)
        self.insertTool = InsertTool(self)
        self.skipTool = SkipTool(self)
        self.breakTool = BreakTool(self)
        self.paintTool = PaintTool(self, win.pathGraphicsView.toolbar)
        #self.pencilTool = PencilTool(self)
        self.pencilTool = NewPencilTool(self)
        self.addSeqTool = AddSeqTool(self)
        self.moveTool = None

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

        tools = ('Select', 'Paint', 'Break', 'Erase', 'Insert', 'Skip',\
                 'Pencil', 'AddSeq')
        ag = QActionGroup(win)
        # for toolName in tools:
        #     toolAction = installTool(toolName, win)
        #     ag.addAction(toolAction)
        map((lambda toolName: ag.addAction(installTool(toolName, win))), tools) 
        ag.setExclusive(True)
        # Select the preferred Startup tool
        startupToolName = app().prefs.getStartupToolName()
        getattr(self, 'choose' + startupToolName + 'Tool')()

    def activeTool(self):
        return self._activeTool

    def setActivePath(self, phg):
        self._activePath = phg

    def activePath(self):
        return self._activePath

    def isSelectToolActive(self):
        if self.activeTool() == self.selectTool:
            return True
        return False

    activeToolChanged = pyqtSignal(str)

    def setActiveTool(self, newActiveTool):
        if newActiveTool == self._activeTool:
            return
        if self.lastLocation():
            newActiveTool.updateLocation(*self.lastLocation())
        currentPathHelix = None
        if self._activeTool:
            self._activeTool.setActive(False)
        self._activeTool = newActiveTool
        self._activeTool.setActive(True)
        self.activeToolChanged.emit(self._activeTool.actionName)

    def lastLocation(self):
        """(PathHelix, posInScene) or None, depending on where
        the mouse is (basically, pathHelix and position of
        the last event seen by the active tool)"""
        if self._activeTool == None:
            return None
        return self._activeTool.lastLocation()
# end class
