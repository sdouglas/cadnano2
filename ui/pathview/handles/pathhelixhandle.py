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
Created by Shawn on 2011-02-05.
"""

from PyQt4.QtCore import QPointF, QRectF, Qt
from PyQt4.QtGui import QBrush, QFont
from PyQt4.QtGui import QGraphicsItem
from PyQt4.QtGui import QGraphicsSimpleTextItem, QGraphicsTextItem
from PyQt4.QtGui import QPen, QDrag, QUndoCommand
import ui.styles as styles
from util import *


class PathHelixHandle(QGraphicsItem):
    """docstring for PathHelixHandle"""
    radius = styles.PATHHELIXHANDLE_RADIUS
    rect = QRectF(0, 0, 2*radius, 2*radius)
    defBrush = QBrush(styles.grayfill)
    defPen = QPen(styles.graystroke, styles.PATHHELIXHANDLE_STROKE_WIDTH)
    hovBrush = QBrush(styles.bluefill)
    hovPen = QPen(styles.bluestroke, styles.PATHHELIXHANDLE_STROKE_WIDTH)
    useBrush = QBrush(styles.orangefill)
    usePen = QPen(styles.orangestroke, styles.PATHHELIXHANDLE_STROKE_WIDTH)

    def __init__(self, vhelix):
        super(PathHelixHandle, self).__init__()
        self.vhelix = vhelix
        self._number = self.vhelix.number()
        self.label = None
        self.focusRing = None
        self.beingHoveredOver = False
        self.setAcceptsHoverEvents(True)
        self.font = QFont("Times", 30, QFont.Bold)
        self.setNumber()
        #self.setFlag(QGraphicsItem.ItemIsMovable)
        self.setFlag(QGraphicsItem.ItemIsSelectable)
        self.setFlag(QGraphicsItem.ItemSendsScenePositionChanges)
    # end def

    def boundingRect(self):
        return self.rect

    def paint(self, painter, option, widget=None):
        if self._number >= 0:
            if self.isSelected():
                painter.setBrush(self.hovBrush)
                painter.setPen(self.hovPen)
            else:
                painter.setBrush(self.useBrush)
                painter.setPen(self.usePen)
        else:
            painter.setBrush(self.defBrush)
            painter.setPen(self.defPen)
        if self.beingHoveredOver:
            painter.setPen(self.hovPen)
        painter.drawEllipse(self.rect)

    def setNumber(self):
        """docstring for setNumber"""
        if self.label == None:
            self.label = QGraphicsSimpleTextItem("%d" % self._number)
            self.label.setFont(self.font)
            self.label.setParentItem(self)
        y_val = self.radius / 3
        if self._number < 10:
            self.label.setPos(self.radius / 1.5, y_val)
        elif self._number < 100:
            self.label.setPos(self.radius / 3, y_val)
        else: # _number >= 100
            self.label.setPos(0, y_val)

    def number(self):
        """docstring for number"""
        return self._number

    class FocusRingPainter(QGraphicsItem):
        """Draws a focus ring around helix in parent"""
        def __init__(self, helix, scene, parent=None):
            super(PathHelixHandle.FocusRingPainter, self).__init__(parent)
            self.parent = parent
            self.scene = scene
            self.helix = helix
            self.setPos(helix.pos())

        def paint(self, painter, option, widget=None):
            painter.setPen(PathHelixHandle.hovPen)
            painter.drawEllipse(self.helix.rect)

        def boundingRect(self):
            return self.helix.rect
    # end class

    def hoverEnterEvent(self, event):
        """
        hoverEnterEvent changes the PathHelixHandle brush and pen from default
        to the hover colors if necessary.
        """
        if self.focusRing == None:
            self.focusRing = PathHelixHandle.FocusRingPainter(self,\
                                                         self.scene(),\
                                                         self.parentItem())
        self.update(self.rect)
        print (self.pos().x(), self.pos().y())
    # end def

    def hoverLeaveEvent(self, event):
        """
        hoverEnterEvent changes the PathHelixHanle brush and pen from hover
        to the default colors if necessary.
        """
        if self.focusRing != None:
            self.focusRing.setParentItem(None)
            self.focusRing = None
        self.update(self.rect)
    # end def

    def mousePressEvent(self, event):
        selectionGroup = self.group()
        #if selectionGroup == None:
        #    selectionGroup = self.parent.phhSelectionGroup
        selectionGroup.setSelected(False)
        selectionGroup.addToGroup(self)
        self.setSelected(True)
        selectionGroup.mousePressEvent(event)
    # end def

    def itemChange(self, change, value):
        # for selection changes test against QGraphicsItem.ItemSelectedChange
        # intercept the change instead of the has changed to enable features.
        # if change == QGraphicsItem.ItemSelectedHasChanged and self.scene():
        if change == QGraphicsItem.ItemSelectedChange and self.scene():
            #selectionGroup = self.parent.phhSelectionGroup
            lock = selectionGroup.parentItem().selectionLock
            if value == True and (lock == None or lock == selectionGroup):
                selectionGroup.addToGroup(self)
                selectionGroup.parentItem().selectionLock = selectionGroup
                return QGraphicsItem.itemChange(self, change, True)
            # end if
            else:
                return QGraphicsItem.itemChange(self, change, False)
            # end else
            self.update(self.boundingRect())
        return QGraphicsItem.itemChange(self, change, value)
    # end def

