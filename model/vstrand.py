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
import strand
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
        #self.vHelix (set by _setVHelix)
        preserveLeftOligoDuringSplit = True

    def __repr__(self):
        accesorToGetSelfFromvHelix = "????"
        if self == self.vHelix.scaf: accesorToGetSelfFromvHelix = "scaf"
        if self == self.vHelix.stap: accesorToGetSelfFromvHelix = "stap"
        return "v[%i].%s"%(self.vHelix.number(), accesorToGetSelfFromvHelix)

    ####################### Public Read API #######################
    # Useful inherited methods:
    #   vstr.get(idx)            get the segment at index idx (or None)
    #   vstr[idx]                same as get
    #   vstr.bounds()            returns a range containing all segments
    #                            this range is tight
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

    def model1String(self, *x):
        """ The 'old' model represented virtual strands and the connections
        between virtual bases on those strands with a string of the form
        illustrated below):
            "_,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,_ _,> <,> <,_ _,_"
        This example represents a three base strand on a 13 base vStrand.
        This method returns an identical representation of the receiver, where
        the first vBase printed is at vStrandStartIdx and the last is at
        vStrandAfterLastIdx-1. """
        if len(x) > 0:
            vStrandStartIdx, vStrandAfterLastIdx = x
        else:
            vStrandStartIdx, vStrandAfterLastIdx = 0, self.vHelix.numBases()
        ri = self._idxOfRangeContaining(vStrandStartIdx,\
                                        returnTupledIdxOfNextRangeOnFail=True)
        ranges = self.ranges
        bases = []
        prvIdxExists = int(self.get(vStrandStartIdx - 1) != None)
        curIdxExists = int(self.get(vStrandStartIdx) != None)
        lut = ('_,_', '_,_', 'ERR', '<,_', '_,_', '_,_', '_,>', '<,>')
        for i in range(vStrandStartIdx, vStrandAfterLastIdx):
            nxtIdxExists = int(self.get(i + 1) != None)
            bases.append(lut[prvIdxExists + 2*curIdxExists + 4*nxtIdxExists])
            prvIdxExists = curIdxExists
            curIdxExists = nxtIdxExists
        return " ".join(bases)

    def exposedEndAt(self, vIdx):
        """
        Returns 'L' or 'R' if a segment exists at vIdx and it
        exposes an unbound endpoint on its 3' or 5' end. Otherwise returns None.
        """
        rangeItem = self.get(vIdx)
        if rangeItem == None:
            return None
        return rangeItem.exposedEndAt(self, vIdx)  # 'L', 'R', or None

    ####################### Public Write API #######################


    ####################### Protected Framework Methods ##############
    def idxs(self, rangeItem):
        """
        Returns (firstIdx, afterLastIdx) simplified representation of the
        rangeItem passed in.
        """
        return rangeItem.idxsOnStrand(self)

    def canMergeTouchingRangeItems(self, rangeItemA, rangeItemB):
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

    def willRemoveRangeItem(self, rangeItem):
        if strand.logger != None:
            strand.logger.write("+%i.remove() %s\n"%(rangeItem.traceID,\
                                                   repr(rangeItem)))

    def didInsertRangeItem(self, rangeItem):
        if strand.logger != None:
            strand.logger.write("+%i.insert() %s\n"%(rangeItem.traceID,\
                                                   repr(rangeItem)))

    def boundsChanged(self):
        pass

    def undoStack(self):
        return self.vHelix.undoStack()

    ####################### Private Write API #######################
    def _setVHelix(self, newVH):
        """
        Should be called only by a VHelix adopting a VStrand as its child.
        """
        self.vHelix = newVH