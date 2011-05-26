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
from .enum import LatticeType, Parity, StrandType, BreakType
from .enum import Crossovers, EndType
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
        # Undo stack is only temporary and should be 
        # removed (causes undoStack() to return part.undoStac())
        # upon setSandboxed(False)
        self._sandboxed = False
    
    def __repr__(self):
        return 'vh%i' % self.number()
    
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
                self._stapleBases.append(Base(self, StrandType.Staple, n))
                self._scaffoldBases.append(Base(self, StrandType.Scaffold, n))
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
        if self._part:
            return self._part.virtualHelixParityEven(self)
        else:
            return self._number % 2 == 0

    def directionOfStrandIs5to3(self,strandtype):
        """
        method to determine 5' to 3' or 3' to 5'
        """
        if self.evenParity() and strandtype == StrandType.Scaffold:
            return True
        elif not self.evenParity() and strandtype == StrandType.Staple:
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
    
    def _strand(self, strandType):
        """The returned strand should be considered privately
        mutable"""
        if strandType == StrandType.Scaffold:
            return self._scaffoldBases
        elif strandType == StrandType.Staple:
            return self._stapleBases
        else:
            raise IndexError

    ########################### Access to Bases ###################
    def hasBaseAt(self, strandType, index):
        """Returns true if a scaffold base is present at index"""
        base = self._baseAt(strandType, index)
        if not base:
            return False
        else:
            return not base.isEmpty()
    
    def validatedBase(self, strandType, index, raiseOnErr=False):
        """Makes sure the basespec (strandType,index) is valid
        and raises or returns (None, None) according to raiseOnErr if
        it isn't valid"""
        if strandType != StrandType.Scaffold and strandType!=StrandType.Staple:
            if raiseOnErr:
                raise IndexError("Base (strand:%s index:%i) Not Valid"%(strandType,index))
            return (None, None)
        index = int(index)
        if index < 0 or index >= self.numBases() - 1:
            if raiseOnErr:
                raise IndexError("Base (strand:%s index:%i) Not Valid"%(strandType,index))
            return (None, None)
        return (strandType, index)
    
    def _baseAt(self, strandType, index, raiseOnErr=False):
        strandType, index = self.validatedBase(strandType, index, raiseOnErr=raiseOnErr)
        if strandType == None:
            return None
        return self._strand(strandType)[index]

    def hasCrossoverAt(self, strandType, index):
        """docstring for hasScafCrossoverAt"""
        base = self._baseAt(strandType, index)
        if not base:
            return False
        else:
            return base.isCrossover()
    
    def hasStrandAt(self, strandType, index):
        """A strand base is a base that is connected to
        other bases on both sides (possibly over a staple)"""
        base = self._baseAt(strandType, index)
        if not base:
            return False
        else:
            return base.isStrand()

    def getEnds(self, strandType):
        """Returns a list of 3' and 5' ends in the format
        [(index, EndType), ...]"""
        ret = []
        strand = self._strand(strandType)
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
        strand = self._strand(strandType)
        i, s = 0, None
        # s is the start index of the segment
        for i in range(len(strand)):
            if strand[i].isEnd():
                if s != None:
                    ret.append((s,i))
                    s = None
                else:
                    s = i
        return ret
    
    def setSandboxed(self, sb):
        if sb and not self._undoStack:
            self._sandboxed = True
            if not self._undoStack:
                self._undoStack = QUndoStack()
        else:
            if self._sandboxed:
                self._sandboxed = False
                self._undoStack = None

    def undoStack(self):
        if self._undoStack:
            return self._undoStack
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
    Outside World -> doSomething() -> DoSomethingUndoCommand -> 
        _doSomething() -> Private API
    or Outside World -> doSomething() -> DoSomethingUndoCommand -> Private API
    """
    def connectStrand(self, strandType, startIndex, endIndex):
        # Connects sequential bases on a single strand, starting with 
        # startIndex and ending with etdIndex (inclusive)
        # Sets {s.n, (s+1).np, ..., (e-2).np, (e-1).np, e.p}
        strand = self._strand(strandType)
        endIndex, startIndex = int(max(startIndex,endIndex)), \
                                        int(min(startIndex,endIndex))
        startIndex = clamp(startIndex, 0, len(strand)-1)
        endIndex = clamp(endIndex, 0, len(strand)-1)
        c = self.ConnectStrandCommand(self, strandType, startIndex, endIndex)    
        self.undoStack().push(c)

    def clearStrand(self, strandType, startIndex, endIndex):
        endIndex, startIndex = int(max(startIndex,endIndex)), \
                                        int(min(startIndex,endIndex))
        strand = strandType == StrandType.Scaffold and \
            self._scaffoldBases or self._stapleBases
        startIndex = clamp(startIndex, 1, len(strand))
        endIndex = clamp(endIndex, 1, len(strand))        
        c = self.ClearStrandCommand(self, strandType, startIndex, endIndex)
        self.undoStack().push(c)
    
    def connectBases(self, type, fromIdx, toVH, toIdx):
        assert(0 <= fromIdx and fromIdx < len(self._strand(type)))
        assert(0 <= toIdx and toIdx < len(toVH._strand(type)))
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
            raise IndexError("%s doesn't look like a StrandType" % type)
        self.connectBases(self, strandType, fromIdx, toVH, toIdx)

    def removeXoverTo(self, type, fromIndex, toVhelix, toIndex):
        """docstring for installXoverTo"""
        strand = self._strand(type)
        fromBase = strand[fromIndex]
        toBase = toVhelix._strand(StrandType.Scaffold)[toIndex]
        if fromBase._nextBase != toBase or fromBase != toBase._prevBase:
            raise IndexError("Crossover does not exist to be removed.")
        toVhelix.breakStrandBeforeBase(type, toIndex)

    ################ Private Base Modification API ###########################
    class ConnectStrandCommand(QUndoCommand):
        def __init__(self, virtualHelix, strandType, startIndex, endIndex):
            super(VirtualHelix.ConnectStrandCommand, self).__init__()
            self._vh = virtualHelix
            self._strandType = strandType
            self._startIndex = startIndex
            self._endIndex = endIndex
            self._oldLinkage = None
            
        def redo(self):
            # Sets {s.n, (s+1).np, ..., (e-2).np, (e-1).np, e.p}
            # st s, s+1, ..., e-1, e are connected
            strand = self._vh._strand(self._strandType)
            ol = self._oldLinkage = []
            if self._vh.directionOfStrandIs5to3(self._strandType):
                for i in range(self._startIndex, self._endIndex):
                    ol.append(strand[i]._set3Prime(strand[i + 1]))
            # end if
            else:
                for i in range(self._startIndex, self._endIndex):
                    ol.append(strand[i]._set5Prime(strand[i + 1]))
            # end else
            self._vh.basesModified.emit()
            
        def undo(self):
            strand = self._vh._strand(self._strandType)
            ol = self._oldLinkage
            assert(ol!=None)  # Must redo/apply before undo
            if self._vh.directionOfStrandIs5to3(self._strandType):
                for i in range(self._endIndex - 1, self._startIndex - 1, -1):
                    strand[i]._unset3Prime(strand[i + 1], *ol[i - self._startIndex])
            # end if
            else:
                for i in range(self._endIndex - 1, self._startIndex - 1, -1):
                    strand[i]._unset5Prime(strand[i + 1], *ol[i - self._startIndex])
            # end else
            
            self._vh.basesModified.emit()
    
    class ClearStrandCommand(QUndoCommand):
        def __init__(self, virtualHelix, strandType, startIndex, endIndex):
            super(VirtualHelix.ClearStrandCommand, self).__init__()
            self._vh = virtualHelix
            self._strandType = strandType
            self._startIndex = startIndex
            self._endIndex = endIndex
            self._oldLinkage = None

        def redo(self):
            # Clears {s.n, (s+1).np, ..., (e-1).np, e.p}
            # Be warned, start index and end index become endpoints
            # if this is called in the middle of a connected strand
            strand = self._vh._strand(self._strandType)
            ol = self._oldLinkage = []
            
            if self._vh.directionOfStrandIs5to3(self._strandType):
                for i in range(self._startIndex - 1, self._endIndex):
                    ol.append(strand[i]._set3Prime(None))
            # end if
            else:
                for i in range(self._startIndex - 1, self._endIndex):
                    ol.append(strand[i]._set5Prime(None))
            # end else
            self._vh.basesModified.emit()

        def undo(self):
            strand = self._vh._strand(self._strandType)
            ol = self._oldLinkage
            assert(ol!=None)  # Must redo/apply before undo
            if self._vh.directionOfStrandIs5to3(self._strandType):
                for i in range(self._endIndex - 1, self._startIndex - 2, -1):
                    strand[i]._unset3Prime(None, *ol[i - self._startIndex+1])
            # end if
            else:
                for i in range(self._endIndex - 1, self._startIndex - 2, -1):
                    strand[i]._unset5Prime(None, *ol[i - self._startIndex+1])
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
            fromB = self._fromHelix._strand(self._strandType)[self._fromIndex]
            toB   = self._toHelix._strand(self._strandType)[self._toIndex]
            
            if self._fromHelix.directionOfStrandIs5to3(self._strandType):
                self._undoDat = fromB._set3Prime(toB)
            else:
                self._undoDat = fromB._set5Prime(toB)
            
            self._fromHelix.basesModified.emit()
            self._toHelix.basesModified.emit()

        def undo(self):
            fromB = self._fromHelix._strand(self._strandType)[self._fromIndex]
            toB   = self._toHelix._strand(self._strandType)[self._toIndex]
            assert(self._undoDat)  # Must redo/apply before undo
            if self._fromHelix.directionOfStrandIs5to3(self._strandType):
                fromB._unset3Prime(toB, *self._undoDat)
            else:
                fromB._unset5Prime(toB, *self._undoDat)
            
            self._fromHelix.basesModified.emit()
            self._toHelix.basesModified.emit()
 
    ################################### Crossovers ########################### 
    def potentialCrossoverList(self, rightNotLeft, strandType):
        """Returns a list of [neighborVirtualHelix, index] potential
        crossovers"""
        ret = []
        luts = (self._part.scafL, self._part.scafR, \
                        self._part.stapL, self._part.stapR)
                        
        # these are the list of crossover points simplified 
        lut = luts[int(rightNotLeft) + 2*int(strandType == StrandType.Staple)]
        
        neighbors = self.getNeighbors()
        for p in range(len(neighbors)):
            neighbor = neighbors[p]
            if not neighbor:
                continue
            for i,j in product(range(0, self.numBases(), step), lut[p]):
                index = i + j
                ret.append([neighbor, index])
        return ret

    def crossoverAt(self, type, fromIndex, neighbor, toIndex):
        return 

    def scaffoldBase(self, index):
        """docstring for scaffoldBase"""
        return self._scaffoldBases[index]

    def possibleNewCrossoverAt(self, type, fromIndex, neighbor, toIndex):
        """Return true if scaffold could crossover to neighbor at index.
        Useful for seeing if potential crossovers from potentialCrossoverList
        should be presented as points at which new a new crossover can be formed."""
        fromB = self._strand(type)[fromIndex]
        toB   = neighbor._strand(type)[toIndex]
        if fromB.isCrossover() or toB.isCrossover():
            return False
        return  not self.scaffoldBase(fromIndex).isEmpty() and \
                not neighbor.scaffoldBase(toIndex).isEmpty()

    def updatePreCrossoverPositions(self, clickIndex=None):
        """docstring for updatePreCrossoverPositions"""
        self._scafLeftPreXoList = []
        self._scafRightPreXoList = []
        self._stapLeftPreXoList = []
        self._stapRightPreXoList = []

        if self._part.crossSectionType() == LatticeType.Honeycomb:
            step = 21
            scafL = Crossovers.honeycombScafLeft
            scafR = Crossovers.honeycombScafRight
            stapL = Crossovers.honeycombStapLeft
            stapR = Crossovers.honeycombStapRight
        elif self._part.crossSectionType() == LatticeType.Square:
            step = 32
            scafL = Crossovers.squareScafLeft
            scafR = Crossovers.squareScafRight
            stapL = Crossovers.squareStapLeft
            stapR = Crossovers.squareStapRight

        if clickIndex == None:  # auto staple
            start = 0
            end = self.numBases()
        else: # user mouse click
            start = max(0, clickIndex - (clickIndex % step) - step)
            end = min(self.numBases(), clickIndex - (clickIndex % step) + step*2)

        neighbors = self.getNeighbors()
        for p in range(len(neighbors)):
            neighbor = neighbors[p]
            if not neighbor:
                continue
            # Scaffold Left
            for i,j in product(range(start, end, step), scafL[p]):
                index = i+j
                if self.possibleNewCrossoverAt(StrandType.Scaffold, index, neighbor, index):
                # if self.possibleScafCrossoverAt(index, neighbor, index):
                    self._scafLeftPreXoList.append([neighbor, index])
            # Scaffold Right
            for i,j in product(range(start, end, step), scafR[p]):
                index = i+j
                if self.possibleNewCrossoverAt(StrandType.Scaffold, index, neighbor, index):
                # if self.possibleScafCrossoverAt(index, neighbor, index):
                    self._scafRightPreXoList.append([neighbor, index])
            # Staple Left
            for i,j in product(range(start, end, step), stapL[p]):
                index = i+j
                if self.possibleNewCrossoverAt(StrandType.Staple, index, neighbor, index):
                # if self.possibleStapCrossoverAt(index, neighbor, index):
                    self._stapLeftPreXoList.append([neighbor, index])
            # Staple Right
            for i,j in product(range(start, end, step), stapR[p]):
                index = i+j
                if self.possibleNewCrossoverAt(StrandType.Staple, index, neighbor, index):
                # if self.possibleStapCrossoverAt(index, neighbor, index):
                    self._stapRightPreXoList.append([neighbor, index])

    # end def
    
    def getLeftScafPreCrossoverIndexList(self):
        return self._scafLeftPreXoList

    def getRightScafPreCrossoverIndexList(self):
        return self._scafRightPreXoList

    def getLeftStapPreCrossoverIndexList(self):
        return self._stapLeftPreXoList

    def getRightStapPreCrossoverIndexList(self):
        return self._stapRightPreXoList

    def getNeighbors(self):
        """The part (which controls helix layout) decides who
        the virtualhelix's neighbors are. A list is returned,
        possibly containing None in some slots, so that
        getNeighbors()[i] corresponds to the neighbor in direction
        i (where the map between directions and indices is defined
        by the part)"""
        return self._part.getVirtualHelixNeighbors(self)

    #################### Archiving / Unarchiving #############################
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
