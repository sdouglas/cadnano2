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
from .enum import LatticeType, Parity, StrandType, BreakType, Crossovers
from observable import Observable
from PyQt4.QtCore import pyqtSignal, QObject
from .base import Base

class VirtualHelix(QObject):   
    """Stores staple and scaffold routing information."""
    def __init__(self, *args, **kwargs):
        super(VirtualHelix, self).__init__()
        self._part = kwargs.get('part', None)
        self._number = kwargs.get('number', None)
        self._row = kwargs.get('row', 0)
        self._col = kwargs.get('col', 0)
        self._size = kwargs.get('size', 0)
        self._stapleBases = [Base(self, n) for n in range(self._size)]
        self._scaffoldBases = [Base(self, n) for n in range(self._size)]
        self._scafLeftPreXoList = []  # locations for PreXoverHandles
        self._scafRightPreXoList = []
        self._stapLeftPreXoList = []
        self._stapRightPreXoList = []
        self.isValid = True  # If loaded from a simple rep, isValid is false until all pointers are resolved
        # Signals
        self.changed = pyqtSignal()  # Some aspect of permanent, saveable state changed
        self.tweaked = pyqtSignal()  # Something relevant to the UI but not the underlying data changed

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

    def resolveSimpleRepIDs(self,idToObj):
        self._part = idToObj[self.partID]
        del self.partID
        self.isValid = True

    def part(self):
        """docstring for part"""
        return self._part

    def number(self):
        """return VirtualHelix number"""
        return self._number
    
    def coord(self):
        return (self._row, self._col)

    def parity(self):  # @toelim
        if self.parityEven():
            return Parity.Even
        else:
            return Parity.Odd
    
    def parityEven(self):
        return self._part.virtualHelixParityEven(self)

    def size(self):
        """The length in bases of the virtual helix."""
        return self._size

    def row(self):
        """return VirtualHelix helical-axis row"""
        return self._row

    def col(self):
        """return VirtualHelix helical-axis column"""
        return self._col

    def stapleBase(self, index):
        """docstring for stapleBase"""
        return self._stapleBases[index]

    def scaffoldBase(self, index):
        """docstring for scaffoldBase"""
        return self._scaffoldBases[index]

    def hasScafAt(self, index):
        """Returns true if a scaffold base is present at index"""
        if index > self._size-1:
            return False
        return not self._scaffoldBases[index].isNull()

    def hasStapAt(self, index):
        """Returns true if a staple base is present at index"""
        if index > self._size-1:
            return False
        return not self._stapleBases[index].isNull()

    def hasScafCrossoverAt(self, index):
        """docstring for hasScafCrossoverAt"""
        if index > self._size-1:
            return False
        return self._scaffoldBases[index].isCrossover()

    def hasStapCrossoverAt(self, index):
        """docstring for hasStapCrossoverAt"""
        if index > self._size-1:
            return False
        return self._stapleBases[index].isCrossover()

    def getScaffoldHandleIndexList(self):
        """
        Returns list containing the indices of bases that are 5' breakpoints,
        3' breakpoints, or crossovers.
        """
        ret = []
        for i in range(len(self._scaffoldBases)):
            if self._scaffoldBases[i].is5primeEnd():
                ret.append(i)
            if self._scaffoldBases[i].is3primeEnd():
                ret.append(i)
            if self._scaffoldBases[i].isCrossover():
                ret.append(i)
        return ret

    def getScaffold5PrimeEnds(self):
        """docstring for getScaffold5PrimeBreaks"""
        ret = []
        for i in range(len(self._scaffoldBases)):
            if self._scaffoldBases[i].is5primeEnd():
                ret.append(i)
        return ret

    def getScaffold3PrimeEnds(self):
        """docstring for getScaffold5PrimeBreaks"""
        ret = []
        for i in range(len(self._scaffoldBases)):
            if self._scaffoldBases[i].is3primeEnd():
                ret.append(i)
        return ret

    def updateAfterBreakpointMove(self, strandType, breakType, \
                                  startIndex, delta):
        """Called by a BreakpointHandle mouseReleaseEvent to update
        the data model."""
        # print "updateAfterBreakpointMove %d from %d by %d bases" % (self.number(), startIndex, delta)
        if delta == 0:
            return
        if strandType == StrandType.Scaffold:
            strandBases = self._scaffoldBases
        elif strandType == StrandType.Staple:
            strandBases = self._stapleBases
        else:
            raise AttributeError

        if (breakType == BreakType.Left3Prime):
            if (delta > 0):  # retract
                for i in range(startIndex, startIndex+delta):
                    strandBases[i].clearPrev()
                    strandBases[i+1].clearNext()
            else:  # extend
                for i in range(startIndex, startIndex+delta, -1):
                    strandBases[i].setNext(strandBases[i-1])
                    strandBases[i-1].setPrev(strandBases[i])
        elif (breakType == BreakType.Left5Prime):
            if (delta > 0):  # retract
                for i in range(startIndex, startIndex+delta):
                    strandBases[i].clearNext()
                    strandBases[i+1].clearPrev()
            else:  # extend
                for i in range(startIndex, startIndex+delta, -1):
                    strandBases[i].setNext(strandBases[i-1])
                    strandBases[i-1].setPrev(strandBases[i])
        elif (breakType == BreakType.Right3Prime):
            if (delta > 0):  # extend
                for i in range(startIndex, startIndex+delta):
                    strandBases[i].setNext(strandBases[i+1])
                    strandBases[i+1].setPrev(strandBases[i])
            else:  # retract
                for i in range(startIndex, startIndex+delta, -1):
                    strandBases[i].clearPrev()
                    strandBases[i-1].clearNext()
        elif (breakType == BreakType.Right5Prime):
            if (delta > 0):  # extend
                for i in range(startIndex, startIndex+delta):
                    strandBases[i].setPrev(strandBases[i+1])
                    strandBases[i+1].setNext(strandBases[i])
            else:  # retract
                for i in range(startIndex, startIndex+delta, -1):
                    strandBases[i].clearNext()
                    strandBases[i-1].clearPrev()
        else:
            raise AttributeError
    
    def getNeighbors():
        self._part.getVirtualHelixNeighbors(self)

    def updatePreCrossoverPositions(self, clickIndex=None):
        """docstring for updatePreCrossoverPositions"""
        self._scafLeftPreXoList = []
        self._scafRightPreXoList = []
        self._stapLeftPreXoList = []
        self._stapRightPreCxList = []

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
            end = self.size()
        else: # user mouse click
            start = max(0, clickIndex - (clickIndex % step) - step)
            end = min(self.size(), clickIndex - (clickIndex % step) + step*2)
        
        #for neighbor in self.getNeighbors()
        #neighborIndexList = self.getNeighborIndexList()
        neighbors = self.getNeighbors()
        for p in [0, 1, 2]:  # [0, 1, 2]
            neighbor = neighbors[p]
            # num = neighbor.number()
            # Scaffold Left
            for i,j in product(range(start, end, step), scafL[p]):
                index = i+j
                if self.possibleScafCrossoverAt(index, neighbor, index):
                    self._scafLeftPreXoList.append([neighbor, index])
            # Scaffold Right
            for i,j in product(range(start, end, step), scafR[p]):
                index = i+j
                if self.possibleScafCrossoverAt(index, neighbor, index):
                    self._scafRightPreXoList.append([neighbor, index])
            # Staple Left
            for i,j in product(range(start, end, step), stapL[p]):
                index = i+j
                if self.possibleStapCrossoverAt(index, neighbor, index):
                    self._stapLeftPreXoList.append([neighbor, index])
            # Staple Right
            for i,j in product(range(start, end, step), stapR[p]):
                index = i+j
                if self.possibleStapCrossoverAt(index, neighbor, index):
                    self._stapRightPreXoList.append([neighbor, index])

        # print "scafLeft:", self._scafLeftPreXoList
        # print "scafRight:", self._scafRightPreXoList
        # print "stapLeft:", self._stapLeftPreXoList
        # print "stapRight:", self._stapRightPreXoList
    # end def

    def possibleScafCrossoverAt(self, fromIndex, neighbor, toIndex):
        """Return true if scaffold could crossover to neighbor at index"""
        if self.scaffoldBase(fromIndex).isCrossover():
            return False
        if neighbor.scaffoldBase(toIndex).isCrossover():
            return False
        if not self.scaffoldBase(fromIndex).isNull() and\
           not neighbor.scaffoldBase(toIndex).isNull():
            return True
        return False

    def possibleStapCrossoverAt(self, fromIndex, neighbor, toIndex):
        """Return true if scaffold could crossover to neighbor at index"""
        if self.stapleBase(fromIndex).isCrossover():
            return False
        if neighbor.stapleBase(toIndex).isCrossover():
            return False
        if not self.stapleBase(fromIndex).isNull() and\
           not neighbor.stapleBase(toIndex).isNull():
            return True
        return False

    def installXoverTo(self, type, fromIndex, toVhelix, toIndex):
        """docstring for installXoverTo"""
        if type == StrandType.Scaffold:
            if self.possibleScafCrossoverAt(fromIndex, toVhelix, toIndex):
                fromBase = self.scaffoldBase(fromIndex)
                toBase = toVhelix.scaffoldBase(toIndex)
                fromBase.setNext(toBase)
                toBase.setPrev(fromBase)
            else:
                raise IndexError("Could not install scaffold crossover")
        elif type == StrandType.Staple:
            if self.possibleStapCrossoverAt(fromIndex, toVhelix, toIndex):
                fromBase = self.stapleBase(fromIndex)
                toBase = toVhelix.stapleBase(toIndex)
                fromBase.setNext(toBase)
                toBase.setPrev(fromBase)
            else:
                raise IndexError("Could not install staple crossover")

    def removeXoverTo(self, type, fromIndex, toVhelix, toIndex):
        """docstring for installXoverTo"""
        if type == StrandType.Scaffold:
            fromBase = self.scaffoldBase(fromIndex)
            toBase = toVhelix.scaffoldBase(toIndex)
            if fromBase.getNext() == toBase and fromBase == toBase.getPrev():
                fromBase.clearNext()
                toBase.clearPrev()
            else:
                raise IndexError("Crossover does not exist to be removed.")
        elif type == StrandType.Staple:
            fromBase = self.stapleBase(fromIndex)
            toBase = toVhelix.stapleBase(toIndex)
            if fromBase.getNext() == toBase and fromBase == toBase.getPrev():
                fromBase.clearNext()
                toBase.clearPrev()
            else:
                raise IndexError("Crossover does not exist to be removed.")

    def getLeftScafPreCrossoverIndexList(self):
        return self._scafLeftPreXoList

    def getRightScafPreCrossoverIndexList(self):
        return self._scafRightPreXoList

    def getLeftStapPreCrossoverIndexList(self):
        return self._stapLeftPreXoList

    def getRightStapPreCrossoverIndexList(self):
        return self._stapRightPreXoList

