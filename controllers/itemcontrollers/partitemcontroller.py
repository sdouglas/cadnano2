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


class PartItemController(object):
    def __init__(self, partItem, modelPart):
        self._partItem = partItem
        self._modelPart = modelPart
        self.connectSignals()

    def connectSignals(self):
        mP = self._modelPart
        pI = self._partItem

        mP.partParentChangedSignal.connect(pI.parentChangedSlot)
        mP.partRemovedSignal.connect(pI.removedSlot)
        mP.partDestroyedSignal.connect(pI.destroyedSlot)
        mP.partPreDecoratorSelectedSignal.connect(pI.partPreDecoratorSelectedSlot)
        mP.partVirtualHelixAddedSignal.connect(pI.virtualHelixAddedSlot)
        mP.partStrandChangedSignal.connect(pI.updatePreXoverItemsSlot)
        mP.partVirtualHelicesReorderedSignal.connect(pI.reorderedSlot)
    # end def

    def disconnectSignals(self):
        mP = self._modelPart
        pI = self._partItem

        mP.partParentChangedSignal.disconnect(pI.parentChangedSlot)
        mP.partRemovedSignal.disconnect(pI.removedSlot)
        mP.partDestroyedSignal.disconnect(pI.destroyedSlot)
        mP.partPreDecoratorSelectedSignal.disconnect(pI.partPreDecoratorSelectedSlot)
        mP.partVirtualHelixAddedSignal.disconnect(pI.virtualHelixAddedSlot)
        mP.partStrandChangedSignal.disconnect(pI.updatePreXoverItemsSlot)
        mP.partVirtualHelicesReorderedSignal.disconnect(pI.reorderedSlot)

    # end def
# end class
