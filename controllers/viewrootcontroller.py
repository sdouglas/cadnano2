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

class ViewRootController():
    def __init__(self, viewRoot, modelDocument):
        self._viewRoot = viewRoot
        self._modelDocument = modelDocument
        self.connectSignals()

    def connectSignals(self):
        mD = self._modelDocument
        vR = self._viewRoot
        util.observe(mD, 'documentPartAddedSignal', vR.partAddedSlot)
        util.observe(mD, 'documentClearSelectionsSignal', vR.clearSelectionsSlot)
        util.observe(mD, 'documentSelectionFilterChangedSignal', vR.selectionFilterChangedSlot)
        util.observe(mD, 'documentViewResetSignal', vR.resetRootItemSlot)
        
    def disconnectSignals(self):
        mD = self._modelDocument
        vR = self._viewRoot
        util.unObserve(mD, 'documentPartAddedSignal', vR.partAddedSlot)
        util.unObserve(mD, 'documentClearSelectionsSignal', vR.clearSelectionsSlot)
        util.unObserve(mD, 'documentSelectionFilterChangedSignal', vR.selectionFilterChangedSlot)
        util.unObserve(mD, 'documentViewResetSignal', vR.resetRootItemSlot)