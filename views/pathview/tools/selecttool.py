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

"""
selecttool
Created by Nick Conway on 2011-05-30.
"""

from abstractpathtool import AbstractPathTool
import util, os, model.strand
from cadnano import ignoreEnv
from model.enum import StrandType
from model.normalstrand import NormalStrand

# import Qt stuff into the module namespace with PySide, PyQt4 independence
util.qtWrapImport('QtCore', globals(), ['Qt', 'QPointF'])
util.qtWrapImport('QtGui', globals(), ['QPen', 'QColor'])


class SelectTool(AbstractPathTool):
    """
    SelectTool is the default tool. It allows editing of breakpoints
    (by clicking and dragging) and toggling of crossovers.
    """
    limitEndptDragging = True
    disallowClickBreaksStrand = True
    drawActionPreview = False
    colorPreview = False

    def __init__(self, controller, **kwargs):
        super(SelectTool, self).__init__(controller)
        self._mouseDownBase = None
        self._mouseDownPH = None
        self._lastValidBase = None
        self._isPressed = False

    NoOperation = 0
    ConnectStrand = 1
    ClearStrand = 2
    RemoveXOver = 3

    def paintOp(self, painter, op, rightSide, topStrand, baseW):
        if op == self.NoOperation:
            painter.setPen(Qt.NoPen)
        elif op == self.ConnectStrand:
            painter.setPen(QPen(QColor(0, 255, 0), 1))
        elif op == self.ClearStrand or\
             op == self.RemoveXOver:
            painter.setPen(QPen(QColor(255, 0, 0), 1))
        else:
            painter.setPen(Qt.NoPen)
        if op == self.RemoveXOver:
            y = 0 if topStrand else baseW
            painter.drawLine(baseW*.25, y-1, baseW*.75, y-1)
            return
        x = baseW if rightSide else 0
        painter.drawLine(x, .25*baseW, x, .75*baseW)

    def paint(self, painter, option, widget=None):
        loc = self.lastLocation()
        if loc==None:
            return
        ph, point = loc
        point = ph.mapFromScene(point)
        vh = ph.vhelix()
        base = self.baseAtPoint(ph, point)
        topStrand = ph.strandIsTop(base[0])
        if base==None:
            return
        # Color preview
        if self.colorPreview:
            painter.setBrush(vh.colorOfBase(*base))
            painter.setPen(Qt.NoPen)
            painter.drawEllipse(\
                QPointF(ph.baseWidth/2, ph.baseWidth/2),\
                ph.baseWidth/4, ph.baseWidth/4)
        # Draw action preview
        if not self.drawActionPreview:
            return

        opL, offsLL, offsLR = self.operationForDraggingInDirectionFromBase(-1,\
                                                        (vh, base[0], base[1]))
        opR, offsRL, offsRR = self.operationForDraggingInDirectionFromBase(1,\
                                                        (vh, base[0], base[1]))

        painter.save()
        self.paintOp(painter, opL, False, topStrand, ph.baseWidth)
        self.paintOp(painter, opR, True, topStrand, ph.baseWidth)
        painter.restore()

    def mousePressPathHelix(self, ph, event):
        """Activate this item as the current helix."""
        # If there is an existing drag operation
        # and we get *another* press, the first
        # drag operation must end
        if self.scene() != None:
            self.scene().clearSelection() # added to clearout selections
        self.finalizeMouseDrag()

        # The key property of a drag operation
        # (if it's None, there should be no drag
        # operation, and if it's non-None, there
        # should be one)
        self._mouseDownY = event.pos().y()
        self._mouseDownBase = ph.baseAtLocation(event.pos().x(),\
                                                self._mouseDownY)
        strand, idx = self._mouseDownBase
        self._lastValidBase = self._mouseDownBase

        # Shift to merge bases - carryover from 1.0
        if (event.modifiers() & Qt.ShiftModifier) and self._mouseDownBase:
            vh = ph.vhelix()
            if vh.hasEndAt(strand, idx):
                if idx > 0 and vh.hasEndAt(strand, idx-1):
                    vh.connectStrand(strand, idx-1, idx)
                if idx < vh.numBases()-1 and vh.hasEndAt(strand, idx+1):
                    vh.connectStrand(strand, idx+1, idx)
                self._mouseDownBase = None  # Cancel drag op
                return

        # Alt to extend bases - carryover from 1.0
        if (event.modifiers() & Qt.AltModifier) and self._mouseDownBase:
            vh = ph.vhelix()
            if vh.hasEndAt(strand, idx):
                vh.autoDragToBoundary(strand, idx)
            self._mouseDownBase = None  # Cancel drag op
            return

        # Begin a drag operation
        self._mouseDownPH = ph
        ph.scene().views()[0].addToPressList(ph)

        if not self._mouseDownBase:
            return
        vh = ph.vhelix()
        self.undoIdxBeforeDrag = vh.undoStack().index()

        self.applyTool(vh, self._mouseDownBase, self._mouseDownBase)

        # Begin a new model drag operation
        vstr = vh.vStrand(strand)
        self.normalStrandToInsert = NormalStrand(VBase(vstr, idx),\
                                                 VBase(vstr, idx + 1))
        vstr.part().addVfbStrands([vstr])

        ph.makeSelfActiveHelix()


    def finalizeMouseDrag(self):
        if self._mouseDownBase == None:
            return
        vh = self._mouseDownPH.vhelix()
        self.normalStrandToInsert.commit()
        self.normalStrandToInsert = None
        vh.palette().shuffle()
        self._mouseDownBase = None
        self._lastValidBase = None
        self._mouseDownPH = None
        self._isPressed = False
        vh.resetSequenceCache()

    def mouseMovePathHelix(self, ph, event):
        if self._mouseDownBase == None:
            return
        vh = ph.vhelix()
        newBase = ph.baseAtLocation(event.pos().x(),\
                                    self._mouseDownY,\
                                    clampX=True)
        if self._mouseDownBase and newBase:
            if self._lastValidBase != newBase:
                self._lastValidBase = newBase
                # vh.undoStack().undo()
                self.rewindDragOp(vh.undoStack())
                self.applyTool(vh, self._mouseDownBase, newBase)

    def mouseReleasePathHelix(self, ph, event):
        self.finalizeMouseDrag()
        if os.environ.get('CADNANO_FSCK_AFTER_SELECT_TOOL_USE', False) and not ignoreEnv:
            ph.vhelix().part().fsck()

    # Unused events should be forwarded to other items
    # (in particular, to ActiveSliceHandle)
    mouseMovePathHelixGroupUnused = True
    mouseReleasePathHelixGroupUnused = True
    mousePressPathHelixGroupUnused = True

    def dragLimitsForDragOpBeginningAtBase(self, fromBase):
        """ returns (firstAllowableIdx, lastAllowableIdx) for
        the toBase of a drag operation beginning at fromBase.
        fromBase = (vHelix, strandType, baseIdx)"""
        vh, strandType, startIdx = fromBase
        maxBase = vh.numBases()-1
        if not self.limitEndptDragging:
            return (0, maxBase)
        l, r = startIdx, startIdx
        while l > 0:
            proposedBaseHasLNeighbor = vh.connectsToNatL(strandType, l-1)
            proposedBaseHasRNeighbor = vh.connectsToNatR(strandType, l-1)
            if proposedBaseHasRNeighbor == proposedBaseHasLNeighbor:
                l = l - 1
            else:
                break
        maxBase = vh.numBases()-1
        while r < maxBase:
            proposedBaseHasLNeighbor = vh.connectsToNatL(strandType, r+1)
            proposedBaseHasRNeighbor = vh.connectsToNatR(strandType, r+1)
            if proposedBaseHasRNeighbor == proposedBaseHasLNeighbor:
                r = r + 1
            else:
                break
        return (l, r)

    # Why add the layer of indirection between operationForDragging...
    # and applyTool? So that we can query for the operation that *would*
    # be performed without actually performing it.
    def operationForDraggingInDirectionFromBase(self, dragDir, base):
        """
        dragDir: 1 for dragging right, -1 for left, 0 for staying on the
        same base.
        base: a specifier in the form (virtualHelix, strandType, baseIndex)
        return value:
        (self.ConnectStrand or self.ClearStrand, fromIdxOffset, toIdxOffset)

        Add fromIdxOffset and toIdxOffset to fromIndex and toIndex,
        respectively, to get the extents for the actual operation.
        """
        vHelix, strandType, baseIdx = base
        startBaseHasLNeighbor = vHelix.hasNeighborL(strandType, baseIdx)
        startBaseHasRNeighbor = vHelix.hasNeighborR(strandType, baseIdx)
        if startBaseHasLNeighbor and (not startBaseHasRNeighbor):
            # base is at one end of a segment which stretches to the left
            segmentDir = -1
        elif (not startBaseHasLNeighbor) and startBaseHasRNeighbor:
            # base is at one end of a segment which stretches to the right
            segmentDir = 1
        else:
            # base is not at one end of a segment
            segmentDir = 0

        startBaseHasLCrossover = vHelix.hasCrossoverL(strandType, baseIdx)
        startBaseHasRCrossover = vHelix.hasCrossoverR(strandType, baseIdx)

        # (Below) we are dragging starting at a CROSSOVER
        if startBaseHasLCrossover or startBaseHasRCrossover:
            if startBaseHasLNeighbor and startBaseHasRNeighbor:
                # It's not a 1-base crossover
                return (self.RemoveXOver, 0, 0)
            else:
                # We give 1-base crossovers a chance to get dragged out
                pass
        # (Below) we are dragging starting in EMPTY STRAND or in the MIDDLE of a SEGMENT
        if segmentDir == 0:
            if startBaseHasLNeighbor and startBaseHasRNeighbor:  # MIDDLE of a SEGMENT
                if self.disallowClickBreaksStrand:
                    return (self.NoOperation, 0, 0)
                if dragDir == -1:  # Dragging to the LEFT
                    handleColor = vHelix.colorOfBase(strandType, baseIdx-1)
                    return (self.ClearStrand, 0, 1, handleColor, vHelix.palette()[0])
                else:              # Dragging to the RIGHT
                    handleColor = vHelix.colorOfBase(strandType, baseIdx)
                    return (self.ClearStrand, 0, 0, vHelix.palette()[0], handleColor)
            elif (not startBaseHasLNeighbor) and (not startBaseHasRNeighbor):  # EMPTY STRAND
                return (self.ConnectStrand, 0, 0, vHelix.palette()[0])
            assert(False)
        # (Below) we are dragging an ENDPOINT and HAVE NOT moved
        elif dragDir == 0:
            return (self.NoOperation, 0, 0)
        # (Below) we are dragging an ENDPOINT and HAVE moved
        elif segmentDir == dragDir:
            handleColor = vHelix.colorOfBase(strandType, baseIdx)
            if dragDir == -1:
                # Start at RIGHT endpoint, dragging LEFT INTO segment
                return (self.ClearStrand, 0, 1, handleColor, None)
            elif dragDir == 1:
                # Start at LEFT endpoint, dragging RIGHT INTO segment
                return (self.ClearStrand, 1, 0, None, handleColor)
            assert(False)
        # (Below) we are also dragging an ENDPOINT and HAVE moved
        elif segmentDir != dragDir:
            if dragDir == -1:
                # Start at LEFT endpoint, dragging LEFT OUT FROM segment
                return (self.ConnectStrand, 0, 0, None)
            elif dragDir == 1:
                # Start at RIGHT endpoint, dragging RIGHT OUT FROM segment
                return (self.ConnectStrand, 0, 0, None)
            assert(False)
        assert(False)

    def clearSequence(self, vh, strandType, idx):
        # for limiting the times a command get's called during a drag
        if self._isPressed != True and vh.isSeqBlank() == False and strandType == StrandType.Scaffold:
            vh.applySequenceAt(StrandType.Scaffold, int(idx), " ", undoStack=vh.part().undoStack())
            self._isPressed = True

    def rewindDragOp(self, undoStack):
        assert(self.undoIdxBeforeDrag != None)
        while undoStack.index() > self.undoIdxBeforeDrag:
            undoStack.undo()

    def applyTool(self, vHelix, fr, to):
        """
        fr (from) and to take the format of (strandType, base)
        """
        fr = list(vHelix.validatedBase(*fr, raiseOnErr=False))
        to = list(vHelix.validatedBase(*to, raiseOnErr=False))
        if (None, None) in (fr, to):  # must start and end on a valid base
            return False
        beginBase = (vHelix, fr[0], fr[1])
        leftDragLimit, rightDragLimit = self.dragLimitsForDragOpBeginningAtBase(beginBase)
        to[1] = util.clamp(to[1], leftDragLimit, rightDragLimit)

        # 1 corresponds to rightwards
        if to[1] == fr[1]:
            dragDir = 0
        elif to[1] > fr[1]:
            dragDir = 1
        else:
            dragDir = -1

        dragOp = self.operationForDraggingInDirectionFromBase(dragDir, beginBase)
        op, frOffset, toOffset = dragOp[0:3]

        if op == self.ConnectStrand:
            self.clearSequence(vHelix, fr[0], fr[1]+frOffset)
            color = dragOp[3]
            vHelix.connectStrand(fr[0], fr[1]+frOffset, to[1]+toOffset, color=color)
        elif op == self.ClearStrand:
            self.clearSequence(vHelix, fr[0], fr[1]+frOffset)
            colorL, colorR = dragOp[3:5]
            vHelix.legacyClearStrand(fr[0], fr[1]+frOffset, to[1]+toOffset, colorL=colorL, colorR=colorR)
        elif op == self.RemoveXOver:
            self.clearSequence(vHelix, fr[0], fr[1])
            vHelix.removeXoversAt(fr[0], fr[1], newColor=vHelix.palette()[0])
        else:
            assert(op == self.NoOperation)
        vHelix.resetSequenceCache()
