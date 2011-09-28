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
from model.enum import LatticeType, Crossovers
from part import Part

class SquarePart(Part):
    _step = 32  # 21 in honeycomb
    _activeSlice = _step
    _majorGridLine = _step / 4
    # Used in VirtualHelix::potentialCrossoverList
    scafL = Crossovers.squareScafLeft
    scafR = Crossovers.squareScafRight
    stapL = Crossovers.squareStapLeft
    stapR = Crossovers.squareStapRight

    def __init__(self, *args, **kwargs):
        super(SquarePart, self).__init__(self, *args, **kwargs)
        self._maxRow = kwargs.get('maxRow', app().prefs.squareRows)
        self._maxCol = kwargs.get('maxCol', app().prefs.squareCols)
        self._maxBase = kwargs.get('maxSteps', app().prefs.squareSteps) * self._step

    def crossSectionType(self):
        return LatticeType.Square
    # end def
    
    def isEvenParity(self, row, column):
        """
        To be implemented by Part subclass, pass
        """
        return (row % 2) == (column % 2)
    # end def
    
    def isOddParity(self, row, column):

        return (row % 2) ^ (column % 2)
    # end def
    
    def latticeToSpatial(self, row, column, scaleFactor=1.0):
        """
        make sure self._radius is a float
        """
        radius = self._radius
        x = row*2*radius
        y = column*2*radius
        return scaleFactor*x, scaleFactor*y
    # end def

    def spatialToLattice(self, x, y, scaleFactor=1.0):
        """
        """
        radius = self._radius
        row = int(x/(2*radius*scaleFactor) + 0.5)
        column = int(y/(2*radius*scaleFactor) + 0.5)
        return row, column
    # end def

    def fillSimpleRep(self, sr):
        super(SquarePart, self).fillSimpleRep(sr)
        sr['.class'] = 'DNASquarePart'
