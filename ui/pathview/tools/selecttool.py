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
    def __init__(self, controller):
        super(SelectTool, self).__init__(controller)
        self._mouseDownBase = None
        self._lastValidBase = None

    def paint(self, painter, option, widget=None):
        pass
    # end def

    def mousePressPathHelix(self, ph, event):
        """Activate this item as the current helix"""
        self._mouseDownY = event.pos().y()
        self._mouseDownBase = ph.baseAtLocation(event.pos().x(),\
                                                self._mouseDownY)
        if self._mouseDownBase:
            vh = ph.vhelix()
            vh.setSandboxed(True)
            if vh.hasCrossoverAt(*self._mouseDownBase):
                # delete cross over
                self.selectToolRemoveXover(vh, self._mouseDownBase)
                self._mouseDownBase = self._mouseDownY = None
            else:
                self.selectToolApply(vh, self._mouseDownBase, self._mouseDownBase)
        ph.makeSelfActiveHelix()

    def mouseMovePathHelix(self, ph, event):
        if self._mouseDownY==None:
            return
        vh = ph.vhelix()
        newBase = ph.baseAtLocation(event.pos().x(), self._mouseDownY, clampX=True)
        if self._mouseDownBase and newBase:
            self._lastValidBase = newBase
            vh.undoStack().undo()
            self.selectToolApply(vh, self._mouseDownBase, newBase)

    def mouseReleasePathHelix(self, ph, event):
        if self._mouseDownY==None:
            return
        vh = ph.vhelix()
        if self._mouseDownBase and self._lastValidBase:
            vh.setSandboxed(False)  # vhelix now uses the document undo stack

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

    def selectToolApply(self, vHelix, fr, to):
        """SelectTool is the default tool that lets one
        create scaffold and staple by dragging starting on
        an empty or endpoint base or destroy scaffold/staple
        by dragging from a connected base. from and to take the
        format of (strandType, base)"""
        fr = vHelix.validatedBase(*fr, raiseOnErr=False)
        to = vHelix.validatedBase(*to, raiseOnErr=False)
        if (None, None) in (fr, to):
            return False
        startOnSegment = vHelix.hasStrandAt(*fr)
        startOnBreakpoint = vHelix.hasEndAt(*fr)
        direction = 1 if to[1] >= fr[1] else -1
        adj = vHelix.validatedBase(fr[0], fr[1] + direction, raiseOnErr=False)
        useClearMode = vHelix.hasStrandAt(*adj)
        # adj: the base adjacent to fr in the same direction as to
        if adj and startOnBreakpoint and vHelix.hasStrandAt(*adj):
            useClearMode = True
        if useClearMode:
            if to[1]<fr[1]:
                vHelix.clearStrand(fr[0], fr[1], to[1]+1)
            else:
                vHelix.clearStrand(fr[0], fr[1], to[1])
        else:
            vHelix.connectStrand(fr[0], fr[1], to[1])
