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
from cadnano import app
from .dnapart import DNAPart
from .enum import LatticeType, Crossovers

class DNASquarePart(DNAPart):
    # Used in VirtualHelix::potentialCrossoverList
    step = 32  # 21 in honeycomb
    scafL = Crossovers.squareScafLeft
    scafR = Crossovers.squareScafRight
    stapL = Crossovers.squareStapLeft
    stapR = Crossovers.squareStapRight
    _activeSlice = step
    _majorGridLine = step/4

    def __init__(self, *args, **kwargs):
        DNAPart.__init__(self)
        self._maxRow = kwargs.get('maxRow', app().prefs.squareRows)
        self._maxCol = kwargs.get('maxCol', app().prefs.squareCols)
        self._maxBase = kwargs.get('maxSteps', app().prefs.squareSteps) * self.step

    def crossSectionType(self):
        return LatticeType.Square
 
    def fillSimpleRep(self, sr):
        super(DNASquarePart, self).fillSimpleRep(sr)
        sr['.class'] = 'DNASquarePart'

    def getVirtualHelixNeighbors(self, vhref):
        neighbors = []
        vh = self.getVirtualHelix(vhref, returnNoneIfAbsent=False)
        (r,c) = vh.coord()
        if self.virtualHelixParityEven(vh):
            neighbors.append(self.getVirtualHelix((r,c+1)))  # p0 neighbor (p0 is a direction)
            neighbors.append(self.getVirtualHelix((r+1,c)))  # p1 neighbor
            neighbors.append(self.getVirtualHelix((r,c-1)))  # p2 neighbor
            neighbors.append(self.getVirtualHelix((r-1,c)))  # p2 neighbor
        else:
            neighbors.append(self.getVirtualHelix((r,c-1)))  # p0 neighbor (p0 is a direction)
            neighbors.append(self.getVirtualHelix((r-1,c)))  # p1 neighbor
            neighbors.append(self.getVirtualHelix((r,c+1)))  # p2 neighbor
            neighbors.append(self.getVirtualHelix((r+1,c)))  # p3 neighbor
        return neighbors  # Note: the order and presence of Nones is important
        # If you need the indices of available directions use range(0,len(neighbors))
