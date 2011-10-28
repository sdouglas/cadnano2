# Copyright 2011 Autodesk, Inc.  All rights reserved.
#
# The MIT License
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
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#
# http://www.opensource.org/licenses/mit-license.php

from controllers.viewrootcontroller import ViewRootController
from partitem import PartItem

import util
util.qtWrapImport('QtCore', globals(), ['pyqtSignal', 'QObject'])
util.qtWrapImport('QtGui', globals(), ['QGraphicsRectItem'])

"""
solidrootitem.py
Created by Simon Breslav on 2011-10-05.
"""


class SolidRootItem(object):
    """
    SolidRootItem is the root item in the SolidView.
    """
    def __init__(self, parent, document):
        self._document = document
        self._controller = ViewRootController(self, document)
        self._modelPart = None
        self._partItems = {}

    ### SLOTS ###
    def partAddedSlot(self, modelPart):
        """
        Receives notification from the model that a part has been added.
        """
        #print "SolidRootItem.partAddedSlot!"
        self._modelPart = modelPart
        partItem = PartItem(modelPart, self)
        self._partItems[partItem] = True

    def selectedPartChangedSlot(self, modelPart):
        """Given a newly selected modelPart"""
        # print "SolidRootItem.selectedPartChangedSlot"
        pass

    ### METHODS ###
    def partItems(self):
        return self._partItems

    def removePartItem(self, partItem):
        del self._partItems[partItem]

    def setModifyState(self, val):
        for p in self._partItems:
            p.setModifyState(val)
