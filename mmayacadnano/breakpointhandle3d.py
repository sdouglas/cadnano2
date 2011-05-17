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

class BreakpointHandle3D(object):
    """docstring for BreakpointHandle3D"""
    def __init__(self, breakpointhandle):
        super(BreakpointHandle3D, self).__init__()
        from ui.pathview.handles.breakpointhandle import BreakpointHandle
        self.breakpointhandle = breakpointhandle

    # Receive notifications from 2D partner
    def destroy(self):
        """Receive notification from 2D breakpoint to delete things on
        this end"""
        pass

    def dragFrom2D(self, newIndex):
        """Receive notifications from 2D breakpoint that it is being dragged"""
        # print "in BreakpointHandle3D: drag to %d" % newIndex
        pass

    # Send notifications to 2D partner
    def dragBreakpoint2D(self, newIndex):
        """Tell 2D partner that 3D breakpoint is being dragged."""
        self.breakpointhandle.dragFrom3D(newIndex)

    def dragReleaseBreakpoint2D(self, newIndex):
        """Tell 2D parner that 3D breakpoint has been dropped at a new
        index."""
        self.breakpointhandle.dragReleaseFrom3D(newIndex)

    def userActionBreakpoint2D(self, actionType):
        """User has performed an action on the breakpoint in the Maya
        interface (e.g. via a marking menu, special keypress, etc.).
        This method notifies the 2D view to update accordingly."""
        self.breakpointhandle.actionFrom3D(actionType)
