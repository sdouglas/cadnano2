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

from exceptions import KeyError
from heapq import heapify, heappush, heappop
from itertools import product, izip
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

    Parts are always parented to the document.
    Parts know about their oligos, and the internal geometry of a part
    Copying a part recursively copies all elements in a part:
        VirtualHelices, Strands, etc

    PartInstances are parented to either the document or an assembly
    PartInstances know global position of the part
    Copying a PartInstance only creates a new PartInstance with the same
    Part(), with a mutable parent and position field.
    """

    _step = 21  # this is the period of the part lattice
    _radius = 1.125 # in nanometer

    def __init__(self, *args, **kwargs):
        """
        Sets the paernt document, sets bounds for part dimensions, and sets up
        bookkeeping for partInstances, Oligos, VirtualHelix's, and helix ID
        number assignment.
        """
        if self.__class__ == Part:
            e = "This class is abstract. Perhaps you want HoneycombPart."
            raise NotImplementedError(e)
        self._document = kwargs.get('document', None)
        super(Part, self).__init__(parent=self._document)
        # Data structure
        self._partInstances = []    # This is a list of ObjectInstances
        self._oligos = {}
        self._virtualHelixHash = {}
        # Dimensions
        self._maxRow = 50
        self._maxCol = 50
        self._minBase = 0
        self._maxBase = 2*self._step-1
        # ID assignment
        self.oddRecycleBin, self.evenRecycleBin = [], []
        self.reserveBin = set()
        self._highestUsedOdd = -1  # Used iff the recycle bin is empty and highestUsedOdd+2 is not in the reserve bin
        self._highestUsedEven = -2  # same
        
        self._activeBaseIndex = self._step
        self._activeVirtualHelix = None
    # end def

    ### SIGNALS ###
    partActiveSliceIndexSignal = pyqtSignal(QObject, int)  # self, index
    partActiveSliceResizeSignal = pyqtSignal(QObject)      # self
    partDestroyedSignal = pyqtSignal(QObject)              # self
    partInstanceAddedSignal = pyqtSignal(QObject)          # self
    partNeedsFittingToViewSignal = pyqtSignal(QObject)     # virtualhelix
    partParentChangedSignal = pyqtSignal(QObject)          # self
    partRemovedSignal = pyqtSignal(QObject)                # self
    partSequenceClearedSignal = pyqtSignal(QObject)        # self
    partVirtualHelixAddedSignal = pyqtSignal(QObject)      # virtualhelix
    partVirtualHelixChangedSignal = pyqtSignal(QObject)    # coords (for a renumber)
    
    # for updating the Slice View displayed helices
    partStrandChangedSignal = pyqtSignal(QObject)           # virtualHelix
    
    # Part, VirtualHelixFrom, StrandType, index, VirtualHelixTo, StrandType, index
    partXOverAddedSignal = pyqtSignal(QObject, QObject, int, int, QObject, int, int)
    
    # Part, VirtualHelixFrom, StrandType, index, VirtualHelixTo, StrandType, index
    partXOverRemovedSignal = pyqtSignal(QObject, QObject, int, int, QObject, int, int)
    ### SLOTS ###

    ### ACCESSORS ###
    def undoStack(self):
        return self._document.undoStack()
    # end def

    def document(self):
        return self._document
    # end def

    def setDocument(self, document):
        self._document = document
    # end def

    def oligos(self):
        return self._oligos

    def subStepSize(self):
        """Note: _subStepSize is defined in subclasses."""
        return self._subStepSize


    ### PUBLIC METHODS FOR QUERYING THE MODEL ###
    def activeBaseIndex(self):
        return self._activeBaseIndex
    # end def

    def activeVirtualHelix(self):
         return self._activeVirtualHelix
     # end def

    def setActiveVirtualHelix(self, virtualHelix):
        self._activeVirtualHelix = virtualHelix
        self.partStrandChangedSignal.emit(virtualHelix)
    # end def
    
    def dimensions(self):
        """Returns a tuple of the max X and maxY coordinates of the lattice."""
        return self.latticeCoordToPositionXY(self._maxRow, self._maxCol)
    # end def

    def isEvenParity(self, row, column):
        """Should be overridden when subclassing."""
        raise NotImplementedError
    # end def

    def hasVirtualHelixAtCoord(self, coord):
        return coord in self._virtualHelixHash
    # end def

    def radius(self):
        return self._radius
    # end def

    def getVirtualHelices(self):
        """yield an iterator to the virtualHelix references in the part"""
        return  self._virtualHelixHash.itervalues()
    # end def

    def maxBaseIdx(self):
        return self._maxBase
    # end def

    def minBaseIdx(self):
        return self._minBase
    # end def

    def virtualHelixAtCoord(self, coord):
        """
        Looks for a virtualHelix at the coordinate, coord = (row, colum)
        if it exists it is returned, else None is returned
        """
        try:
            return self._virtualHelixHash[coord]
        except:
            return None
    # end def

    ### PUBLIC METHODS FOR EDITING THE MODEL ###
    def addOligo(self, oligo):
        self._oligos[oligo] = True
    # end def

    def createVirtualHelix(self, row, col, useUndoStack=True):
        c = Part.CreateVirtualHelixCommand(self, row, col)
        util._execCommandList(self, [c], desc="Add VirtualHelix", \
                                                useUndoStack=useUndoStack)
    # end def
    
    def createSimpleXover(fromVirtualHelix, toVirtualHelix, \
                                    strandType, idx, useUndoStack=True):
        fromSS = fromVirtualHelix.getStrandSetByType(strandType)
        toSS = toVirtualHelix.getStrandSetByType(strandType)
        fromStrand = fromSS.getStrand(idx)
        toStrand = toSS.getStrand(idx)
        if fromStrand.idx3Prime() == idx:
            strand3p = fromStrand
            strand5p = toStrand
        else:
            strand5p = fromStrand
            strand3p = toStrand
        c = Part.CreateXoverCommand(self, self, strand3p, idx, strand5p, idx)
        util._execCommandList(self, [c], desc="Create Xover", \
                                                useUndoStack=useUndoStack)
    # end def
    
    # end def
    def createXover(self, vh):
        """
        1. fnd strands
        """
        pass
    # end def

    def destroy(self):
        self.setParent(None)
        self.deleteLater()  # QObject also emits a destroyed() Signal
    # end def

    def generatorFullLattice(self):
        """
        Returns a generator that yields the row, column lattice points to draw
        relative to the part origin.
        """
        return product(range(self._maxRow), range(self._maxCol))
    # end def

    def generatorSpatialLattice(self, scaleFactor=1.0):
        """
        Returns a generator that yields the XY spatial lattice points to draw
        relative to the part origin.
        """
        # nested for loop in one line
        latticeCoordToPositionXY = self.latticeCoordToPositionXY
        for latticeCoord in product(range(self._maxRow), range(self._maxCol)):
            row, col = latticeCoord
            x, y = latticeCoordToPositionXY(row, col, scaleFactor)
            yield x, y, row, col
    # end def

    def latticeCoordToPositionXY(self, row, col, scaleFactor=1.0):
        """
        Returns a tuple of the (x,y) position for a given lattice row and
        column.

        Note: The x,y position is the upperLeftCorner for the given
        coordinate, and relative to the part instance.
        """
        raise NotImplementedError  # To be implemented by Part subclass
    # end def

    def positionToCoord(self, x, y, scaleFactor=1.0):
        """
        Returns a tuple (row, column) lattice coordinate for a given
        x and y position that is within +/- 0.5 of a true valid lattice
        position.

        Note: mapping should account for int-to-float rounding errors.
        x,y is relative to the Part Instance Position.
        """
        raise NotImplementedError  # To be implemented by Part subclass
    # end def

    def newPart(self):
        return Part(self._document)
    # end def

    def removeOligo(self, oligo):
        self._oligos[oligo] = False
        del self._oligos[oligo]
    # end def

    def removeVirtualHelix(self, virtualHelix=None, coord=None, useUndoStack=True):
        """
        Removes a VirtualHelix from the model. Accepts a reference to the 
        VirtualHelix, or a (row,col) lattice coordinate to perform a lookup.
        """
        if virtualHelix and self.hasVirtualHelixAtCoord(virtualHelix.coord()):
            coord = virtualHelix.coord()
        elif not virtualHelix and coord:
            if self.hasVirtualHelixAtCoord(coord):
                virtualHelix = self.virtualHelixAtCoord(coord)
            else:
                e = "virtualhelix not found by coord lookup"
                raise KeyError(e)
        else:
            e = "Cannot remove virtualhelix: No ref or coord provided."
            raise KeyError(e)
        c = Part.RemoveVirtualHelixCommand(self, virtualHelix)
        util._execCommandList(self, [c], desc="Remove VirtualHelix", \
                                                    useUndoStack=useUndoStack)
    # end def

    def setActiveBaseIndex(self, idx):
        self._activeBaseIndex = idx
        self.partActiveSliceIndexSignal.emit(self, idx)
    # end def

    ### PRIVATE SUPPORT METHODS ###
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

    def _reserveHelixIDNumber(self, parityEven=True, requestedIDnum=None):
        """
        Reserves and returns a unique numerical label appropriate for a
        virtualhelix of a given parity. If a specific index is preferable
        (say, for undo/redo) it can be requested in num.
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
                     while self._highestUsedEven + 2 in self.reserveBin:
                         self._highestUsedEven += 2
                     self._highestUsedEven += 2
                     return self._highestUsedEven
            else:
                if len(self.oddRecycleBin):
                    return heappop(self.oddRecycleBin)
                else:
                    while self._highestUsedOdd + 2 in self.reserveBin:
                        self._highestUsedOdd += 2
                    self._highestUsedOdd += 2
                    return self._highestUsedOdd
        # end else
    # end def

    def _recycleHelixIDNumber(self, n):
        """
        The caller's contract is to ensure that n is not used in *any* helix
        at the time of the calling of this function (or afterwards, unless
        reserveLabelForHelix returns the label again).
        """
        if n % 2 == 0:
            heappush(self.evenRecycleBin,n)
        else:
            heappush(self.oddRecycleBin,n)
    # end def


    ### PUBLIC SUPPORT METHODS ###
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
    
    def getVirtualHelixNeighbors(self, virtualHelix):
        """
        returns the list of neighboring virtualHelices based on parity of an
        input virtualHelix
        
        If a potential neighbor doesn't exist, None is returned in it's place
        """
        neighbors = []
        vh = virtualHelix
        if vh == None:
            return neighbors

        # assign the method to a a local variable
        getVH = self.virtualHelixAtCoord
        # get the vh's row and column r,c 
        (r,c) = vh.coords()
        
        if self.isEvenParity(r, c):
            neighbors.append(getVH((r,c+1)))  # p0 neighbor (p0 is a direction)
            neighbors.append(getVH((r-1,c)))  # p1 neighbor
            neighbors.append(getVH((r,c-1)))  # p2 neighbor
        else:
            neighbors.append(getVH((r,c-1)))  # p0 neighbor (p0 is a direction)
            neighbors.append(getVH((r+1,c)))  # p1 neighbor
            neighbors.append(getVH((r,c+1)))  # p2 neighbor
        return neighbors  # Note: the order and presence of Nones is important
        # If you need the indices of available directions use range(0,len(neighbors))
    # end def
    
    def areVirtualHelicesNeighbors(self, virtualHelixA, virtualHelixB):
        """
        returns True or False
        """
        return virtualHelixB in self.getVirtualHelixNeighbors(virtualHelixA) or \
            virtualHelixA == virtualHelixB
    # end def
    
    def potentialCrossoverList(self, virtualHelix):
        """
        Returns a list of tuples 
        (neighborVirtualHelix, index, strandType, isLowIdx)
        where 
        
        neighborVirtualHelix is a virtualHelix neighbor of the arg virtualHelix
        
        index is the index where a potential Xover might occur
        
        strandType is from the enum (StrandType.Scaffold, StrandType.Staple)
        
        isLowIdx is whether or not it's the at the low index (left in the Path view) 
        of a potential Xover site
        """
        vh = virtualHelix
        ret = []  # LUT = Look Up Table
        part = self
        # these are the list of crossover points simplified
        # they depend on whether the strandType is scaffold or staple
        # create a list of crossover points for each neighbor of the form
        # [(_scafL[i], _scafH[i], _stapL[i], _stapH[i]), ...]
        lutsNeighbor = list(izip(part._scafL, part._scafH, part._stapL, part._stapH))
        
        sTs = (StrandType.Scaffold, StrandType.Staple)
        numBases = part.maxBaseIdx()
        
        # create a range for the helical length dimension of the Part, 
        # incrementing by the lattice step size.
        baseRange = range(0, numBases, part._step)

        fromStrandSets = vh.getStrandSets()
        neighbors = self.getVirtualHelixNeighbors(vh)

        # print neighbors, lutsNeighbor
        for neighbor, lut in izip(neighbors, lutsNeighbor):
            if not neighbor:
                continue
                
            # now arrange again for iteration
            # (_scafL[i], _scafH[i]), (_stapL[i], _stapH[i]) )
            # so we can pair by StrandType
            lutScaf = lut[0:2]
            lutStap = lut[2:4]
            lut = (lutScaf, lutStap)

            toStrandSets = neighbor.getStrandSets()
            for fromSS, toSS, pts, st in izip(fromStrandSets, toStrandSets, lut, sTs):
                # test each period of each lattice for each StrandType
                for pt, isLowIdx in izip(pts, (True, False)):
                    for i, j in product(baseRange, pt):
                        index = i + j
                        if index < numBases:
                            if fromSS.hasNoStrandAtOrNoXover(index) and \
                                    toSS.hasNoStrandAtOrNoXover(index):
                                ret.append((neighbor, index, st, isLowIdx))
                            # end if
                        # end if
                    # end for
                # end for
            # end for
        # end for
        return ret
    # end def
    
    def possibleXoverAt(self, fromVirtualHelix, toVirtualHelix, strandType, idx):
        fromSS = fromVirtualHelix.getStrandSetByType(strandType)
        toSS = toVirtualHelix.getStrandSetByType(strandType)
        return fromSS.hasStrandAtAndNoXover(idx) and \
                toSS.hasStrandAtAndNoXover(idx)
    # end def

    ### COMMANDS ###
    class CreateVirtualHelixCommand(QUndoCommand):
        """Inserts strandToAdd into strandList at index idx."""
        def __init__(self, part, row, col):
            super(Part.CreateVirtualHelixCommand, self).__init__()
            self._part = part
            self._parityEven = part.isEvenParity(row,col)
            idNum = part._reserveHelixIDNumber(self._parityEven, requestedIDnum=None)
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
                part._reserveHelixIDNumber(self._parityEven, requestedIDnum=idNum)
            # end if
            part.partVirtualHelixAddedSignal.emit(vh)
            part.partActiveSliceResizeSignal.emit(part)
        # end def

        def undo(self):
            vh = self._vhelix
            part = self._part
            idNum = self._idNum
            part._removeVirtualHelix(vh)
            part._recycleHelixIDNumber(idNum)
            # clear out part references
            vh.setPart(None)
            vh.setNumber(None)
            vh.virtualHelixRemovedSignal.emit(vh)
            part.partActiveSliceResizeSignal.emit(part)
        # end def
    # end class

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
            part._recycleHelixIDNumber(idNum)
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
                part._reserveHelixIDNumber(self._parityEven, requestedIDnum=idNum)
            part.partVirtualHelixAddedSignal.emit(vh)
            part.partActiveSliceResizeSignal.emit(part)
        # end def
    # end class
    
    class CreateXoverCommand(QUndoCommand):
        """
        Creates a Xover from the 3 prime strand to the 5 prime strand
        this needs to 
        1. preserve the old oligo of the 5prime strand
        2. install the crossover
        3. apply the 3 prime strand oligo to the 5 prime strand
        """
        def __init__(self, part, strand3p, idx3p, strand5p, idx5p):
            super(Part.CreateXoverCommand, self).__init__()
            self._part = part
            self._strand3p = strand3p
            self._idx3p = idx3p
            self._strand5p = strand5p
            self._idx5p = idx5p
            
            self._oldOligo5p = strand5p.oligo()
        # end def

        def redo(self):
            part = self._part
            strand3p = self._strand3p
            idx3p = self._idx3p
            strand5p = self._strand5p
            idx5p = self._idx5p
            olg = strand3p.oligo()
            
            # 2. install the Xover 
            strand3p.set3pConnection(strand5p)
            strand5p.set5pConnection(strand3p)
            
            # 3. apply the 3 prime strand oligo to the 5 prime strand
            for strand in strand5p.generator3pStrand():
                Strand.setOligo(strand, olg)  # emits strandHasNewOligoSignal
            
            ss3 = strand3p.strandSet()
            vh3p = ss3.virtualHelix()
            st3p = ss3.strandType()
            ss5 = strand5p.strandSet()
            vh5p = ss5.virtualHelix()
            st5p = ss5.strandType()
            part.partXOverAddedSignal.emit(part, \
                                        vh3p, st3p, idx3p, \
                                        vh5p, st5p, idx5p,)
        # end def

        def undo(self):
            part = self._part
            strand3p = self._strand3p
            idx3p = self._idx3p
            strand5p = self._strand5p
            idx5p = self._idx5p
            olg = self._oldOligo5p
            
            # 2. uninstall the Xover 
            strand3p.set3pConnection(None)
            strand5p.set5pConnection(None)
            
            # 3. apply the old 5 prime strand oligo to the 5 prime strand
            for strand in strand5p.generator3pStrand():
                Strand.setOligo(strand, olg)  # emits strandHasNewOligoSignal
            
            ss3 = strand3p.strandSet()
            vh3p = ss3.virtualHelix()
            st3p = ss3.strandType()
            ss5 = strand5p.strandSet()
            vh5p = ss5.virtualHelix()
            st5p = ss5.strandType()
            part.partXOverRemovedSignal.emit(part, \
                                        vh3p, st3p, idx3p, \
                                        vh5p, st5p, idx5p,)
        # end def
    # end class