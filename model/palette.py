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
palette.py
Created by Jonathan deWerd.
"""
from random import Random
prng = Random()

class Palette(object):
    """Imagine that palette is an infinite
    list of random colors selected from a
    set of colors. Suppose that a drag operation
    first splits a segment and uses palette[0]
    to color the newly split off segment. Then
    the user moves the mouse so that the drag op
    splits off two segments which it colors using
    palette[0] and palette[1]. Then the drag op
    changes back so that it only requires one color.
    The colors the drag op chooses should remain
    consistent throught the drag, but different drag
    ops should get different colors. This is implemented
    by having a drag op call palette.shuffle() so that
    the next drag op gets new colors for the same indices.
    """
    def __init__(self, colors):
        self._colors = colors
        self._idx = 0
    def __getitem__(self, i):
        c = self._colors
        return c[i%len(c)]
    def shuffle(self):
        prng.shuffle(self._colors)
        self._idx = 0
    def pop(self):
        ret = self[self._idx]
        self._idx += 1
        return ret
        