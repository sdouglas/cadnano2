#!/usr/bin/env python
# encoding: utf-8

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

from exceptions import IndexError
from operator import attrgetter
import util
from array import array

# import Qt stuff into the module namespace with PySide, PyQt4 independence
util.qtWrapImport('QtCore', globals(), ['pyqtSignal', 'QObject', 'Qt'])
util.qtWrapImport('QtGui', globals(), ['QUndoStack', 'QUndoCommand'])

class Strand(QObject):
    """
    A Strand is a continuous stretch of bases that are all in the same
    StrandSet (recall: a VirtualHelix is made up of two StrandSets).

    Every Strand has two endpoints. The naming convention for keeping track
    of these endpoints is based on the relative numeric value of those
    endpoints (low and high). Thus, Strand has a '_baseIdxLow', which is its
    index with the lower numeric value (typically positioned on the left),
    and a '_baseIdxHigh' which is the higher-value index (typically positioned
    on the right)

    Strands can be linked to other strands by "connections". References to
    connected strands are named "_strand5p" and "_strand3p", which correspond
    to the 5' and 3' phosphate linkages in the physical DNA strand, 
    respectively. Since Strands can point 5'-to-3' in either the low-to-high
    or high-to-low directions, connection accessor methods (lowConnection and
    highConnection) are bound during the init for convenience.
    """

    def __init__(self, strandSet, baseIdxLow, baseIdxHigh, oligo=None):
        super(Strand, self).__init__(strandSet)
        self._strandSet = strandSet
        self._baseIdxLow = baseIdxLow  # base index of the strand's left boundary
        self._baseIdxHigh = baseIdxHigh  # base index of the right boundary
        self._oligo = oligo
        self._strand5p = None
        self._strand3p = None
        self._sequence = None
        self._decorators = {}
        # dynamic methods for mapping high/low connection /indices 
        # to corresponding 3Prime 5Prime 
        isDrawn5to3 = strandSet.isDrawn5to3()
        if isDrawn5to3:
            self.idx5Prime = self.lowIdx
            self.idx3Prime = self.highIdx
            self.lowConnection = self.connection5p
            self.setLowConnection = self.set5pConnection
            self.highConnection = self.connection3p
            self.setHighConnection = self.set3pConnection
        else:
            self.idx5Prime = self.highIdx
            self.idx3Prime = self.lowIdx
            self.lowConnection = self.connection3p
            self.setLowConnection = self.set3pConnection
            self.highConnection = self.connection5p
            self.setHighConnection = self.set5pConnection
        self._isDrawn5to3 = isDrawn5to3
    # end def

    def __repr__(self):
        clsName = self.__class__.__name__
        return "<%s(%s, %s)>"%(clsName, self._baseIdxLow, self._baseIdxHigh)

    def generator3pStrand(self):
        """
        Iterate from self to the final _strand3p == None
        5prime to 3prime
        Includes originalCount to check for circular linked list
        """
        originalCount = 0
        node = self
        f = attrgetter('_strand3p')
        while node and originalCount == 0:
            yield node
            # equivalen to: node = node._strand3p
            node = f(node)
            if node == self:
                originalCount += 1
    # end def

    ### SIGNALS ###
    strandHasNewOligoSignal = pyqtSignal(QObject)
    strandDestroyedSignal = pyqtSignal(QObject)
    strandRemovedSignal = pyqtSignal(QObject)
    strandResizedSignal = pyqtSignal(QObject, tuple)
    strandXover3pAddedSignal = pyqtSignal(QObject, QObject) # strand3p, strand5p
    strandXover3pRemovedSignal = pyqtSignal(QObject, QObject) # strand3p, strand5p
    strandUpdateSignal = pyqtSignal(QObject) # strand
    strandDecoratorAddedSignal = pyqtSignal(QObject, QObject, int)
    strandDecoratorDestroyedSignal = pyqtSignal(QObject, int)

    ### SLOTS ###


    ### ACCESSORS ###
    def undoStack(self):
        return self._strandSet.undoStack()

    def decorators(self):
        return self._decorators
    # end def

    def isStaple(self):
        return self._strandSet.isStaple()

    def isScaffold(self):
        return self._strandSet.isScaffold()

    def part(self):
        return self._strandSet.part()
    # end def

    def oligo(self):
        return self._oligo
    # end def
    
    def sequence(self):
        temp = self._sequence
        return temp if temp else ''
    # end def

    def strandSet(self):
        return self._strandSet
    # end def

    def virtualHelix(self):
        return self._strandSet.virtualHelix()
    # end def
    
    def setSequence(self, sequenceString):
        """
        Applies sequence string from 5' to 3'  
        return the tuple (used, unused) portion of the sequenceString
        """
        if sequenceString == None:
            self._sequence = None
            return None, None
        length = self.length()
        temp = sequenceString[0:length]
        # self._sequence = temp if self._isDrawn5to3 else temp[::-1]
        self._sequence = temp 
        return temp, sequenceString[length:]
    # end def
    
    def setComplimentSequence(self, sequenceString, strand):
        """
        This version takes anothers strand and only sets the indices that
        align with the given complimentary strand
        
        return the used portion of the sequenceString
        
        As it depends which direction this is going, and strings are stored in
        memory left to right, we need to test for isDrawn5to3 to map the reverse
        compliment appropriately, as we traverse overlapping strands. 
        
        We reverse the sequence ahead of time if we are applying it 5' to 3',
        otherwise we reverse the sequence post parsing if it's 3' to 5'
        
        Again, sequences are stored as strings in memory 5' to 3' so we need
        to jump through these hoops to iterate 5' to 3' through them correctly
        
        Perhaps it's wiser to merely store them left to right and reverse them
        at draw time, or export time
        """
        sLowIdx, sHighIdx = self._baseIdxLow, self._baseIdxHigh
        cLowIdx, cHighIdx = strand.idxs()
        
        # get the ovelap
        lowIdx, highIdx = util.overlap(sLowIdx, sHighIdx, cLowIdx, cHighIdx)
        
        # only get the characters we're using, while we're at it, make it the
        # reverse compliment
        length = highIdx-lowIdx+1
        
        # see if we are applyng 
        if sequenceString == None:
            # clear out string for in case of not total overlap
            useSeq = ''.join([' ' for x in range(length)])
        else:
            # use the string as is
            useSeq = sequenceString[::-1] if self._isDrawn5to3 else sequenceString
        
        temp = array('c', useSeq)
        if self._sequence == None:
            tempSelf = array('c', ''.join([' ' for x in range(self.length())]) )
        else:
            tempSelf = array('c', self._sequence if self._isDrawn5to3 else self._sequence[::-1])
        
        # generate the index into the compliment string
        start = lowIdx - cLowIdx
        end = start + length
        tempSelf[lowIdx-sLowIdx:highIdx-sLowIdx+1] = temp[start:end]
        self._sequence = tempSelf.tostring()
        
        # if we need to reverse it do it now
        if not self._isDrawn5to3:
            self._sequence = self._sequence[::-1]

        # test to see if the string is empty(), annoyingly expensive
        if len(self._sequence.strip()) == 0:
            self._sequence = None
            
        return self._sequence
    # end def

    ### PUBLIC METHODS FOR QUERYING THE MODEL ###
    def connection3p(self):
        return self._strand3p
    # end def

    def connection5p(self):
        return self._strand5p
    # end def

    def idxs(self):
        return (self._baseIdxLow, self._baseIdxHigh)
    # end def

    def lowIdx(self):
        return self._baseIdxLow
    # end def

    def highIdx(self):
        return self._baseIdxHigh
    # end def

    def idx3Prime(self):
        """docstring for idx3Prime"""
        return self.idx3Prime

    def idx5Prime(self):
        """docstring for idx3Prime"""
        return self.idx5Prime

    def isDrawn5to3(self):
        return self._strandSet.isDrawn5to3()
    # end def

    def length(self):
        return self._baseIdxHigh - self._baseIdxLow + 1
    # end def

    def hasXoverAt(self, idx):
        """
        An xover is necessarily at an enpoint of a strand
        """
        if idx == self.highIdx():
            return True if self.highConnection() != None else False
        elif idx == self.lowIdx():
            return True if self.lowConnection() != None else False
        else:
            return False
    # end def

    def getResizeBounds(self, idx):
        """
        Determines (inclusive) low and high drag boundaries resizing
        from an endpoint located at idx.

        When resizing from _baseIdxLow:
            low bound is determined by checking for lower neighbor strands.
            high bound is the index of this strand's high cap, minus 1.

        When resizing from _baseIdxHigh:
            low bound is the index of this strand's low cap, plus 1.
            high bound is determined by checking for higher neighbor strands.

        When a neighbor is not present, just use the Part boundary.
        """
        neighbors = self._strandSet.getNeighbors(self)
        if idx == self._baseIdxLow:
            if neighbors[0]:
                low = neighbors[0].highIdx()+1
            else:
                low = self.part().minBaseIdx()
            return low, self._baseIdxHigh-1
        else:  # self._baseIdxHigh
            if neighbors[1]:
                high = neighbors[1].lowIdx()-1
            else:
                high = self.part().maxBaseIdx()
                print "high =", high
            return self._baseIdxLow+1, high
    # end def

    ### PUBLIC METHODS FOR EDITING THE MODEL ###
    def set3pConnection(self, strand):
        self._strand3p = strand
    # end def

    def set5pConnection(self, strand):
        self._strand5p = strand
    # end def

    def setIdxs(self, idxs):
        self._baseIdxLow = idxs[0]
        self._baseIdxHigh = idxs[1]
    # end def

    def setStrandSet(self, strandSet):
        self._strandSet = strandSet
    # end def

    def setOligo(self, newOligo, emitSignal=True):
        self._oligo = newOligo
        if emitSignal:
            self.strandHasNewOligoSignal.emit(self)
    # end def

    def addDecorators(self, additionalDecorators):
        """
        used in adding additional decorators during a merge operation
        """
        self._decorators.update(additionalDecorators)
    # def

    def split(self, idx):
        """docstring for break"""
        self._strandSet.splitStrand(self, idx)

    def destroy(self):
        self.setParent(None)
        self.deleteLater()  # QObject also emits a destroyed() Signal
    # end def

    def resize(self, newIdxs, useUndoStack=True):
        c = Strand.ResizeCommand(self, newIdxs)
        util.execCommandList(self, [c], desc="Resize strand", useUndoStack=useUndoStack)
    # end def

    def merge(self, idx):
        """Check for neighbor."""
        lowNeighbor, highNeighbor = self._strandSet.getNeighbors(self)
        # determine where to check for neighboring endpoint
        if idx == self._baseIdxLow:
            if lowNeighbor:
                if lowNeighbor.highIdx() == idx - 1:
                    self._strandSet.mergeStrands(self, lowNeighbor)
        elif idx == self._baseIdxHigh:
            if highNeighbor:
                if highNeighbor.lowIdx() == idx + 1:
                    self._strandSet.mergeStrands(self, highNeighbor)
        else:
            raise IndexError

    ### PUBLIC SUPPORT METHODS ### 
    def removeDecoratorsOutOfRange(self):
        """
        Called by StrandSet's SplitCommand after copying the strand to be
        split. Either copy could have extra decorators that the copy should
        not retain.
        """
        decs = self._decorators
        idxMin, idMax = self.idxs() 
        for key in decs:
            if key > idxMax or key < idxMin:
                decs.pop(key)
            #end if
        # end for
    # end def

    def copy(self):
        pass
    # end def

    def shallowCopy(self):
        """
        can't use python module 'copy' as the dictionary _decorators
        needs to be shallow copied as well, but wouldn't be if copy.copy()
        is used, and copy.deepcopy is undesired
        """
        nS = Strand(self._strandSet, *self.idxs())
        nS._oligo = self._oligo
        nS._strand5p = self._strand5p
        nS._strand3p = self._strand3p
        # required to shallow copy the dictionary
        nS._decorators = dict(self._decorators.items())
        nS._sequence = None# self._sequence
        return nS
    # end def

    def deepCopy(self, strandSet, oligo):
        """
        can't use python module 'copy' as the dictionary _decorators
        needs to be shallow copied as well, but wouldn't be if copy.copy()
        is used, and copy.deepcopy is undesired
        """
        nS = Strand(strandSet, *self.idxs())
        nS._oligo = oligo
        decs = nS._decorators
        for key, decOrig in self._decorators:
            decs[key] = decOrig.deepCopy()
        # end fo
        nS._sequence = self._sequence
        return nS
    # end def

    ### COMMANDS ###
    class ResizeCommand(QUndoCommand):
        def __init__(self, strand, newIdxs):
            super(Strand.ResizeCommand, self).__init__()
            self.strand = strand
            self.oldIndices = strand.idxs()
            self.newIdxs = newIdxs
        # end def

        def redo(self):
            std = self.strand
            nI = self.newIdxs
            strandSet = self.strand.strandSet()
            part = strandSet.part()

            std.setIdxs(nI)
            std.strandResizedSignal.emit(std, nI)

            # for updating the Slice View displayed helices
            part.partStrandChangedSignal.emit(strandSet.virtualHelix())
        # end def

        def undo(self):
            std = self.strand
            oI = self.oldIndices
            strandSet = self.strand.strandSet()
            part = strandSet.part()

            std.setIdxs(oI)
            std.strandResizedSignal.emit(std, oI)

            # for updating the Slice View displayed helices
            part.partStrandChangedSignal.emit(strandSet.virtualHelix())
        # end def
    # end class

