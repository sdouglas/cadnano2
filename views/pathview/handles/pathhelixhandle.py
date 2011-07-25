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
from views import styles

import util
# import Qt stuff into the module namespace with PySide, PyQt4 independence
util.qtWrapImport('QtCore', globals(), ['QPointF', 'QRectF', 'Qt'])
util.qtWrapImport('QtGui', globals(), ['QBrush', 'QFont', 'QGraphicsItem',\
                                       'QGraphicsSimpleTextItem', 'QPen',\
                                       'QGraphicsTextItem', 'QDrag', \
                                       'QUndoCommand'])

class PathHelixHandle(QGraphicsItem):
    """docstring for PathHelixHandle"""
    radius = styles.PATHHELIXHANDLE_RADIUS
    rect = QRectF(0, 0, 2*radius + styles.PATHHELIXHANDLE_STROKE_WIDTH,\
            2*radius + styles.PATHHELIXHANDLE_STROKE_WIDTH)
    defBrush = QBrush(styles.grayfill)
    defPen = QPen(styles.graystroke, styles.PATHHELIXHANDLE_STROKE_WIDTH)
    hovBrush = QBrush(styles.bluefill)
    hovPen = QPen(styles.bluestroke, styles.PATHHELIXHANDLE_STROKE_WIDTH)
    useBrush = QBrush(styles.orangefill)
    usePen = QPen(styles.orangestroke, styles.PATHHELIXHANDLE_STROKE_WIDTH)

    def __init__(self, vhelix, parent):
        super(PathHelixHandle, self).__init__(parent)
        self.vhelix = vhelix
        vhelix.part().virtualHelixAtCoordsChanged.connect(self.someVHChangedItsNumber)
        self.parent = parent
        self._phg = parent
        self.setParentItem(parent)
        self.label = None
        self.focusRing = None
        self.beingHoveredOver = False
        self.setAcceptsHoverEvents(True)
        self.font = styles.PATHHELIXHANDLE_FONT
        self.setNumber()
        self.setFlag(QGraphicsItem.ItemIsSelectable)
        self.setFlag(QGraphicsItem.ItemSendsScenePositionChanges)
    # end def

    def boundingRect(self):
        return self.rect

    def paint(self, painter, option, widget=None):
        if self.number() >= 0:
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

    def someVHChangedItsNumber(self, r, c):
        # If it was our VH, we need to update the number we
        # are displaying!
        if (r,c) == self.vhelix.coord():
            self.setNumber()

    def setNumber(self):
        """docstring for setNumber"""
        if self.label == None:
            self.label = QGraphicsSimpleTextItem("%d" % self.number())
            self.label.setFont(self.font)
            self.label.setParentItem(self)
        else:
            self.label.setText("%d" % self.number())
        y_val = self.radius / 3
        if self.number() < 10:
            self.label.setPos(self.radius / 1.5, y_val)
        elif self.number() < 100:
            self.label.setPos(self.radius / 3, y_val)
        else: # _number >= 100
            self.label.setPos(0, y_val)
        posx = self.label.boundingRect().width()/2
        posy = self.label.boundingRect().height()/2
        self.label.setPos(self.radius-posx, self.radius-posy)

    def number(self):
        """docstring for number"""
        return self.vhelix.number()

    class FocusRingPainter(QGraphicsItem):
        """Draws a focus ring around helix in parent"""
        def __init__(self, helix):
            super(PathHelixHandle.FocusRingPainter, self).__init__(helix)
            self.helix = helix
            # self.setPos(helix.pos())

        def paint(self, painter, option, widget=None):
            painter.setPen(PathHelixHandle.hovPen)
            painter.drawEllipse(self.boundingRect())

        def boundingRect(self):
            return self.helix.boundingRect()
    # end class

    def hoverEnterEvent(self, event):
        """
        hoverEnterEvent changes the PathHelixHandle brush and pen from default
        to the hover colors if necessary.
        """
        if self.focusRing == None:
            self.focusRing = PathHelixHandle.FocusRingPainter(self)
        self.update(self.boundingRect())
    # end def

    def hoverLeaveEvent(self, event):
        """
        hoverEnterEvent changes the PathHelixHanle brush and pen from hover
        to the default colors if necessary.
        """
        self.destroyFocusRing()
        self.update(self.boundingRect())
    # end def

    def destroyFocusRing(self):
        if self.focusRing != None:
            scene = self.focusRing.scene()
            scene.removeItem(self.focusRing)
            self.focusRing = None
    # end def

    def mousePressEvent(self, event):
        selectionGroup = self.group()
        self.destroyFocusRing()
        if selectionGroup == None:
            selectionGroup = self._phg.phhSelectionGroup
        selectionGroup.setSelected(False)
        selectionGroup.addToGroup(self)
        self.setSelected(True)
        selectionGroup.mousePressEvent(event)
    # end def
    
    def restoreParent(self):
        tempP = self._phg.mapFromItem(self.parentItem(), self.pos())
        self.setParentItem(self._phg)
        self.setPos(tempP)
    # end def

    def itemChange(self, change, value):
        # for selection changes test against QGraphicsItem.ItemSelectedChange
        # intercept the change instead of the has changed to enable features.
        # if change == QGraphicsItem.ItemSelectedHasChanged and self.scene():
        if change == QGraphicsItem.ItemSelectedChange and self.scene():
            selectionGroup = self._phg.phhSelectionGroup
            lock = selectionGroup.phg().selectionLock
            if value == True and (lock == None or lock == selectionGroup):
                selectionGroup.addToGroup(self)
                selectionGroup.phg().selectionLock = selectionGroup
                return QGraphicsItem.itemChange(self, change, True)
            # end if
            else:
                return QGraphicsItem.itemChange(self, change, False)
            # end else
            self.update(self.boundingRect())
        return QGraphicsItem.itemChange(self, change, value)
    # end def

