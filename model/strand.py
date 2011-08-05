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
util.qtWrapImport('QtCore', globals(), ['QObject'] )
util.qtWrapImport('QtGui', globals(), ['QUndoCommand'] )
nextStrandDebugIdentifier = 0
logger = None  # Tracing will be written by calling traceDest.write
logger = sys.stdout

class Strand(QObject):
    def __init__(self):
        QObject.__init__(self)
        self.connL = None  # The Strand connected to the 3' end of self
        self.connR = None  # The Strand connected to the 5' end of self
        global nextStrandDebugIdentifier
        self.traceID = nextStrandDebugIdentifier
        nextStrandDebugIdentifier += 1
    def assertConsistent(self):
        if self.vStrand != None:
            assert(self in self.vStrand.ranges)

    def undoStack(self):
        return self.vStrand.vHelix.undoStack()

    def canMergeWith(self, other):
        """ We already have that the ranges for self and other could merge """
        return False  # ...but we're default behavior, so we don't care.

    def getConn3(self):
        return self.connR if self.vStrand.drawn5To3() else self.connL
    def setConn3(self, newConn):
        if self.vStrand.drawn5To3():
            self.connR = newConn
        else:
            self.connL = newConn
    conn3 = property(getConn3, setConn3)

    def getConn5(self):
        return self.vIdxL if self.vStrand.drawn5To3() else self.vIdxR
    def setConn5(self, newVIdx):
        if self.vStrand.drawn5To3():
            self.vIdxL = newVIdx
        else:
            self.vIdxR = newVIdx
    conn5 = property(getConn5, setConn5)




class NormalStrand(Strand):
    """
    Represents a strand composed of connected bases at adjacent virtual base
    coords along the same VStrand. Occupies bases at indices in
    range(normalStrand.vIdxL, normalStrand.vIdxR + 1)
    """
    def __init__(self, vStrand, vIdxL, vIdxR):
        Strand.__init__(self)
        self.vStrand = vStrand
        self.vIdxL = vIdxL
        self.vIdxR = vIdxR
        # self.vIdx3 acts like self.vIdxR if self.vStrand.drawn5To3() else vIdxL
        # self.vIdx5 acts like self.vIdxL if self.vStrand.drawn5To3() else vIdxR
        if logger != None:
            logger.write("%i.init %s\n"%(self.traceID, repr(self)))
    def assertConsistent(self):
        assert( self.leftIdx <= self.rightIdx )
        Strand.assertConsistent(s)
    def __repr__(self):
        return "%s(%s, %i, %i)"%(self.__class__.__name__, repr(self.vStrand),\
                                 self.vIdxL, self.vIdxR)

    def getVIdx3(self):
        return self.vIdxR if self.vStrand.drawn5To3() else self.vIdxL
    def setVIdx3(self, newVIdx):
        if self.vStrand.drawn5To3(): self.vIdxR = newVIdx
        else:                        self.vIdxL = newVIdx
    vIdx3 = property(getVIdx3, setVIdx3)

    def getVIdx5(self):
        return self.vIdxL if self.vStrand.drawn5To3() else self.vIdxR
    def setVIdx5(self, newVIdx):
        if self.vStrand.drawn5To3(): self.vIdxL = newVIdx
        else:                        self.vIdxR = newVIdx
    vIdx5 = property(getVIdx5, setVIdx5)

    def idxsOnStrand(self, vstrand):
        """ Since a NormalStrand occupies exactly one vstrand, this simply
        returns the range of bases on that strand which the receiver
        occupies """
        assert(vstrand == self.vStrand)
        return (self.vIdxL, self.vIdxR + 1)

    def numBases(self):
        return self.vIdxR + 1 - self.vIdxL

    def canMergeWith(self, other):
        """ We already have that the ranges for self and other could merge. """
        return isinstance(other, NormalStrand) and self.vStrand == other.vStrand
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
            if logger != None:
                logger.write("+%i.mergeWith(%i) %s %s"%(strand.traceID,
                                                        strand, otherStrand))
            sL, sR = strand.vIdxL, strand.vIdxR
            oL, oR = otherStrand.vIdxL, otherStrand.vIdxR
            self.vIdxL, self.vIdxR = min(sL, oL), max(sR, oR)
            self.sL, self.sR, self.oL, self.oR = sL, sR, oL, oR
        def undo(self):
            strand, otherStrand = self.strand, self.otherStrand
            if logger != None:
                logger.write("-%i.mergeWith(%i) %s %s"%(strand.traceID,
                                                        strand, otherStrand))
            strand.vIdxL = self.sL
            strand.vIdxR = self.sR
            otherStrand.vIdxL = self.oL
            otherStrand.vIdxR = self.oR

    def changeRange(self, newL, newR, undoStack):
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
            self.oldL, self.oldR = strand.vIdxL, strand.vIdxR
        def redo(self):
            strand, newL, newR = self.strand, self.newL, self.newR
            if logger != None:
                logger.write("+%i.changeRange(%s, %s) %s\n"%(strand.traceID,\
                                                      newL, newR, repr(strand)))
            strand.vIdxL = newL
            strand.vIdxR = newR
        def undo(self):
            strand, oldL, oldR = self.strand, self.oldL, self.oldR
            if logger != None:
                logger.write("-%i.changeRange(%s, %s) %s\n"%(strand.traceID,\
                                                      oldL, oldR, repr(strand)))
            strand.vIdxL = self.oldL
            strand.vIdxR = self.oldR

    def split(self, splitStart, splitAfterLast, keepLeft, undoStack):
        # keepLeft was preserveLeftOligoDuringSplit
        if logger != None:
            logger.write(" %i.split(%i, %i, %s) %s"%(self.traceID,\
                            splitStart, splitAfterLast, keepLeft, repr(strand)))
        vIdxL, vIdxR, vStrand = self.vIdxL, self.vIdxR, self.vStrand
        assert(splitStart <= splitAfterLast)
        newRangeL = (vIdxL, splitStart - 1)
        newRangeLValid = newRangeL[0] <= newRangeL[1]
        newRangeR = (splitAfterLast, vIdxR)
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

    def exposedEndAt(self, vStrand, vIdx):
        """
        Returns 'L' or 'R' if a segment exists at vStrand, idx and it
        exposes an unbound endpoint on its 3' or 5' end. Otherwise returns None.
        """
        assert(vStrand == self.vStrand)
        if vIdx == self.vIdxL:
            if self.connL == None: return 'L'
        if vIdx == self.vIdxR:
            if self.connR == None: return 'R'
        return None


