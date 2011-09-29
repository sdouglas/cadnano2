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

class VirtualHelixItemController():
    def __init__(self, virtualhelixItem, modelStrandSet):
        self._virtualhelixItem = virtualhelixItem
        self._modelStrandSet = modelStrandSet
        self.connectSignals()

    def connectSignals(self):
        self._modelStrandSet.strandsetStrandAddedSignal.connect(self._virtualhelixItem.strandAddedSlot)
        self._modelStrandSet.decoratorAddedSignal.connect(self._virtualhelixItem.decoratorAddedSlot)

    def disconnectSignals(self):
        self._modelStrandSet.strandsetStrandAddedSignal.disconnect(self._virtualhelixItem.strandAddedSlot)
        self._modelStrandSet.decoratorAddedSignal.disconnect(self._virtualhelixItem.decoratorAddedSlot)
