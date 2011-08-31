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

"""
unittests.py

Created by Shawn Douglas on 2011-06-28.
"""

import sys, os
sys.path.insert(0, '.')

import time, code
from PyQt4.QtCore import *
from PyQt4.QtGui import *
import tests.cadnanoguitestcase
from tests.cadnanoguitestcase import CadnanoGuiTestCase
from model.enum import StrandType
from model.virtualhelix import VirtualHelix
import unittest
from rangeset import RangeSet, rangeIntersection
import random
seed = random.Random().randint(0,1<<32)
enviroseed = os.environ.get('UNITTESTS_PRNG_SEED', False)
if enviroseed != False:
    seed = int(enviroseed)
del enviroseed
print "Seeding tests.unittests; use setenv UNITTESTS_PRNG_SEED=%i to replay."%seed


class UnitTests(CadnanoGuiTestCase):
    """
    Unit tests should test individual modules, and do not necessarily need
    to simulate user interaction.

    Create new tests by adding methods to this class that begin with "test".
    See for more detail: http://docs.python.org/library/unittest.html

    Run unit tests by calling "python -m test.unittests" from cadnano2 root
    directory.
    """
    def setUp(self):
        """
        The setUp method is called before running any test. It is used
        to set the general conditions for the tests to run correctly.
        """
        CadnanoGuiTestCase.setUp(self)
        self.prng = random.Random(seed)
        # Add extra unit-test-specific initialization here

    def tearDown(self):
        """
        The tearDown method is called at the end of running each test,
        generally used to clean up any objects created in setUp
        """
        CadnanoGuiTestCase.tearDown(self)
        # Add unit-test-specific cleanup here

    def createTestRangeSet(self):
        """RangeSet createTestRangeSet"""
        ranges = []
        idx = self.prng.randint(-100, 100)
        for i in range(100):
            l = idx
            idx += self.prng.randint(1, 8)
            r = idx
            idx += self.prng.randint(1, 8)
            ranges.append([l, r, i])
        rs = RangeSet()
        rs.ranges = ranges
        rs.assertConsistency()
        return rs

    def testRangeSet_idxOfRangeContaining(self):
        """RangeSet _idxOfRangeContaining"""
        rs = self.createTestRangeSet()
        ranges = rs.ranges
        for i in range(ranges[0][0] - 3, ranges[-1][1] + 3):
            valueByFastMethod = rs._idxOfRangeContaining(i)
            valueBySureMethod = rs._slowIdxOfRangeContaining(i)
            self.assertEqual(valueByFastMethod, valueBySureMethod)
        for i in range(ranges[0][0] - 3, ranges[-1][1] + 3):
            valueByFastMethod = rs._idxOfRangeContaining(i,\
                                       returnTupledIdxOfNextRangeOnFail=True)
            valueBySureMethod = rs._slowIdxOfRangeContaining(i,\
                                       returnTupledIdxOfNextRangeOnFail=True)
            self.assertEqual(valueByFastMethod, valueBySureMethod)

    def testRangeSet_idxRangeOfRangesIntersectingRange(self):
        """RangeSet _idxRangeOfRangesIntersectingRange"""
        rs = self.createTestRangeSet()
        ranges = rs.ranges
        idxMin, idxMax = ranges[0][0], ranges[-1][1]
        for i in range(100):
            l = self.prng.randint(idxMin - 3, idxMax + 3)
            r = l + self.prng.randint(-3, 20)
            valueByFastMethod = rs._idxRangeOfRangesIntersectingRange(l, r)
            valueBySureMethod = rs._slowIdxRangeOfRangesIntersectingRange(l, r)
            self.assertEqual(valueByFastMethod, valueBySureMethod)

    def testRangeSet_rangeIntersection(self):
        """RangeSet intersection"""
        for i in xrange(1000):
            l1 = self.prng.randint(-15, 15)
            r1 = self.prng.randint(-15, 15)
            l2 = self.prng.randint(-15, 15)
            r2 = self.prng.randint(-15, 15)
            realRange1 = set(range(l1, r1))
            realRange2 = set(range(l2, r2))
            realIntersection = realRange1.intersection(realRange2)
            computedIntersection = set(range(\
                             *rangeIntersection((l1, r1), (l2, r2))  ))
            self.assertEqual(realIntersection, computedIntersection)

    def addSomeRangesToRangeSet(self, rangeSet, analagousDict, useUndoStack=False, undoStack=None, testUndo=False):
        """
        Returns (dict, list). The dict maps every index that is a member of
        any inserted range to the metadata (a random integer for test purposes)
        associated with that range. The list is a list of the id(range) of every
        range item that was added to the rangeset at any point.
        """
        addedRangeItems = []
        # Build the rangeset by calling addRange
        for i in range(200):
            initialIdx = self.prng.randint(-100, 100)
            l = self.prng.randint(1, 20)
            tag = self.prng.randint(1,15)
            newRangeItem = (initialIdx, initialIdx + l, tag)
            addedRangeItems.append(newRangeItem)
            for j in range(initialIdx, initialIdx + l):
                analagousDict[j] = tag
            # print "-- add %s == %i--"%(str(newRangeItem), id(newRangeItem))
            if testUndo and undoStack != None:
                beforeAddition = tuple(rangeSet.ranges)
                rangeSet.addRange(newRangeItem,\
                                  undoStack=undoStack,\
                                  useUndoStack=useUndoStack)
                undoStack.undo()
                self.assertEqual(beforeAddition, tuple(rangeSet.ranges))
                undoStack.redo()
            else:
                rangeSet.addRange(newRangeItem,\
                                  useUndoStack=useUndoStack,\
                                  undoStack=undoStack)
            rangeSet.assertConsistency()
        return (analagousDict, addedRangeItems)

    def checkRangeSetAgainstAnalagousDict(self, rangeSet, analagousDict):
        firstIdx, afterLastIdx = rangeSet.bounds()
        firstIdx -= 3
        afterLastIdx += 3
        for i in range(firstIdx, afterLastIdx):
            valToCheck = rangeSet.get(i, None)
            if valToCheck != None:
                valToCheck = valToCheck[2]
            valToCheckAgainst = analagousDict.get(i, None)
            if valToCheck != valToCheckAgainst:
                ri = rangeSet._idxOfRangeContaining(i, returnTupledIdxOfNextRangeOnFail=True)
                print "ranges(ri=%s):%s\n\n\n"%(ri, rangeSet.ranges)
                if type(ri) in (tuple, list):
                    ri = ri[0]
                print "Disagreement at idx %i"%i
                for j in range(*rangeIntersection(\
                                (0, len(rangeSet.ranges)), (ri - 3, ri + 3)  )):
                    print "\trangeSet.ranges[%i] = %s"%(j, rangeSet.ranges[j])
                for j in range(*rangeIntersection(\
                               (firstIdx, afterLastIdx), (i-3, i+3) )):
                    print "\tanalagousDict[%i] = %s"%(j, analagousDict.get(j, None))
            self.assertEqual(valToCheck, valToCheckAgainst)

    def removeSomeRangesFromRangeSet(self, rangeSet, analagousDict):
        for i in range(10):
            initialIdx = self.prng.randint(-100, 100)
            l = self.prng.randint(1, 10)
            rangeSet.removeRange(initialIdx, initialIdx + l, useUndoStack=False)
            rangeSet.assertConsistency()
            for j in range(initialIdx, initialIdx + l):
                analagousDict[j] = None

    def createInsertAndRemovalCounters(self, rs):
        willRemoveCtr = {}
        didInsertCtr = {}
        def willRemoveRangeItem(ri):
            # print "willRemove %s == %i"%(str(ri),id(ri))
            willRemoveCtr[ri] = willRemoveCtr.get(ri, 0) + 1
        def didInsertRangeItem(ri):
            # print "didInsert %s == %i"%(str(ri),id(ri))
            didInsertCtr[ri] = didInsertCtr.get(ri, 0) + 1
        rs.willRemoveRangeItem = willRemoveRangeItem
        rs.didInsertRangeItem = didInsertRangeItem
        return (didInsertCtr, willRemoveCtr)

    def assertCallsBalanced(self, didInsertCtr, willRemoveCtr, RIs, rs):
        for ri in RIs:
            inRangeSet = int(ri in rs.ranges)
            insertCalls = didInsertCtr.get(ri, 0)
            removeCalls = willRemoveCtr.get(ri, 0)
            callsBalanced =  insertCalls == inRangeSet + removeCalls
            self.assertTrue(callsBalanced)

    def testRangeSet_addRange(self):
        rs = RangeSet()
        rd, addedRangeItems = self.addSomeRangesToRangeSet(rs, {})
        self.checkRangeSetAgainstAnalagousDict(rs, rd)

    def testRangeSet_addRange_removeRange(self):
        rs = RangeSet()
        didInsertCtr, willRemoveCtr = self.createInsertAndRemovalCounters(rs)
        rd, RIs = self.addSomeRangesToRangeSet(rs, {})
        self.assertCallsBalanced(didInsertCtr, willRemoveCtr, RIs, rs)
        self.removeSomeRangesFromRangeSet(rs, rd)
        self.assertCallsBalanced(didInsertCtr, willRemoveCtr, RIs, rs)
        self.checkRangeSetAgainstAnalagousDict(rs, rd)

    def testRangeSet_undo(self):
        us = QUndoStack()
        rs = RangeSet()
        didInsertCtr, willRemoveCtr = self.createInsertAndRemovalCounters(rs)
        
        rd, RIs1 = self.addSomeRangesToRangeSet(rs, {}, useUndoStack=True, undoStack=us, testUndo=True)
        RIs = RIs1
        self.assertCallsBalanced(didInsertCtr, willRemoveCtr, RIs, rs)
        rs1 = tuple(rs.ranges)
        
        us.beginMacro("Adding Some Test Ranges")
        rd, RIs2 = self.addSomeRangesToRangeSet(rs, rd, useUndoStack=True, undoStack=us)
        us.endMacro()
        RIs = RIs1 + RIs2
        self.assertCallsBalanced(didInsertCtr, willRemoveCtr, RIs, rs)
        rs2 = tuple(rs.ranges)
        
        us.beginMacro("Adding Some Test Ranges")
        rd, RIs3 = self.addSomeRangesToRangeSet(rs, rd, useUndoStack=True, undoStack=us)
        us.endMacro()
        RIs = RIs + RIs3
        self.assertCallsBalanced(didInsertCtr, willRemoveCtr, RIs, rs)
        rs3 = tuple(rs.ranges)
        
        us.undo()
        self.assertEqual(rs2, tuple(rs.ranges))
        self.assertCallsBalanced(didInsertCtr, willRemoveCtr, RIs, rs)
        
        us.undo()
        self.assertEqual(rs1, tuple(rs.ranges))
        self.assertCallsBalanced(didInsertCtr, willRemoveCtr, RIs, rs)

    def testRangeSet_rangesplitting(self):
        rs = RangeSet()
        splitee, splitter = (0, 10, "Splitee"), (5, 6, "Splitter")
        rs.addRange(splitee, useUndoStack=False)
        rs.addRange(splitter, useUndoStack=False)
        for i in range(0, 5) + range(6, 10):
            if rs.get(i)[2] != "Splitee":
                print "Rangesplitting failed at %i (was %s)"%(i,str(rs.get(i)))
                self.assertTrue(False)
        for i in range(5, 6):
            if rs.get(i)[2] != "Splitter":
                print "Rangesplitting failed at %i"%i
                self.assertTrue(False)

    def runTest(self):
        pass

if __name__ == '__main__':
    tc = UnitTests()
    tc.setUp()
    tc.testRangeSet_addRange()
    # tests.cadnanoguitestcase.main()
