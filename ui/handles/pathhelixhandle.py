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

    def __init__(self, vhelix, position, parent):
        super(PathHelixHandle, self).__init__(parent)
        self.vhelix = vhelix
        self.parent = parent
        self.setParentItem(parent) 
        self.number = self.vhelix.number()
        self.label = None
        self.focusRing = None
        self.beingHoveredOver = False
        self.setAcceptsHoverEvents(True)
        self.setPos(position)
        self.font = QFont("Times", 30, QFont.Bold)
        self.setNumber()
        #self.setFlag(QGraphicsItem.ItemIsMovable)
        self.setFlag(QGraphicsItem.ItemIsSelectable)
        self.setFlag(QGraphicsItem.ItemSendsScenePositionChanges)
    # end def

    def boundingRect(self):
        return self.rect

    def paint(self, painter, option, widget=None):
        if self.number >= 0:
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
            self.label = QGraphicsSimpleTextItem("%d" % self.number)
            self.label.setFont(self.font)
            self.label.setParentItem(self)
        y_val = self.radius / 3
        if self.number < 10:
            self.label.setPos(self.radius / 1.5, y_val)
        elif self.number < 100:
            self.label.setPos(self.radius / 3, y_val)
        else: # number >= 100
            self.label.setPos(0, y_val)

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
                                                         self.parent.scene,\
                                                         self.parent)
        self.update(self.rect)
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

    # def mousePressEvent(self, event):
    #     if event.button() != Qt.LeftButton:
    #         event.ignore()
    #         QGraphicsItem.mousePressEvent(self,event)
    #     else:
    #         self.scene().views()[0].addToPressList(self)
    #         self.setCursor(Qt.ClosedHandCursor)
    # 
    # def customMouseRelease(self, eventPosition):
    #     """docstring for customMouseRelease"""
    #     print "%d customMouseRelease" % self.number

    def itemChange(self, change, value):
        # for selection changes test against QGraphicsItem.ItemSelectedChange
        if change == QGraphicsItem.ItemScenePositionHasChanged and self.scene():
            newPos = value.toPointF()  # value is the new position
            # print "%d to (%d, %d)" % (self.number, newPos.x(), newPos.y())
            # rect = self.scene().sceneRect()
            # if not rect.contains(newPos):
            #     # Keep the item inside the scene rect.
            #     newPos.setX(min(rect.right(), max(newPos.x(), rect.left())))
            #     newPos.setY(min(rect.bottom(), max(newPos.y(), rect.top())))
            #     return newPos
            # # end if
        # end if
        # elif change == QGraphicsItem.ItemPositionChange and self.scene():
        #     print "poop"
        
        # intercept the change instead of the has changed to enable features.
        elif change == QGraphicsItem.ItemSelectedChange and self.scene():
        # elif change == QGraphicsItem.ItemSelectedHasChanged and self.scene():
            qgigroup = self.parent.QGIGroup
            # print "looking for a selection change..."
            if value == True:
                qgigroup.addToGroup(self)
                #qgigroup.addToGroup(self.vhelix)
                print "isSelected = True, and added", self.number
                return QGraphicsItem.itemChange(self, change, False)
            # end if
            else:
                #qgigroup.removeFromGroup(self)
                #qgigroup.removeFromGroup(self.vhelix)
                print "isSelected = False", self.number
            # end else
            self.update(self.rect)
        return QGraphicsItem.itemChange(self, change, value)
    # end def

