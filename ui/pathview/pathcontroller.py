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

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4.QtCore import pyqtSignal
# from tools.pathtool import PathTool
from tools.painttool import PaintTool
from tools.looptool import LoopTool
from tools.skiptool import SkipTool
from tools.breaktool import BreakTool
from tools.erasetool import EraseTool
from tools.selecttool import SelectTool


class PathController(QObject):
    """
    Manages the interactions between Path widgets / UI elements and the model.

    _activeToolWidget indicates which tool is active and lets the user change
    activeTool()

    """
    def __init__(self, win):
        super(PathController, self).__init__()
        self.mainWindow = win
        self._activeTool = None
        self._activeToolWidget = None

        self.selectTool = SelectTool(self)
        self.paintTool = PaintTool(self, win.pathGraphicsView.toolbar)
        self.eraseTool = EraseTool(self)
        self.insertionTool = LoopTool(self)
        self.skipTool = SkipTool(self)
        self.breakTool = BreakTool(self)

        win.actionPathSelect.triggered.connect(self.chooseSelectTool)
        win.actionPathPaint.triggered.connect(self.choosePaintTool)
        win.actionPathMove.triggered.connect(self.chooseMoveTool)
        win.actionPathBreak.triggered.connect(self.chooseBreakTool)
        win.actionPathErase.triggered.connect(self.chooseEraseTool)
        win.actionPathInsert.triggered.connect(self.chooseInsertTool)
        win.actionPathSkip.triggered.connect(self.chooseSkipTool)

        self.toolset = set((win.actionPathSelect, win.actionPathPaint,\
                            win.actionPathMove, win.actionPathBreak,\
                            win.actionPathErase, win.actionPencil,\
                            win.actionPathInsert, win.actionPathSkip))
        ag = QActionGroup(win)
        for a in self.toolset:
            ag.addAction(a)
        ag.setExclusive(True)
        self.chooseSelectTool()


    def activeTool(self):
        return self._activeTool

    def isSelectToolActive(self):
        if self._activeToolWidget is self.mainWindow.actionPathSelect:
            return True
        return False

    activeToolChanged = pyqtSignal()
    def setActiveTool(self, newActiveTool):
        if self._activeTool:
            self._activeTool.setActive(False)
        self._activeTool = newActiveTool
        self._activeTool.setActive(True)
        self.activeToolChanged.emit()

    def chooseSelectTool(self):
        widget = self.mainWindow.actionPathSelect
        if self._activeToolWidget is widget:
            return
        else:
            self._activeToolWidget = widget
        widget.setChecked(True)
        self.setActiveTool(self.selectTool)

    def choosePaintTool(self):
        widget = self.mainWindow.actionPathPaint
        if self._activeToolWidget is widget:
            self.paintTool.nextColor()
        else:
            self._activeToolWidget = widget
        widget.setChecked(True)
        self.setActiveTool(self.paintTool)

    def chooseMoveTool(self):
        widget = self.mainWindow.actionPathMove
        if self._activeToolWidget is widget:
            return
        else:
            self._activeToolWidget = widget
        widget.setChecked(True)
        # self.setActiveTool(self.moveTool)

    def chooseBreakTool(self):
        widget = self.mainWindow.actionPathBreak
        if self._activeToolWidget is widget:
            return
        else:
            self._activeToolWidget = widget
        widget.setChecked(True)
        self.setActiveTool(self.breakTool)

    def chooseEraseTool(self):
        widget = self.mainWindow.actionPathErase
        if self._activeToolWidget is widget:
            return
        else:
            self._activeToolWidget = widget
        widget.setChecked(True)
        self.setActiveTool(self.eraseTool)

    def chooseInsertTool(self):
        widget = self.mainWindow.actionPathInsert
        if self._activeToolWidget is widget:
            return
        else:
            self._activeToolWidget = widget
        widget.setChecked(True)
        self.setActiveTool(self.insertionTool)

    def chooseSkipTool(self):
        widget = self.mainWindow.actionPathSkip
        if self._activeToolWidget is widget:
            return
        else:
            self._activeToolWidget = widget
        widget.setChecked(True)
        self.setActiveTool(self.skipTool)
    # end def
# end class
