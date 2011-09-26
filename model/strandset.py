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

from operator import itemgetter
from itertools import izip, repeat
from strand import Strand

import cadnano2.util as util
# import Qt stuff into the module namespace with PySide, PyQt4 independence
util.qtWrapImport('QtCore', globals(), ['pyqtSignal', 'QObject', 'Qt'])
util.qtWrapImport('QtGui', globals(), ['QUndoStack', 'QUndoCommand'])

starmapExec = util.starmapExec


class StrandSet(QObject):
    def __init__(self, virtualhelix):
        super(StrandSet, self).__init__()
        self._virtualhelix = virtualhelix
        self._strandList = []
        self._undoStack = None
        self._lastStrandSetIndex = None

    def __iter__(self):
        """Iterate over each strand in the strands list."""
        return self._strandList.__iter__()

    ### SIGNALS ###
    strandAddedSignal = pyqtSignal(QObject)

    ### SLOTS ###

    ### PUBLIC METHODS FOR QUERYING THE MODEL ###
    def isDrawn5to3(self):
        return self._virtualhelix.isDrawn5to3(self)

    def getBoundsOfEmptyRegionContaining(self, baseIdx):
        """
        Returns the (tight) bounds of the contiguous stretch of unpopulated
        bases that includes the baseIdx.
        """
        lowIdx, highIdx = self.partBounds()  # init the return values
        lenStrands = len(self._strandList)
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

    def partBounds(self):
        """Return the bounds of the StrandSet as defined in the part."""
        return self._virtualhelix.part().bounds()

    ### PUBLIC METHODS FOR EDITING THE MODEL ###
    def addStrand(self, strand, strandSetIdx, useUndoStack=True):
        """
        Assumes a strand is being created at a valid set of indices.
        """
        c = StrandSet.AddStrandCommand(self._strandList, strand, strandSetIdx)
        self._execCommandList([c], desc="Create strand", useUndoStack=useUndoStack)
        return strandSetIdx

    def addDeserializedStrand(self, strand, strandSetIdx, useUndoStack=False):
        """
        Passes a strand to AddStrandCommand that was read in from file input.
        Omits the step of checking _couldStrandInsertAtLastIndex, since
        we assume that deserialized strands will not cause collisions.
        """
        c = StrandSet.AddStrandCommand(self._strandList, strand, strandSetIdx)
        self._execCommandList([c], desc=None, useUndoStack=useUndoStack)
        return strandSetIdx

    def removeStrand(self, strand, strandSetIdx=None, useUndoStack=True):
        if not strandSetIdx:
            strandSetIdx, isInSet = self._findIndexOfRangeFor(strand)
            if not isInSet:
                raise IndexError
        c = StrandSet.RemoveStrandCommand(self._strandList, strand, strandSetIdx)
        self._execCommandList([c], desc="Delete strand", useUndoStack=useUndoStack)
        return strandSetIdx

    def mergeStrands(self, lowStrand, highStrand, lowHasPriority):
        """
        Merge the lowStrand and highStrand into a single new strand.
        The oligo of priority should be propagated to the other and all of
        its connections.
        """
        idx = None # need to set this properly
        c = StrandSet.MergeCommand(lowStrand, highStrand, idx, lowHasPriority)
        self._execCommandList([c], desc="Merge", useUndoStack=useUndoStack)

    def splitStrand(self, strand, idx):
        "Break strand into two strands"
        pass

    def destroy(self):
        self.setParent(None)
        self.deleteLater()  # QObject will emit a destroyed() Signal

    ### PUBLIC SUPPORT METHODS ###
    def undoStack(self):
        if self._undoStack == None:
            self._undoStack = self._virtualhelix.undoStack()
        return self._undoStack

    def virtualhelix(self):
        return self._virtualhelix

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
        # match on whether the testStrand's lowIndex is
        # within the range of the qStrand
        if sSetIndexLow > -1:
            testStrands = iter(strandList[rangeIndexLow:])
            testStrand = testStrands.next()
            qHigh += 1  # bump it up for a more efficient comparison
            i = 0   # use this to
            while testStrand and testStrand.lowIdx() < qHigh:
                yield testStrand
                # use a nex and a default to cause a break condition
                testStrand = next(testStrands, None)
                i += 1
            # end while

            # cache the last index we left of at
            i = sSetIndexLow + i
            """
            if
            1. we ran out of strands to test adjust
            and
            2. the end condition testStrands highIndex is still inside the
            qstrand but not equal to the end point
                adjust i down 1
            otherwise
            """
            if not testStrand and testStrand.highIdx() < qHigh - 1:
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
        lenStrands = len(strandList)
        if lenStrands == 0:
            return None
        # end if

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
            testStrand = strandList[lSI]
            tLow, tHigh = testStrand.idxs()
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

    def _execCommandList(self, commands, desc=None, useUndoStack=False):
        """
        This is a wrapper for performing QUndoCommands, meant to ensure
        uniform handling of the undoStack and macro descriptions.

        When using the undoStack, commands are pushed onto self.undoStack()
        as part of a macro with description desc. Otherwise, command redo
        methods are called directly.
        """
        if useUndoStack:
            self.undoStack().beginMacro(commandDescription)
            for c in commands:
                self.undoStack().push(c)
            self.undoStack().endMacro()
        else:
            for c in commands:
                c.redo()
    # end def

    ### COMMANDS ###
    class AddStrandCommand(QUndoCommand):
        """Inserts strandToAdd into strandList at index idx."""
        def __init__(self, strandList, strand, strandSetIdx):
            super(StrandSet.AddStrandCommand, self).__init__()
            self._strandList = strandList
            self._strand = strand
            self._sSetIdx = strandSetIdx

        def redo(self):
            print "AddStrandCommand", self._strand, self._sSetIdx
            self._strandList.insert(self._sSetIdx, self._strand)
            # if useUndoStack:  # how should the command gain access to this?
            #     self.strandAddedSignal.emit(self._strand)

        def undo(self):
            self._strandList.pop(self._sSetIdx)
            # if useUndoStack:
            #     self.strand.strandRemovedSignal.emit()
    # end class

    class RemoveStrandCommand(QUndoCommand):
        """docstring for RemoveStrandCommand"""
        def __init__(self, strandList, strand, strandSetIdx):
            super(StrandSet.RemoveStrandCommand, self).__init__()
            self._strandList = strandList
            self._strand = strand
            self._sSetIdx = strandSetIdx

        def redo(self):
            self._strandList.pop(self.sSetIdx)

        def undo(self):
            self._strandList.insert(self.sSetIdx, self._strand)
    # end class

    class MergeCommand(QUndoCommand):
        """
        Must pass this two different strands, and nominally one of the strands 
        again which is the priorityStrand.  The resulting "merged" strand has 
        the properties of the priorityStrand's oligo.  Decorators are preserved

        the strandLow and strandHigh must be presorted such that strandLow
        has a lower range than strandHigh

        lowStrandSetIdx should be known ahead of time as a result of selection
        """
        def __init__(self, strandLow, strandHigh, lowStrandSetIdx, priorityStrand):
            super(StrandSet.MergeCommand, self).__init__()
            self._strandLow = strandLow
            self._strandHigh = strandHigh
            pS = priorityStrand
            self._sSet = sSet = pS.strandSet()

            # the oligos
            self._newOligo = pS.oligo().shallowCopy()
            self._sLowOligo = strandLow.oligo()
            self._sHighOligo = strandHigh.oligo()
            # update the oligo for things like its 5prime end and isLoop
            self._newOligo.strandsMergeUpdate(strandLow, strandHigh)

            # THIS BREAKS ISOLATION FROM STRANDSET IF IT IS IN STRAND
            self._idx = lowStrandSetIdx

            # create the newStrand by copying the priority strand to
            # preserve its stuff
            newIdxs = strandLow.lowIdx(), strandHigh.highIdx()
            newStrand = strandLow.shallowCopy()
            newStrand.setIdxs(*newIdxs)
            # newStrand.setLowConnection(strandLow.lowConnection())
            newStrand.setHighConnection(strandHigh.highConnection())

            # take care of merging decorators
            newStrand.addDecorators(strandHigh.decorators())

            self._newStrand = newStrand
        # end def

        def redo(self):
            sS = self._sSet
            sL = self._strandLow
            sH = self._strandHigh
            nS = self._newStrand
            idx = self._idx
            olg = self._newOligo
            lOlg = self._sLowOligo
            hOlg = self._sHighOligo

            # Remove old strands to the sSet  (orders matter)
            sS.removeStrand(sL, idx)
            sS.removeStrand(sH, idx)

            # add the newStrand to the sSet
            sS.addStrand(nS, idx)

            # set ALL of the oligos
            # this will also emit a Signal to Alert the views
            # map(lambda x: Strand.setOligo(x, olg), olg.strand5p())
            starmapExec(Strand.setOligo, izip(olg.strand5p(), repeat(olg)))

            # add and remove the old oligos from the part
            olg.add()
            lOlg.remove()
            hOlg.remove()

            # emit Signals related to brand new stuff and destroyed stuff LAST

            # out with the old...
            sL.destroyedSignal.emit(sL)
            sH.destroyedSignal.emit(sH)

            # ...in with the new
            sS.strandAddedSignal.emit(nS)
        # end def

        def undo(self):
            sS = self._sSet
            sL = self._strandLow
            sH = self._strandHigh
            nS = self._newStrand
            idx = self._idx
            olg = self._newOligo
            lOlg = self._sLowOligo
            hOlg = self._sHighOligo

            # Remove new strand from the sSet
            sS.removeStrand(nS, idx)

            # add the old Strands to the sSet (orders matter)
            sS.addStrand(sH, idx)
            sS.addStrand(sL, idx)

            # reset ALL of the oligos back
            # this will also emit a Signal to Alert the views
            # map(lambda x: Strand.setOligo(x, lOlg), lOlg.strand5p())
            # map(lambda x: Strand.setOligo(x, hOlg), hOlg.strand5p())
            starmapExec(Strand.setOligo, izip(lOlg.strand5p(), repeat(lOlg)))
            starmapExec(Strand.setOligo, izip(hOlg.strand5p(), repeat(hOlg)))

            # add and remove the old oligos from the part
            olg.remove()
            lOlg.add()
            hOlg.add()

            # emit Signals related to brand new stuff and destroyed stuff LAST

            # out with the new...
            nS.destroyedSignal.emit(nS)

            # ...in with the old
            sS.strandAddedSignal.emit(sH)
            sS.strandAddedSignal.emit(sL)
        # end def
    # end class

    class SplitCommand(QUndoCommand):
        """
        The most 5 prime new strand retains the oligo properties
        of the original longer strand.  This new strand has the same 5 prime
        end index as the original longer strand.

        virtualIndex is the 3 prime end of the most 5 prime new strand
        """
        def __init__(self, strand, strandIdx, virtualIndex):
            super(StrandSet.SplitCommand, self).__init__()
            self._strandOld = strand
            self._strandIdx = strandIdx
            self._sSet = sSet = strand.strandSet()
            self._oldOligo = oligo = strand.oligo()

            # create the newStrand by copying the priority strand to
            # preserve its stuff
            # calculate strand directionality for which strand the
            # 3p priority end is

            # create copies
            self._strandLow = strandLow = strand.shallowCopy()
            self._strandHigh = strandHigh = strand.shallowCopy()
            self._lOligo = lOligo = oligo.shallowCopy()
            self._hOligo = hOligo = oligo.shallowCopy()

            if strand.isDrawn5to3():
                # strandLow has priority
                iNewLow = virtualIndex
                colorLow, colorHigh = oligo.color(), NEWCOLOR
                olg5p, olg3p = lOligo, hOligo
                std5p, std3p = strandLow, strandHigh
            # end if
            else:
                # strandHigh has priority
                iNewLow = virtualIndex - 1
                colorLow, colorHigh = NEWCOLOR, oligo.color()
                olg5p, olg3p = hOligo, lOligo
                std5p, std3p = strandHigh, strandLow
            # end else

            # Update the Strands
            strandLow.setHighConnection(None)
            strandLow.setIdxs(strand.lowIdx(), iNewLow)
            strandHigh.setLowConnection(None)
            strandHigh.setIdxs(iNewLow + 1, strand.highIdx())

            # Update the oligos
            lOligo.setColor(colorLow)
            hOligo.setColor(colorHigh)
            # update the oligo for things like its 5prime end and isLoop
            olg5p.strandsSplitUpdate(std5p, std3p, olg3p, strand)

            # take care of splitting up decorators
            strandLow.removeDecoratorsOutOfRange()
            strandHigh.removeDecoratorsOutOfRange()
        # end def

        def redo(self):
            sS = self._sSet
            sL = self._strandLow
            sH = self._strandHigh
            oS = self._oldStrand
            strandIdx = self._strandIdx
            olg = self._oldOligo
            lOlg = self._sLowOligo
            hOlg = self._sHighOligo

            # Remove oldAtrand from the sSet
            sS.removeStrand(oS, strandIdx)

            # add the new Strands to the sSet (orders matter)
            sS.addStrand(sH, strandIdx)
            sS.addStrand(sL, strandIdx)

            # set ALL of the oligos
            # this will also emit a Signal to Alert the views
            starmapExec(Strand.setOligo, izip(lOlg.strand5p(), repeat(lOlg)))
            starmapExec(Strand.setOligo, izip(hOlg.strand5p(), repeat(hOlg)))

            # add and remove the old oligos from the part
            olg.remove()
            lOlg.add()
            hOlg.add()

            # emit Signals related to brand new stuff and destroyed stuff LAST

            # out with the old...
            nS.destroyedSignal.emit(oS)

            # ...in with the new
            sS.strandAddedSignal.emit(sH)
            sS.strandAddedSignal.emit(sL)
        # end def

        def undo(self):
            sS = self._sSet
            sL = self._strandLow
            sH = self._strandHigh
            oS = self._oldStrand
            strandIdx = self._strandIdx
            olg = self._oldOligo
            lOlg = self._sLowOligo
            hOlg = self._sHighOligo

            # Remove new strands to the sSet (order matters)
            sS.removeStrand(sL, strandIdx)
            sS.removeStrand(sH, strandIdx)

            # add the oldStrand to the sSet
            sS.addStrand(oS, strandIdx)

            # reset ALL of the oligos back
            # this will also emit a Signal to alert the views
            starmapExec(Strand.setOligo, izip(olg.strand5p(), repeat(olg)))

            # add and remove the old oligos from the part
            olg.add()
            lOlg.remove()
            hOlg.remove()

            # emit Signals related to brand new stuff and destroyed stuff LAST

            # out with the new...
            sL.destroyedSignal.emit(sL)
            sH.destroyedSignal.emit(sH)

            # ...in with the old
            sS.strandAddedSignal.emit(oS)
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
        ss = StrandSet(None)
        ss.partBounds = Mock(return_value=(0, 42))
        ss.addStrand(Strand(ss, 1, 5), 0, False)
        assert len(ss._strandList) == 1

    # @with_setup(setUp, tearDown)
    def test_getBoundsOfEmptyRegionContaining(self):
        ss = StrandSet(None)
        ss.partBounds = Mock(return_value=(0, 42))
        ss.addStrand(Strand(ss, 1, 5), 0, False)
        ss.addStrand(Strand(ss, 10, 20), 1, False)
        assert ss.getBoundsOfEmptyRegionContaining(0) == (0, 0)
        assert ss.getBoundsOfEmptyRegionContaining(6) == (6, 9)
        assert ss.getBoundsOfEmptyRegionContaining(7) == (6, 9)
        assert ss.getBoundsOfEmptyRegionContaining(8) == (6, 9)
        assert ss.getBoundsOfEmptyRegionContaining(9) == (6, 9)
        assert ss.getBoundsOfEmptyRegionContaining(21) == (21, 42)
        assert ss.getBoundsOfEmptyRegionContaining(30) == (21, 42)
        assert ss.getBoundsOfEmptyRegionContaining(42) == (21, 42)
        ss.addStrand(Strand(ss, 30, 35), 2, False)
        assert ss.getBoundsOfEmptyRegionContaining(21) == (21, 29)
        assert ss.getBoundsOfEmptyRegionContaining(36) == (36, 42)

