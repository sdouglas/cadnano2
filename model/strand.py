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
util.qtWrapImport('QtCore', globals(), ['QObject'] )
util.qtWrapImport('QtGui', globals(), ['QUndoCommand'] )

class Strand(QObject):
    def assertConsistent(self):
        raise NotImplementedError

    def undoStack(self):
        return self.vBase3.vStrand.vHelix.undoStack()

    # Properties (access with instance.propertyName)
    # vBase{3,5}         the locations of tho 3' and 5' end-bases
    # strand{3,5}        the strands to which this strand's end-bases connect

    def canMergeWith(self, other):
        """ We already have that the ranges for self and other could merge """
        return False  # ...but we're default behavior, so we don't care.




class NormalStrand(Strand):
    """
    Represents a strand composed of connected bases at adjacent virtual base
    coords along the same VStrand.
    """
    def __init__(self, vBaseL, vBaseR):
        QObject.__init__(self)
        self.vBaseL = vBaseL
        self.vBaseR = vBaseR
        # self.vBase3  works via python's property mechanism; see getVBase3
        # self.vBase5  works via python's property mechanism; see getVBase5
        self.neighbor3 = None
        self.neighbor5 = None
        self.traceStack = None  # If set to [], will append trace strings
    def assertConsistent(self):
        assert( self.vBaseL.vStrand == self.vBaseR.vStrand != None )
        assert( self.vBaseL.vIndex < self.vBaseR.vIndex )
    def __repr__(self):
        return "NormalStrand(%s, %s)"%(repr(self.vBaseL), repr(self.vBaseR))

    def getVBase5(self):
        vstrand = self.vBaseL.vStrand
        return self.vBaseL if vstrand.drawn5To3() else self.vBaseR
    def setVBase5(self, newVB5):
        vstrand = self.vBaseL.vStrand
        if vstrand.drawn5To3(): self.vBaseL = newVB5
        else:                   self.vBaseR = newVB5
    vBase5 = property(getVBase5, setVBase5)

    def getVBase3(self):
        vstrand = self.vBaseL.vStrand
        return self.vBaseR if vstrand.drawn5To3() else self.vBaseL
    def setVBase3(self, newVB3):
        vstrand = self.vBaseL.vStrand
        if vstrand.drawn5To3(): self.vBaseR = newVB3
        else:                   self.vBaseL = newVB3
    vBase3 = property(getVBase3, setVBase3)

    def idxsOnStrand(self, vstrand):
        """ Since a NormalStrand occupies exactly one vstrand, this simply
        returns the range of bases on that strand which the receiver
        occupies """
        return (self.vBaseL.vIndex, self.vBaseR.vIndex)

    def numBases(self):
        return self.vBaseR.vIndex - self.vBase3.vIndex

    def canMergeWith(self, other):
        """ We already have that the ranges for self and other could merge. """
        return isinstance(other, NormalStrand) and\
               other.vBase3.vStrand == self.vBase3.vStrand
    def mergeWith(self, other, undoStack):
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
            if strand.traceStack != None:
                strand.traceStack.append("+%s.mergeWith(%s)"%\
                                         (strand, otherStrand))
            s3, s5 = strand.vBase3, strand.vBase5
            self.old3, self.old5 = s3, s5
            o3, o5 = otherStrand.vBase3, otherStrand.vBase5
            if s3.vStrand.drawn5To3():
                new5 = min(s5.vIndex, o5.vIndex)
                new3 = max(s3.vIndex, o3.vIndex)
            else:
                new5 = max(s5.vIndex, o5.vIndex)
                new3 = min(s3.vIndex, o3.vIndex)
            strand.vBase3 = s3.sameStrand(new3)
            strand.vBase5 = s3.sameStrand(new5)
        def undo(self):
            strand, otherStrand = self.strand, self.otherStrand
            if strand.traceStack != None:
                strand.traceStack.append("-%s.mergeWith(%s)"%\
                                         (strand, otherStrand))
            strand.vBase3 = self.old3
            strand.vBase5 = self.old5

    def changeRange(self, newFirstIdx, newAfterLastIdx, undoStack):
        if self.vBase3.vStrand.drawn5To3():
            new5 = self.vBase3.sameStrand(newFirstIdx)
            new3 = self.vBase3.sameStrand(newAfterLastIdx)
        else:
            new3 = self.vBase3.sameStrand(newFirstIdx)
            new5 = self.vBase3.sameStrand(newAfterLastIdx)
        com = self.ChangeRangeCommand(self, new3, new5)
        if undoStack != None:
            undoStack.push(com)
        else:
            com.redo()
        self.assertConsistent()
        return self
    class ChangeRangeCommand(QUndoCommand):
        def __init__(self, strand, new3, new5):
            QUndoCommand.__init__(self)
            self.strand = strand
            self.new3, self.new5 = new3, new5
            self.old3, self.old5 = strand.vBase3, strand.vBase5
        def redo(self):
            strand, new3, new5 = self.strand, self.new3, self.new5
            if strand.traceStack != None:
                strand.traceStack.append("+%s.changeRange(new3=%s, new5=%s)"%\
                                              (strand, new3, new5))
            strand.vBase3 = new3
            strand.vBase5 = new5
        def undo(self):
            strand, new3, new5 = self.strand, self.new3, self.new5
            if strand.traceStack != None:
                strand.traceStack.append("-%s.changeRange(new3=%s, new5=%s)"%\
                                              (strand, new3, new5))
            strand.vBase3 = self.old3
            strand.vBase5 = self.old5

    def split(self, splitStart, splitAfterLast, keepLeft, undoStack):
        # keepLeft was preserveLeftOligoDuringSplit
        idx3, idx5 = self.vBase3.vIndex, self.vBase5.vIndex
        vStrand = self.vBase3.vStrand
        drawn5To3 = vStrand.drawn5To3()
        if keepLeft:
            if drawn5To3:
                self.changeRange(idx5, splitStart, undoStack)
                newItem = NormalStrand(vStrand(splitAfterLast), vStrand(idx3))
            else:
                self.changeRange(idx3, splitStart, undoStack)
                newItem = NormalStrand(vStrand(splitAfterLast), vStrand(idx5))
            self.assertConsistent()
            return (self, newItem)
        else:
            if drawn5To3:
                newItem = NormalStrand(vStrand(idx5), vStrand(splitStart))
                self.changeRange(splitAfterLast, idx3, undoStack)
            else:
                newItem = NormalStrand(vStrand(idx3), vStrand(splitStart))
                self.changeRange(splitAfterLast, idx5, undoStack)
            self.assertConsistent()
            return (newItem, self)
        assert(False)



