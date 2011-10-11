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
from model.enum import LatticeType
from part import Part

class Crossovers:
    squareScafLow = [[4, 26, 15], [18, 28, 7], [10, 20, 31], [2, 12, 23]]
    squareScafHigh = [[5, 27, 16], [19, 29, 8], [11, 21, 0], [3, 13, 24]]
    squareStapLow = [[31], [23], [15], [7]]
    squareStapHigh = [[0], [24], [16], [8]]


class SquarePart(Part):
    _step = 32  # 21 in honeycomb
    _subStepSize = _step / 4
    # Used in VirtualHelix::potentialCrossoverList
    _scafL = Crossovers.squareScafLow
    _scafH = Crossovers.squareScafHigh
    _stapL = Crossovers.squareStapLow
    _stapH = Crossovers.squareStapHigh

    def __init__(self, *args, **kwargs):
        super(SquarePart, self).__init__(self, *args, **kwargs)
        self._maxRow = kwargs.get('maxRow', app().prefs.squareRows)
        self._maxCol = kwargs.get('maxCol', app().prefs.squareCols)
        self._maxBase = kwargs.get('maxSteps', app().prefs.squareSteps) * self._step - 1

    def crossSectionType(self):
        return LatticeType.Square
    # end def

    def isEvenParity(self, row, column):
        return (row % 2) == (column % 2)
    # end def

    def isOddParity(self, row, column):
        return (row % 2) ^ (column % 2)
    # end def

    def latticeCoordToPositionXY(self, row, column, scaleFactor=1.0):
        """
        make sure self._radius is a float
        """
        radius = self._radius
        y = row*2*radius
        x = column*2*radius
        return scaleFactor*x, scaleFactor*y
    # end def

    def positionToCoord(self, x, y, scaleFactor=1.0):
        """
        """
        radius = self._radius
        row = int(y/(2*radius*scaleFactor) + 0.5)
        column = int(x/(2*radius*scaleFactor) + 0.5)
        return row, column
    # end def

    def fillSimpleRep(self, sr):
        super(SquarePart, self).fillSimpleRep(sr)
        sr['.class'] = 'SquarePart'
