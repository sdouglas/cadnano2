#!/usr/bin/env python
# encoding: utf-8

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
util.qtWrapImport('QtGui', globals(), [ 'QUndoCommand', 'QUndoStack'])

class PartGraphicsItem(QGraphicsPathItem):
    def __init__(self, modelPart, parent):
        super(PartGraphicsItem, self).__init__(parent)
        self._modelPart = modelPart
        self._controller = 
        self.connectSignals()

    ### SIGNALS ###

    ### SLOTS ###
    def partParentChangedSlot(self):
        """docstring for partParentChangedSlot"""
        pass

    def partDestroyedSlot(self):
        """docstring for partDestroyedSlot"""
        pass

    def partMovedSlot(self, pos):
        """docstring for partMovedSlot"""
        pass

    def xover3pCreatedSlot(self, strand, idx):
        """docstring for xover3pCreatedSlot"""
        pass

    def xover3pDestroyedSlot(self, strand, idx):
        """docstring for xover3pDestroyedSlot"""
        pass

    ### METHODS ###
    def connectSignals(self):
        self._part.partParentChangedSignal.connect(self.partParentChangedSlot)
        self._part.partDestroyedSignal.connect(self.partDestroyedSlot)
        self._part.partMovedSignal.connect(self.partMovedSlot)
        for oligo in self._part.oligos():
            for strand in oligo.strands():
                strand.xover3pCreatedSignal.connect(self.xover3pCreatedSlot)
                strand.xover3pDestroyedSignal.connect(self.xover3pDestroyedSlot)

    def disconnectSignals(self):
        self._part.partParentChangedSignal.disconnect(self.partParentChangedSlot)
        self._part.partDestroyedSignal.disconnect(self.partDestroyedSlot)
        self._part.partMovedSignal.disconnect(self.partMovedSlot)
        for oligo in self._part.oligos():
            for strand in oligo.strands():
                strand.xover3pCreatedSignal.disconnect(self.xover3pCreatedSlot)
                strand.xover3pDestroyedSignal.disconnect(self.xover3pDestroyedSlot)

    ### COMMANDS ###
