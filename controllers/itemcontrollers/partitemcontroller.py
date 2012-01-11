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

        util.observe(mP, 'partHideSignal', pI.partHideSlot)
        # util.observe(mP, 'partActiveVirtualHelixChangedSignal', pI.partActiveVirtualHelixChangedSlot)
        util.observe(mP, 'partDimensionsChangedSignal', pI.partDimensionsChangedSlot)
        util.observe(mP, 'partParentChangedSignal', pI.partParentChangedSlot)
        util.observe(mP, 'partPreDecoratorSelectedSignal', pI.partPreDecoratorSelectedSlot)
        util.observe(mP, 'partRemovedSignal', pI.partRemovedSlot)
        util.observe(mP, 'partStrandChangedSignal', pI.updatePreXoverItemsSlot)
        util.observe(mP, 'partVirtualHelixAddedSignal', pI.partVirtualHelixAddedSlot)
        util.observe(mP, 'partVirtualHelixRenumberedSignal', pI.partVirtualHelixRenumberedSlot)
        util.observe(mP, 'partVirtualHelixResizedSignal', pI.partVirtualHelixResizedSlot)
        util.observe(mP, 'partVirtualHelicesReorderedSignal', pI.partVirtualHelicesReorderedSlot)
    # end def

    def disconnectSignals(self):
        mP = self._modelPart
        pI = self._partItem
        
        util.unObserve(mP, 'partHideSignal', pI.partHideSlot)
        # util.unObserve(mP, 'partActiveVirtualHelixChangedSignal', pI.partActiveVirtualHelixChangedSlot)
        util.unObserve(mP, 'partDimensionsChangedSignal', pI.partDimensionsChangedSlot)
        util.unObserve(mP, 'partParentChangedSignal', pI.partParentChangedSlot)
        util.unObserve(mP, 'partPreDecoratorSelectedSignal', pI.partPreDecoratorSelectedSlot)
        util.unObserve(mP, 'partRemovedSignal', pI.partRemovedSlot)
        util.unObserve(mP, 'partStrandChangedSignal', pI.updatePreXoverItemsSlot)
        util.unObserve(mP, 'partVirtualHelixAddedSignal', pI.partVirtualHelixAddedSlot)
        util.unObserve(mP, 'partVirtualHelixResizedSignal', pI.partVirtualHelixResizedSlot)
        util.unObserve(mP, 'partVirtualHelicesReorderedSignal', pI.partVirtualHelicesReorderedSlot)
    # end def
# end class
