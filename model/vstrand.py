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

from rangeset import RangeSet
import util
from vbase import VBase
util.qtWrapImport('QtCore', globals(), ['QObject'] )

class VStrand(QObject, RangeSet):
    """
    There are two of these per VirtualHelix. They provide the linear coordinate
    system in which VBase.vIndex() live.
    This subclass of RangeSet is designed to hold Segment items as its ranges.
    """
    def __init__(self, parentVHelix=None):
        QObject.__init__(self)
        RangeSet.__init__(self)
        if parentVHelix != None:
            self._setVHelix(parentVHelix)
        preserveLeftOligoDuringSplit = True

    def __call__(self, idx):
        return VBase(self, idx)

    ####################### Public Read API #######################
    # Useful inherited methods:
    #   vstr.get(idx)            get a segment at index idx
    #   vstr[idx]                same as get
    #   vstr.bounds()            returns a range containing all segments
    # Properties:
    #   vstr.vHelix

    def vComplement():
        """
        Returns the other VStrand in the VHelix that self is a child of.
        """
        vh = self.vHelix
        scaf, stap = vh.scaf(), vh.stap()
        if self == scaf:
            return stap
        assert(self == stap)
        return scaf

    def isScaf(self):
        return self == self.vHelix.scaf()

    def isStap(self):
        return self == self.vHelix.stap()

    def drawn5To3(self):
        return self.vHelix.strandDrawn5To3(self)

    ####################### Framework Overrides / Undo ##############
    def idxs(self, rangeItem):
        """
        Returns (firstIdx, afterLastIdx) simplified representation of the
        rangeItem passed in.
        """
        return rangeItem.idxsOnStrand(self)
        #rangeItems are Strand objects, self is a VStrand
        vb3, vb5 = rangeItem.vBase3, rangeItem.vBase5
        vs3, vs5 = vb3.vStrand, vb5.vStrand
        idx3, idx5 = vb3.vIndex, vb5.vIndex
        if vs3 == vs5 == self:  # Non-crossover
            return (min(idx3, idx5), max(idx3, idx5))
        elif vs3 == self:  # The crossover owns the base that exposes a 3' end
            return (idx3, idx3 + 1)
        elif vs5 == self:  # The crossover owns the base that exposes a 5' end
            return (idx5, idx5 + 1)
        assert(False)

    def canMergeRangeItems(self, rangeItemA, rangeItemB):
        if not RangeSet.canMergeRangeItems(self, rangeItemA, rangeItemB):
            return False
        return rangeItemA.canMergeWith(rangeItemB)
         
    def mergeRangeItems(self, rangeItemA, rangeItemB, undoStack):
        return rangeItemA.mergeWith(rangeItemB, undoStack)

    def changeRangeForItem(self, rangeItem, newStartIdx, newAfterLastIdx, undoStack):
        return rangeItem.changeRange(newStartIdx, newAfterLastIdx, undoStack)

    def splitRangeItem(self, rangeItem, splitStart, splitAfterLast, undoStack):
        return rangeItem.split(splitStart,\
                               splitAfterLast,\
                               self.preserveLeftOligoDuringSplit,\
                               undoStack)

    def undoStack(self):
        return self.vHelix.undoStack()

    ####################### Private Write API #######################
    def _setVHelix(self, newVH):
        """
        Should be called only by a VHelix adopting a VStrand as its child.
        """
        self.vHelix = newVH