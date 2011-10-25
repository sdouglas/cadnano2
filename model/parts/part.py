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
from collections import defaultdict
import random

from model.enum import StrandType
from model.virtualhelix import VirtualHelix
from model.strand import Strand
from model.strandset import StrandSet
from views import styles

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

    _step = 21  # this is the period (in bases) of the part lattice
    _radius = 1.125  # nanometers

    def __init__(self, *args, **kwargs):
        """
        Sets the parent document, sets bounds for part dimensions, and sets up
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
        self._insertions = defaultdict(dict)  # dictionary of insertions per virtualhelix
        self._oligos = {}
        self._virtualHelixHash = {}
        # Dimensions
        self._maxRow = 50  # subclass overrides based on prefs
        self._maxCol = 50
        self._minBase = 0
        self._maxBase = 2 * self._step - 1
        # ID assignment
        self.oddRecycleBin, self.evenRecycleBin = [], []
        self.reserveBin = set()
        self._highestUsedOdd = -1  # Used in _reserveHelixIDNumber
        self._highestUsedEven = -2  # same
        self._importedVHelixOrder = None
        # Runtime state
        self._activeBaseIndex = self._step
        self._activeVirtualHelix = None
    # end def

    def __repr__(self):
        clsName = self.__class__.__name__
        return "<%s %s>" % (clsName, str(id(self))[-4:])

    ### SIGNALS ###
    partActiveSliceIndexSignal = pyqtSignal(QObject, int)  # self, index
    partActiveSliceResizeSignal = pyqtSignal(QObject)      # self
    partDestroyedSignal = pyqtSignal(QObject)              # self
    partDimensionsChangedSignal = pyqtSignal(QObject)      # self
    partInstanceAddedSignal = pyqtSignal(QObject)          # self
    partParentChangedSignal = pyqtSignal(QObject)          # self
    partPreDecoratorSelectedSignal = pyqtSignal(int, int, int)  # row,col,idx
    partRemovedSignal = pyqtSignal(QObject)                # self
    partSequenceClearedSignal = pyqtSignal(QObject)        # self
    partStrandChangedSignal = pyqtSignal(QObject)          # virtualHelix
    partVirtualHelixAddedSignal = pyqtSignal(QObject)      # virtualhelix
    partVirtualHelixRenumberedSignal = pyqtSignal(tuple)   # coord
    partVirtualHelixResizedSignal = pyqtSignal(tuple)      # coord
    partVirtualHelicesReorderedSignal = pyqtSignal(list)   # list of coords

    ### SLOTS ###

    ### ACCESSORS ###
    def document(self):
        return self._document
    # end def

    def oligos(self):
        return self._oligos
    # end def

    def setDocument(self, document):
        self._document = document
    # end def

    def stepSize(self):
        return self._step
    # end def

    def subStepSize(self):
        """Note: _subStepSize is defined in subclasses."""
        return self._subStepSize
    # end def

    def undoStack(self):
        return self._document.undoStack()
    # end def

    ### PUBLIC METHODS FOR QUERYING THE MODEL ###
    def activeBaseIndex(self):
        return self._activeBaseIndex
    # end def

    def activeVirtualHelix(self):
         return self._activeVirtualHelix
     # end def

    def dimensions(self):
        """Returns a tuple of the max X and maxY coordinates of the lattice."""
        return self.latticeCoordToPositionXY(self._maxRow, self._maxCol)
    # end def

    def getStapleSequences(self):
        """getStapleSequences"""
        s = "Start,End,Sequence,Length,Color\n"
        for oligo in self._oligos:
            if oligo.strand5p().strandSet().isStaple():
                s = s + oligo.sequenceExport()
        return s

    def getVirtualHelices(self):
        """yield an iterator to the virtualHelix references in the part"""
        return self._virtualHelixHash.itervalues()
    # end def

    def indexOfRightmostNonemptyBase(self):
        """
        During reduction of the number of bases in a part, the first click
        removes empty bases from the right hand side of the part (red
        left-facing arrow). This method returns the new numBases that will
        effect that reduction.
        """
        ret = self._step-1
        for vh in self.getVirtualHelices():
            ret = max(ret, vh.indexOfRightmostNonemptyBase())
        print "part indexOfRightmostNonemptyBase", ret
        return ret
    # end def

    def insertions(self):
        """Return dictionary of insertions."""
        return self._insertions
    # end def

    def isEvenParity(self, row, column):
        """Should be overridden when subclassing."""
        raise NotImplementedError
    # end def

    def hasVirtualHelixAtCoord(self, coord):
        return coord in self._virtualHelixHash
    # end def

    def maxBaseIdx(self):
        return self._maxBase
    # end def

    def minBaseIdx(self):
        return self._minBase
    # end def

    def numberOfVirtualHelices(self):
        return len(self._virtualHelixHash)
    # end def

    def radius(self):
        return self._radius
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

    def autoStaple(self):
        """Autostaple does the following:
        1. Clear existing staple strands by iterating over each strand 
        and calling RemoveStrandCommand on each. The next strand to remove
        is always at index 0.
        2. Create strands that span regions where scaffold is present.
        3. 
        """
        util.beginSuperMacro(self, desc="Auto-Staple")

        cmds = []
        # clear existing staple strands
        for vh in self.getVirtualHelices():
            stapSS = vh.stapleStrandSet()
            for strand in stapSS:
                c = StrandSet.RemoveStrandCommand(stapSS, strand, 0)  # rm
                cmds.append(c)

        # create strands that span all bases where scaffold is present
        for vh in self.getVirtualHelices():
            segments = []
            scafSS = vh.scaffoldStrandSet()
            for strand in scafSS:
                lo, hi = strand.idxs()
                if len(segments) == 0:
                    segments.append([lo,hi])  # insert 1st strand
                elif segments[-1][1] == lo-1:
                    segments[-1][1] = hi  # extend
                else:
                    segments.append([lo,hi])  # insert another strand
            stapSS = vh.stapleStrandSet()
            for i in range(len(segments)):
                lo, hi = segments[i]
                c = StrandSet.CreateStrandCommand(stapSS, lo, hi, i)
                cmds.append(c)
        util.execCommandList(self, cmds, desc="Create staples")

        # split strands before installing xovers
        for vh in self.getVirtualHelices():
            stapSS = vh.stapleStrandSet()
            is5to3 = stapSS.isDrawn5to3()
            potentialXovers = self.potentialCrossoverList(vh)
            for neighborVh, idx, strandType, isLowIdx in potentialXovers:
                if strandType != StrandType.Staple:
                    continue
                if isLowIdx and is5to3:
                    strand = stapSS.getStrand(idx)
                    neighborSS = neighborVh.stapleStrandSet()
                    nStrand = neighborSS.getStrand(idx)
                    if strand == None or nStrand == None:
                        continue
                    # check for bases on both strands at [idx-1:idx+3]
                    if strand.lowIdx() < idx and strand.highIdx() > idx+1 and\
                       nStrand.lowIdx() < idx and nStrand.highIdx() > idx+1:
                        stapSS.splitStrand(strand, idx)
                        neighborSS.splitStrand(nStrand, idx+1)
                if not isLowIdx and not is5to3:
                    strand = stapSS.getStrand(idx)
                    neighborSS = neighborVh.stapleStrandSet()
                    nStrand = neighborSS.getStrand(idx)
                    if strand == None or nStrand == None:
                        continue
                    # check for bases on both strands at [idx-1:idx+3]
                    if strand.lowIdx() < idx-1 and strand.highIdx() > idx and\
                       nStrand.lowIdx() < idx-1 and nStrand.highIdx() > idx:
                        stapSS.splitStrand(strand, idx)
                        neighborSS.splitStrand(nStrand, idx-1)

        # create crossovers wherever possible (from strand5p only)
        for vh in self.getVirtualHelices():
            stapSS = vh.stapleStrandSet()
            is5to3 = stapSS.isDrawn5to3()
            potentialXovers = self.potentialCrossoverList(vh)
            for neighborVh, idx, strandType, isLowIdx in potentialXovers:
                if strandType != StrandType.Staple:
                    continue
                if (isLowIdx and is5to3) or (not isLowIdx and not is5to3):
                    strand = stapSS.getStrand(idx)
                    neighborSS = neighborVh.stapleStrandSet()
                    nStrand = neighborSS.getStrand(idx)
                    if strand == None or nStrand == None:
                        continue
                    self.createXover(strand, idx, nStrand, idx)
        # do all the commands
        util.endSuperMacro(self)

    def createVirtualHelix(self, row, col, useUndoStack=True):
        c = Part.CreateVirtualHelixCommand(self, row, col)
        util.execCommandList(self, [c], desc="Add VirtualHelix", \
                                                useUndoStack=useUndoStack)
    # end def

    def createXover(self, strand5p, idx5p, strand3p, idx3p, useUndoStack=True):
        # prexoveritem needs to store left or right, and determine
        # locally whether it is from or to
        # pass that info in here in and then do the breaks
        ss5p = strand5p.strandSet()
        ss3p = strand3p.strandSet()
        cmds = []
        util.execCommandList(self, cmds, desc="Create Xover", \
                                                useUndoStack=useUndoStack)
        if useUndoStack:
            self.undoStack().beginMacro("Create Xover")
        if ss5p.strandType() != ss3p.strandType():
            print "Failed xover on try 1"
            return
        if ss5p.isScaffold():
            cmds.append(strand5p.oligo().applySequenceCMD(None))
            cmds.append(strand3p.oligo().applySequenceCMD(None))
        if strand5p == strand3p:
            """
            This is a complicated case basically we need a truth table.
            1 strand becomes 1, 2 or 3 strands depending on where the xover is
            to.  1 and 2 strands happen when the xover is to 1 or more existing
            endpoints.  Since SplitCommand depends on a StrandSet index, we need
            to adjust this strandset index depending which direction the crossover is 
            going in.
            
            Below describes the 3 strand process
            1) Lookup the strands strandset index (ssIdx)
            1) Split attempted on the 3 prime strand, AKA 5prime endpoint of
            one of the new strands.  We have now created 2 strands, and the ssIdx
            is either the same as the first lookup, or one more than it depending 
            on which way the the strand is drawn (isDrawn5to3).  If a split occured
            the 5prime strand is definitely part of the 3prime strand created in this step
            2) Split is attempted on the resulting 2 strands.  There is 
            now 3 strands, and the final 3 prime strand may be one of the two new strands
            created in this step. Check it.
            3) Create the Xover
            """
            c = None
            # lookup the initial strandset index
            found, overlap, ssIdx3p = ss3p._findIndexOfRangeFor(strand3p)
            if strand3p.idx5Prime() == idx3p:  # yes, idx already matches
                temp5 = xoStrand3 = strand3p
            else:
                offset3p = -1 if ss3p.isDrawn5to3() else 1
                if ss3p.strandCanBeSplit(strand3p, idx3p+offset3p):
                    c = ss3p.SplitCommand(strand3p, idx3p+offset3p, ssIdx3p)
                    # cmds.append(c)
                    xoStrand3 = c._strandHigh if ss3p.isDrawn5to3() else c._strandLow
                    # adjust the target 5prime strand, always necessary if a split happens here
                    if idx5p > idx3p and ss3p.isDrawn5to3():
                        temp5 = xoStrand3 
                    elif idx5p < idx3p and not ss3p.isDrawn5to3():
                        temp5 = xoStrand3
                    else:
                        temp5 = c._strandLow if ss3p.isDrawn5to3() else c._strandHigh
                    if useUndoStack:
                        self.undoStack().push(c)
                    else:
                        c.redo()
                else:
                    print "Failed xover on try 2"
                    return
                # end if
            if xoStrand3.idx3Prime() == idx5p:
                xoStrand5 = temp5
            else:
                ssIdx5p = ssIdx3p
                # if the strand was split for the strand3p, then we need to adjust the strandset index
                if c:
                    # the insertion index into the set is increases
                    if ss3p.isDrawn5to3():
                        ssIdx5p = ssIdx3p + 1 if idx5p > idx3p else ssIdx3p
                    else:
                        ssIdx5p =  ssIdx3p + 1 if idx5p > idx3p else ssIdx3p
                if ss5p.strandCanBeSplit(temp5, idx5p):
                    d = ss5p.SplitCommand(temp5, idx5p, ssIdx5p)
                    # cmds.append(d)
                    xoStrand5 = d._strandLow if ss5p.isDrawn5to3() else d._strandHigh
                    if useUndoStack:
                        self.undoStack().push(d)
                    else:
                        d.redo()
                    # adjust the target 3prime strand, IF necessary
                    if idx5p > idx3p and ss3p.isDrawn5to3():
                        xoStrand3 = xoStrand5
                    elif idx5p < idx3p and not ss3p.isDrawn5to3():
                        xoStrand3 = xoStrand5
                else:
                    print "Failed xover on try three", xoStrand3.lowIdx(), xoStrand3.highIdx(), idx5p
                    return
        # end if
        else: #  Do the following if it is in fact a different strand
            # is the 5' end ready for xover installation?
            if strand3p.idx5Prime() == idx3p:  # yes, idx already matches
                xoStrand3 = strand3p
            else:  # no, let's try to split
                offset3p = -1 if ss3p.isDrawn5to3() else 1
                if ss3p.strandCanBeSplit(strand3p, idx3p+offset3p):
                    found, overlap, ssIdx = ss3p._findIndexOfRangeFor(strand3p)
                    if found:
                        c = ss3p.SplitCommand(strand3p, idx3p+offset3p, ssIdx)
                        # cmds.append(c)
                        xoStrand3 = c._strandHigh if ss3p.isDrawn5to3() else c._strandLow
                        if useUndoStack:
                            self.undoStack().push(c)
                        else:
                            c.redo()
                else:  # can't split... abort
                    return

            # is the 3' end ready for xover installation?
            if strand5p.idx3Prime() == idx5p:  # yes, idx already matches
                xoStrand5 = strand5p
            else:
                if ss5p.strandCanBeSplit(strand5p, idx5p):
                    found, overlap, ssIdx = ss5p._findIndexOfRangeFor(strand5p)
                    if found:
                        d = ss5p.SplitCommand(strand5p, idx5p, ssIdx)
                        # cmds.append(d)
                        xoStrand5 = d._strandLow if ss5p.isDrawn5to3() else d._strandHigh
                        if useUndoStack:
                            self.undoStack().push(d)
                        else:
                            d.redo()
                else:  # can't split... abort
                    return
        # end else
        e = Part.CreateXoverCommand(self, xoStrand5, idx5p, xoStrand3, idx3p)
        # cmds.append(c)
        # util.execCommandList(self, cmds, desc="Create Xover", \
        #                                         useUndoStack=useUndoStack)
        if useUndoStack:
            self.undoStack().push(e)
            self.undoStack().endMacro()
        else:
            e.redo()
    # end def

    def removeXover(self, strand5p, strand3p, useUndoStack=True):
        cmds = []
        if strand5p.connection3p() == strand3p:
            c = Part.RemoveXoverCommand(self, strand5p, strand3p)
            cmds.append(c)
            util.execCommandList(self, cmds, desc="Remove Xover", \
                                                    useUndoStack=useUndoStack)
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
        util.execCommandList(self, [c], desc="Remove VirtualHelix", \
                                                    useUndoStack=useUndoStack)
    # end def

    def renumber(self):
        print "%s: renumber() called." % self
    # end def

    def resizeLattice(self):
        """docstring for resizeLattice"""
        pass
    # end def

    def resizeVirtualHelices(self, minDelta, maxDelta, useUndoStack=True):
        """docstring for resizeVirtualHelices"""
        print "resizeVirtualHelices", minDelta, maxDelta
        c = Part.ResizePartCommand(self, minDelta, maxDelta)
        util.execCommandList(self, [c], desc="Resize part", \
                                                    useUndoStack=useUndoStack)
    # end def

    def setActiveBaseIndex(self, idx):
        self._activeBaseIndex = idx
        self.partActiveSliceIndexSignal.emit(self, idx)
    # end def

    def setActiveVirtualHelix(self, virtualHelix):
        self._activeVirtualHelix = virtualHelix
        self.partStrandChangedSignal.emit(virtualHelix)
    # end def

    def selectPreDecorator(self, selectionList):
        """
        Handles view notifications that a predecorator has been selected.
        Will be used to emit a signal preDecoratorSelectedSignal
        """
        if(len(selectionList) == 0):
            print "all PreDecorators were unselected"
            #partPreDecoratorUnSelectedSignal.emit()
        for sel in selectionList:
            (row, col, baseIdx) = (sel[0], sel[1], sel[2])
            print "PreDecorator was selected at (%d, %d)[%d]" % (row, col, baseIdx)
            # partPreDecoratorSelectedSignal.emit(row, col, baseIdx)

    ### PRIVATE SUPPORT METHODS ###
    def _addVirtualHelix(self, virtualHelix):
        """
        private method for adding a virtualHelix to the Parts data structure
        of virtualHelix references
        """
        self._virtualHelixHash[virtualHelix.coord()] = virtualHelix
    # end def

    def _removeVirtualHelix(self, virtualHelix):
        """
        private method for adding a virtualHelix to the Parts data structure
        of virtualHelix references
        """
        del self._virtualHelixHash[virtualHelix.coord()]
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
                    # use self._highestUsedOdd iff the recycle bin is empty
                    # and highestUsedOdd+2 is not in the reserve bin
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

    def _splitBeforeAutoXovers(self, vh5p, vh3p, idx, useUndoStack=True):
        # prexoveritem needs to store left or right, and determine
        # locally whether it is from or to
        # pass that info in here in and then do the breaks
        ss5p = strand5p.strandSet()
        ss3p = strand3p.strandSet()
        cmds = []

        # is the 5' end ready for xover installation?
        if strand3p.idx5Prime() == idx5p:  # yes, idx already matches
            xoStrand3 = strand3p
        else:  # no, let's try to split
            offset3p = -1 if ss3p.isDrawn5to3() else 1
            if ss3p.strandCanBeSplit(strand3p, idx3p+offset3p):
                found, overlap, ssIdx = ss3p._findIndexOfRangeFor(strand3p)
                if found:
                    c = ss3p.SplitCommand(strand3p, idx3p+offset3p, ssIdx)
                    cmds.append(c)
                    xoStrand3 = c._strandHigh if ss3p.isDrawn5to3() else c._strandLow
            else:  # can't split... abort
                return

        # is the 3' end ready for xover installation?
        if strand5p.idx3Prime() == idx5p:  # yes, idx already matches
            xoStrand5 = strand5p
        else:
            if ss5p.strandCanBeSplit(strand5p, idx5p):
                found, overlap, ssIdx = ss5p._findIndexOfRangeFor(strand5p)
                if found:
                    d = ss5p.SplitCommand(strand5p, idx5p, ssIdx)
                    cmds.append(d)
                    xoStrand5 = d._strandLow if ss5p.isDrawn5to3() else d._strandHigh
            else:  # can't split... abort
                return
        c = Part.CreateXoverCommand(self, xoStrand5, idx5p, xoStrand3, idx3p)
        cmds.append(c)
        util.execCommandList(self, cmds, desc="Create Xover", \
                                                useUndoStack=useUndoStack)
    # end def

    ### PUBLIC SUPPORT METHODS ###
    def shallowCopy(self):
        part = self.newPart()
        part._virtualHelices = dict(self._virtualHelices)
        part._oligos = dict(self._oligos)
        part._maxBase = self._maxBase
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
                    lastStrand.setConnection3p(newStrand)
                else: 
                    # set the first condition
                    newOligo.setStrand5p(newStrand)
                newStrand.setConnection5p(lastStrand)
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
        (r,c) = vh.coord()

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

        where:

        neighborVirtualHelix is a virtualHelix neighbor of the arg virtualHelix
        index is the index where a potential Xover might occur
        strandType is from the enum (StrandType.Scaffold, StrandType.Staple)
        isLowIdx is whether or not it's the at the low index (left in the Path
        view) of a potential Xover site
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

    def setImportedVHelixOrder(self, orderedCoordList):
        """Used on file import to store the order of the virtual helices."""
        self._importedVHelixOrder = orderedCoordList
        self.partVirtualHelicesReorderedSignal.emit(orderedCoordList)

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
        Creates a Xover from the 3' end of strand5p to the 5' end of strand3p
        this needs to
        1. preserve the old oligo of strand3p
        2. install the crossover
        3. apply the strand5p oligo to the strand3p
        """
        def __init__(self, part, strand5p, strand5pIdx, strand3p, strand3pIdx):
            super(Part.CreateXoverCommand, self).__init__()
            self._part = part
            self._strand5p = strand5p
            self._strand5pIdx = strand5pIdx
            self._strand3p = strand3p
            self._strand3pIdx = strand3pIdx
            self._oldOligo3p = strand3p.oligo()
            print "The xover init", strand5p, strand3p
        # end def

        def redo(self):
            part = self._part
            strand5p = self._strand5p
            strand5pIdx = self._strand5pIdx
            strand3p = self._strand3p
            strand3pIdx = self._strand3pIdx
            olg5p = strand5p.oligo()
            oldOlg3p = self._oldOligo3p

            # 1. update preserved oligo length
            olg5p.incrementLength(oldOlg3p.length())

            # 2. Remove the old oligo and apply the 5' oligo to the 3' strand
            oldOlg3p.removeFromPart()
            if olg5p == strand3p.oligo():
                olg5p.setLoop(True)
            else:
                for strand in strand3p.generator3pStrand():
                    Strand.setOligo(strand, olg5p)  # emits strandHasNewOligoSignal

            # 3. install the Xover
            strand5p.setConnection3p(strand3p)
            strand3p.setConnection5p(strand5p)
            print "xoverA", strand5p, strand3p.connection5p()
            print "xoverB", strand3p, strand5p.connection3p()

            ss5 = strand5p.strandSet()
            vh5p = ss5.virtualHelix()
            st5p = ss5.strandType()
            ss3 = strand3p.strandSet()
            vh3p = ss3.virtualHelix()
            st3p = ss3.strandType()

            strand5p.strandXover5pChangedSignal.emit(strand5p, strand3p)
            strand5p.strandUpdateSignal.emit(strand5p)
            strand3p.strandUpdateSignal.emit(strand3p)
        # end def

        def undo(self):
            part = self._part
            strand5p = self._strand5p
            strand5pIdx = self._strand5pIdx
            strand3p = self._strand3p
            strand3pIdx = self._strand3pIdx
            oldOlg3p = self._oldOligo3p
            olg5p = strand5p.oligo()

            # 1. uninstall the Xover
            strand5p.setConnection3p(None)
            strand3p.setConnection5p(None)

            # 2. restore the modified oligo length
            olg5p.decrementLength(oldOlg3p.length())

            # 3. apply the old oligo to strand3p
            oldOlg3p.addToPart(part)
            if oldOlg3p.isLoop():
                oldOlg3p.setLoop(False)
            else:
                for strand in strand3p.generator3pStrand():
                    Strand.setOligo(strand, oldOlg3p)  # emits strandHasNewOligoSignal

            ss5 = strand5p.strandSet()
            vh5p = ss5.virtualHelix()
            st5p = ss5.strandType()
            ss3 = strand3p.strandSet()
            vh3p = ss3.virtualHelix()
            st3p = ss3.strandType()

            strand5p.strandXover5pChangedSignal.emit(strand5p, strand3p)
            strand5p.strandUpdateSignal.emit(strand5p)
            strand3p.strandUpdateSignal.emit(strand3p)
        # end def
    # end class

    class RemoveXoverCommand(QUndoCommand):
        """
        Removes a Xover from the 3' end of strand5p to the 5' end of strand3p
        this needs to
        1. preserve the old oligo of strand3p
        2. install the crossover
        3. update the oligo length
        4. apply the new strand3p oligo to the strand3p
        """
        def __init__(self, part, strand5p, strand3p):
            super(Part.RemoveXoverCommand, self).__init__()
            self._part = part
            self._strand5p = strand5p
            self._strand5pIdx = strand5p.idx3Prime()
            self._strand3p = strand3p
            self._strand3pIdx = strand3p.idx5Prime()
            nO3p = self._newOligo3p = strand3p.oligo().shallowCopy()
            colorList = styles.stapColors if strand5p.strandSet().isStaple() else styles.scafColors
            nO3p.setColor(random.choice(colorList).name())
            nO3p.setLength(0)
            for strand in strand3p.generator3pStrand():
                nO3p.incrementLength(strand.totalLength())
            # end def
            nO3p.setStrand5p(strand3p)
        # end def

        def redo(self):
            part = self._part
            strand5p = self._strand5p
            strand5pIdx = self._strand5pIdx
            strand3p = self._strand3p
            strand3pIdx = self._strand3pIdx
            newOlg3p = self._newOligo3p
            olg5p = self._strand5p.oligo()

            # 1. uninstall the Xover
            strand5p.setConnection3p(None)
            strand3p.setConnection5p(None)

            # 2. restore the modified oligo length
            olg5p.decrementLength(newOlg3p.length())

            # 3. apply the old oligo to strand3p
            newOlg3p.addToPart(part)
            if newOlg3p.isLoop():
                newOlg3p.setLoop(False)
            else:
                for strand in strand3p.generator3pStrand():
                    Strand.setOligo(strand, newOlg3p)  # emits strandHasNewOligoSignal

            ss5 = strand5p.strandSet()
            vh5p = ss5.virtualHelix()
            st5p = ss5.strandType()
            ss3 = strand3p.strandSet()
            vh3p = ss3.virtualHelix()
            st3p = ss3.strandType()

            strand5p.strandXover5pChangedSignal.emit(strand5p, strand3p)
            strand5p.strandUpdateSignal.emit(strand5p)
            strand3p.strandUpdateSignal.emit(strand3p)
        # end def

        def undo(self):
            part = self._part
            strand5p = self._strand5p
            strand5pIdx = self._strand5pIdx
            strand3p = self._strand3p
            strand3pIdx = self._strand3pIdx
            olg5p = strand5p.oligo()
            newOlg3p = self._newOligo3p

            # 1. update preserved oligo length
            olg5p.incrementLength(newOlg3p.length())

            # 2. Remove the old oligo and apply the 5' oligo to the 3' strand
            newOlg3p.removeFromPart()
            if olg5p == strand3p.oligo():
                olg5p.setLoop(True)
            else:
                for strand in strand3p.generator3pStrand():
                    Strand.setOligo(strand, olg5p)  # emits strandHasNewOligoSignal

            # 3. install the Xover
            strand5p.setConnection3p(strand3p)
            strand3p.setConnection5p(strand5p)

            ss5 = strand5p.strandSet()
            vh5p = ss5.virtualHelix()
            st5p = ss5.strandType()
            ss3 = strand3p.strandSet()
            vh3p = ss3.virtualHelix()
            st3p = ss3.strandType()

            strand5p.strandXover5pChangedSignal.emit(strand5p, strand3p)
            strand5p.strandUpdateSignal.emit(strand5p)
            strand3p.strandUpdateSignal.emit(strand3p)
        # end def
    # end class

    class ResizePartCommand(QUndoCommand):
        """
        set the maximum and mininum base index in the helical direction

        need to adjust all subelements in the event of a change in the 
        minimum index
        """
        def __init__(self, part, minHelixDelta, maxHelixDelta):
            super(Part.ResizePartCommand, self).__init__()
            self._part = part
            self._minDelta = minHelixDelta
            self._maxDelta = maxHelixDelta
            self._oldActiveIdx = part.activeBaseIndex()
        # end def

        def redo(self):
            part = self._part
            part._minBase += self._minDelta
            part._maxBase += self._maxDelta
            if self._minDelta != 0:
                self.deltaMinDimension(part, self._minDelta)
            for vh in part._virtualHelixHash.itervalues():
                part.partVirtualHelixResizedSignal.emit(vh.coord())
            if self._oldActiveIdx > part._maxBase:
                part.setActiveBaseIndex(part._maxBase)
            part.partDimensionsChangedSignal.emit(part)
        # end def

        def undo(self):
            part = self._part
            part._minBase -= self._minDelta
            part._maxBase -= self._maxDelta
            if self._minDelta != 0:
                self.deltaMinDimension(part, self._minDelta)
            for vh in part._virtualHelixHash.itervalues():
                part.partVirtualHelixResizedSignal.emit(vh.coord())
            if self._oldActiveIdx != part.activeBaseIndex():
                part.setActiveBaseIndex(self._oldActiveIdx)
            part.partDimensionsChangedSignal.emit(part)
        # end def

        def deltaMinDimension(self, part, minDimensionDelta):
            """
            Need to update:
            strands
            insertions
            """
            for vhDict in part._insertions.itervalues():
                for insertion in vhDict:
                    insertion.updateIdx(minDimensionDelta)
                # end for
            # end for
            for vh in part._virtualHelixHash.itervalues():
                for strand in vh.scaffoldStrand().generatorStrand():
                    strand.updateIdxs(minDimensionDelta)
                for strand in vh.stapleStrand().generatorStrand():
                    strand.updateIdxs(minDimensionDelta)
            # end for
        # end def
    # end class
# end class
