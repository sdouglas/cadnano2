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

import util, sys
util.qtWrapImport('QtCore', globals(), ['QObject'])
from model.normalstrand import NormalStrand
from penciltooloperation import PencilToolOperation
from model.vbase import VBase

class SelectToolOperation(PencilToolOperation):
    """
    Handles interactive strand creation / destruction in the manner of the
    SelectTool.
    """
    def __init__(self, startVBase, undoStack):
        """ Begin a session of select-tool interaction """
        PencilToolOperation.__init__(self, startVBase, undoStack)
        if self.logger: self.logger.write('SelectToolOperation.init(%s)\n'%startVBase)

    def setDragBounds(self):
        """
        Sets a more restrictive set of dragging boundaries for SelectTool.
        
        1. prevent dragging outside the grid
        2. prevent dragging down to single base strands
        3. prevent dragging over neighboring strands
        """
        # prevent dragging outside the grid
        self.dragBoundL = 0
        self.dragBoundR = self.startVBase.part().dimensions()[2]-1
        # prevent dragging down to single base strands
        strandBeforeIdx, strandAtIdx, strandAfterIdx = \
                        self.startVStrand.strandsNearVBase(self.startVBase)
        if strandAtIdx != None:
            if self.startVBase == strandAtIdx.vBaseL:
                self.dragBoundR = min(strandAtIdx.vBaseR.vIndex()-1,
                                      self.dragBoundR)
            elif self.startVBase == strandAtIdx.vBaseR:
                self.dragBoundL = max(strandAtIdx.vBaseL.vIndex()+1,
                                      self.dragBoundL)
        # prevent dragging over neighboring strands
        if strandBeforeIdx != None:
            self.dragBoundL = max(self.dragBoundL,\
                                  strandBeforeIdx.idxs()[1])
        if strandAfterIdx != None:
            self.dragBoundR = min(strandAfterIdx.idxs()[0]-1,
                                  self.dragBoundR)

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
        self.rewind()
        dragStartBase, dragEndBase = self.startVBase, newDestVBase
        dragStartExposedEnds = dragStartBase.exposedEnds()
        dragStartStrand = dragStartBase.strand()
        dragEndStrand = dragEndBase.strand()
        startIdx, endIdx = dragStartBase.vIndex(), dragEndBase.vIndex()
        vStrand = dragStartBase.vStrand()

        if not isinstance(newDestVBase, VBase):
            print "not instance VBase"
            return

        if self.imposeDragBounds:
            if endIdx < self.dragBoundL:
                endIdx = self.dragBoundL
            elif endIdx > self.dragBoundR:
                endIdx = self.dragBoundR

        if 'R' in dragStartExposedEnds:
            if endIdx < startIdx:  # Dragging a right-facing endpoint left
                vStrand.clearStrand(endIdx + 1, startIdx + 1,\
                                   useUndoStack=True, undoStack=self.undoStack)
            elif startIdx < endIdx:  # Dragging a right-facing endpoint right
                
                vStrand.connectStrand(startIdx, endIdx,\
                                   useUndoStack=True, undoStack=self.undoStack)
            else:
                pass  # Click on an endpoint
        elif 'L' in dragStartExposedEnds:
            if endIdx < startIdx:  # Dragging a left-facing endpoint left
                vStrand.connectStrand(endIdx, startIdx,\
                                   useUndoStack=True, undoStack=self.undoStack)
            elif startIdx < endIdx:  # Dragging a left-facing endpoint right
                vStrand.clearStrand(startIdx, endIdx,\
                                   useUndoStack=True, undoStack=self.undoStack)
            else:
                pass  # Click on an endpoint
        else:
            vStrand.connectStrand(startIdx, endIdx,\
                                  useUndoStack=True, undoStack=self.undoStack)

    def actionJustConnect(self, vBase):
        """ Just connect the right exposed end of lStrand to the left exposed
        end of rStrand """
        # ends = vBase.exposedEnds()
        # idx = vBase.vIndex()
        # if 'L' in ends:
        #     if :  # check to the left for touching vBase
        #     vBase.vStrand().connectStrand(idx, idx-1,\
        #                           useUndoStack=True, undoStack=self.undoStack)
        # elif 'R' in ends:
        #     if :  # check to the right for touching vBase
        #     vBase.vStrand().connectStrand(idx, idx+1,\
        #                           useUndoStack=True, undoStack=self.undoStack)
        if self.logger: self.logger.write('SelectToolOperation.actionJustConnect\n')

    def actionResizeStrand(self, vBase):
        ends = vBase.exposedEnds()
        if 'L' in ends:
            vBase.vStrand().connectStrand(vBase.vIndex(), self.dragBoundL,\
                                  useUndoStack=True, undoStack=self.undoStack)
        elif 'R' in ends:
            vBase.vStrand().connectStrand(vBase.vIndex(), self.dragBoundR,\
                                  useUndoStack=True, undoStack=self.undoStack)
        if self.logger: self.logger.write('SelectToolOperation.actionResizeStrand\n')
