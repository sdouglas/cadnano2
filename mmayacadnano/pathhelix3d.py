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
PathHelix3D.py

Created by Shawn on 2011-03-30.
"""

from ui.handles.breakpointhandle import BreakpointHandle
from model.virtualhelix import StrandType
from breakpointhandle3d import BreakpointHandle3D


class PathHelix3D(object):
    """
    PathHelix3D controls the 3D "view" of the VirtualHelix data.
    It should handle the drawing of actual representations of the DNA
    in the Maya interface (equivalents to the horizontal colored lines in the
    2D view)
    """
    def __init__(self, pathhelix):
        super(PathHelix3D, self).__init__()
        self.pathhelix = pathhelix
        self.row = pathhelix.row()
        self.col = pathhelix.col()

    def updateDNA(self, strandType, endpoints):
        """Notified when DNA lines have been redrawn (due to dragging a
        breakpoint, adding a crossover, etc.). Returns a list of startpoint
        and endpoint indices corresponding to where the lines in the 2D grid
        are drawn."""
        # print "in PathHelix3D:"
        type = "Scaffold"
        if strandType == StrandType.Staple:
            type = "Staple"
        for [startIndex, endIndex] in endpoints:
            # print "%s DNA is now present at (%d, %d) from %d to %d" % \
            #        (type, self.row, self.col, startIndex, endIndex)
            pass
