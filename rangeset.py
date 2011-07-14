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

class RangeSet():
    """
    Represents a subset of the integers that can be
    efficiently represented as a finite list of ranges, and
    allows the attachment of metadata to each index.
    There is a close analogy between a RangeSet and a dictionary.
    In the unit tests, this analogy is taken advantage of (look
    for variables named rs and rd, for RangeSet and dict respectively).
    The dictionary maps integers to arbitrary values. The difference
    is that the operation
    
    for i in range(5, 103):
        analogousDict[i] = key
    
    is fast, memory efficient, and looks like
    
    rangeSet.addRange(5, 103, key)
    
    and analogousDict.get(...) and rangeSet.get(...) correspond.
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
            rdat = self.ranges[i + 1][2:]
            if ll == rf:
                # Adjacent ranges containing the same metadata
                # MUST be merged
                if ldat == rdat:
                    for j in rangeIntersection([0, len(self.ranges)], [i - 3, i + 3]):
                        print "self.ranges[%i]: %s"%(j, self.ranges)
                    print "Problem between items at idx %i, %i (same metadata, not merged)"\
                          %(i, i + 1)
                    assert(ldat != rdat)

    ############################### Public Read API ###########################

    def get(self, idx, retvalOnIdxNotInSelf=None):
        """
        In the analogy to dict, rs.get is identical to rd.get.
        Returns the metadata at idx or retvalOnIndexNotInSelf if
        idx is not in the receiver.
        """
        idx = self._idxOfRangeContaining(idx)
        if idx == None:
            return retvalOnIdxNotInSelf
        return self.ranges[idx][2]

    def __contains__(intVal):
        """
        In the analogy to dict, checks to see if intVal is in the
        set of keys.
        """
        return self._idxOfRangeContaining(intVal) != None

    def containsAllInRange(rangeStart, afterRangeEnd):
        """
        Returns weather or not the receiver contains all i st
        rangeStart <= i < afterRangeEnd
        """
        idxRange = self._idxRangeOfRangesIntersectingRange(rangeStart, rangeEnd)
        previousLastIdx = None
        for i in range(*idxRange):
            if previousLastIdx == None:
                previousLastIdx = self.ranges[i][1]
            else:
                if previousLastIdx != self.ranges[i][0]:
                    return False
        return True

    def containsAnyInRange(rangeStart, rangeEnd):
        idxRange = self._idxRangeOfRangesIntersectingRange(rangeStart, rangeEnd)
        return idxRange[1] - idxRange[0] > 0

    ################################ Public Write API ############################
    def add(self, index, metadata=True):
        self.addRange(index, index+1, metadata)

    def addRange(self, firstIndex, afterLastIndex, metadata=True):
        if firstIndex >= afterLastIndex:
            return
        intersectingIdxRange = self._idxRangeOfRangesIntersectingRange(firstIndex - 1,
                                                                       afterLastIndex + 1)
        # (first Index (into self.ranges) of an Intersecting Range)
        firstIIR, afterLastIIR = intersectingIdxRange
        if afterLastIIR == firstIIR:
            self.ranges.insert(firstIIR, (firstIndex, afterLastIndex, metadata))
            return
        rangesToReplaceExistingIntersectingRanges = [\
                            (firstIndex, afterLastIndex, metadata)]
        # First Intersecting Range {Left idx, After right idx, MetaData}
        firstIRL, firstIRAr, firstIRMD = self.ranges[firstIIR]
        if firstIRL < firstIndex:
            #           [AddRange---------------------)
            #       [FirstIntersectingExistingRange)[...)
            canMergeWithFirstIR = firstIRMD == metadata
            if canMergeWithFirstIR:
                rangesToReplaceExistingIntersectingRanges = [\
                        (firstIRL, afterLastIndex, metadata)]
            else:
                rangesToReplaceExistingIntersectingRanges =    [\
                        (firstIRL, firstIndex, firstIRMD),\
                        (firstIndex, afterLastIndex, metadata) ]
        lastIRL, lastIRAr, lastIRMD = self.ranges[afterLastIIR - 1]
        if lastIRAr > afterLastIndex:
            canMergeWithLastIR = lastIRMD == metadata
            if canMergeWithLastIR:
                oldLastReplacementRange = rangesToReplaceExistingIntersectingRanges.pop()
                newLastReplacementRange = (\
                            oldLastReplacementRange[0],\
                            lastIRAr,\
                            metadata      )
                rangesToReplaceExistingIntersectingRanges.append(newLastReplacementRange)
            else:
                newLastReplacementRange = (afterLastIndex, lastIRAr, lastIRMD)
                rangesToReplaceExistingIntersectingRanges.append(newLastReplacementRange)
        self.ranges[firstIIR:afterLastIIR] = rangesToReplaceExistingIntersectingRanges

    def removeRange(self, firstIndex, afterLastIndex):
        if firstIndex >= afterLastIndex:
            return
        intersectingIdxRange = self._idxRangeOfRangesIntersectingRange(firstIndex,
                                                                       afterLastIndex)
        rangesToReplaceExistingIntersectingRanges = []
        # (first Index (into self.ranges) of an Intersecting Range)
        firstIIR, afterLastIIR = intersectingIdxRange
        if afterLastIIR == firstIIR:
            return
        firstIRL, firstIRAr, firstIRMD = self.ranges[firstIIR]
        if firstIRL < firstIndex:
            rangesToReplaceExistingIntersectingRanges.append((\
                    firstIRL, firstIndex, firstIRMD\
                                                            ))
        lastIRL, lastIRAr, lastIRMD = self.ranges[afterLastIIR - 1]
        if lastIRAr > afterLastIndex:
            rangesToReplaceExistingIntersectingRanges.append((\
                    afterLastIndex, lastIRAr, lastIRMD\
                                                            ))
        self.ranges[firstIIR:afterLastIIR] = rangesToReplaceExistingIntersectingRanges

    ################################ Private Read API #############################
    def _idxOfRangeContaining(self, intVal, returnTupledIdxOfNextRangeOnFail=False):
        """
        Returns the index in self.ranges of the range
        containing intVal or None if none does.
        """
        ranges = self.ranges
        if not ranges:
            if returnTupledIdxOfNextRangeOnFail:
                return (0,)
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
        