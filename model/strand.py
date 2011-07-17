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

import util
util.qtWrapImport('QtCore', globals(), ['QObject'] )

class Strand(QObject):
    """
    Represents a segment of DNA that
    1) Has a length (# nucleotides, possibly 0)
    2) Has a 3' and 5' endpoint (VBase instances, which locate the
       endpoints in conceptual or 3D space (like coordinates))
    3) The set of vhelix which contain bases of the segment
       is a nonproper subset of {startVB.vHelix(), endVB.vHelix()}
    4) Might have another segment connected to either or both of
       its 3' and 5' ends
    Represens a horizontal (in the path view) stretch of connected
    bases
    """

    def __init__(self, VB3p, VB5p):
        QObject.__init__(self)
        assert(VB3p.vStrand() == endVB.vStrand())
        # Location of the first base that belongs to self
        # with a 3' connection to the previous segment
        # (VBases are like coordinates in that they specify
        # the location of a base)
        self._3pVBase = VB3p
        self._3pSegment = None
        
        # Location of the last base that belongs to self
        # with a 5' connection to the next segment
        self._5pVBase = VB5p
        self._5pSegment = None

    def vBase3p(self):
        return self._3pVBase

    def vBase5p(self):
        return self._5pVBase

    def segment3p(self):
        return self._3pSegment

    def segment5p(self):
        return self._5pSegment

