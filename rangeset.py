class RangeSet():
    """
    Represents a subset of the integers that can be
    efficiently represented as a finite list of ranges
    """
    def __init__(self):
        # Each range is stored as a tuple
        # (firstIdx, afterLastIdx, ...)
        # A range r contains i iff firstIdx <= i < afterLastIdx.
        self.ranges = []

    def assertConsistency(self):
        """
        Raises an exception if the receiver's invariants
        are not maintained
        """
        for i in range(len(self.ranges)):
            f, l, md = self.ranges[i]
            assert(f < l)  # All ranges contain an index
        for i in range(len(self.ranges)-1):
            # Naming convention:
            # {l:left, r:right}{f:firstIdx, l:afterLastIdx}
            lf, ll, lmd = self.ranges[i]
            rf, rl, rmd = self.ranges[i + 1]
            assert(ll <= rf)  # Ranges are sorted, don't overlap
            ldat = self.ranges[i][2:]
            rdat = self.ranges[i][2:]
            if ll == rf:
                # Adjacent ranges containing the same metadata
                # MUST be merged
                assert(ldat == rdat)

    ############################### Public Read API ###########################

    def __contains__(intVal):
        """
        The defining set operation.
        """
        return self._idxOfRangeContaining(intVal) != None

    def containsAllInRange(rangeStart, afterRangeEnd):
        """
        Returns weather or not the receiver contains all i st
        rangeStart <= i < afterRangeEnd
        """
        if rangeStart >= afterRangeEnd:
            return True
        idx = self._idxOfRangeContaining(intVal)
        if idx == None:
            return False
        ranges = self.ranges
        lenRanges = len(ranges)
        while True:
            endCurrentRange = ranges[idx][1]
            if endCurrentRange >= afterRangeEnd:
                return True
            # endCurrentRange < afterRangeEnd
            idx += 1
            if idx >= lenRanges:
                # If there is no next range, the receiver
                # cannot possibly contain rangeEnd
                return False
            # There is a next range, but is there a gap between
            # it and the previous range?
            if endCurrentRange != ranges[idx][0]:
                return False
        assert(False)

    def containsAnyInRange(rangeStart, rangeEnd):
        if rangeStart >= rangeEnd:
            return False
        firstPossibleIdx = self._idxOfRangeContaining(rangeStart,\
                                                      returnTupledIdxOfNextRangeOnFail=True)
        ranges = self.ranges
        if isinstance(firstPossibleIdx, (int, long)):
            return True
        if firstPossibleIdx >= len(ranges):
            return False

    ################################ Public Write API ############################
    def add(index, metadata=None):
        self.addRange(index, index+1, metadata)

    def addRange(firstIndex, afterLastIndex, metadata=None):
        intersectingIdxRange = self._idxRangeOfRangesIntersectingRange(firstIndex,
                                                                       afterLastIndex)
        # FFirst range, {FFirst index, afterLLast index, MMetaDData}
        dontKillFirstII, dontKillLastII = False, False
        firstIntersectingRange = self.ranges[intersectingIdxs[0]]
        ff, fl, fmd = firstIntersectingRange
        if ff < firstIndex:
            firstIntersectingRange[1] = firstIndex
            dontKillFirstII = True
        lastIntersectingRange = self.ranges[intersectingIdxs[-1]]
        lf, ll, lmd = lastIntersectingRange
        if firstIntersectingRange != lastIntersectingRange\
           and lf < afterLastIndex\
           and ll > afterLastIndex:
            lastIntersectingRange[0] = afterLastIndex
            dontKillLastII = True

    ################################ Private Read API #############################
    def _idxOfRangeContaining(self, intVal, returnTupledIdxOfNextRangeOnFail=False):
        """
        Returns the index in self.ranges of the range
        containing intVal or None if none does.
        """
        ranges = self.ranges
        if not ranges:
            return None
        # m <= the index of any range containing
        # intVal, M >= the index of any range containing
        # intVal.
        m, M = 0, len(ranges)-1
        while m <= M:
            mid = (m+M)/2
            if ranges[mid][1] <= intVal:
                m = mid + 1
            elif ranges[mid][0] > intVal:
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
        ranges = self.ranges
        lenRanges = len(ranges)
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
            f, l, md = ranges[lastIdx]
            if f >= rangeEnd:
                return [idx, lastIdx]
            lastIdx += 1
        assert(False)

    def _invalidateCaches(self):
        pass
    
    ############# Slow but sure methods for unit testing ##############
    
    def _slowIdxOfRangeContaining(self, intVal, returnTupledIdxOfNextRangeOnFail=False):
        for i in range(len(self.ranges)):
            r = self.ranges[i]
            if r[0] <= intVal < r[1]:
                return i
            if r[0] > intVal and returnTupledIdxOfNextRangeOnFail:
                return (i,)
        if returnTupledIdxOfNextRangeOnFail:
            return (len(self.ranges),)
        return None

    def _slowIdxRangeOfRangesIntersectingRange(self, rangeStart, rangeEnd):
        if rangeStart >= rangeEnd:
            return [0,0]
        firstIdx = None
        for i in range(len(self.ranges)):
            f, l, md = self.ranges[i]
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
        