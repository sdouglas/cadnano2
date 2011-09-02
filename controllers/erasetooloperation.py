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

import sys
import util
from model.strands.normalstrand import NormalStrand
from model.strands.vbase import VBase
from penciltooloperation import PencilToolOperation

class EraseToolOperation(PencilToolOperation):
    """
    Handles interactive strand creation / destruction in the manner of the
    EraseTool.
    """
    imposeDragBounds = False
    logger = None

    def __init__(self, startVBase, undoStack):
        """ Begin a session of erase-tool interaction """
        self.strandBeforeIdx = self.strandAtIdx = self.strandAfterIdx = None
        PencilToolOperation.__init__(self, startVBase, None, undoStack)
        if self.logger: self.logger.write('EraseToolOperation.init(%s)\n'%startVBase)

    def setDragBounds(self):
        pass

    def updateDestination(self, newDestVBase):
        """
        Looks at self.startVBase and newDestVBase then calls the appropriate
        actionWhatever method on self.
        """
        if isinstance(newDestVBase, (int, long)):
            newDestVBase = VBase(self.startVBase.vStrand, newDestVBase)
        if newDestVBase == self.lastDestVBase:
            return
        else:
            self.lastDestVBase = newDestVBase
        if newDestVBase != None:
            destStrand = newDestVBase.strand()
            if destStrand != None:
                self.actionEraseVstrandAt(destStrand)

    def actionEraseVstrandAt(self, destStrand):
        """Clear the destStrand and any xovers it is connected to."""
        l, r = destStrand.idxs()
        if destStrand.connL() != None:
            l -= 1
        if destStrand.connR() != None:
            r += 1
        destStrand.vStrand().clearStrand(l, r, useUndoStack=True,\
                                               undoStack=self.undoStack)
        if self.logger: self.logger.write('EraseToolOperation.actionEraseVstrandAt\n')

    def actionResizeStrand(self, vBase):
        ends = vBase.exposedEnds()
        if 'L' in ends:
            vBase.vStrand().connectStrand(vBase.vIndex(), self.dragBoundL,\
                                  useUndoStack=True, undoStack=self.undoStack)
        if 'R' in ends:
            vBase.vStrand().connectStrand(vBase.vIndex(), self.dragBoundR,\
                                  useUndoStack=True, undoStack=self.undoStack)
        if self.logger: self.logger.write('EraseToolOperation.actionResizeStrand\n')
