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
pathhelixhandle.py
Created by Shawn on 2011-02-06.
"""

from exceptions import AttributeError, NotImplementedError
from PyQt4.QtCore import QPointF, QRectF, Qt, SIGNAL, QMimeData
from PyQt4.QtGui import QBrush
from PyQt4.QtGui import QGraphicsItem
from PyQt4.QtGui import QPainterPath
from PyQt4.QtGui import QPolygonF
from PyQt4.QtGui import QPen, QDrag, QUndoCommand
from model.base import EndType
from model.virtualhelix import StrandType, Parity, BreakType
import ui.styles as styles

from mmayacadnano.breakpointhandle3d import BreakpointHandle3D # For Campbell


class BreakpointHandle(QGraphicsItem):
    """
    BreakpointHandle responds to mouse input and serves as an interface
    for modifying scaffold and staple strands at 5' and 3' ends.
    
    Each handle tracks its own starting position. When it is dragged and
    released, it notifies the PathController if its DNApart should be
    updated.
    """
    pen = QPen(styles.minorgridstroke, styles.PATH_GRID_STROKE_WIDTH)
    nopen = QPen(Qt.NoPen)
    brush = QBrush(styles.bluestroke)
    nobrush = QBrush(Qt.NoBrush)
    baseWidth = styles.PATH_BASE_WIDTH

    def __init__(self, vhelix, endType, strandType, baseIndex, parent=None):
        """Determine parity from vhelix. Make sure the breakpoint is
        drawn in the correct orientation depending on parity and whether
        it's a 5' end or a 3' end."""
        super(BreakpointHandle, self).__init__(parent)
        self.setFlag(QGraphicsItem.ItemIsMovable)
        self.parent = parent
        self.setParentItem(parent) 
        self.vhelix = vhelix
        self.endType = endType
        self.strandType = strandType
        self.type = None  # direction + end type (see mouseReleaseEvent)
        self.baseIndex = baseIndex  # public
        self.tempIndex = baseIndex
        self.minIndex = 0
        self.maxIndex = (vhelix.part().getCanvasSize()-1)
        self.rect = QRectF(0, 0, self.baseWidth, self.baseWidth)
        self.setParity()
        self.x0 = baseIndex * self.baseWidth
        self.y0 = self.getYoffset()
        self.setPos(QPointF(self.x0, self.y0))
        self.setPainterPathType()
        self.pressX = 0
        self.pressXoffset = 0
        self.setCursor(Qt.OpenHandCursor)
        self._dragMode = False
        self.breakpoint3D = BreakpointHandle3D(self)  # for Campbell

    def boundingRect(self):
        return self.rect

    def paint(self, painter, option, widget=None):
        painter.setBrush(self.brush)
        painter.setPen(self.nopen)
        painter.drawPath(self.painterpath)
        painter.setBrush(self.nobrush)
        painter.setPen(self.pen)
        painter.drawRect(self.rect)

    def setParity(self):
        """docstring for setParity"""
        if self.vhelix.number() % 2 == 0:
            self.parity = Parity.Even
        else:
            self.parity = Parity.Odd

    def getYoffset(self):
        """
        This function returns the appropriate Y offset according to the
        rule that even-parity staples and odd-parity scaffolds run in the
        negative-z direction and are drawn in the lower half of the
        path helix grid.
        """
        if (self.parity == Parity.Even and self.strandType == StrandType.Staple) or \
           (self.parity == Parity.Odd and self.strandType == StrandType.Scaffold):
            return self.baseWidth
        else:
            return 0

    def setPainterPathType(self):
        """Breakpoint Handles are drawn differently depending on context.
        This function determines the correct appearance based on endType
        (5' or 3'), strandType (scaffold or staple), and helix parity
        (even or odd)."""
        if self.parity == Parity.Even:
            if self.endType == EndType.FivePrime:
                self.type = BreakType.Left5Prime
                self.painterpath = self.getLeft5PrimePainterPath()
            elif self.endType == EndType.ThreePrime:
                self.type = BreakType.Right3Prime
                self.painterpath = self.getRight3PrimePainterPath()
            else:
                raise AttributeError
        elif self.parity == Parity.Odd:
            if self.endType == EndType.FivePrime:
                self.type = BreakType.Right5Prime
                self.painterpath = self.getRight5PrimePainterPath()
            elif self.endType == EndType.ThreePrime:
                self.type = BreakType.Left3Prime
                self.painterpath = self.getLeft3PrimePainterPath()
            else:
                raise AttributeError
        else:
            raise AttributeError

    def getLeft5PrimePainterPath(self):
        """Return a QPainterPath that draws a rectangle that is shifted
        to the right such that the base path line should extend to the right,
        i.e. the breakpoint sits at the left edge of a path.
        (Function naming is arbitrary, so left vs right is based on the 
        position of the breakpointhandle relative to the rest of the path).
        """
        pp = QPainterPath()
        # pp.addRect(0, 0, self.baseWidth, self.baseWidth)
        pp.addRect(0.25*self.baseWidth, 0.125*self.baseWidth, 0.75*self.baseWidth, 0.75*self.baseWidth)
        return pp

    def getLeft3PrimePainterPath(self):
        """Return a QPainterPath that draws a triangle that points left
        and is shifted to the right such that the base path line should
        extend to the right, i.e. the breakpoint sits at the left edge of a
        path."""
        poly = QPolygonF()
        poly.append(QPointF(self.baseWidth,0))
        poly.append(QPointF(0.25*self.baseWidth,0.5*self.baseWidth))
        poly.append(QPointF(self.baseWidth,self.baseWidth))
        pp = QPainterPath()
        pp.addPolygon(poly)
        return pp

    def getRight5PrimePainterPath(self):
        """Return a QPainterPath that draws a rectangle that is shifted
        to the left such that the base path line should extend to the left,
        i.e. the breakpoint sits at the right edge of a path."""
        pp = QPainterPath()
        # pp.addRect(0, 0, self.baseWidth, self.baseWidth)
        pp.addRect(0, 0.125*self.baseWidth, 0.75*self.baseWidth, 0.75*self.baseWidth)
        return pp

    def getRight3PrimePainterPath(self):
        """Return a QPainterPath that draws a triangle that points right
        and is shifted to the left such that the base path line should
        extend to the left, i.e. the breakpoint sits at the right edge of a
        path."""
        poly = QPolygonF()
        poly.append(QPointF(0, 0))
        poly.append(QPointF(0.75*self.baseWidth, 0.5*self.baseWidth))
        poly.append(QPointF(0, self.baseWidth))
        pp = QPainterPath()
        pp.addPolygon(poly)
        return pp

    def mouseMoveEvent(self, event):
        """Snaps handle into place when dragging."""
        if self._dragMode == True:
            moveX = event.scenePos().x()
            delta = moveX-self.pressX
            self.tempIndex = int((self.baseIndex*self.baseWidth+\
                              self.pressXoffset+delta) / self.baseWidth)
            if self.tempIndex < self.minIndex:
                self.tempIndex = self.minIndex
            elif self.tempIndex > self.maxIndex:
                self.tempIndex = self.maxIndex
            self.x0 = self.tempIndex * self.baseWidth
            self.setPos(self.x0, self.y0)
            self.setCursor(Qt.OpenHandCursor)
            self.breakpoint3D.dragFrom2D(self.tempIndex)
        else:
            QGraphicsItem.mousePressEvent(self,event)

    def mousePressEvent(self, event):
        if event.button() != Qt.LeftButton:
            event.ignore()
            QGraphicsItem.mousePressEvent(self,event)
        else:
            self.scene().views()[0].addToPressList(self)
            self._dragMode = True
            self.pressX = event.scenePos().x()
            self.pressXoffset = self.pressX % self.baseWidth
            self.setCursor(Qt.ClosedHandCursor)

    def mouseUp(self, epos):
        """Snaps to grid after mouse released. Updates vhelix data according
        to what movement took place."""
        if self.tempIndex == self.baseIndex:
            return
        delta = int(self.tempIndex - self.baseIndex)
        self.vhelix.updateAfterBreakpointMove(self.strandType,\
                                              self.type,\
                                              self.baseIndex,\
                                              delta)
        self.baseIndex = self.tempIndex
        self.parent.updateBreakBounds(self.strandType)
        self.parent.redrawLines(self.strandType)
        self._dragMode = False

    def setDragBounds(self, minIndex, maxIndex):
        """Called by PathHelix.updateBreakBounds to notify breakpoint handle
        of where it can legally move along the vhelix."""
        self.minIndex = minIndex
        self.maxIndex = maxIndex

    def dragFrom3D(self, newIndex):
        """Called by mMaya BreakpointHandle3D to notify cadnano that the
        3D handle is being dragged to a new location, and should be
        dragged in the 2D view as well. No updates are made to the model."""

        # *** not tested ***

        if self.newIndex < self.minIndex:
            self.newIndex = self.minIndex
        elif self.newIndex > self.maxIndex:
            self.newIndex = self.maxIndex
        self.x0 = self.newIndex * self.baseWidth # determine new location
        self.setPos(self.x0, self.y0) # move there

    def dragReleaseFrom3D(self, newIndex):
        """Called by mMaya BreakpointHandle3D to notify cadnano that the
        3D handle has moved to a new location. All updates to the data
        structure are then handled by cadnano on the 2D side."""

        # *** not tested ***

        if self.baseIndex == newIndex:
            return
        delta = int(newIndex - self.baseIndex)
        # update data stucture after move
        self.vhelix.updateAfterBreakpointMove(self.strandType,\
                                              self.type,\
                                              self.baseIndex,\
                                              delta)
        self.baseIndex = newIndex
        self.parent.updateBreakBounds(self.strandType) # new breakpoint bounds
        self.parent.redrawLines(self.strandType) # new 2D lines

    def actionFrom3D(self, actionType):
        """Called by mMaya BreakpointHandle3D to notify cadnano that the
        3D handle has received a user action. All updates to the data
        structure are then handled by cadnano on the 2D side."""
        raise NotImplementedError
