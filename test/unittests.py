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
import test.cadnanoguitestcase
from test.cadnanoguitestcase import CadnanoGuiTestCase
from model.enum import StrandType
from model.virtualhelix import VirtualHelix
import unittest
from rangeset import RangeSet
import random
seed = random.Random().randint(0,1<<32)
enviroseed = os.environ.get('UNITTESTS_PRNG_SEED', False)
if enviroseed != False:
    seed = int(enviroseed)
del enviroseed
print "Seeding test.unittests; use setenv UNITTESTS_PRNG_SEED=%i to replay."%seed


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

    def testAutoDragToBoundary(self):
        """docstring for testDrag"""
        vh0 = VirtualHelix(numBases=42, idnum=0)
        vh0.connectStrand(StrandType.Scaffold, 20, 22)
        str0 = "0 Scaffold: _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,> <,> <,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_\n0 Staple:   _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_"
        self.assertEqual(repr(vh0), str0)
        vh0.autoDragToBoundary(StrandType.Scaffold, 20)
        str1 = "0 Scaffold: _,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_\n0 Staple:   _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_"
        self.assertEqual(repr(vh0), str1)
        vh0.autoDragToBoundary(StrandType.Scaffold, 22)
        str2 = "0 Scaffold: _,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,> <,_\n0 Staple:   _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_"
        self.assertEqual(repr(vh0), str2)

    def testRangeSet_idxOfRangeContaining(self):
        ranges = []
        idx = self.prng.randint(-100, 100)
        for i in range(100):
            l = idx
            idx += self.prng.randint(1, 8)
            r = idx
            idx += self.prng.randint(0, 8)
            ranges.append([l, r, i])
        rs = RangeSet()
        rs.ranges = ranges
        for i in range(ranges[0][0] - 3, ranges[-1][1] + 3):
            valueByFastMethod = rs._idxOfRangeContaining(i)
            valueBySureMethod = rs._slowIdxOfRangeContaining(i)
            self.assertEqual(valueByFastMethod, valueBySureMethod)
        for i in range(ranges[0][0] - 3, ranges[-1][1] + 3):
            valueByFastMethod = rs._idxOfRangeContaining(i,\
                                       returnTupledIdxOfNextRangeOnFail=True)
            valueBySureMethod = rs._slowIdxOfRangeContaining(i,\
                                       returnTupledIdxOfNextRangeOnFail=True)
            # if valueBySureMethod != valueByFastMethod:
            #     for j in range(len(ranges)-4,len(ranges)):
            #         print "ranges[%i] = %s"%(j, ranges[j])
            #     print "rs._idxOfRangeContaining(%i) = %s"%(i, valueByFastMethod)
            #     print "rs._slowIdxOfRangeContaining(%i) = %s"%(i, valueBySureMethod)
            #     code.interact('', local=locals())
            self.assertEqual(valueByFastMethod, valueBySureMethod)

    def testRangeSet_idxRangeOfRangesIntersectingRange(self):
        ranges = []
        idx = self.prng.randint(-100, 100)
        for i in range(100):
            l = idx
            idx += self.prng.randint(1, 8)
            r = idx
            idx += self.prng.randint(0, 8)
            ranges.append([l, r, i])
        rs = RangeSet()
        rs.ranges = ranges
        idxMin, idxMax = ranges[0][0], ranges[-1][1]
        for i in range(100):
            l = self.prng.randint(idxMin - 3, idxMax + 3)
            r = l + self.prng.randint(-3, 20)
            valueByFastMethod = rs._idxRangeOfRangesIntersectingRange(l, r)
            valueBySureMethod = rs._slowIdxRangeOfRangesIntersectingRange(l, r)
            self.assertEqual(valueByFastMethod, valueBySureMethod)

    def runTest(self):
        pass

if __name__ == '__main__':
    tc = UnitTests()
    tc.setUp()
    tc.testRangeSet_idxRangeOfRangesIntersectingRange()
    # test.cadnanoguitestcase.main()
