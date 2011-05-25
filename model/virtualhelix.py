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
virtualhelix.py
Created by Jonathan deWerd on 2011-01-26.
"""
import sys
from exceptions import AttributeError, IndexError
from itertools import product
from .enum import LatticeType, Parity, StrandType, BreakType, Crossovers, EndType
from PyQt4.QtCore import pyqtSignal, QObject
from PyQt4.QtGui import QUndoCommand, QUndoStack
from .base import Base
from util import *

class VirtualHelix(QObject):
    """Stores staple and scaffold routing information."""
    basesModified = pyqtSignal()
    dimensionsModified = pyqtSignal()
    
    def __init__(self, *args, **kwargs):
        super(VirtualHelix, self).__init__()
        self._part = kwargs.get('part', None)
        self._row = kwargs.get('row', 0)
        self._col = kwargs.get('col', 0)
        self._stapleBases = []
        self._scaffoldBases = []
        self._number = kwargs.get('idnum', -1)
        numBases = kwargs.get('numBases', None)
        if numBases:
            self._numBases = numBases
        else:
            self._numBases = None
            numBases = self.numBases()
        self.setNumBases(numBases)
        self._scafLPoXo  = []  # Potential Crossover
        self._scafRPoXo = []
        self._stapLPoXo  = []
        self._stapRPoXo = []
        self._undoStack = None
    
    def __repr__(self):
        return 'vh%i'%self.number()
    
    def __str__(self):
        scaf = '%-2iScaffold: ' % self.number() + \
                            ' '.join((str(b) for b in self._scaffoldBases))
        stap = '%-2iStaple:   ' % self.number() + \
                                ' '.join((str(b) for b in self._stapleBases))
        return scaf + '\n' + stap

    def numBases(self):
        if self._numBases:
            return self._numBases
        return self._part.numBases()
    
    def setNumBases(self, newNumBases=None):
        # @toundo
        if self.part():
            assert(self.part().numBases()==newNumBases)
        elif self._numBases!=None:
            self._numBases = newNumBases
        oldNB = len(self._stapleBases)
        if newNumBases > oldNB:
            for n in range(oldNB, newNumBases):
                self._stapleBases.append(Base(self, n))
                self._scaffoldBases.append(Base(self, n))
        self.dimensionsModified.emit()

    def part(self):
        return self._part

    def number(self):
        """return VirtualHelix number"""
        return self._number
    
    def setNumber(self, newNumber):
        self._part.renumberVirtualHelix(self, newNumber)
    
    def _setNumber(self, newNumber):
        """_part is responsible for assigning ids, so only it gets to
        use this method."""
        self._number = newNumber
        self.changed.emit()
    
    def coord(self):
        return (self._row, self._col)

    def evenParity(self):
        """
        returns True or False
        """
        return self._part.virtualHelixParityEven(self)

    def directionOfStrandIs5to3(self,strandtype):
        """
        method to determine 5' to 3' or 3' to 5'
        """
        if self.evenParity() and strandtype == Strandtype.Scaffold:
            return True
        elif not self.evenParity() and strandtype == Strandtype.Staple:
            return True
        else:
            return False
    # end def
    
    def row(self):
        """return VirtualHelix helical-axis row"""
        return self._row

    def col(self):
        """return VirtualHelix helical-axis column"""
        return self._col
    
    def strand(self, strandType):
        """The returned strand should be considered privately
        mutable"""
        if strandType == StrandType.Scaffold:
            return self._scaffoldBases
        elif strandType == StrandType.Staple:
            return self._stapleBases
        else:
            raise IndexError

    ########################### Access to Bases ###################
    def _stapleBase(self, index):
        """private to virtualhelix"""
        return self._stapleBases[index]

    def _scaffoldBase(self, index):
        """private to virtualhelix"""
        return self._scaffoldBases[index]

    def hasScafAt(self, index):
        """Returns true if a scaffold base is present at index"""
        if index > self.numBases()-1:
            return False
        return not self._scaffoldBases[index].isEmpty()

    def hasStapAt(self, index):
        """Returns true if a staple base is present at index"""
        if index > self.numBases()-1:
            return False
        return not self._stapleBases[index].isEmpty()

    def hasCrossoverAt(self, strandType, index):
        """docstring for hasScafCrossoverAt"""
        strand = self.strand(strandType)
        if index>=len(strand) or index<0:
            return False
        return strand[index].isCrossover()

    def getEnds(self, strandType):
        """Returns a list of 3' and 5' ends in the format
        [(index, EndType), ...]"""
        ret = []
        strand = self.strand(strandType)
        for i in range(len(strand)):
            if strand[i].is5primeEnd():
                ret.append((i, EndType.FivePrime))
            if strand[i].is3primeEnd():
                ret.append((i, EndType.ThreePrime))
        return ret
    
    def getSegments(self, strandType):
        """Returns a list of segments of connected bases in the form
        [(startIdx, endIdx), ...]"""
        ret = []
        strand = self.strand(strandType)
        i, s = 0, None
        # s is the start index of the segment
        for i in range(len(strand)):
            if strand[i].isEnd():
                if s!=None:
                    ret.append((s,i))
                    s = None
                else:
                    s = i
        return ret

    def undoStack(self):
        if self.part():
            return self.part().undoStack()
        if not self._undoStack:
            self._undoStack = QUndoStack()
        return self._undoStack
            
    ################## Public Base Modification API #########
    """
    Overview: the bases in a virtualhelix can be modified
    with the public methods, which under the hood just validate
    their arguments and push
    undo commands (of a similar name to the public methods)
    that call private methods (often of exactly the same name
    as the public methods except for a prefixed underscore).
    Outside World -> doSomething() -> DoSomethingUndoCommand -> _doSomething() -> Private API
    or Outside World -> doSomething() -> DoSomethingUndoCommand -> Private API
    """
    def connectStrand(self, strandType, startIndex, endIndex):
        # Connects sequential bases on a single strand, starting with 
        # startIndex and ending with etdIndex (inclusive)
        # Sets {s.n, (s+1).np, ..., (e-2).np, (e-1).np, e.p}
        strand = self.strand(strandType)
        endIndex, startIndex = int(max(startIndex,endIndex)), int(min(startIndex,endIndex))
        startIndex = clamp(startIndex, 0, len(strand)-1)
        endIndex = clamp(endIndex, 0, len(strand)-1)
        c = self.ConnectStrandCommand(self, strandType, startIndex, endIndex)    
        self.undoStack().push(c)

    def clearStrand(self, strandType, startIndex, endIndex):
        startIndex, endIndex = int(startIndex), int(endIndex)
        strand = strandType==StrandType.Scaffold and self._scaffoldBases or self._stapleBases
        assert(startIndex>=1 and startIndex<=len(strand))
        assert(endIndex>=1 and endIndex<=len(strand))
        c = self.ClearStrandCommand(self, strandType, startIndex, endIndex)
        self.undoStack().push(c)
    
    def connectBases(self, type, fromIdx, toVH, toIdx):
        assert(0<=fromIdx and fromIdx<len(self.strand(type)))
        assert(0<=toIdx and toIdx<len(toVH.strand(type)))
        c = self.ConnectBasesCommand(type, self, fromIdx, toVH, toIdx)
        self.undoStack().push(c)
    
    # Derived private API
    def breakStrandBeforeBase(self, strandType, breakBeforeIndex):
        breakBeforeIndex = int(breakBeforeIndex)
        assert(breakBeforeIndex > 0)
        assert(breakBeforeIndex < len(strand))
        self.clearStrand(strandType, breakBeforeIndex, breakBeforeIndex)

    def installXoverTo(self, type, fromIndex, toVhelix, toIndex):
        """docstring for installXoverTo"""
        if type == StrandType.Scaffold:
            assert(self.possibleNewCrossoverAt(fromIndex, toVhelix, toIndex))
        elif type == StrandType.Staple:
            assert(self.possibleStapCrossoverAt(fromIndex, toVhelix, toIndex))
        else:
            raise IndexError("%s doesn't look like a StrandType"%type)
        self.connectBases(self, strandType, fromIdx, toVH, toIdx)

    def removeXoverTo(self, type, fromIndex, toVhelix, toIndex):
        """docstring for installXoverTo"""
        strand = self.strand(type)
        fromBase = strand[fromIndex]
        toBase = toVhelix.strand(StrandType.Scaffold)[toIndex]
        if fromBase._nextBase != toBase or fromBase != toBase._prevBase:
            raise IndexError("Crossover does not exist to be removed.")
        toVhelix.breakStrandBeforeBase(type, toIndex)

    ################################### Private Base Modification API #############################    
    class ConnectStrandCommand(QUndoCommand):
        def __init__(self, virtualHelix, strandType, startIndex, endIndex):
            super(VirtualHelix.ConnectStrandCommand, self).__init__()
            self._vh = virtualHelix
            self._strandType = strandType
            self._startIndex = startIndex
            self._endIndex = endIndex
            
        def redo(self):
            # Sets {s.n, (s+1).np, ..., (e-2).np, (e-1).np, e.p}
            # st s, s+1, ..., e-1, e are connected
            strand = self._vh.strand(self._strandType)
            ol = self._oldLinkage = []
            if directionOfStrandIs5to3(self._strandType)):
                for i in range(self._startIndex, self._endIndex):
                    ol.append(strand[i]._set3Prime(strand[i+1]))
            # end if
            else:
                for i in range(self._startIndex, self._endIndex):
                    ol.append(strand[i]._set5Prime(strand[i+1]))
            # end else
            self._vh.basesModified.emit()
            
        def undo(self):
            strand = self._vh.strand(self._strandType)
            ol = self._oldLinkage
            assert(ol)  # Must redo/apply before undo
            
            if directionOfStrandIs5to3(self._strandType)):
                for i in range(self._endIndex-1, self._startIndex-1, -1):
                    strand[i]._set3Prime(*ol[i-self._startIndex])
            # end if
            else:
                for i in range(self._endIndex-1, self._startIndex-1, -1):
                    strand[i]._set5Prime(*ol[i-self._startIndex])
            # end else
            
            self._vh.basesModified.emit()
    
    class ClearStrandCommand(QUndoCommand):
        def __init__(self, virtualHelix, strandType, startIndex, endIndex):
            super(VirtualHelix.ClearStrandCommand, self).__init__()
            self._vh = virtualHelix
            self._strandType = strandType
            self._startIndex = startIndex
            self._endIndex = endIndex

        def redo(self):
            # Clears {s.n, (s+1).np, ..., (e-1).np, e.p}
            # Be warned, start index and end index become endpoints
            # if this is called in the middle of a connected strand
            strand = self._vh.strand(self._strandType)
            ol = self._oldLinkage = []
            
            if directionOfStrandIs5to3(self._strandType)):
                for i in range(self._startIndex-1, self._endIndex):
                    ol.append(strand[i]._set3Prime(None))
            # end if
            else:
                for i in range(self._startIndex-1, self._endIndex):
                    ol.append(strand[i]._set5Prime(None))
            # end else
            self._vh.basesModified.emit()

        def undo(self):
            strand = self._vh.strand(self._strandType)
            ol = self._oldLinkage
            assert(ol)  # Must redo/apply before undo
            if directionOfStrandIs5to3(self._strandType)):
                for i in range(self._endIndex-1, self._startIndex-2, -1):
                    strand[i]._set3Prime(*ol[i-self._startIndex])
            # end if
            else:
                for i in range(self._endIndex-1, self._startIndex-2, -1):
                    strand[i]._set5Prime(*ol[i-self._startIndex])
            # end else
            self._vh.basesModified.emit()
    
    class ConnectBasesCommand(QUndoCommand):
        def __init__(self, type, fromHelix, fromIndex, toHelix, toIndex):
            super(VirtualHelix.ConnectBasesCommand, self).__init__()
            self._strandType = type
            self._fromHelix = fromHelix
            self._fromIndex = fromIndex
            self._toHelix = toHelix
            self._toIndex = toIndex
            
        def redo(self):
            fromB = self._fromHelix.strand(self._strandType)[self._fromIndex]
            toB   = self._toHelix.strand(self._strandType)[self._toIndex]
            
            if directionOfStrandIs5to3(self._strandType)):
                self._undoDat = fromB._set3Prime(toB)
            # end if
            else:
                self._undoDat = fromB._set5Prime(toB)
            # end else
            
            self._fromHelix.basesModified.emit()
            self._toHelix.basesModified.emit()

        def undo(self):
            fromB = self._fromHelix.strand(self._strandType)[self._fromIndex]
            assert(self._undoDat)  # Must redo/apply before undo
            if directionOfStrandIs5to3(self._strandType)):
                fromB._set3Prime(*self._undoDat)
            # end if
            else:
               fromB._set5Prime(*self._undoDat) 
            # else
            
            self._fromHelix.basesModified.emit()
            self._toHelix.basesModified.emit()
 
    ################################### Crossovers #############################   
    def potentialCrossoverList(self, rightNotLeft, strandType):
        """Returns a list of [neighborVirtualHelix, index] potential
        crossovers"""
        ret = []
        luts = (self._part.scafL, self._part.scafR, self._part.stapL, self._part.stapR)
        lut = luts[int(rightNotLeft)+2*int(strandType==StrandType.Staple)]
        neighbors = self.getNeighbors()
        for p in range(len(neighbors)):
            neighbor = neighbors[p]
            if not neighbor:
                continue
            for i,j in product(range(0, self.numBases(), step), lut[p]):
                index = i+j
                ret.append([neighbor, index])
        return ret

    def crossoverAt(self, type, fromIndex, neighbor, toIndex):
        return 

    def possibleNewCrossoverAt(self, type, fromIndex, neighbor, toIndex):
        """Return true if scaffold could crossover to neighbor at index.
        Useful for seeing if potential crossovers from potentialCrossoverList
        should be presented as points at which new a new crossover can be formed."""
        fromB = self.strand(type)[fromIndex]
        toB   = neighbor.strand(type)[toIndex]
        if fromB.isCrossover() or toB.isCrossover():
            return False
        return  not self.scaffoldBase(fromIndex).isEmpty() and\
                not neighbor.scaffoldBase(toIndex).isEmpty()

    def getNeighbors(self):
        """The part (which controls helix layout) decides who
        the virtualhelix's neighbors are. A list is returned,
        possibly containing None in some slots, so that
        getNeighbors()[i] corresponds to the neighbor in direction
        i (where the map between directions and indices is defined
        by the part)"""
        return self._part.getVirtualHelixNeighbors(self)

    ################################## Archiving / Unarchiving ##################################
    def simpleRep(self, encoder):
        """Returns a representation in terms of simple JSON-encodable types
        or types that implement simpleRep"""
        ret = {'.class': "DNAPart"}
        ret['part'] = encoder.idForObject(self._part)
        ret['number'] = self._number
        ret['size'] = self._size
        ret['stapleBases'] = self._stapleBases
        ret['scaffoldBases'] = self._scaffoldBases
        return ret

    @classmethod
    def fromSimpleRep(cls, rep):
        """Instantiates one of the parent class from the simple
        representation rep"""
        ret = VirtualHelix()
        ret.partID = rep['part']
        ret._number = rep['number']
        ret._row = rep['row']
        ret._col = rep['col']
        ret._stapleBases = rep['stapleBases']
        ret._scaffoldBases = rep['scaffoldBases']
        ret.isValid = False
        return ret
