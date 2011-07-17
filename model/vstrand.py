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

    ####################### Public Read API #######################
    # Useful inherited methods:
    #   vstr.get(idx)            get a segment at index idx
    #   vstr[idx]                same as get
    #   vstr.bounds()            returns a range containing all segments

    def vHelix(self):
        return self._vHelix

    def vComplement():
        """
        Returns the other VStrand in the VHelix that self is a child of.
        """
        vh = self._vHelix
        scaf, stap = vh.scaf(), vh.stap()
        if self == scaf:
            return stap
        assert(self == stap)
        return scaf

    def isScaf(self):
        return self == self._vHelix.scaf()

    def isStap(self):
        return self == self._vHelix.stap()

    def drawn5To3(self):
        return self._vHelix.strandDrawn5To3(self)

    ####################### Framework Overrides / Undo ##############
    def idxs(self, rangeItem):
        """
        Returns (firstIdx, afterLastIdx) simplified representation of the
        rangeItem passed in.
        """
        idx3, idx5 = rangeItem.vBase3p().vIndex(), rangeItem.vBase5p().vIndex()
        return (min(idx3, idx5), max(idx3, idx5))

    #def canMergeRangeItems(self, leftRangeItem, rightRangeItem):
    #def mergeRangeItems(self, leftRangeItem, rightRangeItem, undoStack=None):

    def changeRangeForItem(self, rangeItem, newStartIdx, newAfterLastIdx, undoStack=None):
        """
        Changes the range corresponding to rangeItem.
        Careful, this isn't a public method. It gets called to notify a subclass
        of a change, not to effect the change itself.
        If a subclass needs to support undo, it should push this onto the undo stack.
        """
        return (newStartIdx, newAfterLastIdx, rangeItem[2])

    def willRemoveRangeItem(self, rangeItem, undoStack=None):
        """
        Gets called exactly once on every rangeItem that was once passed to
        addRange but will now be deleted from self.ranges (wrt the public API,
        this is when it becomes inaccessable to the get method)
        If a subclass needs to support undo, it should push this onto the undo stack.
        """
        pass

    def undoStack(self):
        return self._vHelix.undoStack()

    ####################### Private Write API #######################
    def _setVHelix(self, newVH):
        """
        Should be called only by a VHelix adopting a VStrand as its child.
        """
        self._vHelix = newVH