class LoopStrand(NormalStrand):
    """
    Represents multiple actual bases located at a single virtual base. It's
    called 'Loop' because in the limit where you have many bases that occupy
    a single virtual base they bulge outwards, forming a loop.
    """
    def __init__(self, vBase, numberOfActualBases):
        self.vBase3 = self.vBase5 = vBase
        self.numBases = numberOfActualBases
    def assertConsistent(self):
        assert(self.vBase3 == self.vBase5)
    def __repr__(self):
        return "LoopStrand(%s, %i)"%(self.vBase3, self.numBases)
    def numBases(self): return self.numBases




class SkipStrand(NormalStrand):
    """
    Conceptual opposite of LoopStrand. Takes up multiple virtual bases but
    doesn't add any real bases to the Oligo's sequence.
    """
    def __repr__(self):
        return "SkipStrand(%s, %s)"%(self.vBase3, self.vBase5)
    def numBases(self): return 0




class XOverStrand(NormalStrand):
    """
    Owns exactly two bases, each of which is on a different vStrand.
    Since the concepts of a "Left" and "Right" base becomes less useful
    for a strand that crosses between vHelix, XOverStrands adopt the convention
    that self.vBaseL==self.vBase3 and self.vBaseR==self.vBase5.
    """
    def numBases(self): return 2
    def assertConsistent(self):
        assert( self.vBase3.vStrand != self.vBase5.vStrand )
        assert( self.vBase3.vStrand.isScaf() == self.vBase5.vStrand.isScaf() )
    def idxsOnStrand(self, vstrand):
        vb3, vb5 = self.vBase3, self.vBase5
        if vb3.vStrand == vstrand:
            idx = vb3.vIndex
        else:
            # If the assert fails, somebody asked for which indexes this
            # crossover occupied on a strand which it never touches!
            assert(vb5.vStrand == vstrand)
            idx = vb5.vIndex
        return (idx, idx + 1)
