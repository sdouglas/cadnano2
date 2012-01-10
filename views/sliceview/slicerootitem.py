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

from exceptions import ImportError
from controllers.viewrootcontroller import ViewRootController
from partitem import PartItem
import util
util.qtWrapImport('QtCore', globals(), ['pyqtSignal', 'QObject'])
util.qtWrapImport('QtGui', globals(), ['QGraphicsRectItem'])


class SliceRootItem(QGraphicsRectItem):
    """
    PathRootItem is the root item in the PathView. It gets added directly
    to the pathscene by DocumentWindow. It receives two signals
    (partAddedSignal and selectedPartChangedSignal) via its ViewRootController.

    PathRootItem must instantiate its own controller to receive signals
    from the model.
    """
    def __init__(self, rect, parent, window, document):
        super(SliceRootItem, self).__init__(rect, parent)
        self._window = window
        self._document = document
        self._controller = ViewRootController(self, document)
        self._instanceItems = {}

    ### SIGNALS ###

    ### SLOTS ###
    def partAddedSlot(self, sender, modelPart):
        """
        Receives notification from the model that a part has been added.
        Views that subclass AbstractView should override this method.
        """
        self._modelPart = modelPart
        partItem = PartItem(modelPart, parent=self)
        self._instanceItems[partItem] = partItem
        self.setModifyState(self._window.actionModify.isChecked())
    # end def

    def selectedChangedSlot(self, itemDict):
        """docstring for selectedChangedSlot"""
        pass
    # end def
    
    def selectionFilterChangedSlot(self, sender, filterNameList):
        pass
    # end def
    
    def clearSelectionsSlot(self, doc):
        self.scene().views()[0].clearSelectionLockAndCallbacks()
    # end def
    
    def resetRootItemSlot(self, doc):
        pass
    # end def

    ### ACCESSORS ###
    def sliceToolManager(self):
        """docstring for sliceToolManager"""
        return self._window.sliceToolManager
    # end def

    def window(self):
        return self._window
    # end def

    ### METHODS ###
    def removePartItem(self, partItem):
        del self._instanceItems[partItem]
    # end def

    def resetDocumentAndController(self, document):
        """docstring for resetDocumentAndController"""
        self._document = document
        self._controller = ViewRootController(self, document)
        if len(self._instanceItems) > 0:
            raise ImportError
    # end def

    def setModifyState(self, bool):
        """docstring for setModifyState"""
        for partItem in self._instanceItems:
            partItem.setModifyState(bool)
    # end def
