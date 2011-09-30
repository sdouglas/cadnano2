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

import random
from operator import itemgetter
from itertools import izip, repeat
from strand import Strand
import util
# import cadnano2.util as util
# import Qt stuff into the module namespace with PySide, PyQt4 independence
util.qtWrapImport('QtCore', globals(), ['pyqtSignal', 'QObject', 'Qt'])
util.qtWrapImport('QtGui', globals(), ['QUndoStack', 'QUndoCommand'])


class StrandSet(QObject):
    """
    StrandSet is a container class for Strands, and provides the several
    publicly accessible methods for editing strands, including operations
    for creation, destruction, resizing, splitting, and merging strands.

    Views may also query StrandSet for information that is useful in
    determining that edits can be made, such as the bounds of empty
    space in which a strand can be resized.
    """

    def __init__(self, strandType, virtualHelix):
        super(StrandSet, self).__init__(virtualHelix)
        self._virtualHelix = virtualHelix
        self._strandList = []
        self._undoStack = None
        self._lastStrandSetIndex = None
        self._strandType = strandType

    def __iter__(self):
        """Iterate over each strand in the strands list."""
        return self._strandList.__iter__()

    def __repr__(self):
        type = self._strandType[:4]
        num = self._virtualHelix.number()
        return "%s_StrandSet(%d)" % (type, num)

    ### SIGNALS ###
    strandsetStrandAddedSignal = pyqtSignal(QObject)

    ### SLOTS ###

    ### PUBLIC METHODS FOR QUERYING THE MODEL ###
    def isDrawn5to3(self):
        return self._virtualHelix.isDrawn5to3(self)

    def strandType(self):
        return self._strandType
    # end def

    def part(self):
        return self._virtualHelix.part()

    def getNeighbors(self, strand):
        strandSetIdx, isInSet = _findIndexOfRangeFor(strand)
        sList = self._strandList
        if isInSet:
            if strandSetIdx > 0:
                lowStrand = sList[strandSetIdx]
            else:
                lowStrand = None
            if strandSetIdx < len(sList) - 2:
                highStrand = sList[strandSetIdx + 1]
            else:
                highStrand = None
            return lowStrand, highStrand
        else:
            raise IndexError
    # end def

    def getBoundsOfEmptyRegionContaining(self, baseIdx):
        """
        Returns the (tight) bounds of the contiguous stretch of unpopulated
        bases that includes the baseIdx.
        """
        lowIdx, highIdx = 0, self.partMaxBaseIdx()  # init the return values
        lenStrands = len(self._strandList)
        
        # not sure how to set this up this to help in caching
        # lastIdx = self._lastStrandSetIndex
        
        if lenStrands == 0:  # empty strandset, just return the part bounds
            return (lowIdx, highIdx)

        low = 0              # index of the first (left-most) strand
        high = lenStrands    # index of the last (right-most) strand
        while low < high:    # perform binary search to find empty region
            middle = (low + high) / 2
            currentStrand = self._strandList[middle]
            cLow, cHigh = currentStrand.idxs()
            if baseIdx < cLow:  # baseIdx is to the left of crntStrand
                high = middle   # continue binary search to the left
                highIdx = cLow - 1  # set highIdx to left of crntStrand
            elif baseIdx > cHigh:   # baseIdx is to the right of crntStrand
                low = middle + 1    # continue binary search to the right
                lowIdx = cHigh + 1  # set lowIdx to the right of crntStrand
            else:
                return (None, None)  # baseIdx was not empty
        self._lastStrandSetIndex = (low + high) / 2  # set cache
        return (lowIdx, highIdx)

    def partMaxBaseIdx(self):
        """Return the bounds of the StrandSet as defined in the part."""
        return self._virtualHelix.part().maxBaseIdx()

    ### PUBLIC METHODS FOR EDITING THE MODEL ###
    def createStrand(self, baseIdxLow, baseIdxHigh, useUndoStack=True):
        """
        Assumes a strand is being created at a valid set of indices.
        """
        boundsLow, boundsHigh = self.getBoundsOfEmptyRegionContaining(baseIdxLow)
        assert(baseIdxLow < baseIdxHigh)
        assert(boundsLow <= baseIdxLow)
        assert(baseIdxHigh <= boundsHigh)
        strandSetIdx = self._lastStrandSetIndex
        c = StrandSet.CreateStrandCommand(self, baseIdxLow, baseIdxHigh, strandSetIdx)
        util._execCommandList(self, [c], desc="Create strand", useUndoStack=useUndoStack)
        return strandSetIdx

    def createDeserializedStrand(self, baseIdxLow, baseIdxHigh, useUndoStack=False):
        """
        Passes a strand to AddStrandCommand that was read in from file input.
        Omits the step of checking _couldStrandInsertAtLastIndex, since
        we assume that deserialized strands will not cause collisions.
        """
        boundsLow, boundsHigh = self.getBoundsOfEmptyRegionContaining(baseIdxLow)
        assert(baseIdxLow < baseIdxHigh)
        assert(boundsLow <= baseIdxLow)
        assert(baseIdxHigh <= boundsHigh)
        strandSetIdx = self._lastStrandSetIndex
        c = StrandSet.CreateStrandCommand(self, baseIdxLow, baseIdxHigh, strandSetIdx)
        util._execCommandList(self, [c], desc=None, useUndoStack=useUndoStack)
        return strandSetIdx

    def removeStrand(self, strand, strandSetIdx=None, useUndoStack=True):
        if not strandSetIdx:
            strandSetIdx, isInSet = self._findIndexOfRangeFor(strand)
            if not isInSet:
                raise IndexError
        c = StrandSet.RemoveStrandCommand(self, strand, strandSetIdx)
        util._execCommandList(self, [c], desc="Delete strand", useUndoStack=useUndoStack)
        return strandSetIdx

    def mergeStrands(self, priorityStrand, otherStrand, useUndoStack=True):
        """
        Merge the priorityStrand and otherStrand into a single new strand.
        The oligo of priority should be propagated to the other and all of
        its connections.
        """
        lowAndHighStrands = self.canBeMerged(priorityStrand, otherStrand)
        if lowAndHighStrands:
            strandLow, strandigh = lowAndHighStrands
            lowStrandSetIdx, isInSet = _findIndexOfRangeFor(strandLow)
            if isInSet:
                c = StrandSet.MergeCommand(strandLow, strandHigh, \
                                                lowStrandSetIdx, firstStrand)
                util._execCommandList(self, [c], desc="Merge", useUndoStack=useUndoStack)
    # end def

    def strandsCanBeMerged(self, strandA, strandB):
        """
        returns None if the strands can't be merged, otherwise
        if the strands can be merge it returns the strand with the lower index

        only checks that the strands are of the same StrandSet and that the
        end points differ by 1.  DOES NOT check if the Strands overlap, that
        should be handled by addStrand
        """
        if strandA.strandSet() != strandB.strandSet():
            return None
        if abs(strandA.lowIdx() - strandB.highIdx()) == 1 or \
            abs(strandB.lowIdx() - strandA.highIdx()) == 1:
            if strandA.lowIndex() < strandB.lowIndex():
                return strandA, strandB
            else:
                return strandB, strandA
        else:
            return None
    # end def

    def splitStrand(self, strand, baseIdx, useUndoStack=True):
        "Break strand into two strands"
        if strandCanBeSplit(strand, baseIdx):
            strandSetIdx, isInSet = _findIndexOfRangeFor(strand)
            if isInSet:
                c = StrandSet.SplitCommand(strand, baseIdx, strandSetIdx)
                util._execCommandList(self, [c], desc="Split", useUndoStack=useUndoStack)
    # end def

    def strandCanBeSplit(self, strand, baseIdx):
        """
        Make sure the base index is within the strand
        Don't split right next to a 3Prime end
        Don't split on endpoint (AKA a crossover)
        """
        # no endpoints
        if baseIdx == strand.lowIdx() or baseIdx == strand.highIdx():
            return False
        # make sure the base index within the strand
        elif strand.lowIdx() > baseIdx or baseIdx > strand.highIdx():
            return False
        elif abs(baseIdx - strand.idx3Prime()) > 1:
            return True
    # end def

    def destroy(self):
        self.setParent(None)
        self.deleteLater()  # QObject will emit a destroyed() Signal

    ### PUBLIC SUPPORT METHODS ###
    def undoStack(self):
        if self._undoStack == None:
            self._undoStack = self._virtualHelix.undoStack()
        return self._undoStack

    def virtualHelix(self):
        return self._virtualHelix

    def strandToBeDestroyed(self, strand):
        """when is this method called?"""
        strandList = self.strandList
        del strandList[strand.idx]

    ### PRIVATE SUPPORT METHODS ###
    def _couldStrandInsertAtLastIndex(self, strand):
        """Verification of insertability based on cached last index."""
        lastInd = self._lastStrandSetIndex
        if lastInd == None:
            return False  # how do we insert the first strand if this always returns False?
        else:
            strandList = self._strandList
            sTestHigh = strandList[lastInd].lowIdx()
            sTestLow = strandList[lastInd - 1].highIdx() if lastInd > 0 else -1
            sLow, sHigh = strand.idxs()
            if sTestLow < sLow and sHigh < sTestHigh:
                return True
            else:
                return False

    def _findOverlappingRanges(self, qstrand, useCache=False):
        """
        a binary search for the strands in self._strandList overlapping with
        a query strands, or qstrands, indices.

        Useful for operations on complementary strands such as applying a
        sequence

        This is an generator for now

        Strategy:
        1.
            search the _strandList for a strand the first strand that has a
            highIndex >= lowIndex of the query strand.
            save that strandSet index as sSetIndexLow.
            if No strand satisfies this condition, return an empty list

            Unless it matches the query strand's lowIndex exactly,
            Step 1 is O(log N) where N in length of self._strandList to the max,
            that is it needs to exhaust the search

            conversely you could search for first strand that has a
            lowIndex LESS than or equal to the lowIndex of the query strand.

        2.
            starting at self._strandList[sSetIndexLow] test each strand to see if
            it's indexLow is LESS than or equal to qstrand.indexHigh.  If it is
            yield/return that strand.  If it's GREATER than the indexHigh, or
            you run out of strands to check, the generator terminates
        """
        strandList = self._strandList
        lenStrands = len(strandList)
        if lenStrands == 0:
            return
        # end if

        low = 0
        high = lenStrands
        qLow, qHigh = qstrand.idxs()

        # Step 1: get rangeIndexLow with a binary search
        if useCache:  # or self.doesLastSetIndexMatch(qstrand, strandList):
            # cache match!
            sSetIndexLow = self._lastStrandSetIndex
        else:
            sSetIndexLow = -1
            while low < high:
                middle = (low + high) / 2
                currentStrand = strandList[middle]

                # pre get indices from the currently tested strand
                cLow, cHigh = currentStrand.idxs()

                if cHigh == qLow:
                    # match, break out of while loop
                    sSetIndexLow = middle
                    break
                elif cHigh > qLow:
                    # store the candidate index
                    sSetIndexLow = middle
                    # adjust the high index to find a better candidate if
                    # it exists
                    high = middle - 1
                # end elif
                else:  # cHigh < qLow
                    # If a strand exists it must be a higher rangeIndex
                    # leave the high the same
                    low = middle + 1
                #end elif
            # end while
        # end else

        # Step 2: create a generator on matches
        # match on whether the tempStrand's lowIndex is
        # within the range of the qStrand
        if sSetIndexLow > -1:
            tempStrands = iter(strandList[rangeIndexLow:])
            tempStrand = tempStrands.next()
            qHigh += 1  # bump it up for a more efficient comparison
            i = 0   # use this to
            while tempStrand and tempStrand.lowIdx() < qHigh:
                yield tempStrand
                # use a next and a default to cause a break condition
                tempStrand = next(tempStrands, None)
                i += 1
            # end while

            # cache the last index we left of at
            i = sSetIndexLow + i
            """
            if
            1. we ran out of strands to test adjust
            and
            2. the end condition tempStrands highIndex is still inside the
            qstrand but not equal to the end point
                adjust i down 1
            otherwise
            """
            if not tempStrand and tempStrand.highIdx() < qHigh - 1:
                i -= 1
            # assign cache but double check it's a valid index
            self._lastStrandSetIndex = i if -1 < i < lenStrands else None
            return
        else:
            # no strand was found
            # go ahead and clear the cache
            self._lastStrandSetIndex = None
            return
    # end def

    def _findIndexOfRangeFor(self, strand):
        """
        a binary search for a strand in self._strandList

        returns a tuple (int, bool)

        returns a positive value index in self._strandList
        if the element is in the set

        returns a negative value index in self._strandList
        if the element is not in the set, to be used as an insertion point

        returns True if the strand is in range

        returns False if the strand is not in range
            in this case, if a strand is for some reason passed to this
            method that overlaps an existing range, it will return
            a positive 1 in addition to False rather than raise an exception
        """
        strandList = self._strandList
        lastIdx = self._lastStrandSetIndex
        lenStrands = len(strandList)
        if lenStrands == 0:
            return None
        # end if
        
        # check cache
        if lastIdx and lastIdx < lenStrands and strandList[lastIdx] == strand:
            return lastIdx, True
        
        low = 0
        high = lenStrands

        sLow, sHigh = strand.idxs()

        while low < high:
            middle = (low + high) / 2
            currentStrand = strandList[middle]

            # pre get indices from currently tested strand
            cLow, cHigh = currentStrand.idxs()

            if currentStrand == strand:
                # strand is an existing range
                self._lastStrandSetIndex = middle
                return middle, True
            # end if
            elif cLow > sHigh:
                high = middle - 1
            # end elif
            elif cHigh < sLow:
                low = middle + 1
            # end elif
            else:
                if cLow <= sLow <= cHigh or cLow <= sHigh <= cHigh:
                    # strand is within an existing range
                    # but is not that range
                    return 1, False
                else:
                # object not in set, here's where you'd insert it
                    return -middle, False
            # end else
        return -low, False
    # end def

    def _doesLastSetIndexMatch(self, qstrand, strandList):
        """
        strandList is passed to save a lookup
        """
        lSI = self._lastStrandSetIndex
        if lSI:
            qLow, qHigh = qstrand.idxs()
            tempStrand = strandList[lSI]
            tLow, tHigh = tempStrand.idxs()
            if not (qLow <= tLow <= qHigh or qLow <= tHigh <= qHigh):
                return False
            else:  # get a difference
                dif = abs(qLow - tLow)
                # check neighboring strandList just in case
                difLow = dif + 1
                if lSI > 0:
                    tLow, tHigh = strand[lSI - 1].idxs()
                    if qLow <= tLow <= qHigh or qLow <= tHigh <= qHigh:
                        difLow = abs(qLow - tLow)
                difHigh = dif + 1
                if lSI < len(strand) - 1:
                    tLow, tHigh = strand[lSI + 1].idxs()
                    if qLow <= tLow <= qHigh or qLow <= tHigh <= qHigh:
                        difHigh = abs(qLow - tLow)
                # check that the cached strand is in fact the right guy
                if dif < difLow and dif < difHigh:
                    return True
                else:
                    False
            # end else
        # end if
        else:
            return False
        # end else
    # end def

    ### COMMANDS ###
    class CreateStrandCommand(QUndoCommand):
        """
        Create a new Strand based with bounds (baseIdxLow, baseIdxHigh),
        and insert it into the strandSet at position strandSetIdx. Also,
        create a new Oligo, add it to the Part, and point the new Strand
        at the oligo.
        """
        def __init__(self, strandSet, baseIdxLow, baseIdxHigh, strandSetIdx):
            super(StrandSet.CreateStrandCommand, self).__init__()
            self._strandSet = strandSet
            self._sSetIdx = strandSetIdx
            self._strand = Strand(strandSet, baseIdxLow, baseIdxHigh)
            self._newOligo = Oligo(strandSet.part())
        # end def

        def redo(self):
            # Add the new strand to the StrandSet strandList
            strand = self._strand
            strandSet = self._strandSet
            strandSet._strandList.insert(self._sSetIdx, strand)
            # Set up the new oligo
            oligo = self._newOligo
            oligo.setStrand5p(strand)
            oligo.incrementStrandLength(strand)
            oligo.AddToPart(strandSet.part())
            strand.setOligo(oligo)
            # Emit a signal to notify on completion
            strandSet.strandsetStrandAddedSignal.emit(strand)
        # end def

        def undo(self):
            # Remove the strand from StrandSet strandList
            strand = self._strand
            strandSet = self._strandSet
            strandSet._strandList.pop(self._sSetIdx)
            # Get rid of the new oligo
            oligo = self._newOligo
            oligo.setStrand5p(None)
            oligo.decrementStrandLength(strand)
            oligo.removeFromPart()
            strand.setOligo(None)
            # Emit a signal to notify on completion
            strand.removedSignal.emit(strand)
        # end def
    # end class

    class RemoveStrandCommand(QUndoCommand):
        """
        RemoveStrandCommand deletes a strand. It should only be called on
        strands with no connections to other strands.
        """
        def __init__(self, strandSet, strand, strandSetIdx):
            super(StrandSet.RemoveStrandCommand, self).__init__()
            self._strandSet = strandSet
            self._strand = strand
            self._sSetIdx = strandSetIdx
            self._oligo = strand.oligo()
        # end def

        def redo(self):
            # Remove the strand
            strand = self._strand
            strandSet = self._strandSet
            strandSet._strandList.pop(self._sSetIdx)
            # Remove the strand from the oligo
            oligo = self.oligo
            oligo.setStrand5p(None)
            oligo.decrementStrandLength(strand)
            oligo.removeFromPart()
            strand.setOligo(None)  # remove cross refs
            # Emit a signal to notify on completion
            strand.removedSignal.emit(strand)
        # end def

        def undo(self):
            # Restore the strand
            strand = self._strand
            strandSet = self._strandSet
            strandSet._strandList.insert(self._sSetIdx, strand)
            # Restore the oligo
            oligo = self.oligo
            oligo.setStrand5p(strand)
            oligo.incrementStrandLength(strand)
            oligo.addToPart(strandSet.part())
            strand.setOligo(oligo)
            # Emit a signal to notify on completion
            strandSet.strandsetStrandAddedSignal.emit(strand)
        # end def
    # end class

    class MergeCommand(QUndoCommand):
        """
        This class takes two Strands and merges them.  This Class should be
        private to StrandSet as knowledge of a strandSetIndex outside of this
        of the StrandSet class implies knowledge of the StrandSet
        implementation

        Must pass this two different strands, and nominally one of the strands
        again which is the priorityStrand.  The resulting "merged" strand has
        the properties of the priorityStrand's oligo.  Decorators are preserved

        the strandLow and strandHigh must be presorted such that strandLow
        has a lower range than strandHigh

        lowStrandSetIdx should be known ahead of time as a result of selection
        """
        def __init__(self, strandLow, strandHigh, lowStrandSetIdx, priorityStrand):
            super(StrandSet.MergeCommand, self).__init__()
            # Store strands
            self._strandLow = strandLow
            self._strandHigh = strandHigh
            pS = priorityStrand
            self._sSet = sSet = pS.strandSet()
            # Store oligos
            self._newOligo = pS.oligo().shallowCopy()
            self._sLowOligo = strandLow.oligo()
            self._sHighOligo = strandHigh.oligo()
            # Update the oligo for things like its 5prime end and isLoop
            self._newOligo.strandsMergeUpdate(strandLow, strandHigh)
            self._sSetIdx = lowStrandSetIdx
            # Create the newStrand by copying the priority strand to
            # preserve its properties
            newIdxs = strandLow.lowIdx(), strandHigh.highIdx()
            newStrand = strandLow.shallowCopy()
            newStrand.setIdxs(*newIdxs)
            newStrand.setHighConnection(strandHigh.highConnection())
            # Merging any decorators
            newStrand.addDecorators(strandHigh.decorators())
            self._newStrand = newStrand
        # end def

        def redo(self):
            sS = self._sSet
            sL = self._strandLow
            sH = self._strandHigh
            nS = self._newStrand
            idx = self._sSetIdx
            olg = self._newOligo
            lOlg = self._sLowOligo
            hOlg = self._sHighOligo
            # Remove old strands from the sSet (reusing idx, so order matters)
            sS.removeStrand(sL, idx)
            sS.removeStrand(sH, idx)
            # Add the newStrand to the sSet
            sS.addStrand(nS, idx)
            # Traverse the strands via 3'conns to assign the new oligo
            for strand in olg.strand5p().generator3pStrand():
                Strand.setOligo(strand, olg)  # emits strandHasNewOligoSignal
            # Add new oligo and remove old oligos
            olg.addToPart()
            lOlg.removeFromPart()
            hOlg.removeFromPart()
            # Emit Signals related to destruction and addition
            sL.removedSignal.emit(sL)  # out with the old...
            sH.removedSignal.emit(sH)  # out with the old...
            sS.strandsetStrandAddedSignal.emit(nS)  # ...in with the new
        # end def

        def undo(self):
            sS = self._sSet
            sL = self._strandLow
            sH = self._strandHigh
            nS = self._newStrand
            idx = self._sSetIdx
            olg = self._newOligo
            lOlg = self._sLowOligo
            hOlg = self._sHighOligo
            # Remove the newStrand from the sSet
            sS.removeStrand(nS, idx)
            # Add old strands to the sSet (reusing idx, so order matters)
            sS.addStrand(sH, idx)
            sS.addStrand(sL, idx)
            # Traverse the strands via 3'conns to assign the old oligo
            for strand in lOlg.strand5p().generator3pStrand():
                Strand.setOligo(strand, lOlg)  # emits strandHasNewOligoSignal
            for strand in hOlg.strand5p().generator3pStrand():
                Strand.setOligo(strand, hOlg)  # emits strandHasNewOligoSignal
            # Remove new oligo and add old oligos
            olg.removeFromPart()
            lOlg.addToPart()
            hOlg.addToPart()
            # Emit Signals related to destruction and addition
            nS.removedSignal.emit(nS)  # out with the new...
            sS.strandsetStrandAddedSignal.emit(sH)  # ...in with the old
            sS.strandsetStrandAddedSignal.emit(sL)  # ...in with the old
        # end def
    # end class

    class SplitCommand(QUndoCommand):
        """
        The SplitCommand takes as input a strand and "splits" the strand in
        two, such that one new strand 3' end is at baseIdx, and the other
        new strand 5' end is at baseIdx +/- 1 (depending on the direction
        of the strands).

        Under the hood:
        On redo, this command actually is creates two new copies of the
        original strand, resizes each and modifies their connections.
        On undo, the new copies are removed and the original is restored.
        """
        def __init__(self, strand, baseIdx, strandSetIdx):
            super(StrandSet.SplitCommand, self).__init__()
            # Store inputs
            self._strandOld = strand
            self._sSetIdx = strandSetIdx
            self._sSet = sSet = strand.strandSet()
            self._oldOligo = oligo = strand.oligo()
            # Create copies
            self._strandLow = strandLow = strand.shallowCopy()
            self._strandHigh = strandHigh = strand.shallowCopy()
            self._lOligo = lOligo = oligo.shallowCopy()
            self._hOligo = hOligo = oligo.shallowCopy()
            # Determine oligo retention based on strand priority
            if strand.isDrawn5to3():  # strandLow has priority
                iNewLow = baseIdx
                colorLow = oligo.color()
                colorHigh = random.choice(styles.stapleColors).name()
                olg5p, olg3p = lOligo, hOligo
                std5p, std3p = strandLow, strandHigh
            else:  # strandHigh has priority
                iNewLow = baseIdx - 1
                colorLow = random.choice(styles.stapleColors).name()
                colorHigh = oligo.color()
                olg5p, olg3p = hOligo, lOligo
                std5p, std3p = strandHigh, strandLow
            # Update strand connectivity
            strandLow.setHighConnection(None)
            strandHigh.setLowConnection(None)
            # Resize strands and update decorators
            strandLow.setIdxs(strand.lowIdx(), iNewLow)
            strandHigh.setIdxs(iNewLow + 1, strand.highIdx())
            strandLow.removeDecoratorsOutOfRange()
            strandHigh.removeDecoratorsOutOfRange()
            # Update the oligo color
            lOligo.setColor(colorLow)
            hOligo.setColor(colorHigh)
            # Update the oligo for things like its 5prime end and isLoop
            olg5p.strandsSplitUpdate(std5p, std3p, olg3p, strand)
        # end def

        def redo(self):
            sS = self._sSet
            sL = self._strandLow
            sH = self._strandHigh
            oS = self._oldStrand
            idx = self._sSetIdx
            olg = self._oldOligo
            lOlg = self._sLowOligo
            hOlg = self._sHighOligo
            # Remove old Strand from the sSet
            sS.removeStrand(oS, idx)
            # Add new strands to the sSet (reusing idx, so order matters)
            sS.addStrand(sH, idx)
            sS.addStrand(sL, idx)
            # Traverse the strands via 3'conns to assign the new oligos
            for strand in lOlg.strand5p().generator3pStrand():
                Strand.setOligo(strand, lOlg)  # emits strandHasNewOligoSignal
            for strand in hOlg.strand5p().generator3pStrand():
                Strand.setOligo(strand, hOlg)  # emits strandHasNewOligoSignal
            # Add new oligo and remove old oligos from the part
            part = olg.removeFromPart()
            lOlg.addToPart()
            hOlg.addToPart()
            # Emit Signals related to destruction and addition
            nS.removedSignal.emit(oS)  # out with the old...
            sS.strandsetStrandAddedSignal.emit(sH)  # ...in with the new
            sS.strandsetStrandAddedSignal.emit(sL)  # ...in with the new
        # end def

        def undo(self):
            sS = self._sSet
            sL = self._strandLow
            sH = self._strandHigh
            oS = self._oldStrand
            idx = self._sSetIdx
            olg = self._oldOligo
            lOlg = self._sLowOligo
            hOlg = self._sHighOligo
            # Remove new strands from the sSet (reusing idx, so order matters)
            sS.removeStrand(sL, idx)
            sS.removeStrand(sH, idx)
            # Add the old strand to the sSet
            sS.addStrand(oS, idx)
            # Traverse the strands via 3'conns to assign the old oligo
            for strand in olg.strand5p().generator3pStrand():
                Strand.setOligo(strand, olg)
            # Add old oligo and remove new oligos from the part
            olg.addToPart()
            lOlg.removeFromPart()
            hOlg.removeFromPart()
            # Emit Signals related to destruction and addition
            sL.removedSignal.emit(sL)  # out with the new...
            sH.removedSignal.emit(sH)  # out with the new...
            sS.strandsetStrandAddedSignal.emit(oS)  # ...in with the old
        # end def
    # end class

    def deepCopy(self, virtualHelix):
        """docstring for deepCopy"""
        pass
    # end def
