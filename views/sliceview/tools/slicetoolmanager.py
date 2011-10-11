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


class SliceToolManager(QObject):
    """Manages interactions between the slice widgets/UI and the model."""
    def __init__(self, win):
        """
        We store mainWindow because a controller's got to have
        references to both the layer above (UI) and the layer below (model)
        """
        super(SliceToolManager, self).__init__()
        self._window = win
        self._connectWindowSignalsToSelf()

    ### SIGNALS ###
    activeSliceSetToFirstIndexSignal = pyqtSignal()
    activeSliceSetToLastIndexSignal = pyqtSignal()
    activePartRenumber = pyqtSignal()

    ### SLOTS ###
    def activeSliceFirstSlot(self):
        """
        Use a signal to notify the ActiveSliceHandle to move. A signal is used
        because the SliceToolManager must be instantiated first, and the
        ActiveSliceHandle can later subscribe.
        """
        part = self._window.selectedPart()
        if part != None:
            part.setActiveBaseIndex(0)

    def activeSliceLastSlot(self):
        part = self._window.selectedPart()
        if part != None:
            part.setActiveBaseIndex(part.maxBaseIdx()-1)

    def actionRenumberSlot(self):
        part = self._window.selectedPart()
        if part != None:
            part.renumber()

    ### METHODS ###
    def _connectWindowSignalsToSelf(self):
        """This method serves to group all the signal & slot connections
        made by SliceToolManager"""
        self._window.actionSliceFirst.triggered.connect(self.activeSliceFirstSlot)
        self._window.actionSliceLast.triggered.connect(self.activeSliceLastSlot)
        self._window.actionRenumber.triggered.connect(self.actionRenumberSlot)
