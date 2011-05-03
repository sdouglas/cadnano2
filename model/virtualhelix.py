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
from .base import Base
import sys, weakref

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
        return ret

    def resolveSimpleRepIDs(self,idToObj):
        self._part = idToObj[self.partID]
        del self.partID

    def part(self):
        """docstring for part"""
        return self._part

    def number(self):
        """return VirtualHelix number"""
        return self._number

    def size(self):
        """docstring for size"""
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
    
    def hasScaf(self, index):
        """Returns true if a scaffold base is present at index"""
        if index > self._size:
            return False
        base = self._scaffoldBases[index]
        if not base.isNull():
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

class StrandType:
    Scaffold = 0
    Staple = 1

class Parity:
    Even = 0
    Odd = 1

class BreakType:
    Left5Prime = 0
    Left3Prime = 1
    Right5Prime = 2
    Right3Prime = 3
