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
import model.oligo
from operation import Operation
from model.strands.vbase import VBase
from model.strands.xoverstrand import XOverStrand3, XOverStrand5

class PencilToolOperation(Operation):
    """
    Handles interactive strand creation / destruction in the manner of the
    Pencil Tool.
    """
    imposeDragBounds = True
    allowBreakingByClickInsideStrands = True
    allow1BaseStrandCreation = True
    logger = None

    def __init__(self, startVBase, useLeft, undoStack):
        """ Begin a session of pencil-tool interaction """
        Operation.__init__(self, undoStack)
        self.newStrand = NormalStrand(startVBase, startVBase)
        self.startVStrand = self.newStrand.vStrand()
        self.startVBase = startVBase
        self.useLeft = useLeft
        self.lastDestVBase = None
        self.newStrandInVfbPool = False
        self.newOligoProvider = model.oligo.DragOperationOligoProvider()
        if self.imposeDragBounds:  # calculate drag boundaries
            self.setDragBounds()
        self.updateDestination(startVBase)
        if self.logger:
            self.logger.write('PencilToolOperation.init(%s)\n'%startVBase)

    def setDragBounds(self):
        # prevent dragging outside the grid
        self.dragBoundL = 0
        self.dragBoundR = self.startVBase.part().dimensions()[2]-1

    def updateDestination(self, newDestVBase):
        """ Looks at self.startVBase and newDestVBase then calls the appropriate
        actionWhatever method on self. """
        if isinstance(newDestVBase, (int, long)):
            newDestVBase = VBase(self.startVBase.vStrand(), newDestVBase)
        if newDestVBase == self.lastDestVBase:
            return
        else:
            self.lastDestVBase = newDestVBase
        self.rewind()
        self.newOligoProvider.rewind()
        dragStartBase, dragEndBase = self.startVBase, newDestVBase
        dragStartExposedEnds = dragStartBase.exposedEnds()
        # special case: single-base strand
        if 'L' in dragStartExposedEnds and 'R' in dragStartExposedEnds:
            dragStartExposedEnds = 'L' if self.useLeft else 'R'
        dragStartStrand = dragStartBase.strand()
        dragEndStrand = dragEndBase.strand()
        startIdx, endIdx = dragStartBase.vIndex(), dragEndBase.vIndex()
        vStrand = dragStartBase.vStrand()

        if self.imposeDragBounds:
            if endIdx < self.dragBoundL:
                endIdx = self.dragBoundL
            elif endIdx > self.dragBoundR:
                endIdx = self.dragBoundR

        willConnect, willClear = False, False
        start, end, keepLeft = startIdx, endIdx, True

        if 'R' in dragStartExposedEnds:
            if endIdx < startIdx:  # Dragging a right-facing endpoint left
                willClear = True
                start = endIdx+1
                end = startIdx+1
            elif startIdx < endIdx:  # Dragging a right-facing endpoint right
                willConnect = True
            else:
                pass  # Click on an endpoint
        elif 'L' in dragStartExposedEnds:
            if endIdx < startIdx:  # Dragging a left-facing endpoint left
                willConnect = True
            elif startIdx < endIdx:  # Dragging a left-facing endpoint right
                willClear = True
            else:
                pass  # Click on an endpoint
        elif dragStartStrand != None and self.allowBreakingByClickInsideStrands:
            if endIdx < startIdx:  # Dragging left inside a strand
                willClear = True
                end += 1
            elif startIdx < endIdx:  # Dragging right inside a strand
                willClear = True
                keepLeft = False
            else:  # Click inside a strand
                willClear = True
                keepLeft = False
        else:
            if startIdx == endIdx and self.allow1BaseStrandCreation == False:
                return
            willConnect = True

        if willConnect:
            vStrand.connectStrand(start, end, useUndoStack=True,\
                                              undoStack=self.undoStack)
        elif willClear:
            # tally the xovers that will be cleared
            affectedStrands = vStrand.rangeItemsTouchingRange(start, end)
            restoreList = []
            for strand in affectedStrands:
                if isinstance(strand, (XOverStrand3, XOverStrand5)):
                    if isinstance(strand, XOverStrand3):
                        xover = strand.conn3()
                        neighbor = xover.conn3()
                    else:
                        xover = strand.conn5()
                        neighbor = xover.conn5()
                    if neighbor != None:
                        x0, x1 = xover.idxs()  # cleared xover
                        n0, n1 = neighbor.idxs()  # neigbor
                        if n0 < x0:
                            restoreList.append((xover.vStrand(), n1-1, x0))
                        else:
                            restoreList.append((xover.vStrand(), x0, n0))
            # do the clear operation
            vStrand.clearStrand(start, end, useUndoStack=True,\
                                undoStack=self.undoStack, keepLeft=keepLeft,\
                                newOligoProvider=self.newOligoProvider)
            # restore the material 
            for strand, rStart, rEnd in restoreList:
                strand.connectStrand(rStart, rEnd,\
                        useUndoStack=True, ndoStack=self.undoStack,\
                        newOligoProvider=self.newOligoProvider)

    def end(self):
        """ Make the changes displayed by the last call to
        updateDestination permanent. Mostly, cause trouble for a user who
        erroneously tries to use the same PencilToolOperation twice.
        Also perform special mouseup behavior. """
        if self.logger:
            self.logger.write('PencilToolOperation.end\n')
        if self.startVBase == self.lastDestVBase:
            strand = self.startVBase.strand()
            if isinstance(strand, (XOverStrand3, XOverStrand5)):
                self.rewind()
                self.newOligoProvider.rewind()
                idx = self.startVBase.vIndex()
                # mark xover to replace with normalstrand here
                self.startVBase.vStrand().clearStrand(idx, idx + 1,\
                                   useUndoStack=True, undoStack=self.undoStack)
        del self.newStrand
        del self.startVBase
        del self.newStrandInVfbPool
        del self.lastDestVBase
