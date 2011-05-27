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
from exceptions import NotImplementedError
import json
from .part import Part
from .virtualhelix import VirtualHelix
from .enum import LatticeType
from PyQt4.QtCore import pyqtSignal, QObject
from util import *
from heapq import *


class DNAPart(Part):
    def __init__(self, *args, **kwargs):
        if self.__class__ == DNAPart:
            raise NotImplementedError("This class is abstract. Perhaps you want DNAHoneycombPart.")
        super(DNAPart, self).__init__(self, *args, **kwargs)
        self._numberToVirtualHelix = {}  # number -> VirutalHelix
        self._coordToVirtualHelix = {}  # (row,col) -> VirtualHelix
        self._staples = []
        self._scaffolds = []
        self._name = kwargs.get('name', 'untitled')
        self._maxRow = kwargs.get('maxRow', 20)
        self._maxCol = kwargs.get('maxCol', 20)
        # ID assignment infra
        self.oddRecycleBin, self.evenRecycleBin = [], []
        self.reserveBin = set()
        self.highestUsedOdd = -1  # Used iff the recycle bin is empty and highestUsedOdd+2 is not in the reserve bin
        self.highestUsedEven = -2  # same
        # Transient state
        self._selection = set()
        # self._maxBase = 0  # Abstract (honeycomb is 42)
        # self._activeSlice = 0  # Abstract (honeycomb is 21)        
    
    def dimensions(self):
        return (self._maxRow, self._maxCol, self._maxBase)
    
    def numBases(self):
        return self.dimensions()[2]
    
    dimensionsWillChange = pyqtSignal()
    def setDimensions(self, newDim):
        self.dimensionsWillChange.emit(newDim)
        self._maxRow, self._maxCol, self._maxBase = newDim
        for n in self._numberToVirtualHelix:
            self._numberToVirtualHelix[n].setNumBases(self._maxBase)
        
    ############################# Archiving/Unarchiving #############################
    def simpleRep(self, encoder):
        """
        Provides a representation of the receiver in terms of simple
        (container,atomic) classes and other objects implementing simpleRep
        """
        ret = {'.class': "DNAPart"}
        ret['virtualHelices'] = self._virtualHelices
        ret['name'] = self._name
        ret['staples'] = self._staples
        ret['scaffolds'] = self._scaffolds
        return ret
    
    @classmethod
    def fromSimpleRep(cls, rep):
        ret = DNAPart()
        ret._virtualHelices = rep['virtualHelices']
        ret._name = rep['name']
        ret._staples = rep['staples']
        ret._scaffolds = rep['scaffolds']
        return ret
    
    ############################# VirtualHelix CRUD #############################
    # Take note: vhrefs are the shiny new way to talk to dnapart about its constituent
    # virtualhelices. Wherever you see f(...,vhref,...) you can
    # f(...,27,...)         use the virtualhelix's id number
    # f(...,vh,...)         use an actual virtualhelix
    # f(...,(1,42),...)     use the coordinate representation of its position
    def getVirtualHelix(self, vhref, returnNoneIfAbsent=True):
        """A vhref is the number of a virtual helix, the (row, col) of a virtual helix,
        or the virtual helix itself. For conveniece, CRUD should now work with any of them."""
        vh = None
        if type(vhref) in (int, long):
            vh = self._numberToVirtualHelix.get(vhref, None)
        elif type(vhref) in (tuple, list):
            vh = self._coordToVirtualHelix.get(vhref, None)
        else:
            vh = vhref
        if not isinstance(vh, VirtualHelix):
            if returnNoneIfAbsent:
                return None
            else:
                raise IndexError("Couldn't find the virtual helix in part %s referenced by index %s"%(self, vhref))
        return vh

    helixAdded = pyqtSignal(object)
    def addVirtualHelixAt(self, coords):
        """Adds a new VirtualHelix to the part in response to user input and
        adds slicehelix as an observer."""
        row, col = coords
        newID = self.reserveHelixIDNumber(parityEven=self.coordinateParityEven(coords))
        vhelix = VirtualHelix(part=self,
                              row=row,\
                              col=col,\
                              idnum=newID,\
                              numBases=self.dimensions()[2])
        self._numberToVirtualHelix[newID] = vhelix
        self._coordToVirtualHelix[(row, col)] = vhelix
        self.helixAdded.emit(vhelix)
        return vhelix

    helixWillBeRemoved = pyqtSignal(object)
    def removeVirtualHelix(self, vhref, returnFalseIfAbsent=False):
        """Called by SliceHelix.removeVirtualHelix() to update data."""
        vh = self.getVirtualHelix(vhref, returnNoneIfAbsent = True)
        if vh == None:
            if returnFalseIfAbsent:
                return False
            else:
                raise IndexError('Couldn\'t find virtual helix %s for removal'%str(vhref))
        self.helixWillBeRemoved.emit(vh)
        del self._coordToVirtualHelix[vh.coord()]
        del self._numberToVirtualHelix[vh.number()]
        self.recycleHelixIDNumber(vh.number())
        return True
    
    def renumberVirtualHelix(self, vhref, newNumber, returnFalseIfAbsent=False):
        vh = getVirtualHelix(vhref, returnNoneIfAbsent = True)
        if not vh:
            if returnFalseIfAbsent:
                return False
            else:
                raise IndexError('Couldn\'t find virtual helix %s for removal'%str(vhref))
        assert(not self.getVirtualHelix(self, newNumber))
        del self._numberToVirtualHelix[vh.number()]
        self._numberToVirtualHelix[newNumber] = vh
        vh._setNumber(newNumber)
        self.changed.emit()
        

    def getVirtualHelixCount(self):
        """docstring for getVirtualHelixList"""
        return len(self._numberToVirtualHelix)
    
    def getVirtualHelices(self):
        return [self._numberToVirtualHelix[n] for n in self._numberToVirtualHelix]
    
    ############################# VirtualHelix ID Number Management #############################
    # Used in both square, honeycomb lattices and so it's shared here
    def reserveHelixIDNumber(self, parityEven=True, num=None):
        """
        Reserves and returns a unique numerical label appropriate for a virtualhelix of
        a given parity. If a specific index is preferable (say, for undo/redo) it can be
        requested in num.
        """
        if num != None: # We are handling a request for a particular number
            assert num >= 0, long(num) == num
            if num in self.oddRecycleBin:
                self.oddRecycleBin.remove(num)
                heapify(self.oddRecycleBin)
                return num
            if num in self.evenRecycleBin:
                self.evenRecycleBin.remove(num)
                heapify(self.evenRecycleBin)
                return num
            self.reserveBin.add(num)
            return num
        # Just find any valid index (subject to parity constraints)
        if parityEven:
             if len(self.evenRecycleBin):
                 return heappop(self.evenRecycleBin)
             else:
                 while self.highestUsedEven + 2 in self.reserveBin:
                     self.highestUsedEven += 2
                 self.highestUsedEven += 2
                 return self.highestUsedEven
        else:
            if len(self.oddRecycleBin):
                return heappop(self.oddRecycleBin)
            else:
                while self.highestUsedOdd + 2 in self.reserveBin:
                    self.highestUsedOdd += 2
                self.highestUsedOdd += 2
                return self.highestUsedOdd

    def recycleHelixIDNumber(self, n):
        """
        The caller's contract is to ensure that n is not used in *any* helix
        at the time of the calling of this function (or afterwards, unless
        reserveLabelForHelix returns the label again)"""
        if n % 2 == 0:
            heappush(self.evenRecycleBin,n)
        else:
            heappush(self.oddRecycleBin,n)

    ############################# Transient State (doesn't get saved) #############################    
    def selection(self):
        """The set of helices that has been clicked or shift-clicked in
        the slice view. @todo 1) implement this 2) make the selected 
        helices more prominent in the path view (this would allow one 
        to deal with lots and lots of helices)"""
        return self._selection
    
    selectionWillChange = pyqtSignal(object)
    def setSelection(self, newSelection):
        ns = set(newSelection)
        self.selectionWillChange.emit(ns)
        self._selection = ns
    
    def activeSlice(self):
        """The active slice is the index of the slice selected by the
        vertical slider in the path view"""
        return self._activeSlice
    
    activeSliceWillChange = pyqtSignal(object)
    def setActiveSlice(self, newSliceIndex):
        ni = clamp(newSliceIndex, 0, self.dimensions()[2]-1)
        if self._activeSlice == ni:
            return
        self.activeSliceWillChange.emit(ni)
        self._activeSlice = ni
    