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

from heapq import heapify, heappush
from itertools import product
from model.enum import StrandType
from model.virtualhelix import VirtualHelix
import util

util.qtWrapImport('QtCore', globals(), ['pyqtSignal', 'QObject'])
util.qtWrapImport('QtGui', globals(), ['QUndoCommand'])


class Part(QObject):
    """
    A Part is a group of VirtualHelix items that are on the same lattice.
    Parts are the model component that most directly corresponds to a
    DNA origami design.
    """

    _step = 21  # this is the period of the part lattice
    _radius = 1.125 # in nanometer
    
    def __init__(self, *args, **kwargs):
        """
        Parts are always parented to the document.
        Parts know about their oligos, and the internal geometry of a part
        Copying a part recursively copies all elements in a part:
            VirtualHelices, Strands, etc

        PartInstances are parented to either the document or an assembly
        PartInstances know global position of the part
        Copying a PartInstance only creates a new PartInstance with the same
        Part(), with a mutable parent and position field.
        """
        if self.__class__ == Part:
            raise NotImplementedError("This class is abstract. Perhaps you want HoneycombPart.")
        self._document = kwargs.get('document', None)
        super(Part, self).__init__(parent=self._document)
        self._partInstances = []    # This is a list of ObjectInstances
        self._oligos = {}
        self._virtualHelixHash = {}   # should this be a list or a dictionary?  I think dictionary
        
        self._maxRow = 50
        self._maxCol = 50
        self._maxBase = 2*self._step
        self._minBase = 0
        
        # ID assignment infra
        self.oddRecycleBin, self.evenRecycleBin = [], []
        self.reserveBin = set()
        self.highestUsedOdd = -1  # Used iff the recycle bin is empty and highestUsedOdd+2 is not in the reserve bin
        self.highestUsedEven = -2  # same
        
        self._activeBaseIndex = self._step
    # end def

    ### SIGNALS ###
    partParentChangedSignal = pyqtSignal(QObject)  # self
    partInstanceAddedSignal = pyqtSignal(QObject)  # self
    partRemovedSignal = pyqtSignal(QObject)  # self
    partDestroyedSignal = pyqtSignal(QObject)  # self
    partSequenceClearedSignal = pyqtSignal(QObject)  # self
    partNeedsFittingToViewSignal = pyqtSignal(QObject)  # virtualhelix
    partVirtualHelixAddedSignal = pyqtSignal(QObject)  # virtualhelix
    
    partVirtualHelixChangedSignal = pyqtSignal(QObject) # emit the coordinates
    # virtualHelixAtCoordsChangedSignal = pyqtSignal(int, int) # emit the coordinates
    
    partActiveSliceResizeSignal = pyqtSignal(QObject)    # self
    partActiveSliceIndexSignal = pyqtSignal(QObject, int)   # self, index

    ### SLOTS ###

    ### METHODS ###
    def undoStack(self):
        return self._document.undoStack()

    def destroy(self):
        # QObject also emits a destroyed() Signal
        self.setParent(None)
        self.deleteLater()
    # end def

    def document(self):
        return self._document

    def setDocument(self, document):
        """docstring for setDocument"""
        self._document = document
    # end def
    
    def radius(self):
        return self._radius
    # end def

    def oligos(self):
        return self._oligos

    def addOligo(self, oligo):
        self._oligos[oligo] = True

    def removeOligo(self, oligo):
        self._oligos[oligo] = False
        self.destroyOligo(oligo)

    def destroyOligo(self, oligo):
        del self._oligos[oligo]
    
    def isEvenParity(self, row, column):
        """
        To be implemented by Part subclass, pass
        """
        raise NotImplementedError
    # end def
    
    def activeBaseIndex(self):
        return self._activeBaseIndex
    # end def
    
    def setActiveBaseIndex(self, idx):
        self._activeBaseIndex = idx
        self.partActiveSliceIndexSignal.emit(self, idx)
    # end def
    
    def minBaseIdx(self):
        return self._minBase
    # end def
    
    def maxBaseIdx(self):
        return self._maxBase
    # end def
    
    def maxBaseIndices(self):
        """Return the latice indice bounds relative to the origin."""
        return self._minBase, self._maxBase
    # end def
    
    def generatorSpatialLattice(self, scaleFactor=1.0):
        """
        returns a generator that yields the XY spatial lattice points to draw
        
        relative to the part origin
        """
        # nested for loop in one line
        latticeToSpatial = self.latticeToSpatial
        for latticeCoord in product(range(self._maxRow), range(self._maxCol)):
            row, col = latticeCoord
            x, y = latticeToSpatial(row, col, scaleFactor)
            yield x, y, row, col
        # latticeCoordGen = product(range(self._maxRow), range(self._maxCol))
        # return starmap(self.latticeToSpatial, \
        #                 izip( latticeCoordGen, repeat(scaleFactor)))
    # end def
    
    def generatorFullLattice(self):
        """
        returns a generator that yields the row, column lattice points to draw
        
        relative to the part origin
        """
        return product(range(self._maxRow), range(self._maxCol))
    # end def
    
    def dimensions(self):
        """
        return a tuple of the max X and maxY coordinates of the lattice
        """
        return self.latticeToSpatial(self._maxRow, self._maxCol)
    # end def

    def latticeToSpatial(self, row, col, scaleFactor=1.0):
        """
        To be implemented by Part subclass
        returns a tuple of the XY spatial Coordinates mapping from the lattice
        coordinates, relative to the Part Instance Position

        returns the upperLeftCorner for a given tuple of lattice Coordinates
        """
        raise NotImplementedError
    # end def

    def spatialToLattice(self, x, y, scaleFactor=1.0):
        """
        returns a tuple of the lattice coordinates mapping from the
        XY spatial Coordinates
        must account for rounding errors converting ints to floats

        spatialCoord is relative to the Part Instance Position

        Assumes spatialCoord is a with +/- 0.5 of a true valid 
        lattice position
        """
        raise NotImplementedError
    # end def

    def createVirtualHelix(self, row, col, useUndoStack=True):
        c = Part.CreateVirtualHelixCommand(self, row, col)
        util._execCommandList(self, [c], desc="Add VirtualHelix", \
                                                useUndoStack=useUndoStack)
    # end def

    def removeVirtualHelix(self, virtualHelix=None, coord=None, useUndoStack=True):
        """
        takes a virtualHelix or coord to remove a virtual helix
        """
        if virtualHelix and self.hasVirtualHelixAtCoord(virtualHelix.coord()):
            coord = virtualHelix.coord()
        elif not virtualHelix and coord:
            if self.hasVirtualHelixAtCoord(coord):
                virtualHelix = self.virtualHelixAtCoord(coord)
            else:
                raise Exception
        else:
            raise Exception 
        c = Part.RemoveVirtualHelixCommand(self, virtualHelix)
        util._execCommandList(self, [c], desc="Remove VirtualHelix", \
                                                    useUndoStack=useUndoStack)
    # end def

    def getVirtualHelices(self):
        """
        yield an iterator to the virtualHelix references in the part
        """
        return  self._virtualHelixHash.itervalues()
    # def 

    def virtualHelixAtCoord(self, coord):
        self._virtualHelixHash[coord]
    # end def

    def hasVirtualHelixAtCoord(self, coord):
        return coord in self._virtualHelixHash
    # end def

    def _addVirtualHelix(self, virtualHelix):
        """
        private method for adding a virtualHelix to the Parts data structure
        of virtualHelix references
        """
        self._virtualHelixHash[virtualHelix.coords()] = virtualHelix
    # end def

    def _removeVirtualHelix(self, virtualHelix):
        """
        private method for adding a virtualHelix to the Parts data structure
        of virtualHelix references
        """
        del self._virtualHelixHash[virtualHelix.coords()]
    # end def

    def subStepSize(self):
        """docstring for subStepSize"""
        return self._subStepSize

    def newPart(self):
        """
        reimplement this method for each type of Part
        """
        return Part(self._document)
    # end def

    def shallowCopy(self):
        part = self.newPart()
        part._virtualHelices = dict(self._virtualHelices)
        part._oligos = dict(self._oligos)
        part._maxBaseIdx = self._maxBaseIdx
        part._partInstances = list(self._partInstances)
        return part
    # end def

    def deepCopy(self):
        """
        1) Create a new part
        2) copy the VirtualHelices
        3) Now you need to map the ORIGINALs Oligos onto the COPY's Oligos
        To do this you can for each Oligo in the ORIGINAL
            a) get the strand5p() of the ORIGINAL
            b) get the corresponding strand5p() in the COPY based on
                i) lookup the hash idNum of the ORIGINAL strand5p() VirtualHelix
                ii) get the StrandSet() that you created in Step 2 for the 
                StrandType of the original using the hash idNum
        """
        # 1) new part
        part = self.newPart()
        for key, vhelix in self._virtualHelices:
            # 2) Copy VirtualHelix 
            part._virtualHelices[key] = vhelix.deepCopy(part)
        # end for
        # 3) Copy oligos
        for oligo, val in self._oligos:
            strandGenerator = oligo.strand5p().generator3pStrand()
            strandType = oligo.strand5p().strandType()
            newOligo = oligo.deepCopy(part)
            lastStrand = None
            for strand in strandGenerator:
                idNum = strand.virtualHelix().number()
                newVHelix = part._virtualHelices[idNum]
                newStrandSet = newVHelix().getStrandSetByType(strandType)
                newStrand = strand.deepCopy(newStrandSet, newOligo)
                if lastStrand:
                    lastStrand.set3pConnection(newStrand)
                else: 
                    # set the first condition
                    newOligo.setStrand5p(newStrand)
                newStrand.set5pConnection(lastStrand)
                newStrandSet.addStrand(newStrand)
                lastStrand = newStrand
            # end for
            # check loop condition
            if oligo.isLoop():
                s5p = newOligo.strand5p()
                lastStrand.set3pconnection(s5p)
                s5p.set5pconnection(lastStrand)
            # add to part
            oligo.add()
        # end for
        return part
    # end def

    ### COMMANDS ###
    class CreateVirtualHelixCommand(QUndoCommand):
        """Inserts strandToAdd into strandList at index idx."""
        def __init__(self, part, row, col):
            super(Part.CreateVirtualHelixCommand, self).__init__()
            self._part = part
            self._parityEven = part.isEvenParity(row,col)
            idNum = part.reserveHelixIDNumber(self._parityEven, requestedIDnum=None)
            self._vhelix = VirtualHelix(part, row, col, idNum)
            self._idNum = idNum
        # end def

        def redo(self):
            vh = self._vhelix
            part = self._part
            idNum = self._idNum
            vh.setPart(part)
            part._addVirtualHelix(vh)
            vh.setNumber(idNum)
            if not vh.number():
                part.reserveHelixIDNumber(self._parityEven, requestedIDnum=idNum)
            # end if
            part.partVirtualHelixAddedSignal.emit(vh)
            part.partActiveSliceResizeSignal.emit(part)
        # end def

        def undo(self):
            vh = self._vhelix
            part = self._part
            idNum = self._idNum
            part._removeVirtualHelix(vh)
            part.recycleHelixIDNumber(idNum)
            # clear out part references
            vh.setPart(None)
            vh.setNumber(None)
            vh.virtualHelixRemovedSignal.emit(vh)
            part.partActiveSliceResizeSignal.emit(part)
        # end def
    # end class

    ### COMMANDS ###
    class RemoveVirtualHelixCommand(QUndoCommand):
        """Inserts strandToAdd into strandList at index idx."""
        def __init__(self, part, virtualHelix):
            super(Part.RemoveVirtualHelixCommand, self).__init__()
            self._part = part
            self._vhelix = virtualHelix
            self._idNum = virtualHelix.number()
            # is the number even or odd?  Assumes a valid idNum, row,col combo
            self._parityEven = (self._idNum % 2) == 0
        # end def

        def redo(self):
            vh = self._vhelix
            part = self._part
            idNum = self._idNum
            part._removeVirtualHelix(vh)
            part.recycleHelixIDNumber(idNum)
            # clear out part references
            vh.setPart(None)
            vh.setNumber(None)
            vh.virtualhelixRemovedSignal.emit(vh)
            part.partActiveSliceResizeSignal.emit(part)
        # end def

        def undo(self):
            vh = self._vhelix
            part = self._part
            idNum = self._idNum
            vh.setPart(part)
            part._addVirtualHelix(vh)
            vh.setNumber(idNum)
            if not vh.number():
                part.reserveHelixIDNumber(self._parityEven, requestedIDnum=idNum)
            part.partVirtualHelixAddedSignal.emit(vh)
            part.partActiveSliceResizeSignal.emit(part)
        # end def
    # end class

    ############################# VirtualHelix ID Number Management #############################
    # Used in both square, honeycomb lattices and so it's shared here
    def reserveHelixIDNumber(self, parityEven=True, requestedIDnum=None):
        """
        Reserves and returns a unique numerical label appropriate for a virtualhelix of
        a given parity. If a specific index is preferable (say, for undo/redo) it can be
        requested in num.
        """
        num = requestedIDnum
        if num != None: # We are handling a request for a particular number
            assert num >= 0, long(num) == num
            # assert not num in self._numberToVirtualHelix
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
        # end if
        else:
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
        # end else
    # end def

    def recycleHelixIDNumber(self, n):
        """
        The caller's contract is to ensure that n is not used in *any* helix
        at the time of the calling of this function (or afterwards, unless
        reserveLabelForHelix returns the label again)"""
        if n % 2 == 0:
            heappush(self.evenRecycleBin,n)
        else:
            heappush(self.oddRecycleBin,n)
    # end def
    
    ### COMMANDS ###
    