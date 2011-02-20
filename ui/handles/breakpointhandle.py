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

from exceptions import AttributeError
from PyQt4.QtCore import QPointF, QRectF, Qt
from PyQt4.QtGui import QBrush
from PyQt4.QtGui import QGraphicsItem
from PyQt4.QtGui import QPainterPath
from PyQt4.QtGui import QPolygonF
from PyQt4.QtGui import QPen, QDrag, QUndoCommand
import ui.styles as styles


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

    def __init__(self, vhelix, endType, strandType, baseIndex):
        """Determine parity from vhelix. Make sure the breakpoint is
        drawn in the correct orientation depending on parity and whether
        it's a 5' end or a 3' end."""
        super(BreakpointHandle, self).__init__()
        self.setFlag(QGraphicsItem.ItemIsMovable)
        self.vhelix = vhelix
        self.endType = endType
        self.strandType = strandType
        self.baseIndex = baseIndex
        self.minX = 0
        self.maxX = (vhelix.part().getCanvasSize()-1) * self.baseWidth
        self.rect = QRectF(0, 0, self.baseWidth, self.baseWidth)
        self.setParity()
        self.x0 = baseIndex * self.baseWidth
        self.y0 = self.getYoffset()
        self.setPos(QPointF(self.x0, self.y0))
        self.setPainterPathType()

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
                self.painterpath = self.getLeft5PrimePainterPath()
            elif self.endType == EndType.ThreePrime:
                self.painterpath = self.getRight3PrimePainterPath()
            else:
                raise AttributeError
        elif self.parity == Parity.Odd:
            if self.endType == EndType.FivePrime:
                self.painterpath = self.getRight5PrimePainterPath()
            elif self.endType == EndType.ThreePrime:
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
        pp.addRect(0.25*self.baseWidth, 0, 0.75*self.baseWidth, self.baseWidth)
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
        pp.addRect(0, 0, 0.75*self.baseWidth, self.baseWidth)
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
        """Only allow dragging in the x direction."""
        xf = event.scenePos().x()
        if xf > self.minX and xf < self.maxX:
            self.translate(xf - self.x0, 0)
            self.x0 = xf

    def mouseReleaseEvent(self, event):
        """Snaps to grid after mouse released."""
        d = self.x0 % self.baseWidth
        if d < (self.baseWidth / 2):  # snap left
            self.translate(-d, 0)
            self.x0 -= d
        else:  # snap right
            self.translate((self.baseWidth-d), 0)
            self.x0 += (self.baseWidth-d)
        

    def setDragBounds(self, minIndex, maxIndex):
        """docstring for setBounds"""
        self.minX = minIndex * self.baseWidth
        self.maxX = maxIndex * self.baseWidth
# end class

class StrandType:
    Scaffold = 0
    Staple = 1

class EndType:
    FivePrime = 0
    ThreePrime = 1

class Parity:
    Even = 0
    Odd = 1