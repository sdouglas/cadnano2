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
pathhelix.py
Created by Shawn on 2011-01-27.
"""

from exceptions import AttributeError, ValueError
from PyQt4.QtCore import Qt
from PyQt4.QtCore import QLine, QRectF
from PyQt4.QtGui import QBrush
from PyQt4.QtGui import QGraphicsItem
from PyQt4.QtGui import QGraphicsSimpleTextItem
from PyQt4.QtGui import QPainter, QPainterPath
from PyQt4.QtGui import QPen, QDrag, QUndoCommand
import ui.styles as styles
from model.enum import EndType, LatticeType, StrandType
from model.virtualhelix import VirtualHelix
from handles.breakpointhandle import BreakpointHandle
from mmayacadnano.pathhelix3d import PathHelix3D  # For Campbell
from weakref import ref


class PathHelix(QGraphicsItem):
    """
    PathHelix is the primary "view" of the VirtualHelix data.
    It manages the ui interactions from the user, such as
    dragging breakpoints or crossovers addition/removal,
    and updates the data model accordingly.

    parent should be set to...
    """
    minorGridPen = QPen(styles.minorgridstroke, 1)
    majorGridPen = QPen(styles.majorgridstroke, 2)
    scafPen = QPen(styles.scafstroke, 0)
    nobrush = QBrush(Qt.NoBrush)
    baseWidth = styles.PATH_BASE_WIDTH

    def __init__(self, vhelix, parent):
        super(PathHelix, self).__init__(parent)
        self.setAcceptHoverEvents(True)  # for pathtools
        self._scafBreakpointHandles = []
        self._stapBreakpointHandles = []
        self._scafXoverHandles = []
        self._stapXoverHandles = []
        self._segmentLines = None
        self._minorGridPainterPath = None
        self._majorGridPainterPath = None
        self.setParentItem(parent)
        self.step = 21  # 32 for Square lattice
        self.pathController = parent.pathController  # assumes parent is phg
        self.setZValue(styles.ZPATHHELIX)
        self.rect = QRectF()
        self._vhelix = None
        self.setVHelix(vhelix)
    # end def

    def vhelix(self):
        return self._vhelix
        
    def setVHelix(self, newVH):
        if self._vhelix:
            self._vhelix.basesModified.disconnect(self.vhelixBasesModified)
            self._vhelix.vhelixDimensionsModified.disconnect(self.vhelixDimensionsModified)
        self._vhelix = newVH
        newVH.basesModified.connect(self.vhelixBasesModified)
        newVH.dimensionsModified.connect(self.vhelixDimensionsModified)
        self.vhelixDimensionsModified()
        self.vhelixBasesModified()

    def number(self):
        return self._vhelix.number()

    def row(self):
        return self._vhelix.row()

    def col(self):
        return self._vhelix.col()

    def evenParity(self):
        return self._vhelix.evenParity()

    def vhelixDimensionsModified(self):
        """Sets rect width to reflect number of bases in vhelix. Sets
        rect height to the width of two bases (one for scaffold and
        one for staple)"""
        canvasSize = self._vhelix.part().numBases()
        self.prepareGeometryChange()
        self.rect.setWidth(self.baseWidth * canvasSize)
        self.rect.setHeight(2 * self.baseWidth)
        self._minorGridPainterPath = None
        self._majorGridPainterPath = None

    def boundingRect(self):
        return self.rect
    
    ################################ Events ################################
    def hoverEnterEvent(self, event):
        if self.pathController.toolUse == True:
            self.pathController.toolHoverEnter(self,event)
        else:
            QGraphicsItem.hoverEnterEvent(self,event)
    # end def
    
    def hoverLeaveEvent(self, event):
        if self.pathController.toolUse == True:
            self.pathController.toolHoverLeave(self,event)
        else:
            QGraphicsItem.hoverLeaveEvent(self,event)
    # end def
    
    def hoverMoveEvent(self, event):
        if self.pathController.toolUse == True:
            self.pathController.toolHoverMove(self,event)
        else:
            QGraphicsItem.hoverMoveEvent(self,event)
    # end def

    def mousePressEvent(self, event):
        """Activate this item as the current helix"""
        if self.pathController.toolUse == True:
            self.pathController.toolPress(self,event)
        eventIndex = int(event.pos().x() / styles.PATH_BASE_WIDTH)
        self.updateAsActiveHelix(eventIndex)
    # end def

    def hidePreXoverHandles(self):
        pass
    # end def

    def addXoverHandle(self, xh, strandType):
        """addXoverHandle gets called by PathHelixGroup
        when the handles are changed (e.g. by sliceHelixClickedSlot
        or when a crossover is added)."""
        if strandType == StrandType.Scaffold:
            self._scafXoverHandles.append(xh)
        elif strandType == StrandType.StrandType:
            self._stapXoverHandles.append(xh)
        else:
            raise AttributeError("strandType not recognized.")
    # end def

    def removeXoverHandle(self, xh, strandType):
        """addXoverHandle gets called by PathHelixGroup
        when the handles are changed (e.g. by sliceHelixClickedSlot
        or when a crossover is added)."""
        if strandType == StrandType.Scaffold:
            self._scafXoverHandles.remove(xh)
        elif strandType == StrandType.StrandType:
            self._stapXoverHandles.remove(xh)
        else:
            raise AttributeError("strandType not recognized.")
    # end def

    def updateAsActiveHelix(self, index):
        if self.parentItem().activeHelix != None:  # deactivate old
            self.parentItem().activeHelix.hidePreXoverHandles()
        # end if
        self.parentItem().activeHelix = self  # activate new
        self._vhelix.updatePreCrossoverPositions(index)
        self.parentItem().notifyPreCrossoverGroupAfterUpdate(self._vhelix)
        self.update(self.boundingRect())
    # end def

    ################################ Loading and Updating State From VHelix ##########################
    def vhelixBasesModified(self):
        self.refreshBreakpoints()
        self._segmentLines = None  # Clear drawing cache of lines

    def refreshBreakpoints(self):
        """docstring for refreshBreakpoints"""
        print "refreshing breakpoints"
        for bh in self._scafBreakpointHandles:
            bh.setParentItem(None)
        self._scafBreakpointHandles = []
        for bh in self._stapBreakpointHandles:
            bh.setParentItem(None)
        self._stapBreakpointHandles = []
        for strandType in (StrandType.Staple, StrandType.Scaffold):
            for baseIndex, endType in self.vhelix().getEnds(strandType):
                bh = BreakpointHandle(self.vhelix(), endType,\
                                      strandType, baseIndex, parent=self)
                if strandType == StrandType.Staple:
                    self._stapBreakpointHandles.append(bh)
                else:
                    self._scafBreakpointHandles.append(bh)

    ################################ Drawing ##########################
    def paint(self, painter, option, widget=None):
        painter.setBrush(self.nobrush)
        painter.setPen(self.minorGridPen)
        painter.drawPath(self.minorGridPainterPath())  # Minor grid lines
        painter.setPen(self.majorGridPen)
        painter.drawPath(self.majorGridPainterPath())  # Major grid lines
        painter.setPen(self.scafPen)
        painter.drawLines(self.segmentLines())
    # end def

    def minorGridPainterPath(self):
        """
        Returns a QPainterPath object for the minor grid lines.
        The path also includes a border outline and a midline for
        dividing scaffold and staple bases.
        """
        if self._minorGridPainterPath:
            return self._minorGridPainterPath
        path = QPainterPath()
        canvasSize = self._vhelix.part().numBases()
        # border
        path.addRect(0, 0, self.baseWidth * canvasSize, 2 * self.baseWidth)
        # minor tick marks
        for i in range(canvasSize):
            if (i % 7 != 0):
                x = round(self.baseWidth*i) + .5
                path.moveTo(x, 0)
                path.lineTo(x, 2 * self.baseWidth)
        # staple-scaffold divider
        path.moveTo(0, self.baseWidth)
        path.lineTo(self.baseWidth * canvasSize, self.baseWidth)
        self._minorGridPainterPath = path
        return path

    def majorGridPainterPath(self):
        """
        Returns a QPainterPath object for the major grid lines.
        This is separated from the minor grid lines so different
        pens can be used for each.
        """
        if self._majorGridPainterPath:
            return self._majorGridPainterPath
        path = QPainterPath()
        canvasSize = self._vhelix.part().numBases()
        # major tick marks
        for i in range(0, canvasSize + 1, 7):
            x = round(self.baseWidth*i) + .5
            path.moveTo(x, .5)
            path.lineTo(x, 2 * self.baseWidth - .5)
        self._majorGridPainterPath = path
        return path

    def getYoffset(self, strandType):
        """
        This function returns the appropriate Y offset according to the
        rule that even-parity staples and odd-parity scaffolds run in the
        negative-z direction and are drawn in the lower half of the
        path helix grid.
        """
        if (self.evenParity() and strandType == StrandType.Staple):
            return self.baseWidth + (self.baseWidth >> 1)
        if (not self.evenParity() and strandType == StrandType.Scaffold):
            return self.baseWidth + (self.baseWidth >> 1)
        else:
            return self.baseWidth >> 1

    def segmentLines(self):
        """Draw horizontal lines where non-breakpoint, non-crossover strand
           is present"""
        if self._segmentLines:
            return self._segmentLines
        self._segmentLines = []
        for strandType in (StrandType.Scaffold, StrandType.Staple):
            y = self.getYoffset(strandType)  # determine y offset
            for [startIndex, endIndex] in self._vhelix.getSegments(strandType):
                x1 = (startIndex * self.baseWidth) + (self.baseWidth >> 1)
                x2 = (endIndex * self.baseWidth) + (self.baseWidth >> 1)
                self._segmentLines.append(QLine(x1, y, x2, y))  # create QLine list
        return self._segmentLines

# end class
