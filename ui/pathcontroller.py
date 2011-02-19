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


class PathController():
    """
    Manages the interactions between Path widgets / UI elements and the model
    """

    def __init__(self, win):
        self.mainWindow = win
        win.actionPathSelect.triggered.connect(self.chooseSelectTool)
        win.actionPathMove.triggered.connect(self.chooseMoveTool)
        win.actionPathBreak.triggered.connect(self.chooseBreakTool)
        win.actionPathErase.triggered.connect(self.chooseEraseTool)
        win.actionPathForce.triggered.connect(self.chooseForceTool)
        win.actionPathInsertion.triggered.connect(self.chooseInsertTool)
        win.actionPathSkip.triggered.connect(self.chooseSkipTool)
        self.toolset = set((win.actionPathSelect, win.actionPathMove,\
                            win.actionPathBreak, win.actionPathErase,\
                            win.actionPathForce, win.actionPathInsertion,\
                            win.actionPathSkip))
        ag = QActionGroup(win)
        for a in self.toolset:
            ag.addAction(a)
        ag.setExclusive(True)
        self.currentTool = None
        self.chooseSelectTool()

    def chooseSelectTool(self):
        widget = self.mainWindow.actionPathSelect
        if self.currentTool is widget:
            return
        else:
            self.currentTool = widget
        widget.setChecked(True)

    def chooseMoveTool(self):
        widget = self.mainWindow.actionPathMove
        if self.currentTool is widget:
            return
        else:
            self.currentTool = widget
        widget.setChecked(True)

    def chooseBreakTool(self):
        widget = self.mainWindow.actionPathBreak
        if self.currentTool is widget:
            return
        else:
            self.currentTool = widget
        widget.setChecked(True)

    def chooseEraseTool(self):
        widget = self.mainWindow.actionPathErase
        if self.currentTool is widget:
            return
        else:
            self.currentTool = widget
        widget.setChecked(True)

    def chooseForceTool(self):
        widget = self.mainWindow.actionPathForce
        if self.currentTool is widget:
            return
        else:
            self.currentTool = widget
        widget.setChecked(True)

    def chooseInsertTool(self):
        widget = self.mainWindow.actionPathInsertion
        if self.currentTool is widget:
            return
        else:
            self.currentTool = widget
        widget.setChecked(True)

    def chooseSkipTool(self):
        widget = self.mainWindow.actionPathSkip
        if self.currentTool is widget:
            return
        else:
            self.currentTool = widget
        widget.setChecked(True)
