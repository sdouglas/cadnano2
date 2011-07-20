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

class VBase(object):
    """
    Base is a convenience class that holds information identifying
    a certain base on a virtual helix, namely its coordinates:
    a vStrand object and the index along the one dimensional coordinate
    system defined by the vStrand. VBase objects are immutable.

    Uses properties: http://docs.python.org/library/functions.html#property
    """
    def __init__(self, vStrand, vIndex):
        object.__init__()
        self.vStrand = vStrand
        self.vIndex = vIndex
    def __repr__(self):
        strand = self.vStrand
        vhNum = strand.vHelix.number()
        strandStr = "scaf" if strand.isScaf() else "stap"
        return "v[%i].%s(%i)"%(vhNum, strandStr, self.vIndex)

    def coords(self):
        return (self.vStrand, self.vIndex)

    def vHelix(self):
        return self.vStrand.vHelix()

    def part(self):
        return self.vHelix().part()

    def __eq__(self, other):
        return self.coords() == other.coords()

    def vComplement(self):
        """
        Base on the same vHelix at the same vIndex but opposite strand.
        """
        return VBase(self.vStrand.vComplement(), self.vIndex)

    def sameStrand(self, idx):
        """
        Returns a VBase on the same vStrand but at the given index.
        """
        return VBase(self.vStrand, idx)

    def translated(self, delta):
        """
        Returns a VBase on the same strand with its indexs shifted by delta.
        """
        return VBase(self.vStrand, self.vIndex + delta)

    def vPrev5(self):
        """
        Returns a VBase one base in 5' direction along the vhelix.
        """
        if self.drawn5To3():
            return self.prevL()
        else:
            return self.prevR()

    def vNext3(self):
        """
        Returns a vbase one base in 3' direction along the vhelix.
        """
        if self.drawn5To3():
            return self.nextR()
        else:
            return self.prevL()

    def vNextR(self):
        """
        Returns a vbase one to the right in the path view
        """
        return VBase(self.vStrand, self.index + 1)

    def vPrevL(self):
        """
        Returns a vbase one to the left in the path view
        """
        return VBase(self._vStrand, self._index - 1)
