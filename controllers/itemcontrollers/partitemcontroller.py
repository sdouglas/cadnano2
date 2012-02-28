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

class PartItemController(object):
    def __init__(self, partItem, modelPart):
        self._partItem = partItem
        self._modelPart = modelPart
        self.connectSignals()

    def connectSignals(self):
        mP = self._modelPart
        pI = self._partItem

        if hasattr(pI, "partHideSlot"):
            mP.partHideSignal.connect(pI.partHideSlot)
        if hasattr(pI, "partActiveVirtualHelixChangedSlot"):
            mP.partActiveVirtualHelixChangedSignal.connect(pI.partActiveVirtualHelixChangedSlot)

        mP.partDimensionsChangedSignal.connect(pI.partDimensionsChangedSlot)
        mP.partParentChangedSignal.connect(pI.partParentChangedSlot)
        mP.partPreDecoratorSelectedSignal.connect(pI.partPreDecoratorSelectedSlot)
        mP.partRemovedSignal.connect(pI.partRemovedSlot)
        mP.partStrandChangedSignal.connect(pI.updatePreXoverItemsSlot)
        mP.partVirtualHelixAddedSignal.connect(pI.partVirtualHelixAddedSlot)
        mP.partVirtualHelixRenumberedSignal.connect(pI.partVirtualHelixRenumberedSlot)
        mP.partVirtualHelixResizedSignal.connect(pI.partVirtualHelixResizedSlot)
        mP.partVirtualHelicesReorderedSignal.connect(pI.partVirtualHelicesReorderedSlot)
    # end def

    def disconnectSignals(self):
        mP = self._modelPart
        pI = self._partItem
        
        if hasattr(pI, "partHideSlot"):
            mP.partHideSignal.disconnect(pI.partHideSlot)
        if hasattr(pI, "partActiveVirtualHelixChangedSlot"):
            mP.partActiveVirtualHelixChangedSignal.disconnect(pI.partActiveVirtualHelixChangedSlot)

        mP.partDimensionsChangedSignal.disconnect(pI.partDimensionsChangedSlot)
        mP.partParentChangedSignal.disconnect(pI.partParentChangedSlot)
        mP.partPreDecoratorSelectedSignal.disconnect(pI.partPreDecoratorSelectedSlot)
        mP.partRemovedSignal.disconnect(pI.partRemovedSlot)
        mP.partStrandChangedSignal.disconnect(pI.updatePreXoverItemsSlot)
        mP.partVirtualHelixAddedSignal.disconnect(pI.partVirtualHelixAddedSlot)
        mP.partVirtualHelixRenumberedSignal.disconnect(pI.partVirtualHelixRenumberedSlot)
        mP.partVirtualHelixResizedSignal.disconnect(pI.partVirtualHelixResizedSlot)
        mP.partVirtualHelicesReorderedSignal.disconnect(pI.partVirtualHelicesReorderedSlot)
    # end def
# end class
