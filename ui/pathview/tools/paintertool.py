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
paintertool
Created by Jonathan deWerd on 2011-05-26.
"""


class PainterTool(object):
    def __init__(self):
        super(PainterTool, self).__init__()
        self._mouseDownBase = None

    def mousePressPathHelix(self, ph, event):
        """Activate this item as the current helix"""
        self._mouseDownY = event.pos().y()
        self._mouseDownBase = ph.baseAtLocation(event.pos().x(),\
                                                self._mouseDownY)
        if self._mouseDownBase:
            vh = ph.vhelix()
            vh.setSandboxed(True)
            self.painterToolApply(vh, self._mouseDownBase, self._mouseDownBase)

    def mouseMovePathHelix(self, ph, event):
        vh = ph.vhelix()
        newBase = ph.baseAtLocation(event.pos().x(), self._mouseDownY)
        if self._mouseDownBase and newBase:
            self._lastValidBase = newBase
            vh.undoStack().undo()
            self.painterToolApply(vh, self._mouseDownBase, newBase)

    def mouseReleasePathHelix(self, ph, event):
        vh = ph.vhelix()
        if self._mouseDownBase and self._lastValidBase:
            # vh.undoStack().undo()
            vh.setSandboxed(False)  # vhelix now uses the document undo stack
            # self.painterToolApply(vh, self._mouseDownBase, self._lastValidBase)
        if self._mouseDownBase != None:
            ph.updateAsActiveHelix(self._mouseDownBase[1])

    def painterToolApply(self, vHelix, fr, to):
        """PainterTool is the default tool that lets one
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
            vHelix.clearStrand(fr[0], fr[1], to[1])
        else:
            vHelix.connectStrand(fr[0], fr[1], to[1])
