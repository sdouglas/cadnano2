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
from .enum import LatticeType, StrandType
from heapq import *
import copy
from views import styles
from readwritelock import ReadWriteLock
from threading import Condition
import itertools

import util
# import Qt stuff into the module namespace with PySide, PyQt4 independence
util.qtWrapImport('QtCore', globals(), ['QObject', 'pyqtSignal'])
util.qtWrapImport('QtGui', globals(), [ 'QUndoCommand'])

class DNAPart(Part):
    """
    Emits:
        dimensionsWillChange(newNumRows, newNumCols, newNumBases)
        dimensionsDidChange()
        virtualHelixAtCoordsChanged(row, col)  # the VH at row, col will
            * change its idnum (the dnapart owns the idnum)
            * change its virtualhelix object (maybe from or to None)
        persistentDataChanged()  # The saveable data contained in the receiver
                                 # will or did change. This means one of
            * virtualHelixAtCoordsChanged was triggered
            * dimensionsWillChange was triggered
            * basesModified was emitted by some child VH
        selectionWillChange()
    """
    # object 1 is the tuple (3 prime vhelix, index), 
    # object 2 is the (5 prime vhelix, index)
    # int is the strandtype
    createXover = pyqtSignal(object, object, int)
    # object 1 is (3'vhelix, 3'strandType, 3'index)
    # object 2 is (QPointF)destination
    # if the floating Xover is being destroyed,
    #  object 1 is None
    #  object 2 is None
    updateFloatingXover = pyqtSignal(object, object)
    needsFittingToView = pyqtSignal()

    _selectAllBehavior = True  # Always select all helices in part
    # Bases are always added and removed in multiples of the
    # addition/removal unit
    def selectAllBehavior(self):
        return self._selectAllBehavior

    def __init__(self, *args, **kwargs):
        if self.__class__ == DNAPart:
            raise NotImplementedError("This class is abstract. Perhaps you want DNAHoneycombPart.")
        super(DNAPart, self).__init__(self, *args, **kwargs)
        self._numberToVirtualHelix = {}  # number -> VirtualHelix
        self._name = kwargs.get('name', 'untitled')
        self._maxRow = kwargs.get('maxRow', 20)
        self._maxCol = kwargs.get('maxCol', 20)
        self._maxBase = kwargs.get('maxSteps', 2) * self.step

        # ID assignment infra
        self.oddRecycleBin, self.evenRecycleBin = [], []
        self.reserveBin = set()
        self.highestUsedOdd = -1  # Used iff the recycle bin is empty and highestUsedOdd+2 is not in the reserve bin
        self.highestUsedEven = -2  # same

        # Transient and/or cached state
        self._staples = []
        self._scaffolds = []
        self._selection = list()
        self._coordToVirtualHelix = {}  # (row,col) -> VirtualHelix
        
        # Abstract
        if self._selectAllBehavior:
            self.virtualHelixAtCoordsChanged.connect(self.updateSelectionFromVHChange)

        # This variable is directly used and entirely managed by
        # virtualhelix for consolidation of basesModified signals.
        self.basesModifiedVHs = set()

        # We also keep track of the specific bases that were modified
        # so that we can efficiently recalculate strand lengths.
        # self.basesModified is cleared by and ONLY by dnapart's
        # recalculateStrandLengths method.
        self.basesModified = set()
        self.numTimesStrandLengthsRecalcd = 0
        self.lock = ReadWriteLock()
        self.modificationCondition = Condition()
        self.basesModifySilently = False

        # Event propagation
        self.virtualHelixAtCoordsChanged.connect(self.persistentDataChangedEvent)
        self.dimensionsWillChange.connect(self.persistentDataChangedEvent)
        self.dimensionsDidChange.connect(self.ensureActiveBaseIsWithinNewDims)
    
    def fsck(self):
        # for vh in self._numberToVirtualHelix.itervalues():
        #     vh.fsck()
        map(fsk, self._numberToVirtualHelix.itervalues())

    def destroy(self):
        if self._selectAllBehavior == True:
            self.virtualHelixAtCoordsChanged.disconnect(self.updateSelectionFromVHChange)
        self.virtualHelixAtCoordsChanged.disconnect(self.persistentDataChangedEvent)
        self.dimensionsWillChange.disconnect(self.persistentDataChangedEvent)
    # end def

    persistentDataChanged = pyqtSignal()
    def persistentDataChangedEvent(self, *args, **kwargs):
        self.persistentDataChanged.emit()

    def setDocument(self, newDoc):
        """Only called by Document"""
        super(DNAPart, self).setDocument(newDoc)

    def palette(self):
        return styles.default_palette

    def name(self):
        return self._name

    nameWillChange = pyqtSignal(str)
    def setName(self, newName):
        self.nameWillChange.emit(newName)
        self._name = newName

    def dimensions(self):
        return (self._maxRow, self._maxCol, self._maxBase)

    def numBases(self):
        return self._maxBase

    def __repr__(self):
        s = self.__class__.__name__+"[" +\
            ','.join(repr(self._numberToVirtualHelix[k])\
            for k in self._numberToVirtualHelix) + "]"
        return s

    def coordinateParityEven(self, coords):
        row, col = coords
        return (row % 2) ^ (col % 2) == 0

    def virtualHelixParityEven(self, vhref):
        """A property of the part, because the part is responsible for laying out
        the virtualhelices and parity is a property of the layout more than it is a
        property of a helix (maybe a non-honeycomb layout could support a different
        notion of parity?)"""
        vh = self.getVirtualHelix(vhref, returnNoneIfAbsent=False)
        return self.coordinateParityEven(vh.coord())

    def getVirtualHelixNeighbors(self, vhref):
        neighbors = []
        vh = self.getVirtualHelix(vhref, returnNoneIfAbsent=False)
        (r,c) = vh.coord()
        if self.virtualHelixParityEven(vh):
            neighbors.append(self.getVirtualHelix((r,c+1)))  # p0 neighbor (p0 is a direction)
            neighbors.append(self.getVirtualHelix((r-1,c)))  # p1 neighbor
            neighbors.append(self.getVirtualHelix((r,c-1)))  # p2 neighbor
        else:
            neighbors.append(self.getVirtualHelix((r,c-1)))  # p0 neighbor (p0 is a direction)
            neighbors.append(self.getVirtualHelix((r+1,c)))  # p1 neighbor
            neighbors.append(self.getVirtualHelix((r,c+1)))  # p2 neighbor
        return neighbors  # Note: the order and presence of Nones is important
        # If you need the indices of available directions use range(0,len(neighbors))

    dimensionsWillChange = pyqtSignal(object)
    dimensionsDidChange = pyqtSignal()
    def setDimensions(self, newDim, useUndoStack=True, undoStack=None):
        c = DNAPart.SetDimensionsCommand(self, newDim)
        if useUndoStack:
            if undoStack == None:
                undoStack = self.undoStack()
            undoStack.push(c)
        else:
            c.redo()

    class SetDimensionsCommand(QUndoCommand):
        def __init__(self, part, newDim):
            QUndoCommand.__init__(self)
            self.newDim = newDim
            self.part = part
        def redo(self, actuallyUndo=False):
            dimToChangeTo, part = self.newDim, self.part
            self.oldDim = part.dimensions()
            part._maxRow, part._maxCol, part._maxBase = dimToChangeTo
            subCommands = []
            for vh in part._numberToVirtualHelix.itervalues():
                c = vh.SetNumBasesCommand(vh, part._maxBase)
                c.redo()
                subCommands.append(c)
            self.subCommands = subCommands
            part.dimensionsDidChange.emit()
        def undo(self):
            dimToChangeTo, part = self.oldDim, self.part
            part._maxRow, part._maxCol, part._maxBase = dimToChangeTo
            for c in reversed(self.subCommands):
                c.undo()

    def majorGrid(self):
        return self._majorGridLine

    def crossSectionStep(self):
        """Returns the cross-section type of the DNA part."""
        return self.step

    ############################# Archiving/Unarchiving #############################
    def fillSimpleRep(self, sr):
        """
        Provides a representation of the receiver in terms of simple
        (container,atomic) classes and other objects implementing simpleRep
        """
        sr['.class'] = "DNAPart"
        # JSON doesn't like keys that aren't strings, so we cheat and use an array
        # Entries look like ((row,col),num,vh)
        # coordsAndNumToVH = []
        # for vh in self._coordToVirtualHelix.itervalues():
        #     coordsAndNumToVH.append((vh.coord(), vh.number(), vh))
        coordsAndNumToVH = map(lambda vh: (vh.coord(), vh.number(), vh), self._coordToVirtualHelix.itervalues())
        sr['virtualHelices'] = coordsAndNumToVH
        sr['name'] = self.name()
        sr['maxBase'] = self._maxBase

    # First objects that are being unarchived are sent
    # ClassNameFrom.classAttribute(incompleteArchivedDict)
    # which has only strings and numbers in its dict and then,
    # sometime later (with ascending finishInitPriority) they get
    # finishInitWithArchivedDict, this time with all entries
    finishInitPriority = 0.0
    def finishInitWithArchivedDict(self, completeArchivedDict):
        row, col, mb = self.dimensions()
        vh = completeArchivedDict['virtualHelices'][0][2]
        self.setDimensions((row, col, vh.numBases()), useUndoStack=False)
        for coord, num, vh in completeArchivedDict['virtualHelices']:
            if num % 2:
                self.highestUsedOdd = max(self.highestUsedOdd, num)
            else:
                self.highestUsedEven = max(self.highestUsedEven, num)
            self.addVirtualHelixAt(coord, vh, requestSpecificIdnum=num, noUndo=True)
        self.setName(completeArchivedDict['name'])

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
                err = "Couldn't find the virtual helix in part %s "+\
                      "referenced by index %s" % (self, vhref)
                raise IndexError(err)
        return vh

    def getVirtualHelices(self):
        return (self._numberToVirtualHelix[n] for n in self._numberToVirtualHelix)

    def __len__(self):
        return len(self._numberToVirtualHelix)

    virtualHelixAtCoordsChanged = pyqtSignal(int, int)
    def addVirtualHelixAt(self, coords, vh, requestSpecificIdnum=None, noUndo=False):
        c = self.AddHelixCommand(self, tuple(coords), vh, requestSpecificIdnum)
        if noUndo:
            c.redo()
        else:
            self.undoStack().push(c)
            
    def removeVirtualHelicesAt(self, vhList, requestSpecificIdnum=None, noUndo=False):
        if noUndo:
            def removeCommands(vh):
                if vh != None:
                    vh.clearAllStrands()
                    c = self.RemoveHelixCommand(self, vh.coord(), vh, requestSpecificIdnum)
                    c.redo()
            # end def
            map(removeCommands, vhList)
        else:
            self.undoStack().beginMacro("Remove Virtual Helix")
            def removeCommands(vh):
                if vh != None:
                    vh.clearAllStrands()
                    c = self.RemoveHelixCommand(self, vh.coord(), vh, requestSpecificIdnum)
                    self.undoStack().push(c)
            # end def
            map(removeCommands, vhList)
            self.undoStack().endMacro()
    # end def

    def matchHelixNumberingToPhgDisplayOrder(self, phg):
        # evens, odds = [], []
        # for vh in phg.displayedVHs():
        #     n = vh.number()
        #     if n%2:
        #         odds.append(n)
        #     else:
        #         evens.append(n)
        
        # update for speed!
        dispVHs = phg.displayedVHs()
        odds = filter(lambda vh: True if vh.number() % 2 else False, dispVHs) 
        evens = filter(lambda vh: True if not vh.number() % 2 else False, dispVHs) 

        oldNumbers = list(evens + odds)
        evens.sort()
        odds.sort()
        newNumbers = evens + odds
        c = self.RenumberHelicesCommand(self, oldNumbers, newNumbers)
        self.undoStack().push(c)

    # emits virtualHelixAtCoordsChanged
    def renumberVirtualHelix(self, vhref, newNumber, automaticallyRenumberConflictingHelix=False):
        vh = getVirtualHelix(vhref, returnNoneIfAbsent = False)
        helixAlreadyAtNewNum = self.getVirtualHelix(newNumber)
        if helixAlreadyAtNewNum:
            if automaticallyRenumberConflictingHelix:
                n = self.reserveHelixIDNumber(parityEven=(newNumber%2==0))
                self.recycleHelixIDNumber(n)
                self.renumberVirtualHelix(helixAlreadyAtNewNum, n)
            else:
                assert(False)  # Tried to assign an idnum belonging to another helix to vhref
        c = self.RenumberHelixCommand(self, vh.coords(), newNumber)

    def getVirtualHelixCount(self):
        """docstring for getVirtualHelixList"""
        return len(self._numberToVirtualHelix)

    def getVirtualHelices(self):
        return self._numberToVirtualHelix.itervalues()

    def updateAcyclicLengths(self):
        # Cyclic structures should get initial highlighting from the fact that
        # bases are highlighted by default.
        for vh in self.getVirtualHelices():
            vh.updateLengthsFrom5pEnds()

    def autoStaple(self):
        """
        Install staples to pair with all scaffold present in the model and
        connect all crossovers.

        Commits prior to 6eb16c3420b70a5f3966 for slower version of next bit
        """
        self.basesModifySilently = True
        self.undoStack().beginMacro("Auto Staple")
        def autoStaple_sub1(vh):
            # Copy the scaffold strand's segments to the staple strand
            vh.legacyClearStrand(StrandType.Staple, 1, vh.numBases()-1)
            segments, ends3, ends5 = vh.getSegmentsAndEndpoints(StrandType.Scaffold)
            map(lambda (segStart, segEnd): \
                    vh.connectStrand(StrandType.Staple, segStart, segEnd,\
                                     speedy=True, police=False), segments)
            for i in range(len(segments)-1):
                segIEnd = segments[i][1]
                if segIEnd + 1 == segments[i+1][0]:
                    vh.connectStrand(StrandType.Staple, segIEnd, segIEnd + 1)
        # end def
        vhs = self.getVirtualHelices()
        map(autoStaple_sub1, vhs)
        def autoStaple_sub2(vh):
            # We only add crossovers for which vh will have the 3' end to
            # avoid adding each crossover twice. We can do this by adding
            # only crossovers that face left (or right) because all crossovers
            # with 3' crossovers (or 5') will face either left or right
            # on a given helix.
            facingR = not vh.directionOfStrandIs5to3(StrandType.Staple)
            pxovers = vh.potentialCrossoverList(facingR, StrandType.Staple)
            def loopXovers((toVH, idx)):
                if vh.possibleNewCrossoverAt(StrandType.Staple, idx, toVH, idx):
                    vh.installXoverFrom3To5(StrandType.Staple, idx, toVH, idx, speedy=False, police=False)
            map(loopXovers, pxovers)  # Loop through potential xovers
        # end def
        vhs = self.getVirtualHelices()  # gets a generator, so call it again
        map(autoStaple_sub2, vhs)
        self.undoStack().endMacro()
        self.basesModifySilently = False
        list(self.basesModifiedVHs)[0].emitBasesModifiedIfNeeded()
    # end def

    def autoDragAllBreakpoints(self):
        """Carryover from cadnano1. Shift+Alt+Click on activeslichandle tells
        all breakpoints to extend as far as possible."""
        vhs = self.getVirtualHelices()
        self.undoStack().beginMacro("Auto-drag Scaffold(s)")
        # for vh in vhs:
        #     vh.autoDragAllBreakpoints(StrandType.Scaffold)
        map(VirtualHelix.autoDragAllBreakpoints, vhs, \
                            itertools.repeat(StrandType.Scaffold, len(self._numberToVirtualHelix)))
        self.undoStack().endMacro()

    def indexOfRightmostNonemptyBase(self):
        """
        During reduction of the number of bases in a part,
        the first click removes empty bases from the right hand
        side of the part (red left-facing arrow). This method
        returnes the new numBases that will effect that reduction.
        """
        # ret = -1
        # for vh in self.getVirtualHelices():
        #     ret = max(ret, vh.indexOfRightmostNonemptyBase())
        # return ret
        return max(map(VirtualHelix.indexOfRightmostNonemptyBase, self.getVirtualHelices()))

    def getStapleSequences(self):
        """
        join with map provides best performance for concatenating lists of 
        strings
        """
        ret = "Start,End,Sequence,Length,Color\n"
        vhelices = self.getVirtualHelices()
        def gSS(vh):
            vh5 = vh
            # retrieve the 5 prime endpoints of the staple strands
            oligo_ends = vh.getEndpoints(StrandType.Staple)[1]
            def oligo_end_sub(endpoint):
                bases = vh5._basesConnectedTo(StrandType.Staple, endpoint)
                def baseSeq(base):
                    # put the insertion first since it's already rcomp
                    if base.lazy_sequence() == (" ", " "):
                        return ''  # skip
                    else:
                        return base.lazy_sequence()[1] + \
                                           base.lazy_sequence()[0]
                                           
                sequencestring = ''.join(map(baseSeq, bases))
                # sequencestring = reduce(lambda x,y: x + y, map(baseSeq, bases), '')
                # sequencestring = array.array('c', map(baseSeq, bases)).tostring()
                
                # sequencestring = util.nowhite(sequencestring)
                sequencestring = util.markwhite(sequencestring)
                output = "%d[%d],%d[%d],%s,%s,%s\n" % \
                        (vh5.number(), \
                        bases[0]._n, \
                        bases[len(bases)-1].vhelixNum(), \
                        bases[len(bases)-1]._n, \
                        sequencestring, \
                        len(sequencestring), \
                        bases[0].getColor().name())
                return output
            # end def
            return ''.join(map(oligo_end_sub, oligo_ends))
            # return reduce(lambda x,y: x + y, map(oligo_end_sub, oligo_ends), '')
            # return array.array('c', map(oligo_end_sub, oligo_ends)).tostring()
        # end def
        return ret +''.join(map(gSS, vhelices))
        # return reduce(lambda x,y: x + y, map(gSS, vhelices), ret)
        # return ret + array.array('c', map(gSS, vhelices)).tostring()

    ############################# VirtualHelix Private CRUD #############################
    def _recalculateStrandLengths(self):
        """
        Bases cache the length of the oligo they are in. This
        method updates that cache."""
        self.numTimesStrandLengthsRecalcd += 1
        modifiedBases = self.basesModified
        while modifiedBases:
            b = modifiedBases.pop()
            if b==None:
                continue
            basesConnectedToB = b._vhelix._basesConnectedTo(b._strandtype, b._n)
            if not basesConnectedToB:
                continue
            # Remove this strand from modifiedBases
            modifiedBases.difference_update(basesConnectedToB)
            lengthOfStrand = len(basesConnectedToB)
            circular = basesConnectedToB[0]._5pBase != None
            tooLong = lengthOfStrand > styles.oligoLenAboveWhichHighlight
            tooShort = lengthOfStrand < styles.oligoLenBelowWhichHighlight
            isStap = b._strandtype == StrandType.Staple
            highlight = isStap and (tooShort or tooLong or circular)
            for baseInStrand in basesConnectedToB:
                baseInStrand._shouldHighlight = highlight

    class AddHelixCommand(QUndoCommand):
        """
        Adds a helix to dnapart. Called by self.addVirtualHelixAt().
        """
        def __init__(self, dnapart, coords, vhelix, requestSpecificIdnum=None):
            super(DNAPart.AddHelixCommand, self).__init__()
            self._part = dnapart
            self._coords = coords  # row, col
            self._parity = self._part.coordinateParityEven(coords)
            self._vhelix = vhelix
            self._requestedNum = requestSpecificIdnum

        def redo(self, actuallyUndo=False):
            if self._vhelix:
                newID = self._part.reserveHelixIDNumber(
                                            parityEven=self._parity,\
                                            requestedIDnum=self._requestedNum)
                self._vhelix._setPart(self._part, self._coords, newID)
                self._vhelix.basesModified.connect(self._part.persistentDataChangedEvent)
                self._part._numberToVirtualHelix[newID] = self._vhelix
                self._part._coordToVirtualHelix[self._coords] = self._vhelix
            self._part.virtualHelixAtCoordsChanged.emit(self._coords[0],\
                                                        self._coords[1])

        def undo(self):
            vh = self._part.getVirtualHelix(self._coords)
            if vh:
                vh.basesModified.disconnect(self._part.persistentDataChangedEvent)
                del self._part._coordToVirtualHelix[vh.coord()]
                del self._part._numberToVirtualHelix[vh.number()]
                self._part.recycleHelixIDNumber(vh.number())
            self._part.virtualHelixAtCoordsChanged.emit(self._coords[0],\
                                                        self._coords[1])
    # end class
    
    class RemoveHelixCommand(QUndoCommand):
        """
        Adds a helix to dnapart. Called by self.addVirtualHelixAt().
        """
        def __init__(self, dnapart, coords, vhelix, requestSpecificIdnum=None):
            super(DNAPart.RemoveHelixCommand, self).__init__()
            self._part = dnapart
            self._coords = coords  # row, col
            self._parity = self._part.coordinateParityEven(coords)
            self._vhelix = vhelix
            self._requestedNum = requestSpecificIdnum
            
        def redo(self):
            vh = self._vhelix
            if vh:
                vh.basesModified.disconnect(self._part.persistentDataChangedEvent)
                del self._part._coordToVirtualHelix[vh.coord()]
                del self._part._numberToVirtualHelix[vh.number()]
                self._part.recycleHelixIDNumber(vh.number())
            self._part.virtualHelixAtCoordsChanged.emit(self._coords[0],\
                                                        self._coords[1])
        # end def

        def undo(self, actuallyUndo=False):
            # print "undo remove helix"
            vh = self._vhelix
            if vh == None:
                vh = self._part.getVirtualHelix(self._coords)
            if vh == None:
                vh = VirtualHelix(numBases=self._part.crossSectionStep())
                # vh.basesModified.connect(self.update)

            if vh:
                newID = self._part.reserveHelixIDNumber(
                                            parityEven=self._parity,\
                                            requestedIDnum=self._requestedNum)
                vh._setPart(self._part, self._coords, newID)
                self._vhelix.basesModified.connect(self._part.persistentDataChangedEvent)
                self._part._numberToVirtualHelix[newID] = vh
                self._part._coordToVirtualHelix[self._coords] = vh
            self._part.virtualHelixAtCoordsChanged.emit(self._coords[0],\
                                                        self._coords[1])
        # end def
    # end class


    class RenumberHelixCommand(QUndoCommand):
        def __init__(self, dnapart, coords, newNumber):
            super(DNAPart.RenumberHelixCommand, self).__init__()
            self.coords = coords
            self.part = dnapart
            self.newNum = newNumber

        def redo(self, actuallyUndo=False):
            # Private responsibilities of renumbering vh to newNum:
            #  1) Ensure self._numberToVirtualHelix[newNum] == vh
            #  2) Ensure vh._number == newNum (update VH's cache)
            #  3) Maintain "ID assignment infra"
            #  4) Emit virtualHelixAtCoordsChanged
            p = self.part
            vh = p.getVirtualHelix(self.coords, returnNoneIfAbsent = False)
            currentNum = vh.number()
            if actuallyUndo:
                newNum = self.oldNum
            else:
                self.oldNum = currentNum
            assert(not p.getVirtualHelix(newNum))
            del p._numberToVirtualHelix[currentNum]
            p._numberToVirtualHelix[newNum] = vh  # (1)
            vh._setNumber(newNum)  # (2)
            self.reserveHelixIDNumber(requestedIDnum=newNum)  # (3)
            # dnapart owns the idnum of a virtualhelix, so we
            # are the ones that send an update when it changes
            p.virtualHelixAtCoordsChanged.emit(self.row, self.col)  # (4)

        def undo(self):
            self.redo(actuallyUndo=True)


    class RenumberHelicesCommand(QUndoCommand):
        """
        This command undoably renumbers a list of vhs.  It can undo/redo 
        all renumbering in one command
        """
        def __init__(self, dnapart, oldNumbers, newNumbers):
            super(DNAPart.RenumberHelicesCommand, self).__init__()
            self._dnapart = dnapart
            # self._phg = phg
            self._oldNumbers = oldNumbers
            self._newNumbers = newNumbers
            # Ensure that the arguments are sane
            oldNumSet = set(oldNumbers)
            currentNumSet = set(dnapart._numberToVirtualHelix.keys())
            newNumSet = set(newNumbers)
            # Ensure that there are no duplicates
            assert(len(oldNumSet)==len(oldNumbers) and len(newNumSet)==len(newNumbers))
            # Ensure that every old number has a new number
            assert(len(self._oldNumbers) == len(self._newNumbers))
            # Ensure that no number will be duplicated
            self.novelNumbers = newNumSet - oldNumSet
            assert(self.novelNumbers.isdisjoint(currentNumSet))
            self.retiredNumbers = oldNumSet - newNumSet
            
        def redo(self, actuallyUndo=False):
            # Private responsibilities of renumbering vh to newNum:
            #  1) Ensure self._numberToVirtualHelix[newNum] == vh
            #  2) Ensure vh._number == newNum (update VH's cache)
            #  3) Maintain "ID assignment infra"
            #  4) Emit virtualHelixAtCoordsChanged
            p = self._dnapart
            newNumToVH = copy.copy(p._numberToVirtualHelix)
            oldNums = self._oldNumbers
            newNums = self._newNumbers
            if actuallyUndo:  # UNDO/REDO swap
                oldNums, newNums = newNums, oldNums
            changedVH = []
            for i in range(len(self._oldNumbers)):
                oldNum = self._oldNumbers[i]
                newNum = self._newNumbers[i]
                if oldNum != newNum:
                    vh = p._numberToVirtualHelix[oldNum]
                    changedVH.append(vh)  # (4)
                    # if the newnumber is already being used 
                    # just overwrite it
                    newNumToVH[newNum] = vh  # (1)
                    vh._setNumber(newNum)  # (2)
            novelNumbers = self.novelNumbers
            retiredNumbers = self.retiredNumbers
            if actuallyUndo:  # UNDO/REDO swap
                novelNumbers, retiredNumbers = retiredNumbers, novelNumbers
            for n in retiredNumbers:
                del newNum[n]
                self.recycleHelixIDNumber(n)  # (3)
            for n in novelNumbers:
                self.reserveHelixIDNumber(requestedIDnum=n)  # (3)

            p._numberToVirtualHelix = newNumToVH  # (1)

            for vh in changedVH:  # (4)
                p.virtualHelixAtCoordsChanged.emit(*vh.coord())

        def undo(self):
            self.redo(actuallyUndo=True)
    
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
            assert not num in self._numberToVirtualHelix
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

    ################## Transient State (doesn't get saved) ###################
    def selection(self):
        """The set of helices that has been clicked or shift-clicked in
        the slice view. @todo 1) implement this 2) make the selected 
        helices more prominent in the path view (this would allow one 
        to deal with lots and lots of helices)"""
        return list(self._selection)

    selectionWillChange = pyqtSignal(object)
    def setSelection(self, newSelection):
        if self._selectAllBehavior:
            newSelection = self.getVirtualHelices()
        ns = list(newSelection)
        self.selectionWillChange.emit(ns)
        self._selection = ns

    def selectAll(self, *args, **kwargs):
        self.setSelection(self.getVirtualHelices())

    def updateSelectionFromVHChange(self, row, col):
        coord = (row, col)
        vh = self.getVirtualHelix(coord)
        if vh != None:
            s = self.selection()
            s.append(vh)
            self.setSelection(s)
        else:
            s = [vh for vh in self.selection() if vh.coord()!=coord]
            self.setSelection(s)

    def activeSlice(self):
        """The active slice is the index of the slice selected by the
        vertical slider in the path view"""
        return self._activeSlice

    activeSliceWillChange = pyqtSignal(object)
    def setActiveSlice(self, newSliceIndex):
        ni = util.clamp(newSliceIndex, 0, self.dimensions()[2]-1)
        if self._activeSlice == ni:
            return
        self.activeSliceWillChange.emit(ni)
        self._activeSlice = ni
    
    def ensureActiveBaseIsWithinNewDims(self):
        self.setActiveSlice(self.activeSlice())
