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

import util
# import Qt stuff into the module namespace with PySide, PyQt4 independence
util.qtWrapImport('QtCore', globals(), ['pyqtSignal', 'QObject'])
util.qtWrapImport('QtGui', globals(), [ 'QActionGroup'])

class SliceController(QObject):
    """
    Manages interactions between the slice widgets/UI and the model.
    """
    activeSliceLastSignal = pyqtSignal()
    activeSliceFirstSignal = pyqtSignal()
    
    def __init__(self, win):
        """
        We store mainWindow because a controller's got to have
        references to both the layer above (UI) and the layer below (model)
        """
        super(SliceController, self).__init__()
        self.mainWindow = win
        self.testRecorder = None
        win.actionSliceSelect.triggered.connect(self.chooseSelectTool)
        # win.actionSliceMove.triggered.connect(self.chooseMoveTool)
        win.actionSliceFirst.triggered.connect(self.sliceFirstClicked)
        win.actionSliceLast.triggered.connect(self.sliceLastClicked)
        win.actionRenumber.triggered.connect(self.renumberClicked)

        self.toolset =[win.actionSliceSelect]  # win.actionSliceMove
        ag = QActionGroup(win)
        for a in self.toolset:
            ag.addAction(a)
        ag.setExclusive(True)
        self.currentTool = None
        self.chooseSelectTool()

    def chooseSelectTool(self):
        widget = self.mainWindow.actionSliceSelect
        if self.currentTool is widget:
            return
        else:
            self.currentTool = widget
        widget.setChecked(True)

    # def chooseMoveTool(self):
    #     widget = self.mainWindow.actionSliceMove
    #     if self.currentTool is widget:
    #         return
    #     else:
    #         self.currentTool = widget
    #     widget.setChecked(True)
    # end def

    def sliceLastClicked(self):
        """docstring for sliceLastClicked"""
        self.activeSliceLastSignal.emit()
    # end def

    def sliceFirstClicked(self):
        self.activeSliceFirstSignal.emit()
    # end def

    def renumberClicked(self):
        self.mainWindow.pathController.activePath().renumber()
