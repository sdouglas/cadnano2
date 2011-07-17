def rangeIntersection(firstRange, secondRange):
    ff, fl = firstRange
    sf, sl = secondRange
    if ff >= fl:
        return [0, 0]
    if sf >= sl:
        return [0, 0]
    l, r = max(ff, sf), min(fl, sl)
    if l >= r:
        return [0, 0]
    return [l, r]

class RangeSet(object):
    """
    Represents a set of objects (rangeItems or RIs) that each conceptually
    occupy a contiguous subset of the integers under the additional constraints
    1) no two items in the set overlap (occupy an identical integer)
    2) any two adjacent items a, b st canMergeRangeItems(a,b) == True upon
       insertion of the last one to be inserted will be merged
    """
    def __init__(self):
        self.ranges = []

    ############################### Invariants ###########################
    def assertConsistency(self):
        """
        Raises an exception if the receiver's invariants
        are not maintained
        """
        for i in range(len(self.ranges)):
            f, l = self.idxs(self.ranges[i])
            assert(f < l)  # All ranges contain an index
        for i in range(len(self.ranges)-1):
            # Naming convention:
            # {l:left, r:right}{f:firstIdx, l:afterLastIdx}
            lf, ll = self.idxs(self.ranges[i])
            rf, rl = self.idxs(self.ranges[i + 1])
            if ll > rf:
                # Ranges are sorted, don't overlap
                for j in range(*rangeIntersection([0, len(self.ranges)], [i - 3, i + 3])):
                    print "self.ranges[%i]: %s"%(j, self.ranges[j])                
                print "Problem between items at idx %i, %i (can be merged, not merged)"\
                      %(i, i + 1)
                assert(False)  
            if ll == rf:
                # Adjacent ranges containing the same metadata
                # MUST be merged
                if self.canMergeRangeItems(self.ranges[i], self.ranges[i + 1]):
                    for j in range(*rangeIntersection([0, len(self.ranges)], [i - 3, i + 3])):
                        print "self.ranges[%i]: %s"%(j, self.ranges[j])
                    print "Problem between items at idx %i, %i (can be merged, not merged)"\
                          %(i, i + 1)
                    assert(False)

    ############################### Framework ###########################
    # If you want a RangeSet that stores something other than tuples of
    # integers representing ranges of indexes, these are the methods to override

    def idxs(self, rangeItem):
        """
        Returns (firstIdx, afterLastIdx) simplified representation of the
        rangeItem passed in.
        """
        return rangeItem[0:2]

    def canMergeRangeItems(self, leftRangeItem, rightRangeItem):
        ll, lr = self.idxs(leftRangeItem)
        rl, rr = self.idxs(rightRangeItem)
        sameMetadata = leftRangeItem[2] == rightRangeItem[2]
        separated = lr < rl
        correctOrder = ll < rl
        return sameMetadata and not separated and correctOrder

    def mergeRangeItems(self, leftRangeItem, rightRangeItem, undoStack=None):
        """
        If a subclass needs to support undo, it should push whatever it does
        here onto undoStack (iff undoStack is not None). It can also just return
        an entirely new object in which case undo will be handled automatically.
        """
        return (leftRangeItem[0], rightRangeItem[1], leftRangeItem[2])

    def changeRangeForItem(self, rangeItem, newStartIdx, newAfterLastIdx, undoStack=None):
        """
        Changes the range corresponding to rangeItem.
        Careful, this isn't a public method. It gets called to notify a subclass
        of a change, not to effect the change itself.

        If a subclass needs to support undo, it should push whatever it does
        here onto undoStack (iff undoStack is not None). It can also just return
        an entirely new object in which case undo will be handled automatically.
        """
        return (newStartIdx, newAfterLastIdx, rangeItem[2])

    def willRemoveRangeItem(self, rangeItem):
        """
        Gets called on a rangeItem that used to be in self.ranges but will
        no longer be in self.ranges.
        """
        pass

    def didInsertRangeItem(self, rangeItem):
        """
        Gets called on a rangeItem that has just been inserted into self.ranges.
        """
        pass

    def boundsChanged(self):
        """
        Gets called whenever something in the write API causes the value
        returned by bounds() to change.
        """
        pass

    def defaultUndoStack(self):
        return None

    ############################### Public Read API ###########################

    def get(self, idx, retvalOnIdxNotInSelf=None):
        """
        In the analogy to dict, rs.get is identical to rd.get.
        Returns the range at idx or retvalOnIndexNotInSelf if
        idx is not in any range of the receiver.
        """
        idx = self._idxOfRangeContaining(idx)
        if idx == None:
            return retvalOnIdxNotInSelf
        return self.ranges[idx]

    def __getitem__(self, idx):
        return nself.get(idx)

    def __contains__(self, intVal):
        """
        In the analogy to dict, checks to see if intVal is in the
        set of keys.
        """
        return self._idxOfRangeContaining(intVal) != None

    def bounds(self):
        """
        Returns a range tuple (lowestIdx, oneAfterHighestIdx) that would contain
        every range in the receiver.
        """
        if len(self.ranges) == 0:
            return (0, 0)
        ff, fl = self.idxs(self.ranges[0])
        lf, ll = self.idxs(self.ranges[-1])
        return (ff, ll)

    def containsAllInRange(rangeStart, afterRangeEnd):
        """
        Returns weather or not the receiver contains all i st
        rangeStart <= i < afterRangeEnd
        """
        idxRange = self._idxRangeOfRangesIntersectingRange(rangeStart, rangeEnd)
        previousLastIdx = None
        for i in range(*idxRange):
            l, r = self.idxs(self.ranges[i])
            if previousLastIdx == None:
                previousLastIdx = r
            else:
                if previousLastIdx != l:
                    return False
                previousLastIdx = r
        return True

    def containsAnyInRange(rangeStart, rangeEnd):
        idxRange = self._idxRangeOfRangesIntersectingRange(rangeStart, rangeEnd)
        return idxRange[1] - idxRange[0] > 0

    def __iter__(self):
        """
        Iterate over the range items in self.
        """
        return self.ranges.__iter__()

    ################################ Public Write API ############################
    def addRange(self, rangeItem, undoStack=True):
        """
        Adds rangeItem to the receiver, ensuring that the range given by
        self.idxs(rangeItem) does not overlap any other rangeItem in the receiver
        (this is enforced by deleting or truncating any rangeItems in the way)
        and tries to merge the newly inserted rangeItem with its neighbors.
        """
        firstIndex, afterLastIndex = self.idxs(rangeItem)
        if firstIndex >= afterLastIndex:
            return
        oldBounds = self.bounds()
        if undoStack == True:
            undoStack = self.defaultUndoStack()
        if undoStack != None:
            undoStack.beginMacro('RangeSet.addRange')
        intersectingIdxRange = self._idxRangeOfRangesIntersectingRange(firstIndex - 1,
                                                                       afterLastIndex + 1)
        # (first Index (into self.ranges) of an Intersecting Range)
        firstIIR, afterLastIIR = intersectingIdxRange
        if afterLastIIR == firstIIR:
            self.ranges.insert(firstIIR, rangeItem)
            return
        rangesToReplaceExistingIntersectingRanges = [rangeItem]
        # First Intersecting Range {Left idx, After right idx, MetaData}
        firstIR = self.ranges[firstIIR]
        firstIRL, firstIRAr = self.idxs(firstIR)
        if firstIRL < firstIndex:
            #           [AddRange---------------------)
            #       [FirstIntersectingExistingRange)[...)
            if self.canMergeRangeItems(firstIR, rangeItem):
                newItem = self.mergeRangeItems(firstIR,\
                                               rangeItem,\
                                               undoStack=undoStack)
                rangesToReplaceExistingIntersectingRanges = [newItem]
            else:
                newItem = self.changeRangeForItem(firstIR,\
                                                  firstIRL,\
                                                  firstIndex)
                rangesToReplaceExistingIntersectingRanges = [newItem, rangeItem]
        lastIR = self.ranges[afterLastIIR - 1]
        lastIRL, lastIRAr = self.idxs(lastIR)
        if lastIRAr > afterLastIndex:
            if self.canMergeRangeItems(rangeItem, lastIR):
                oldLastReplacementItem = rangesToReplaceExistingIntersectingRanges.pop()
                newItem = self.mergeRangeItems(oldLastReplacementItem,\
                                               lastIR,\
                                               undoStack=undoStack)
                rangesToReplaceExistingIntersectingRanges.append(newItem)
            else:
                newItem = self.changeRangeForItem(lastIR,\
                                                  afterLastIndex,\
                                                  lastIRAr)
                rangesToReplaceExistingIntersectingRanges.append(newItem)
        com = self.ReplaceRangeItemsCommand(self,\
                                      firstIIR,\
                                      afterLastIIR,\
                                      rangesToReplaceExistingIntersectingRanges)
        if undoStack != None:
            undoStack.push(com)
            undoStack.endMacro()
        else:
            com.redo()
        if oldBounds != self.bounds():
            self.boundsChanged()

    def removeRange(self, firstIndex, afterLastIndex, undoStack=True):
        if firstIndex >= afterLastIndex:
            return
        oldBounds = self.bounds()
        if undoStack == True:
            undoStack = self.defaultUndoStack()
        if undoStack != None:
            undoStack.beginMacro('RangeSet.addRange')
        intersectingIdxRange = self._idxRangeOfRangesIntersectingRange(firstIndex,
                                                                       afterLastIndex)
        rangesToReplaceExistingIntersectingRanges = []
        # (first Index (into self.ranges) of an Intersecting Range)
        firstIIR, afterLastIIR = intersectingIdxRange
        if afterLastIIR == firstIIR:
            return
        firstIR = self.ranges[firstIIR]
        firstIRL, firstIRAr = self.idxs(firstIR)
        if firstIRL < firstIndex:
            newItem = self.changeRangeForItem(firstIR, firstIRL, firstIndex)
            rangesToReplaceExistingIntersectingRanges.append(newItem)
        lastIR = self.ranges[afterLastIIR - 1]
        lastIRL, lastIRAr = self.idxs(lastIR)
        if lastIRAr > afterLastIndex:
            newItem = self.changeRangeForItem(lastIR, afterLastIndex, lastIRAr)
            rangesToReplaceExistingIntersectingRanges.append(newItem)
        com = self.ReplaceRangeItemsCommand(self,\
                                      firstIIR,\
                                      afterLastIIR,\
                                      rangesToReplaceExistingIntersectingRanges)
        if undoStack != None:
            undoStack.push(com)
            undoStack.endMacro()
        else:
            com.redo()
        if oldBounds != self.bounds():
            self.boundsChanged()

    def resizeRangeAtIdx(self, idx, newFirstIndex, newAfterLastIdx, undoStack=True):
        """
        Finds the largest contiguous range of indices in the receiver that includes
        idx and changes it 
        """
        rangeItemIdx = self._idxOfRangeContaining(idx)
        if rangeItemIdx == None:
            desc = 'RangeSet %s was asked to resize a nonexistant range at %i'%\
                                                            (self, rangeItemIdx)
            raise TypeError(desc)
        rangeItem = self.ranges[ri]
        self.ranges[rangeItem:rangeItem + 1] = []
        self.changeRangeForItem(rangeItem)
        self.addRange(rangeItem)

    ################################ Private Write API #########################
    class ReplaceRangeItemsCommand(object):
        def __init__(self, rangeSet, firstIdx, afterLastIdx, replacementRIs):
            self.rangeSet = rangeSet
            self.firstIdx = firstIdx
            self.afterLastIdx = afterLastIdx
            self.replacementRIs = replacementRIs
        def redo(self):
            rangeArr = self.rangeSet.ranges
            self.replacedRIs = rangeArr[self.firstIdx:self.afterLastIdx]
            replacedSet = set(self.replacedRIs)
            replacementSet = set(self.replacementRIs)
            for ri in replacedSet - replacementSet:
                self.rangeSet.willRemoveRangeItem(ri)
            rangeArr[self.firstIdx:self.afterLastIdx] = self.replacementRIs
            for ri in replacementSet - replacedSet:
                self.rangeSet.didInsertRangeItem(ri)
        def undo(self):
            assert(self.replacedRIs)  # Must redo before undo
            replacedSet = set(self.replacementRIs)
            replacementSet = set(self.replacedRIs)
            for ri in replacedSet - replacementSet:
                self.rangeSet.willRemoveRangeItem(ri)
            lastIdx = len(self.replacementSet)
            rangeArr = self.rangeSet.ranges
            rangeArr[self.firstIdx:lastIdx] = self.replacedRIs
            for ri in replacementSet - replacedSet:
                self.rangeSet.didInsertRangeItem(ri)

    ################################ Private Read API ##########################
    def _idxOfRangeContaining(self, intVal, returnTupledIdxOfNextRangeOnFail=False):
        """
        Returns the index in self.ranges of the range
        containing intVal or None if none does.
        """
        if not self.ranges:
            if returnTupledIdxOfNextRangeOnFail:
                return (0,)
            return None
        # m <= the index of any range containing
        # intVal, M >= the index of any range containing
        # intVal.
        m, M = 0, len(self.ranges)-1
        while m <= M:
            mid = (m+M)/2
            rangeItem = self.ranges[mid]
            l, r = self.idxs(rangeItem)
            if r <= intVal:
                m = mid + 1
            elif l > intVal:
                M = mid - 1
            else:  # v and r[mid][0] <= intVal < r[mid][1]
                return mid
        if returnTupledIdxOfNextRangeOnFail:
            # The tuple is an indicator that the search failed
            return (m,)
        return None

    def _idxRangeOfRangesIntersectingRange(self, rangeStart, rangeEnd):
        """
        Returns a range (first, afterLast) of indices into self.ranges,
        where the range represented by each index intersects [rangeStart,rangeEnd)
        """
        if rangeStart >= rangeEnd:
            return [0, 0]  # Empty range
        idx = self._idxOfRangeContaining(rangeStart,\
                                         returnTupledIdxOfNextRangeOnFail=True)
        lenRanges = len(self.ranges)
        if not isinstance(idx, (int, long)):
            # idx is a tuple containing an integer indexing in ranges
            # to the first range intersecting [rangeStart, infinity)
            # or len(ranges)+1 because one couldn't be found
            assert(isinstance(idx, (list, tuple)))
            idx = idx[0]
        if idx >= lenRanges:
            return [lenRanges, lenRanges]  # Empty range
        # idx now refers to the location in self.ranges of the first
        # range intersecting [rangeStart, infinity)
        lastIdx = idx
        while True:
            if lastIdx >= lenRanges:
                return [idx, lastIdx]
            f, l = self.idxs(self.ranges[lastIdx])
            if f >= rangeEnd:
                return [idx, lastIdx]
            lastIdx += 1
        assert(False)

    def _invalidateCaches(self):
        pass
    
    ############# Slow but sure methods for unit testing ##############
    
    def _slowIdxOfRangeContaining(self, intVal, returnTupledIdxOfNextRangeOnFail=False):
        for i in range(len(self.ranges)):
            rangeItem = self.ranges[i]
            l, r = self.idxs(rangeItem)
            if l <= intVal < r:
                return i
            if l > intVal and returnTupledIdxOfNextRangeOnFail:
                return (i,)
        if returnTupledIdxOfNextRangeOnFail:
            return (len(self.ranges),)
        return None

    def _slowIdxRangeOfRangesIntersectingRange(self, rangeStart, rangeEnd):
        if rangeStart >= rangeEnd:
            return [0,0]
        firstIdx = None
        for i in range(len(self.ranges)):
            rangeItem = self.ranges[i]
            f, l = self.idxs(rangeItem)
            leftOfTarget = l <= rangeStart
            rightOfTarget = f >= rangeEnd
            if not leftOfTarget and firstIdx == None:
                firstIdx = i
            if rightOfTarget:
                if firstIdx == None:
                    firstIdx = i
                return [firstIdx, i]
        if firstIdx == None:
            firstIdx = len(self.ranges)
        return [firstIdx, len(self.ranges)]
        