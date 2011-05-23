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
from model.enum import EndType, StrandType, BreakType
import ui.styles as styles
from util import *

from mmayacadnano.breakpointhandle3d import BreakpointHandle3D  # For Campbell

baseWidth = styles.PATH_BASE_WIDTH
ppL5 = QPainterPath()  # Left 5' PainterPath
ppR5 = QPainterPath()  # Right 5' PainterPath
ppL3 = QPainterPath()  # Left 3' PainterPath
ppR3 = QPainterPath()  # Right 3' PainterPath
# set up ppL5
ppL5.addRect(0.25 * baseWidth, 0.125 * baseWidth,\
             0.75 * baseWidth, 0.75 * baseWidth)
# set up ppR5
ppR5.addRect(0, 0.125 * baseWidth,\
             0.75 * baseWidth, 0.75 * baseWidth)
# set up ppL3
l3poly = QPolygonF()
l3poly.append(QPointF(baseWidth, 0))
l3poly.append(QPointF(0.25 * baseWidth, 0.5 * baseWidth))
l3poly.append(QPointF(baseWidth, baseWidth))
ppL3.addPolygon(l3poly)
# set up ppR3
r3poly = QPolygonF()
r3poly.append(QPointF(0, 0))
r3poly.append(QPointF(0.75 * baseWidth, 0.5 * baseWidth))
r3poly.append(QPointF(0, baseWidth))
ppR3.addPolygon(r3poly)


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
    selectbrush = QBrush(styles.bluishstroke)
    nobrush = QBrush(Qt.NoBrush)

    def __init__(self, vhelix, endType, strandType, baseIndex, parent=None):
        """Determine parity from vhelix. Make sure the breakpoint is
        drawn in the correct orientation depending on parity and whether
        it's a 5' end or a 3' end."""
        super(BreakpointHandle, self).__init__(parent)
        self.pathController = parent.parentItem().pathController
        self.undoStack =\
            self.pathController.mainWindow.undoStack
        self.restoreParentItem = parent
        self.setParentItem(parent)
        self._vhelix = vhelix
        self.endType = endType
        self.strandType = strandType
        self.type = None  # direction + end type (see mouseReleaseEvent)
        self.baseIndex = baseIndex  # public
        self.tempIndex = baseIndex
        self.minIndex = 0
        self.maxIndex = (vhelix.part().numBases() - 1)
        self.rect = QRectF(0, 0, baseWidth, baseWidth)
        self.x0 = baseIndex * baseWidth
        self.y0 = self.getYoffset()
        self.setPos(QPointF(self.x0, self.y0))
        self.setPainterPathType()
        self.pressX = 0
        self.pressXoffset = 0
        self._dragMode = False
        self.setFlag(QGraphicsItem.ItemIsMovable)
        self.setFlag(QGraphicsItem.ItemIsSelectable)
        self.breakpoint3D = BreakpointHandle3D(self)  # for Campbell
        self.setZValue(styles.ZBREAKPOINTHANDLE)
        self.setAcceptHoverEvents(True)
    # end def

    def restoreParent(self):
        tempP = self.restoreParentItem.mapFromItem(self.parentItem(),\
                                                   self.pos())
        self.setParentItem(self.restoreParentItem)
        self.setPos(tempP)
    # end def

    def boundingRect(self):
        return self.rect

    def paint(self, painter, option, widget=None):
        if self.isSelected():
            painter.setBrush(self.selectbrush)
            painter.setPen(self.nopen)
        else:
            painter.setBrush(self.brush)
            painter.setPen(self.nopen)
        painter.drawPath(self.painterpath)
        #painter.setBrush(self.nobrush)
        #painter.setPen(self.pen)
        # painter.drawRect(self.rect)
    # end def

    def getYoffset(self):
        """
        This function returns the appropriate Y offset according to the
        rule that even-parity staples and odd-parity scaffolds run in the
        negative-z direction and are drawn in the lower half of the
        path helix grid.
        """
        if (self._vhelix.evenParity() and\
            self.strandType == StrandType.Staple) or \
           (not self._vhelix.evenParity() and\
            self.strandType == StrandType.Scaffold):
            return baseWidth
        else:
            return 0

    def setPainterPathType(self):
        """Breakpoint Handles are drawn differently depending on context.
        This function determines the correct appearance based on endType
        (5' or 3'), strandType (scaffold or staple), and helix parity
        (even or odd)."""
        if self._vhelix.evenParity():
            if self.endType == EndType.FivePrime:
                self.type = BreakType.Left5Prime
                self.painterpath = ppL5
            elif self.endType == EndType.ThreePrime:
                self.type = BreakType.Right3Prime
                self.painterpath = ppR3
            else:
                raise AttributeError("BPH: EndType not recognized")
        else:
            if self.endType == EndType.FivePrime:
                self.type = BreakType.Right5Prime
                self.painterpath = ppR5
            elif self.endType == EndType.ThreePrime:
                self.type = BreakType.Left3Prime
                self.painterpath = ppL3
            else:
                raise AttributeError("BPH: EndType not recognized")
  
    def hoverEnterEvent(self,event):
        if self.pathController.toolUse == False:
            self.setCursor(Qt.OpenHandCursor)
        QGraphicsItem.hoverEnterEvent(self,event)
    # end def
    
    def hoverMoveEvent(self,event):
        if self.pathController.toolUse == True:
            # pass None, but if needed pass self.restoreParentItem
            self.pathController.toolHoverMove(None, event,flag=True)
        QGraphicsItem.hoverMoveEvent(self,event)
    # end def
    
    def hoverLeaveEvent(self,event):
        self.setCursor(Qt.ArrowCursor)
        QGraphicsItem.hoverLeaveEvent(self,event)
    # end def

    def mouseMoveEvent(self, event):
        """Snaps handle into place when dragging."""
        if self._dragMode == True:
            moveX = event.scenePos().x()
            delta = moveX - self.pressX
            offset = self.baseIndex * baseWidth + self.pressXoffset + delta;
            self.tempIndex = clamp(int(offset)/baseWidth, self.minIndex, self.maxIndex)
            self.x0 = self.tempIndex * baseWidth
            self.setPos(self.x0, self.y0)
            self.setCursor(Qt.OpenHandCursor)
        else:
            QGraphicsItem.mousePressEvent(self, event)

    def mousePressEvent(self, event):
        if event.button() != Qt.LeftButton:
            QGraphicsItem.mousePressEvent(self, event)
        else:
            if self.pathController.toolUse == False:
                self.scene().views()[0].addToPressList(self)
                self._dragMode = True
                self.scene().clearSelection()
                self.pressX = event.scenePos().x()
                self.pressXoffset = self.pressX % baseWidth
                self.setCursor(Qt.ClosedHandCursor)
            else:
                self.pathController.toolPress(None, event)
    # end def

    def customMouseRelease(self, eventPosition):
        """Snaps to grid after mouse released. Updates vhelix data according
        to what movement took place."""
        if self.tempIndex == self.baseIndex:
            return
        delta = int(self.tempIndex - self.baseIndex)
        self._vhelix.updateAfterBreakpointMove(self.strandType,\
                                              self.type,\
                                              self.baseIndex,\
                                              delta)
        self.undoStack.beginMacro("break move %d[%d] to %d[%d]" % \
                                    (self._vhelix.number(), self.baseIndex,\
                                     self._vhelix.number(), self.tempIndex))
        self.undoStack.push(BreakpointHandle.MoveCommand(self,\
                                                         self.baseIndex,\
                                                         self.tempIndex))
        self.undoStack.endMacro()
        self.baseIndex = self.tempIndex
        self.parentItem().updateDragBounds(self.strandType)
        self.parentItem().redrawLines(self.strandType)
        self._dragMode = False
        self.setCursor(Qt.OpenHandCursor)
    # end def

    def itemChange(self, change, value):
        # for selection changes test against QGraphicsItem.ItemSelectedChange
        if change == QGraphicsItem.ItemSelectedChange and self.scene():
        # if change == QGraphicsItem.ItemSelectedHasChanged and self.scene():
            selectionGroup = self.parentItem().parentItem().bphSelectionGroup
            lock = selectionGroup.parentItem().selectionLock
            # print "looking for a selection change..."
            # if value == True:
            if value == True and (lock == None or lock == selectionGroup):
                selectionGroup.addToGroup(self)
                selectionGroup.parentItem().selectionLock = selectionGroup
                return QGraphicsItem.itemChange(self, change, False)
            # end if
            else:
                pass
                return QGraphicsItem.itemChange(self, change, False)
            # end else
            self.update(self.rect)
        return QGraphicsItem.itemChange(self, change, value)
    # end def
