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
from .dnapart import DNAPart
from .enum import LatticeType, Crossovers

class DNAHoneycombPart(DNAPart):
    step = 21  # 32 in square
    scafL = Crossovers.honeycombScafLeft
    scafR = Crossovers.honeycombScafRight
    stapL = Crossovers.honeycombStapLeft
    stapR = Crossovers.honeycombStapRight
    
    def __init__(self, *args, **kwargs):
        super(DNAHoneycombPart, self).__init__(*args, **kwargs)
        self._maxBase = 42
        self._activeSlice = 21
        
    def __repr__(self):
        return "HoneycombPart[" + ','.join(repr(self._numberToVirtualHelix[k]) for k in self._numberToVirtualHelix) + "]"

    def coordinateParityEven(self, coords):
        row, col = coords
        return (row % 2) ^ (col % 2) == 0
    
    def virtualHelixParityEven(self, vhref):
        """A property of the part, because the part is responsible for laying out
        the virtualhelices and parity is a property of the layout more than it is a
        property of a helix (maybe a non-honeycomb layout could support a different
        notion of parity?)"""
        vh = self.getVirtualHelix(vhref, returnNoneIfAbsent=False)
        return self.coordinateParityEven(vh.coord())
    
    def getVirtualHelixNeighbors(self, vhref):
        neighbors = []
        vh = self.getVirtualHelix(vhref, returnNoneIfAbsent=False)
        (r,c) = vh.coord()
        if self.virtualHelixParityEven(vh):
            neighbors.append(self.getVirtualHelix((r,c+1)))  # p0 neighbor (p0 is a direction)
            neighbors.append(self.getVirtualHelix((r-1,c)))  # p1 neighbor
            neighbors.append(self.getVirtualHelix((r,c-1)))  # p2 neighbor
        else:
            neighbors.append(self.getVirtualHelix((r,c-1)))  # p0 neighbor (p0 is a direction)
            neighbors.append(self.getVirtualHelix((r+1,c)))  # p1 neighbor
            neighbors.append(self.getVirtualHelix((r,c+1)))  # p2 neighbor
        return neighbors  # Note: the order and presence of Nones is important
        # If you need the indices of available directions use range(0,len(neighbors))
    
    def crossSectionType(self):
        """Returns the cross-section type of the DNA part."""
        return LatticeType.Honeycomb
    