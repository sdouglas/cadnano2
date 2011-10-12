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
from oligo import Oligo
from enum import StrandType
from views import styles 

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
    space in which a strand can be created or resized.
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
        if self._strandType == 0:
            type = 'scaf'
        else:
            type = 'stap'
        num = self._virtualHelix.number()
        return "<%s_StrandSet(%d)>" % (type, num)

    ### SIGNALS ###
    strandsetStrandAddedSignal = pyqtSignal(QObject)

    ### SLOTS ###

    ### ACCESSORS ###
    def part(self):
        return self._virtualHelix.part()

    ### PUBLIC METHODS FOR QUERYING THE MODEL ###
    def isDrawn5to3(self):
        return self._virtualHelix.isDrawn5to3(self)

    def strandType(self):
        return self._strandType

    def isStaple(self):
        return self._strandType == StrandType.Staple

    def isScaffold(self):
        return self._strandType == StrandType.Scaffold

    def getNeighbors(self, strand):
        isInSet, overlap, strandSetIdx = self._findIndexOfRangeFor(strand)
        sList = self._strandList
        if isInSet:
            if strandSetIdx > 0:
                lowStrand = sList[strandSetIdx - 1]
            else:
                lowStrand = None
            if strandSetIdx < len(sList) - 1:
                highStrand = sList[strandSetIdx + 1]
            else:
                highStrand = None
            return lowStrand, highStrand
        else:
            raise IndexError
    # end def

    def complimentStrandSet(self):
        """
        """
        vh = self.virtualHelix()
        if self.isStaple():
            return vh.scaffoldStrandSet()
        else:
            return vh.stapleStrandSet()
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
            mid = (low + high) / 2
            midStrand = self._strandList[mid]
            mLow, mHigh = midStrand.idxs()
            if baseIdx < mLow:  # baseIdx is to the left of crntStrand
                high = mid   # continue binary search to the left
                highIdx = mLow - 1  # set highIdx to left of crntStrand
            elif baseIdx > mHigh:   # baseIdx is to the right of crntStrand
                low = mid + 1    # continue binary search to the right
                lowIdx = mHigh + 1  # set lowIdx to the right of crntStrand
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
        canInsert, strandSetIdx = self.getIndexToInsert(baseIdxLow, baseIdxHigh)
        if canInsert:
            c = StrandSet.CreateStrandCommand(self, baseIdxLow, baseIdxHigh, strandSetIdx)
            util.execCommandList(self, [c], desc="Create strand", useUndoStack=useUndoStack)
            return strandSetIdx
        else:
            return -1
    # end def

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
        canInsert, strandSetIdx = self.getIndexToInsert(baseIdxLow, baseIdxHigh)
        if canInsert:
            c = StrandSet.CreateStrandCommand(self, baseIdxLow, baseIdxHigh, strandSetIdx)
            util.execCommandList(self, [c], desc=None, useUndoStack=useUndoStack)
            return strandSetIdx
        else:
            return -1

    def removeStrand(self, strand, strandSetIdx=None, useUndoStack=True):
        if not strandSetIdx:
            isInSet, overlap, strandSetIdx = self._findIndexOfRangeFor(strand)
            if not isInSet:
                raise IndexError
        c = StrandSet.RemoveStrandCommand(self, strand, strandSetIdx)
        util.execCommandList(self, [c], desc="Remove strand", useUndoStack=useUndoStack)
        return strandSetIdx

    def mergeStrands(self, priorityStrand, otherStrand, useUndoStack=True):
        """
        Merge the priorityStrand and otherStrand into a single new strand.
        The oligo of priority should be propagated to the other and all of
        its connections.
        """
        lowAndHighStrands = self.strandsCanBeMerged(priorityStrand, otherStrand)
        if lowAndHighStrands:
            strandLow, strandHigh = lowAndHighStrands
            isInSet, overlap, lowStrandSetIdx = self._findIndexOfRangeFor(strandLow)
            if isInSet:
                c = StrandSet.MergeCommand(strandLow, strandHigh, \
                                                lowStrandSetIdx, priorityStrand)
                util.execCommandList(self, [c], desc="Merge", useUndoStack=useUndoStack)
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
            if strandA.lowIdx() < strandB.lowIdx():
                return strandA, strandB
            else:
                return strandB, strandA
        else:
            return None
    # end def

    def splitStrand(self, strand, baseIdx, useUndoStack=True):
        "Break strand into two strands"
        if self.strandCanBeSplit(strand, baseIdx):
            isInSet, overlap, strandSetIdx = self._findIndexOfRangeFor(strand)
            if isInSet:
                c = StrandSet.SplitCommand(strand, baseIdx, strandSetIdx)
                util.execCommandList(self, [c], desc="Split", useUndoStack=useUndoStack)
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

    def hasStrandAt(self, idxLow, idxHigh):
        """
        """
        dummyStrand = Strand(self, idxLow, idxHigh)
        strandList = [s for s in self._findOverlappingRanges(dummyStrand)]
        dummyStrand._strandSet = None
        dummyStrand.setParent(None)
        dummyStrand.deleteLater()
        dummyStrand = None
        return len(strandList) > 0
    # end def

    def hasStrandAtAndNoXover(self, idx):
        dummyStrand = Strand(self, idx, idx)
        strandList = [s for s in self._findOverlappingRanges(dummyStrand)]
        dummyStrand._strandSet = None
        dummyStrand.setParent(None)
        dummyStrand.deleteLater()
        dummyStrand = None
        if len(strandList) > 0:
            return False if strandList[0].hasXoverAt(idx) else True
        else:
            return False
    # end def

    def hasNoStrandAtOrNoXover(self, idx):
        dummyStrand = Strand(self, idx, idx)
        strandList = [s for s in self._findOverlappingRanges(dummyStrand)]
        dummyStrand._strandSet = None
        dummyStrand.setParent(None)
        dummyStrand.deleteLater()
        dummyStrand = None
        if len(strandList) > 0:
            return False if strandList[0].hasXoverAt(idx) else True
        else:
            return True
    # end def

    def getIndexToInsert(self, idxLow, idxHigh):
        """
        """
        canInsert = True
        dummyStrand = Strand(self, idxLow, idxHigh)
        if self._couldStrandInsertAtLastIndex(dummyStrand):
            return canInsert, self._lastStrandSetIndex
        isInSet, overlap, idx = self._findIndexOfRangeFor(dummyStrand)
        dummyStrand._strandSet = None
        dummyStrand.setParent(None)
        dummyStrand.deleteLater()
        dummyStrand = None
        if overlap:
            canInsert = False
        return canInsert, idx
    # end def

    def getStrand(self, baseIdx):
        """Returns the strand that overlaps with baseIdx."""
        dummyStrand = Strand(self, baseIdx, baseIdx)
        strandList = [s for s in self._findOverlappingRanges(dummyStrand)]
        dummyStrand._strandSet = None
        dummyStrand.setParent(None)
        dummyStrand.deleteLater()
        dummyStrand = None
        return strandList[0] if len(strandList) > 0 else None
    # end def

    ### PRIVATE SUPPORT METHODS ###
    def _addToStrandList(self, strand, idx):
        """Inserts strand into the _strandList at idx."""
        self._strandList.insert(idx, strand)

    def _removeFromStrandList(self, strand):
        """Remove strand from _strandList."""
        self._strandList.remove(strand)

    def _couldStrandInsertAtLastIndex(self, strand):
        """Verification of insertability based on cached last index."""
        lastInd = self._lastStrandSetIndex
        if lastInd == None:
            return False
        else:
            strandList = self._strandList
            sTestHigh = strandList[lastInd].lowIdx() if lastInd < len(strandList) else self.partMaxBaseIdx()
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
                mid = (low + high) / 2
                midStrand = strandList[mid]

                # pre get indices from the currently tested strand
                mLow, mHigh = midStrand.idxs()

                if mHigh == qLow:
                    # match, break out of while loop
                    sSetIndexLow = mid
                    break
                elif mHigh > qLow:
                    # store the candidate index
                    sSetIndexLow = mid
                    # adjust the high index to find a better candidate if
                    # it exists
                    high = mid
                # end elif
                else:  # mHigh < qLow
                    # If a strand exists it must be a higher rangeIndex
                    # leave the high the same
                    low = mid + 1
                #end elif
            # end while
        # end else

        # Step 2: create a generator on matches
        # match on whether the tempStrand's lowIndex is
        # within the range of the qStrand
        if sSetIndexLow > -1:
            tempStrands = iter(strandList[sSetIndexLow:])
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
                OR
            2. the end condition tempStrands highIndex is still inside the
            qstrand but not equal to the end point
                adjust i down 1
            otherwise
            """
            if not tempStrand or tempStrand.highIdx() < qHigh - 1:
                i -= 1
            # assign cache but double check it's a valid index
            self._lastStrandSetIndex = i if -1 < i < lenStrands else None
            return
        else:
            # no strand was found
            # go ahead and clear the cache
            self._lastStrandSetIndex = None if len(self._strandList) > 0 else 0
            return
    # end def

    def _findIndexOfRangeFor(self, strand):
        """
        Performs a binary search for strand in self._strandList.

        If the strand is found, we want to return its index and we don't care
        about whether it overlaps with anything.

        If the strand is not found, we want to return whether it would
        overlap with any existing strands, and if not, the index where it
        would go.

        Returns a tuple (found, overlap, idx)
            found is True if strand in self._strandList
            overlap is True if strand is not found, and would overlap with
            existing strands in self._strandList
            idx is the index where the strand was found if found is True
            idx is the index where the strand could be inserted if found
            is False and overlap is False.
        """
        # setup
        strandList = self._strandList
        lastIdx = self._lastStrandSetIndex
        lenStrands = len(strandList)
        # base case: empty list, can insert at 0
        if lenStrands == 0:
            return (False, False, 0)
        # check cache
        if lastIdx:
            if lastIdx < lenStrands and strandList[lastIdx] == strand:
                return (True, False, lastIdx)
        # init search bounds
        low, high = 0, lenStrands
        sLow, sHigh = strand.idxs()
        # perform binary search
        while low < high:
            mid = (low+high)/2
            midStrand = strandList[mid]
            mLow, mHigh = midStrand.idxs()
            if midStrand == strand:
                self._lastStrandSetIndex = mid
                return (True, False, mid)
            elif mHigh < sLow:
                #  strand                [sLow----)
                # mStrand  (----mHigh]
                low = mid + 1  # search higher
            elif mLow > sHigh:
                #  strand  (----sHigh]
                # mStrand                [mLow----)
                high = mid  # search lower
            else:
                if mLow <= sLow <= mHigh:
                    # overlap: right side of mStrand
                    #  strand         [sLow---------------)
                    # mStrand  [mLow----------mHigh]
                    self._lastStrandSetIndex = None
                    return (False, True, None)
                elif mLow <= sHigh <= mHigh:
                    # overlap: left side of mStrand
                    #  strand  (--------------sHigh]
                    # mStrand         [mLow-----------mHigh]
                    self._lastStrandSetIndex = None
                    return (False, True, None)
                elif sLow <= mLow and mHigh <= sHigh:
                    # overlap: strand encompases existing
                    #  strand  [sLow-------------------sHigh]
                    # mStrand         [mLow----mHigh]
                    # note: inverse case is already covered above
                    self._lastStrandSetIndex = None
                    return (False, True, None)
                else:
                    # strand not in set, here's where you'd insert it
                    self._lastStrandSetIndex = mid
                    return (False, False, mid)
            # end else
        self._lastStrandSetIndex = low
        return (False, False, low)
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
            color = None if strandSet.isScaffold() else random.choice(styles.stapleColors).name()
            self._newOligo = Oligo(None, color)  # redo will set part
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
            oligo.addToPart(strandSet.part())
            strand.setOligo(oligo)
            # Emit a signal to notify on completion
            strandSet.strandsetStrandAddedSignal.emit(strand)
            # for updating the Slice View displayed helices
            strandSet.part().partStrandChangedSignal.emit(strandSet.virtualHelix())
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
            
            # Emit a signal to notify on completion
            strand.strandRemovedSignal.emit(strand)
            
            strand.setOligo(None)

            # for updating the Slice View displayed helices
            strandSet.part().partStrandChangedSignal.emit(strandSet.virtualHelix())
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
            oligo = self._oligo
            
            oligo.setStrand5p(None)
            oligo.decrementStrandLength(strand)
            oligo.removeFromPart()
            
            # Emit a signal to notify on completion
            strand.strandRemovedSignal.emit(strand)
            
            strand.setOligo(None)  # remove cross refs
            
            # for updating the Slice View displayed helices
            strandSet.part().partStrandChangedSignal.emit(strandSet.virtualHelix())
        # end def

        def undo(self):
            # Restore the strand
            strand = self._strand
            strandSet = self._strandSet
            strandSet._strandList.insert(self._sSetIdx, strand)
            # Restore the oligo
            oligo = self._oligo
            
            oligo.setStrand5p(strand)
            oligo.incrementStrandLength(strand)
            oligo.addToPart(strandSet.part())
            strand.setOligo(oligo)
            # Emit a signal to notify on completion
            strandSet.strandsetStrandAddedSignal.emit(strand)
            # for updating the Slice View displayed helices
            strandSet.part().partStrandChangedSignal.emit(strandSet.virtualHelix())
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
            self._newOligo.strandMergeUpdate(strandLow, strandHigh)
            self._sSetIdx = lowStrandSetIdx
            # Create the newStrand by copying the priority strand to
            # preserve its properties
            newIdxs = strandLow.lowIdx(), strandHigh.highIdx()
            newStrand = strandLow.shallowCopy()
            newStrand.setIdxs(newIdxs)
            newStrand.setConnectionHigh(strandHigh.connectionHigh())
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
            lOlg = sL.oligo()
            hOlg = sH.oligo()
            # Remove old strands from the sSet (reusing idx, so order matters)
            sS._removeFromStrandList(sL)
            sS._removeFromStrandList(sH)
            # Add the newStrand to the sSet
            sS._addToStrandList(nS, idx)
            # Traverse the strands via 3'conns to assign the new oligo
            for strand in olg.strand5p().generator3pStrand():
                Strand.setOligo(strand, olg)  # emits strandHasNewOligoSignal
            # Add new oligo and remove old oligos
            olg.addToPart(sS.part())
            lOlg.removeFromPart()
            hOlg.removeFromPart()

            # Emit Signals related to destruction and addition
            sL.strandRemovedSignal.emit(sL)  # out with the old...
            sH.strandRemovedSignal.emit(sH)  # out with the old...
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
            sS._removeFromStrandList(nS)
            # Add old strands to the sSet (reusing idx, so order matters)
            sS._addToStrandList(sH, idx)
            sS._addToStrandList(sL, idx)
            # Traverse the strands via 3'conns to assign the old oligo
            for strand in lOlg.strand5p().generator3pStrand():
                Strand.setOligo(strand, lOlg)  # emits strandHasNewOligoSignal
            for strand in hOlg.strand5p().generator3pStrand():
                Strand.setOligo(strand, hOlg)  # emits strandHasNewOligoSignal
            # Remove new oligo and add old oligos
            olg.removeFromPart()
            lOlg.addToPart(sL.part())
            hOlg.addToPart(sH.part())
            # Emit Signals related to destruction and addition
            nS.strandRemovedSignal.emit(nS)  # out with the new...
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
            self._oldStrand = strand
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
            strandLow.setConnectionHigh(None)
            strandHigh.setConnectionLow(None)
            # Resize strands and update decorators
            strandLow.setIdxs((strand.lowIdx(), iNewLow))
            strandHigh.setIdxs((iNewLow + 1, strand.highIdx()))
            strandLow.removeDecoratorsOutOfRange()
            strandHigh.removeDecoratorsOutOfRange()
            # Update the oligo color
            lOligo.setColor(colorLow)
            hOligo.setColor(colorHigh)
            # Update the oligo for things like its 5prime end and isLoop
            olg5p.strandSplitUpdate(std5p, std3p, olg3p, strand)
        # end def

        def redo(self):
            sS = self._sSet
            sL = self._strandLow
            sH = self._strandHigh
            oS = self._oldStrand
            idx = self._sSetIdx
            olg = self._oldOligo
            lOlg = self._lOligo
            hOlg = self._hOligo
            # Remove old Strand from the sSet
            sS._removeFromStrandList(oS)
            # Add new strands to the sSet (reusing idx, so order matters)
            sS._addToStrandList(sH, idx)
            sS._addToStrandList(sL, idx)
            # Traverse the strands via 3'conns to assign the new oligos
            for strand in lOlg.strand5p().generator3pStrand():
                Strand.setOligo(strand, lOlg)  # emits strandHasNewOligoSignal
            for strand in hOlg.strand5p().generator3pStrand():
                Strand.setOligo(strand, hOlg)  # emits strandHasNewOligoSignal
            # Add new oligo and remove old oligos from the part
            part = olg.removeFromPart()
            lOlg.addToPart(sL.part())
            hOlg.addToPart(sH.part())
            # Emit Signals related to destruction and addition
            oS.strandRemovedSignal.emit(oS)  # out with the old...
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
            lOlg = self._lOligo
            hOlg = self._hOligo
            # Remove new strands from the sSet (reusing idx, so order matters)
            sS._removeFromStrandList(sL)
            sS._removeFromStrandList(sH)
            # Add the old strand to the sSet
            sS._addToStrandList(oS, idx)
            # Traverse the strands via 3'conns to assign the old oligo
            for strand in olg.strand5p().generator3pStrand():
                Strand.setOligo(strand, olg)
            # Add old oligo and remove new oligos from the part
            olg.addToPart(sS.part())
            lOlg.removeFromPart()
            hOlg.removeFromPart()
            # Emit Signals related to destruction and addition
            sL.strandRemovedSignal.emit(sL)  # out with the new...
            sH.strandRemovedSignal.emit(sH)  # out with the new...
            sS.strandsetStrandAddedSignal.emit(oS)  # ...in with the old
        # end def
    # end class

    def deepCopy(self, virtualHelix):
        """docstring for deepCopy"""
        pass
    # end def
# end class


class TestStrandSet():
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_findIndexOfRangeFor(self):
        from mock import Mock
        # Test strandsets with 0, 1, or 2 elements for each type
        # of search:
        #   exact-hit
        #   miss-low-without-overlap
        #   miss-high-without-overlap
        #   miss-low-with-overlap
        #   miss-high-with-overlap
        #   overlap-inside-strand-bounds
        #   overlap-outside-strand-bounds
        #   overlap-with-multiple-strands

        # ssEmpty: []
        #   search for <Strand( 3,  5)> -> found=F, overlap=F, idx=0

        # ssOne = [<Strand(10, 15)>]
        #   search for <Strand(10, 15)> -> found=T, overlap=F, idx=0
        #   search for <Strand( 3,  5)> -> found=F, overlap=F, idx=0
        #   search for <Strand(20, 25)> -> found=F, overlap=F, idx=1
        #   search for <Strand( 3, 12)> -> found=F, overlap=T, idx=None
        #   search for <Strand(13, 20)> -> found=F, overlap=T, idx=None
        #   search for <Strand( 0, 20)> -> found=F, overlap=T, idx=None
        #   search for <Strand(11, 14)> -> found=F, overlap=T, idx=None

        # ssTwo: [<Strand(3, 5)>, <Strand(10, 15)>]
        #   search for <Strand( 3,  5)> -> found=T, overlap=F, idx=0
        #   search for <Strand(10, 15)> -> found=T, overlap=F, idx=1
        #   search for <Strand( 0,  2)> -> found=F, overlap=F, idx=0
        #   search for <Strand( 6,  9)> -> found=F, overlap=F, idx=1
        #   search for <Strand(20, 25)> -> found=F, overlap=F, idx=2
        #   search for <Strand( 0,  4)> -> found=F, overlap=T, idx=None
        #   search for <Strand( 0,  4)> -> found=F, overlap=T, idx=None
        #   search for <Strand(13, 20)> -> found=F, overlap=T, idx=None

        # create the strand sets
        ssTemp = StrandSet(None, None)
        ssTemp.isDrawn5to3 = Mock(return_value=True)
        ssEmpty = StrandSet(None, None)
        ssEmpty.isDrawn5to3 = Mock(return_value=True)
        ssOne = StrandSet(None, None)
        ssOne.isDrawn5to3 = Mock(return_value=True)
        ssOne._strandList = [Strand(ssOne, 10, 15)]
        ssTwo = StrandSet(None, None)
        ssTwo.isDrawn5to3 = Mock(return_value=True)
        ssTwo._strandList = [Strand(ssTwo, 3, 5), Strand(ssTwo, 10, 15)]

        # test ssEmpty
        strand = ssTwo._strandList[0]
        found, overlap, idx = ssEmpty._findIndexOfRangeFor(strand)
        assert found == False and overlap == False and idx == 0

        # test ssOne
        #   search [<Strand(10, 15)>] for <Strand(10, 15)>
        strand = ssOne._strandList[0]
        found, overlap, idx = ssOne._findIndexOfRangeFor(strand)
        assert found == True and overlap == False and idx == 0
        #   search [<Strand(10, 15)>] for <Strand(3, 5)>
        strand = Strand(ssTemp, 3, 5)
        found, overlap, idx = ssOne._findIndexOfRangeFor(strand)
        assert found == False and overlap == False and idx == 0
        #   search [<Strand(10, 15)>] for <Strand(20, 25)>
        strand = Strand(ssTemp, 20, 25)
        found, overlap, idx = ssOne._findIndexOfRangeFor(strand)
        assert found == False and overlap == False and idx == 1
        #   search [<Strand(10, 15)>] for <Strand( 3, 12)>
        strand = Strand(ssTemp, 3, 12)
        found, overlap, idx = ssOne._findIndexOfRangeFor(strand)
        assert found == False and overlap == True and idx == None
        #   search [<Strand(10, 15)>] for <Strand(13, 20)>
        strand = Strand(ssTemp, 13, 20)
        found, overlap, idx = ssOne._findIndexOfRangeFor(strand)
        assert found == False and overlap == True and idx == None
        #   search [<Strand(10, 15)>] for <Strand(0, 20)>
        strand = Strand(ssTemp, 0, 20)
        found, overlap, idx = ssOne._findIndexOfRangeFor(strand)
        assert found == False and overlap == True and idx == None
        #   search [<Strand(10, 15)>] for <Strand(11, 14)>
        strand = Strand(ssTemp, 11, 14)
        found, overlap, idx = ssOne._findIndexOfRangeFor(strand)
        assert found == False and overlap == True and idx == None

        # test ssTwo
        # ssTwo: [<Strand(3, 5)>, <Strand(10, 15)>]
        #   search [<Strand(3, 5)>, <Strand(10, 15)>] for <Strand(3, 5)>
        strand = ssTwo._strandList[0]
        found, overlap, idx = ssTwo._findIndexOfRangeFor(strand)
        assert found == True and overlap == False and idx == 0
        #   search [<Strand(3, 5)>, <Strand(10, 15)>] for <Strand(10, 15)>
        strand = ssTwo._strandList[1]
        found, overlap, idx = ssTwo._findIndexOfRangeFor(strand)
        assert found == True and overlap == False and idx == 1
        #   search [<Strand(3, 5)>, <Strand(10, 15)>] for <Strand(0, 2)>
        strand = Strand(ssTemp, 0, 2)
        found, overlap, idx = ssTwo._findIndexOfRangeFor(strand)
        assert found == False and overlap == False and idx == 0
        #   search [<Strand(3, 5)>, <Strand(10, 15)>] for <Strand(6, 9)>
        strand = Strand(ssTemp, 6, 9)
        found, overlap, idx = ssTwo._findIndexOfRangeFor(strand)
        assert found == False and overlap == False and idx == 1
        #   search [<Strand(3, 5)>, <Strand(10, 15)>] for <Strand(20, 25)>
        strand = Strand(ssTemp, 20, 25)
        found, overlap, idx = ssTwo._findIndexOfRangeFor(strand)
        assert found == False and overlap == False and idx == 2
        #   search [<Strand(3, 5)>, <Strand(10, 15)>] for <Strand(0, 4)>
        strand = Strand(ssTemp, 0, 4)
        found, overlap, idx = ssTwo._findIndexOfRangeFor(strand)
        assert found == False and overlap == True and idx == None
        #   search [<Strand(3, 5)>, <Strand(10, 15)>] for <Strand(4, 7)>
        strand = Strand(ssTemp, 4, 7)
        found, overlap, idx = ssTwo._findIndexOfRangeFor(strand)
        assert found == False and overlap == True and idx == None
        #   search [<Strand(3, 5)>, <Strand(10, 15)>] for <Strand(8, 12)>
        strand = Strand(ssTemp, 8, 12)
        found, overlap, idx = ssTwo._findIndexOfRangeFor(strand)
        assert found == False and overlap == True and idx == None
        #   search [<Strand(3, 5)>, <Strand(10, 15)>] for <Strand(13, 20)>
        strand = Strand(ssTemp, 13, 20)
        found, overlap, idx = ssTwo._findIndexOfRangeFor(strand)
        assert found == False and overlap == True and idx == None
        #   search [<Strand(3, 5)>, <Strand(10, 15)>] for <Strand(0, 13)>
        strand = Strand(ssTemp, 0, 13)
        found, overlap, idx = ssTwo._findIndexOfRangeFor(strand)
        assert found == False and overlap == True and idx == None
        #   search [<Strand(3, 5)>, <Strand(10, 15)>] for <Strand(0, 20)>
        strand = Strand(ssTemp, 0, 20)
        found, overlap, idx = ssTwo._findIndexOfRangeFor(strand)
        assert found == False and overlap == True and idx == None


    # @with_setup(setUp, tearDown)
    # def test_getBoundsOfEmptyRegionContaining(self):
    #     ss = StrandSet(None, None)
    #     ss.maxBaseIdx = Mock(return_value=(0, 42))
    #     ss.createStrand(Strand(ss, 1, 5), 0, False)
    #     ss.createStrand(Strand(ss, 10, 20), 1, False)
    #     assert ss.getBoundsOfEmptyRegionContaining(0) == (0, 0)
    #     assert ss.getBoundsOfEmptyRegionContaining(6) == (6, 9)
    #     assert ss.getBoundsOfEmptyRegionContaining(7) == (6, 9)
    #     assert ss.getBoundsOfEmptyRegionContaining(8) == (6, 9)
    #     assert ss.getBoundsOfEmptyRegionContaining(9) == (6, 9)
    #     assert ss.getBoundsOfEmptyRegionContaining(21) == (21, 42)
    #     assert ss.getBoundsOfEmptyRegionContaining(30) == (21, 42)
    #     assert ss.getBoundsOfEmptyRegionContaining(42) == (21, 42)
    #     ss.createStrand(Strand(ss, 30, 35), 2, False)
    #     assert ss.getBoundsOfEmptyRegionContaining(21) == (21, 29)
    #     assert ss.getBoundsOfEmptyRegionContaining(36) == (36, 42)
