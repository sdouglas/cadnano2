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
from strand import Strand
from model.vbase import VBase
util.qtWrapImport('QtCore', globals(), ['QObject', 'pyqtSignal'] )
util.qtWrapImport('QtGui', globals(), ['QUndoCommand'] )
nextStrandDebugIdentifier = 0

class NormalStrand(Strand):
    """
    Represents a strand composed of connected bases at adjacent virtual base
    coords along the same VStrand. Occupies bases at indices in
    range(normalStrand.vBaseL, normalStrand.vBaseR + 1)
    """
    logger = None
    def __init__(self, vBaseL, vBaseR):
        Strand.__init__(self)
        self.vBaseL = vBaseL
        self.vBaseR = vBaseR
        # self.vBase3 acts like self.vBaseR if self.vStrand().drawn5To3() else vBaseL
        # self.vBase5 acts like self.vBaseL if self.vStrand().drawn5To3() else vBaseR
        if self.logger != None:
            self.logger.write("%i.init %s\n"%(self.traceID, repr(self)))
        self.assertConsistent()
        self._hasPreviewConnectionL = False
        self._hasPreviewConnectionR = False

    def commit(self):
        """
        TODO
        """
        pass
    # end def

    def assertConsistent(self):
        assert( self.vBaseL <= self.vBaseR )
        Strand.assertConsistent(self)

    def __repr__(self):
        clsName = self.__class__.__name__
        vstr = repr(self.vStrand())
        return "%s(%s, %s)"%(clsName, self.vBaseL, self.vBaseR)

    def getVBase3(self):
        return self.vBaseR if self.vStrand().drawn5To3() else self.vBaseL
    vBase3 = property(getVBase3)

    def getVBase5(self):
        return self.vBaseL if self.vStrand().drawn5To3() else self.vBaseR
    vBase5 = property(getVBase5)

    def vStrand(self):
        return self.vBaseL.vStrand

    def apparentlyConnectedL(self):
        return self._hasPreviewConnectionL or self.connL() != None

    def apparentlyConnectedR(self):
        return self._hasPreviewConnectionR or self.connR() != None

    def defaultUndoStack(self):
        return self.vBaseL.part().undoStack()

    def idxsOnStrand(self, vstrand):
        """ Since a NormalStrand occupies exactly one vstrand, this simply
        returns the range of bases on that strand which the receiver
        occupies """
        assert(vstrand == self.vStrand())
        return (self.vBaseL.vIndex, self.vBaseR.vIndex + 1)

    def numBases(self):
        return self.vBaseR.vIndex + 1 - self.vBaseL.vIndex

    def canMergeWithTouchingStrand(self, other):
        """ We already have that the ranges for self and other could merge. """
        return isinstance(other, NormalStrand) and\
               self.vBaseL.vStrand == other.vStrand
    def mergeWith(self, other, undoStack):
        """ self retains its identity (oligo, color, oligo's sequence, etc) in
        this merge """
        com = self.MergeCommand(self, other)
        if undoStack != None:
            undoStack.push(com)
        else:
            com.redo()
        return self
    class MergeCommand(QUndoCommand):
        def __init__(self, strand, otherStrand):
            QUndoCommand.__init__(self)
            self.strand = strand
            self.otherStrand = otherStrand
        def redo(self):
            strand, otherStrand = self.strand, self.otherStrand
            if strand.logger != None:
                strand.logger.write("+%i.mergeWith(%i) %s %s"%(strand.traceID,\
                                                        strand, otherStrand))
            sL, sR = strand.vBaseL, strand.vBaseR
            oL, oR = otherStrand.vBaseL, otherStrand.vBaseR
            self.vBaseL, self.vBaseR = min(sL, oL), max(sR, oR)
            self.sL, self.sR, self.oL, self.oR = sL, sR, oL, oR
            self.strand.didMove.emit(self.strand)
        def undo(self):
            strand, otherStrand = self.strand, self.otherStrand
            if strand.logger != None:
                strand.logger.write("-%i.mergeWith(%i) %s %s"%(strand.traceID,\
                                                          strand, otherStrand))
            strand.vBaseL = self.sL
            strand.vBaseR = self.sR
            otherStrand.vBaseL = self.oL
            otherStrand.vBaseR = self.oR
            self.strand.didMove.emit(self.strand)

    def changeRange(self, newL, newR, undoStack):
        if type(newL) in (int, long):
            newL = self.vBaseL.sameStrand(newL)
        if type(newR) in (int, long):
            newR = self.vBaseR.sameStrand(newR)
        com = self.ChangeRangeCommand(self, newL, newR)
        if undoStack != None:
            undoStack.push(com)
        else:
            com.redo()
        self.assertConsistent()
        return self
    class ChangeRangeCommand(QUndoCommand):
        def __init__(self, strand, newL, newR):
            QUndoCommand.__init__(self)
            self.strand = strand
            self.newL, self.newR = newL, newR
            self.oldL, self.oldR = strand.vBaseL, strand.vBaseR
        def redo(self):
            strand, newL, newR = self.strand, self.newL, self.newR
            if strand.logger != None:
                strand.logger.write("+%i.changeRange(%s, %s) %s\n"%(\
                                 strand.traceID, newL, newR, repr(strand)))
            strand.vBaseL = newL
            strand.vBaseR = newR
            self.strand.didMove.emit(self.strand)
        def undo(self):
            strand, oldL, oldR = self.strand, self.oldL, self.oldR
            if strand.logger != None:
                strand.logger.write("-%i.changeRange(%s, %s) %s\n"%(\
                                    strand.traceID, oldL, oldR, repr(strand)))
            strand.vBaseL = self.oldL
            strand.vBaseR = self.oldR
            self.strand.didMove.emit(self.strand)

    def split(self, splitStart, splitAfterLast, keepLeft, undoStack):
        # keepLeft was preserveLeftOligoDuringSplit
        if self.logger != None:
            self.logger.write(" %i.split(%i, %i, %s) %s"%(self.traceID,\
                            splitStart, splitAfterLast, keepLeft, repr(strand)))
        vBaseL, vBaseR, vStrand = self.vBaseL, self.vBaseR, self.vStrand()
        assert(splitStart <= splitAfterLast)
        newRangeL = (vBaseL, splitStart - 1)
        newRangeLValid = newRangeL[0] <= newRangeL[1]
        newRangeR = (splitAfterLast, vBaseR)
        newRangeRValid = newRangeR[0] <= newRangeR[1]
        ret = []
        if keepLeft:
            if newRangeLValid: ret.append(\
                   self.changeRange(newRangeL[0], newRangeL[1], undoStack)  )
            if newRangeRValid: ret.append(\
                   NormalStrand(vStrand(splitAfterLast), *newRangeR)        )
        else:
            if newRangeLValid: ret.append(\
                   self.changeRange(newRangeR[0], newRangeR[1], undoStack)  )
            if newRangeRValid: ret.append(\
                   NormalStrand(vStrand(splitAfterLast), *newRangeL)        )
        for strand in ret: strand.assertConsistent()
        return ret

    def exposedEndsAt(self, vBase):
        """
        Returns 'L' or 'R' if a segment exists at vStrand, idx and it
        exposes an unbound endpoint on its 3' or 5' end. Otherwise returns None.http://store.apple.com/us/browse/campaigns/back_to_school?aid=www-naus-bts2011-0526-16
        """
        ret = ''
        drawn5To3 = vBase.vStrand.drawn5To3()
        if vBase == self.vBaseL:
            ret += 'L5' if drawn5To3 else 'L3'
        if vBase == self.vBaseR:
            ret += 'R3' if drawn5To3 else 'R5'
        return ret