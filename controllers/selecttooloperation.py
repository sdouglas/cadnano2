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
from model.strands.normalstrand import NormalStrand
from penciltooloperation import PencilToolOperation
from model.strands.vbase import VBase
from model.strands.xoverstrand import XOverStrand3, XOverStrand5

class SelectToolOperation(PencilToolOperation):
    """
    Handles interactive strand creation / destruction in the manner of the
    SelectTool.
    """
    logger = None
    imposeDragBounds = True
    allowBreakingByClickInsideStrands = False
    allow1BaseStrandCreation = False

    def __init__(self, startVBase, useLeft, undoStack):
        """ Begin a session of select-tool interaction """
        self.strandBeforeIdx = self.strandAtIdx = self.strandAfterIdx = None
        PencilToolOperation.__init__(self, startVBase, useLeft, undoStack)
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
        # prevent dragging past single base strands
        self.strandBeforeIdx, self.strandAtIdx, self.strandAfterIdx = \
                        self.startVStrand.strandsNearVBase(self.startVBase)
        if self.strandAtIdx != None:
            dragStartExposedEnds = self.startVBase.exposedEnds()
            if 'L' in dragStartExposedEnds and 'R' in dragStartExposedEnds:
                # single-base strand, prevent erasure
                if self.useLeft:
                    self.dragBoundR = self.startVBase.vIndex()
                else:
                    self.dragBoundL = self.startVBase.vIndex()
            elif isinstance(self.strandAtIdx, XOverStrand3) or\
                 isinstance(self.strandAtIdx, XOverStrand5):
                 if 'L' in dragStartExposedEnds:
                     self.dragBoundR = min(self.strandAtIdx.vBaseR.vIndex(),
                                           self.dragBoundR)
                 if 'R' in dragStartExposedEnds:
                     self.dragBoundL = max(self.strandAtIdx.vBaseL.vIndex(),
                                           self.dragBoundL)
            elif self.startVBase == self.strandAtIdx.vBaseL and\
                 'L' in dragStartExposedEnds:
                self.dragBoundR = min(self.strandAtIdx.vBaseR.vIndex(),
                                      self.dragBoundR)
            elif self.startVBase == self.strandAtIdx.vBaseR and\
                 'R' in dragStartExposedEnds:
                self.dragBoundL = max(self.strandAtIdx.vBaseL.vIndex(),
                                      self.dragBoundL)
        # prevent dragging over neighboring strands
        if self.strandBeforeIdx != None:
            self.dragBoundL = max(self.dragBoundL,\
                                  self.strandBeforeIdx.idxs()[1])
        if self.strandAfterIdx != None:
            self.dragBoundR = min(self.strandAfterIdx.idxs()[0]-1,
                                  self.dragBoundR)

    def actionMergeWithAdjacent(self, vBase):
        """
        Connect the right exposed end of lStrand to the left exposed end of
        rStrand.
        """
        ends = vBase.exposedEnds()
        idx = vBase.vIndex()
        
        # single-base vstrand between two ends: <,_ |,| _,>
        if ('L' in ends and 'R' in ends) and\
           (self.strandBeforeIdx != None and self.strandAfterIdx != None) and\
           (self.strandBeforeIdx.vBaseR.vIndex() == idx-1) and\
           (self.strandAfterIdx.vBaseL.vIndex() == idx+1):
            if self.useLeft:
                    vBase.vStrand().connectStrand(idx, idx-1,\
                                  useUndoStack=True, undoStack=self.undoStack)
            else:
                    vBase.vStrand().connectStrand(idx, idx+1,\
                                  useUndoStack=True, undoStack=self.undoStack)
        # left end exposed
        elif 'L' in ends and self.strandBeforeIdx != None:
            if self.strandBeforeIdx.vBaseR.vIndex() == idx-1:
                vBase.vStrand().connectStrand(idx, idx-1,\
                                  useUndoStack=True, undoStack=self.undoStack)
        # right end exposed
        elif 'R' in ends and self.strandAfterIdx != None:
            if self.strandAfterIdx.vBaseL.vIndex() == idx+1:
                vBase.vStrand().connectStrand(idx, idx+1,\
                                  useUndoStack=True, undoStack=self.undoStack)
        if self.logger: self.logger.write('SelectToolOperation.actionMergeWithAdjacent\n')

    def actionExpandStrandToFillAvailableSpace(self, vBase):
        ends = vBase.exposedEnds()
        if 'L' in ends:
            vBase.vStrand().connectStrand(vBase.vIndex(), self.dragBoundL,\
                                  useUndoStack=True, undoStack=self.undoStack)
        if 'R' in ends:
            vBase.vStrand().connectStrand(vBase.vIndex(), self.dragBoundR,\
                                  useUndoStack=True, undoStack=self.undoStack)
        if self.logger: self.logger.write('SelectToolOperation.actionResizeStrand\n')