# end class


# from nose.tools import with_setup
from mock import Mock

class TestStrandSet():
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_addStrand(self):
        ss = StrandSet(None, None)
        ss.maxBaseIdx = Mock(return_value=42)
        ss.createStrand(1, 5, 0, False)
        assert len(ss._strandList) == 1

    # @with_setup(setUp, tearDown)
    def test_getBoundsOfEmptyRegionContaining(self):
        ss = StrandSet(None, None)
        ss.maxBaseIdx = Mock(return_value=(0, 42))
        ss.createStrand(Strand(ss, 1, 5), 0, False)
        ss.createStrand(Strand(ss, 10, 20), 1, False)
        assert ss.getBoundsOfEmptyRegionContaining(0) == (0, 0)
        assert ss.getBoundsOfEmptyRegionContaining(6) == (6, 9)
        assert ss.getBoundsOfEmptyRegionContaining(7) == (6, 9)
        assert ss.getBoundsOfEmptyRegionContaining(8) == (6, 9)
        assert ss.getBoundsOfEmptyRegionContaining(9) == (6, 9)
        assert ss.getBoundsOfEmptyRegionContaining(21) == (21, 42)
        assert ss.getBoundsOfEmptyRegionContaining(30) == (21, 42)
        assert ss.getBoundsOfEmptyRegionContaining(42) == (21, 42)
        ss.createStrand(Strand(ss, 30, 35), 2, False)
        assert ss.getBoundsOfEmptyRegionContaining(21) == (21, 29)
        assert ss.getBoundsOfEmptyRegionContaining(36) == (36, 42)
