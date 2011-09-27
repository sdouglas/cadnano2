#!/usr/bin/env python
# encoding: utf-8

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
from part import Part
from model.enum import LatticeType


class Crossovers:
    honeycombScafLeft = [[1, 11], [8, 18], [4, 15]]
    honeycombScafRight = [[2, 12], [9, 19], [5, 16]]
    honeycombStapLeft = [[6], [13], [20]]
    honeycombStapRight = [[7], [14], [0]]


class HoneycombPart(Part):
    _step = 21  # 32 in square
    _activeSlice = _step
    _majorGridLine = _step / 3
    # Used in VirtualHelix::potentialCrossoverList
    scafL = Crossovers.honeycombScafLeft
    scafR = Crossovers.honeycombScafRight
    stapL = Crossovers.honeycombStapLeft
    stapR = Crossovers.honeycombStapRight

    def __init__(self, *args, **kwargs):
        Part.__init__(self, *args, **kwargs)
        self._maxRow = kwargs.get('maxRow', app().prefs.honeycombRows)
        self._maxCol = kwargs.get('maxCol', app().prefs.honeycombCols)
        self._maxBase = kwargs.get('maxSteps', app().prefs.honeycombSteps) * self._step

    def crossSectionType(self):
        """Returns the cross-section type of the DNA part."""
        return LatticeType.Honeycomb

    ########################## Archiving / Unarchiving #########################
    def fillSimpleRep(self, sr):
        super(HoneycombPart, self).fillSimpleRep(sr)
        sr['.class'] = 'HoneycombPart'
