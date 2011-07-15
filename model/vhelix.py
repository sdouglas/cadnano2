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
vstrand.py
Created by Jonathan deWerd on 2011-07-15.
"""

from rangeset import RangeSet

class VHelix(object):
    def __init__(self):
        # Set by parent
        # self._part
        # self._coords
        # self._idnum
        self._scaf = RangeSet()
        self._stap = RangeSet()

    ########################## Public Read API ##########################

    def part(self):
        return self._part

    def coords(self):
        return self._coords

    def idnum(self):
        return self._idnum

    def strandDrawn5To3(self, vStrand):
        return self._part.strandDrawn5To3(self._coords, vStrand)

    ########################## Private Write API ##########################

    def _setPart(self, part, coords, idnum):
        """
        Parts use this method to notify the receiver that it has been added to
        a part at coords with a given idnum.
        """
        self._part = newPart
        self._coords = coords
        self._idnum = idnum
