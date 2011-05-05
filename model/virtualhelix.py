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
import sys, weakref
from exceptions import AttributeError, IndexError
from itertools import product
from .base import Base
from .enum import LatticeType, Parity, StrandType, BreakType, Crossovers

class VirtualHelix(object):
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
        self._observers = []
        self._p0 = None  # honeycomb: \, square: ?
        self._p1 = None  # honeycomb: |, square: ?
        self._p2 = None  # honeycomb: /, square: ?
        self._p3 = None  #               square: ?
        self._scafLeftPreXoList = []  # locations for PreCrossoverHandles
        self._scafRightPreXoList = []
        self._stapLeftPreXoList = []
        self._stapRightPreXoList = []

    def simpleRep(self, encoder):
        """Returns a representation in terms of simple JSON-encodable types
        or types that implement simpleRep"""
        ret = {'.class': "DNAPart"}
        ret['part'] = encoder.idForObject(self._part)
        ret['number'] = self._number
        ret['size'] = self._size
        ret['stapleBases'] = self._stapleBases
        ret['scaffoldBases'] = self._scaffoldBases
        ret['p0'] = encoder.idForObject(self._p0)
        ret['p1'] = encoder.idForObject(self._p1)
        ret['p2'] = encoder.idForObject(self._p2)
        ret['p3'] = encoder.idForObject(self._p3)
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
        ret.p0ID = rep['p0']
        ret.p1ID = rep['p1']
        ret.p2ID = rep['p2']
        ret.p3ID = rep['p3']
        return ret

    def resolveSimpleRepIDs(self,idToObj):
        self._part = idToObj[self.partID]
        del self.partID
        self._p0 = idToObj[self.p0ID]
        del self.p0ID
        self._p1 = idToObj[self.p1ID]
        del self.p1ID
        self._p2 = idToObj[self.p2ID]
        del self.p2ID
        self._p3 = idToObj[self.p3ID]
        del self.p3ID

    def part(self):
        """docstring for part"""
        return self._part

    def number(self):
        """return VirtualHelix number"""
        return self._number

    def parity(self):
        if self._number == None:
            raise AttributeError
        if self._number % 2 == 0:
            return Parity.Even
        else:
            return Parity.Odd

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

    def setP0(self, vhelix):
        """Sets p0 neighbor to vhelix."""
        self._p0 = vhelix

    def setP1(self, vhelix):
        """Sets p1 neighbor to vhelix."""
        self._p1 = vhelix

    def setP2(self, vhelix):
        """Sets p3 neighbor to vhelix."""
        self._p2 = vhelix

    def setP3(self, vhelix):
        """Sets p3 neighbor to vhelix. Used by square lattice only."""
        self._p3 = vhelix

    def getNeighborIndexList(self):
        """docstring for getNeighborIndexList"""
        ret = []
        if self._p0 != None:
            ret.append(0)
        if self._p1 != None:
            ret.append(1)
        if self._p2 != None:
            ret.append(2)
        if self._p3 != None:
            ret.append(3)
        return ret

    def getNeighbor(self, num):
        """return ref to neighbor pNum"""
        if num in [0, 1, 2, 3]:
            ret = [self._p0, self._p1, self._p2, self._p3][num]
            return ret
        else:
            raise IndexError

    def connectNeighbors(self, p0, p1, p2, p3):
        """docstring for connectNeighbor"""
        if p0 != None:
            self.setP0(p0)
            p0.setP0(self)
        if p1 != None:
            self.setP1(p1)
            p1.setP1(self)
        if p2 != None:
            self.setP2(p2)
            p2.setP2(self)
        if p3 != None:  # used by square lattice only
            self.setP3(p3)
            p3.setP3(self)

    def hasScafAt(self, index):
        """Returns true if a scaffold base is present at index"""
        if index > self._size-1:
            return False
        if self._scaffoldBases[index].isNull():
            return False
        return True

    def hasStapAt(self, index):
        """Returns true if a staple base is present at index"""
        if index > self._size-1:
            return False
        if self._stapleBases[index].isNull():
            return False
        return True

    def hasScafCrossoverAt(self, index):
        """docstring for hasScafCrossoverAt"""
        if index > self._size-1:
            return False
        if self._scaffoldBases[index].isCrossover():
            return True
        return False

    def hasStapCrossoverAt(self, index):
        """docstring for hasStapCrossoverAt"""
        if index > self._size-1:
            return False
        if self._stapleBases[index].isCrossover():
            return True
        return False

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

    def updateObservers(self):
        for o in self._observers:
            if o():
                o().update()

    def addObserver(self, obs):
        self._observers.append(weakref.ref(obs, lambda x: self._observers.remove(x)))

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

        neighborIndexList = self.getNeighborIndexList()
        for p in neighborIndexList:  # [0, 1, 2]
            neighbor = self.getNeighbor(p)
            # num = neighbor.number()
            # Scaffold Left
            for i,j in product(range(start, end, step), scafL[p]):
                index = i+j
                if self.possibleScafCrossoverAt(index, neighbor):
                    self._scafLeftPreXoList.append([neighbor, index])
            # Scaffold Right
            for i,j in product(range(start, end, step), scafR[p]):
                index = i+j
                if self.possibleScafCrossoverAt(index, neighbor):
                    self._scafRightPreXoList.append([neighbor, index])
            # Staple Left
            for i,j in product(range(start, end, step), stapL[p]):
                index = i+j
                if self.possibleStapCrossoverAt(index, neighbor):
                    self._stapLeftPreXoList.append([neighbor, index])
            # Staple Right
            for i,j in product(range(start, end, step), stapR[p]):
                index = i+j
                if self.possibleStapCrossoverAt(index, neighbor):
                    self._stapRightPreXoList.append([neighbor, index])

        print "scafLeft:", self._scafLeftPreXoList
        print "scafRight:", self._scafRightPreXoList
        # print "stapLeft:", self._stapLeftPreXoList
        # print "stapRight:", self._stapRightPreXoList
    # end def

    def possibleScafCrossoverAt(self, index, neighbor):
        """Return true if scaffold could crossover to neighbor at index"""
        if self.scaffoldBase(index).isCrossover():
            return False
        if neighbor.scaffoldBase(index).isCrossover():
            return False
        if not self.scaffoldBase(index).isNull() and\
           not neighbor.scaffoldBase(index).isNull():
            return True
        return False

    def possibleStapCrossoverAt(self, index, neighbor):
        """Return true if scaffold could crossover to neighbor at index"""
        if self.stapleBase(index).isCrossover():
            return False
        if neighbor.stapleBase(index).isCrossover():
            return False
        if not self.stapleBase(index).isNull() and\
           not neighbor.stapleBase(index).isNull():
            return True
        return False

    def getLeftScafPreCrossoverIndexList(self):
        return self._scafLeftPreXoList

    def getRightScafPreCrossoverIndexList(self):
        return self._scafRightPreXoList

    def getLeftStapPreCrossoverIndexList(self):
        return self._stapLeftPreXoList

    def getRightStapPreCrossoverIndexList(self):
        return self._stapRightPreXoList

