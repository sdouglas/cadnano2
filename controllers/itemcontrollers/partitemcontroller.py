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


class PartItemController():
    def __init__(self, partItem, modelPart):
        self._partItem = partItem
        self._modelPart = modelPart
        self.connectSignals()

    def connectSignals(self):
        modelPart = self._modelPart
        partItem = self._partItem

        modelPart.parentChangedSignal.connect(partItem.parentChangedSlot)
        modelPart.removedSignal.connect(partItem.removedSlot)
        modelPart.destroyedSignal.connect(partItem.destroyedSlot)
        modelPart.virtualHelixAddedSignal.connect(partItem.virtualHelixAddedSlot)

        for oligo in modelPart.oligos():
            for strand in oligo.strands():
                strand.xover3pCreatedSignal.connect(partItem.xover3pCreatedSlot)
                #strand.xover3pDestroyedSignal.connect(partItem.xover3pDestroyedSlot)

    def disconnectSignals(self):
        modelPart = self._modelPart
        partItem = self._partItem
        
        modelPart.parentChangedSignal.disconnect(partItem.parentChangedSlot)
        modelPart.removedSignal.disconnect(partItem.destroyedSlot)
        modelPart.destroyedSignal.disconnect(partItem.destroyedSlot)
        modelPart.virtualHelixAddedSignal.disconnect(partItem.virtualHelixAddedSlot)

        for oligo in modelPart.oligos():
            for strand in oligo.strands():
                strand.xover3pCreatedSignal.disconnect(partItem.xover3pCreatedSlot)
                #strand.xover3pDestroyedSignal.disconnect(partItem.xover3pDestroyedSlot)