class LoopStrand(Strand):
    """
    Represents multiple actual bases located at a single virtual base. It's
    called 'Loop' because in the limit where you have many bases that occupy
    a single virtual base they bulge outwards, forming a loop.
    """
    def __init__(self, vStrand, vIdx, numberOfActualBases):
        NormalStrand.__init__(self)
        self.vStrand = vStrand
        self.vIdx = vIdx
        self.numBases = numberOfActualBases
    def assertConsistent(self):
        Strand.assertConsistent(self)
    def __repr__(self):
        return "LoopStrand(%s, %i, %i)"%(self.vStrand,\
                                         self.vIdxL, self.numBases)
    def numBases(self):
        return self.numBases
    def getVIdxL(self):
        return self.vIdx
    vIdxL = property(getVIdxL)
    def getVIdxR(self):
        return self.vIdx + 1
    vIdxR = property(getVIdxR)

    def exposedEndAt(self, vStrand, vIdx):
        """
        Returns 'L' or 'R' if a segment exists at vStrand, idx and it
        exposes an unbound endpoint on its 3' or 5' end. Otherwise returns None.
        """
        assert(vStrand == self.vStrand)
        if vIdx == self.vIdx:
            if self.connL == None: return 'L'
            if self.connR == None: return 'R'
        return None




class SkipStrand(NormalStrand):
    """
    Conceptual opposite of LoopStrand. Takes up 1 or more virtual bases but
    doesn't add any real bases to the Oligo's sequence.
    """
    def __repr__(self):
        return "SkipStrand(%s, %s, %s)"%(self.vStrand, self.vIdxL, self.vIdxR)
    def numBases(self): return 0




class XOverStrand(Strand):
    """
    Owns exactly two bases, each of which is on a different vStrand.
    Since the concepts of a "Left" and "Right" base becomes less useful
    for a strand that crosses between vHelix, XOverStrands adopt the convention
    that self.vBaseL==self.vBase3 and self.vBaseR==self.vBase5.
    """
    def __init__(self, vStrand3, vIdx3, vStrand5, vIdx5):
        self.vStrand3, self.vIdx3 = vStrand3, vIdx3
        self.vStrand5, self.vIdx5 = vStrand5, vIdx5
    def __repr__(self):
        return "XOverStrand(%s, %s, %s, %s)"%(vStrand3, vIdx3, vStrand5, vIdx5)
    def numBases(self): return 2
    def assertConsistent(self):
        assert( self.vBase3.vStrand != self.vBase5.vStrand )
        assert( self.vBase3.vStrand.isScaf() == self.vBase5.vStrand.isScaf() )
    def idxsOnStrand(self, vstrand):
        if   vstrand == self.vStrand3:
            idx = self.vIdx3
        elif vstrand == self.vStrand5:
            idx = self.vIdx5
        else:
            assert(False)  # Knows not about the strand of which you speak
        return (idx, idx + 1)

    def exposedEndAt(self, vStrand, vIdx):
        """
        Returns 'L' or 'R' if a segment exists at vStrand, idx and it
        exposes an unbound endpoint on its 3' or 5' end. Otherwise returns None.
        """
        if self.vStrand3 == vStrand and vIdx == self.vIdx3:
            lIs5 = self.vStrand3.drawn5To3()
            if self.conn3 == None:
                return 'R' if lIs5 else 'L'
        
            if self.connR == None: return 'R'
        return None
