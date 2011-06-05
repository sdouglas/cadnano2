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
selecttool
Created by Nick Conway on 2011-05-30.
"""

from abstractpathtool import AbstractPathTool

class SelectTool(AbstractPathTool):
    """
    SelectTool is the default tool. It allows editing of breakpoints
    (by clicking and dragging) and toggling of crossovers.
    """
    def __init__(self, controller):
        super(SelectTool, self).__init__(controller)
        self._mouseDownBase = None
        self._mouseDownPH = None
        self._lastValidBase = None
        self._dragLimits = None

    def paint(self, painter, option, widget=None):
        pass
    # end def

    def mousePressPathHelix(self, ph, event):
        """Activate this item as the current helix."""
        # self.finalizeMouseDrag()
        self._mouseDownY = event.pos().y()
        self._mouseDownPH = ph
        ph.scene().views()[0].addToPressList(ph)
        
        self._mouseDownBase = ph.baseAtLocation(event.pos().x(),\
                                                self._mouseDownY)
        if self._mouseDownBase:
            vh = ph.vhelix()
            if vh.hasCrossoverAt(*self._mouseDownBase):  # remove it
                self.selectToolRemoveXover(vh, self._mouseDownBase)
                self._mouseDownBase = self._mouseDownY = None
            else:
                vh.setSandboxed(True)
                self._dragLimits = vh.getDragLimits(*self._mouseDownBase)
                self._lastValidBase = self._mouseDownBase
                self.applyTool(vh, self._mouseDownBase, self._mouseDownBase)
        ph.makeSelfActiveHelix()

    def finalizeMouseDrag(self):
        if not self._mouseDownBase:
            return
        vh = self._mouseDownPH.vhelix()
        vh.undoStack().undo()
        vh.setSandboxed(False)
        self.applyTool(vh, self._mouseDownBase, self._lastValidBase)
        self._mouseDownBase = None
        self._lastValidBase = None
        self._mouseDownPH = None

    def mouseMovePathHelix(self, ph, event):
        if self._mouseDownY == None:
            return
        vh = ph.vhelix()
        newBase = ph.baseAtLocation(event.pos().x(), self._mouseDownY, clampX=True)
        if self._mouseDownBase and newBase:
            if self._lastValidBase != newBase and \
               newBase[1] >= self._dragLimits[0] and\
               newBase[1] <= self._dragLimits[1]:
                self._lastValidBase = newBase
                vh.undoStack().undo()
                self.applyTool(vh, self._mouseDownBase, newBase)

    def mouseReleasePathHelix(self, ph, event):
        self.finalizeMouseDrag()

    def selectToolRemoveXover(self,vHelix, base):
        base = vHelix.validatedBase(*base, raiseOnErr=False)
        if None in base:
            return False
        # call of the next function assumes that the base has been vetted to be
        # an actual crossover
        # the removepair is the ( (3p_vh, ind) , (5p_vh, ind) )
        removepair = vHelix.getXover(*base)
        removepair[0][0].removeXoverTo(base[0], removepair[0][1], \
                                       removepair[1][0], removepair[1][1])
    # end def

    def applyTool(self, vHelix, fr, to):
        """
        fr (from) and to take the format of (strandType, base)
        """
        fr = vHelix.validatedBase(*fr, raiseOnErr=False)
        to = vHelix.validatedBase(*to, raiseOnErr=False)
        if (None, None) in (fr, to):  # must start and end on a valid base
            return False

        startOnBreakpoint = vHelix.hasEndAt(*fr)
        if not startOnBreakpoint:  # must start on a breakpoint
            return False

        # determine if we're adding or clearing bases
        is5to3 = vHelix.directionOfStrandIs5to3(fr[0])
        if (startOnBreakpoint == 5 and is5to3) or\
           (startOnBreakpoint == 3 and not is5to3):
            segmentDir = 1
        else:
            segmentDir = -1
        dragDir = 1 if to[1] >= fr[1] else -1  # which way are we dragging?
        
        if dragDir == segmentDir:  # CLEARING bases
            if to[1] < fr[1]:  # dragging left
                vHelix.clearStrand(fr[0], fr[1], to[1]+1)
            elif to[1] > fr[1]:
                vHelix.clearStrand(fr[0], fr[1], to[1])
            else:
                pass  # shouldn't get here if newBase is actually new
        else:  # ADDING bases
            if to[1] < fr[1]:  # dragging left
                vHelix.connectStrand(fr[0], fr[1], to[1])
            elif to[1] > fr[1]:
                vHelix.connectStrand(fr[0], fr[1], to[1])
            else:
                pass  # shouldn't get here if newBase is actually new
