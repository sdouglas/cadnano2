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

from controllers.itemcontrollers.partitemcontroller import PartItemController
from virtualhelixitem import VirtualHelixItem

import util
# import Qt stuff into the module namespace with PySide, PyQt4 independence
util.qtWrapImport('QtCore', globals(), ['pyqtSignal', 'QObject'])
util.qtWrapImport('QtGui', globals(), ['QUndoCommand', 'QUndoStack',
                                       'QGraphicsPathItem'])

class PartItem(QGraphicsPathItem):
    def __init__(self, modelPart, toolManager, parent):
        super(PartItem, self).__init__(parent)
        self._modelPart = modelPart
        self._toolManager = toolManager
        self._controller = PartItemController(self, modelPart)

    ### SIGNALS ###

    ### SLOTS ###
    def parentChangedSlot(self):
        """docstring for partParentChangedSlot"""
        print "PartItem.partParentChangedSlot"
        pass

    def removedSlot(self):
        """docstring for partDestroyedSlot"""
        print "PartItem.partDestroyedSlot"
        pass

    def destroyedSlot(self):
        """docstring for partDestroyedSlot"""
        print "PartItem.partDestroyedSlot"
        pass

    def movedSlot(self, pos):
        """docstring for partMovedSlot"""
        print "PartItem.partMovedSlot"
        pass

    def virtualHelixAddedSlot(self, modelVirtualHelix):
        """
        When a virtual helix is added to the model, this slot handles
        the instantiation of a virtualhelix item.
        """
        print "PartItem.virtualHelixAddedSlot"
        virtualHelixItem = VirtualHelixItem(self, modelVirtualHelix)

    def virtualHelixRemovedSlot(self):
        """docstring for virtualHelixAddedSlot"""
        print "PartItem.virtualHelixRemovedSlot"
        pass

    def xover3pCreatedSlot(self, strand, idx):
        """docstring for xover3pCreatedSlot"""
        print "PartItem.xover3pCreatedSlot"
        pass

    def xover3pDestroyedSlot(self, strand, idx):
        """docstring for xover3pDestroyedSlot"""
        print "PartItem.xover3pDestroyedSlot"
        pass

    ### METHODS ###
    def modelPart(self):
        """Return a reference to the model's part object"""
        return self._modelPart

