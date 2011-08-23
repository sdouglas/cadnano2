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
                                       'QUndoCommand', 'QGraphicsEllipseItem',\
                                       'QTransform', 'QStyle'])

from .src.graphicsellipseitem import GraphicsEllipseItem

class PathHelixHandle(GraphicsEllipseItem):
    """docstring for PathHelixHandle"""
    radius = styles.PATHHELIXHANDLE_RADIUS
    
    # update the following lines if you want different stroke widths 
    # for hilighting.  Qt doesn't allow internal strokes.
    rect = QRectF(0, 0, 2*radius + styles.PATHHELIXHANDLE_STROKE_WIDTH,\
            2*radius + styles.PATHHELIXHANDLE_STROKE_WIDTH)
    # rect = QRectF(0, 0, 2*radius, 2*radius)
    
    hiliteWidth = 2
    
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
        self._phg = parent
        self.label = None
        self.focusRing = None
        self.beingHoveredOver = False
        self.setAcceptsHoverEvents(True)
        self.font = styles.PATHHELIXHANDLE_FONT
        self.setNumber()
        self.setFlag(QGraphicsItem.ItemIsSelectable)
        self.setFlag(QGraphicsItem.ItemSendsScenePositionChanges)
        self.penAndBrushSet(False)
        self.setRect(self.rect)
        self.setZValue(styles.ZPATHHELIX)
    # end def
    
    def penAndBrushSet(self, value):
        if self.number() >= 0:
            if value == True:
                self.setBrush(self.hovBrush)
                self.setPen(self.hovPen)
            else:
                self.setBrush(self.useBrush)
                self.setPen(self.usePen)
        else:
            self.setBrush(self.defBrush)
            self.setPen(self.defPen)
        self.update(self.boundingRect())
    # end def

    def someVHChangedItsNumber(self, r, c):
        # If it was our VH, we need to update the number we
        # are displaying!
        if (r,c) == self.vhelix.coord():
            self.setNumber()
    # end def

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
    # end def

    def number(self):
        """docstring for number"""
        return self.vhelix.number()

    def hoverEnterEvent(self, event):
        """
        hoverEnterEvent changes the PathHelixHandle brush and pen from default
        to the hover colors if necessary.
        """
        if not self.isSelected():
            if self.number() >= 0:
                if self.isSelected():
                    self.setBrush(self.hovBrush)
                else:
                    self.setBrush(self.useBrush)
            else:
                self.setBrush(self.defBrush)
            self.setPen(self.hovPen)
            self.update(self.boundingRect())
    # end def

    def hoverLeaveEvent(self, event):
        """
        hoverEnterEvent changes the PathHelixHanle brush and pen from hover
        to the default colors if necessary.
        """
        if not self.isSelected():
            self.penAndBrushSet(False)
            self.update(self.boundingRect())
    # end def

    def mousePressEvent(self, event):
        """
        All mousePressEvents are passed to the group if it's in a group
        """
        selectionGroup = self.group()
        if selectionGroup != None:
            selectionGroup.mousePressEvent(event)
        else:
            QGraphicsItem.mousePressEvent(self, event)
    # end def
    
    def mouseMoveEvent(self, event):
        """
        All mouseMoveEvents are passed to the group if it's in a group
        """
        selectionGroup = self.group()
        if selectionGroup != None:
            selectionGroup.mousePressEvent(event)
        else:
            QGraphicsItem.mouseMoveEvent(self, event)
    # end def
    
    def restoreParent(self, pos=None):
        """
        Required to restore parenting and positioning in the phg
        """
        
        # map the position
        if pos == None:
            tempP = self._phg.mapFromItem(self.parentObject(), self.pos())
        else:
            tempP = self._phg.mapToItem(self.parentObject(), pos)
        self.setParentItem(self._phg)
        self.penAndBrushSet(False)

        assert(self.parentObject() == self._phg)
        # print "restore", self.number(), self.parentObject(), self.group()
        assert(self.group() == None)
        self.setPos(tempP)
        self.setSelected(False)
    # end def

    def itemChange(self, change, value):
        # for selection changes test against QGraphicsItem.ItemSelectedChange
        # intercept the change instead of the has changed to enable features.
        if change == QGraphicsItem.ItemSelectedHasChanged and self.scene():
            selectionGroup = self._phg.phhSelectionGroup
            lock = selectionGroup.phg().selectionLock
            
            # only add if the selectionGroup is not locked out
            if value == True and (lock == None or lock == selectionGroup):
                if self.group() != selectionGroup:
                    # print "preadd", self.number(), self.parentObject(), self.group()
                    selectionGroup.addToGroup(self)
                    # print "postadd", self.number(), self.parentObject(), self.group()
                    selectionGroup.phg().selectionLock = selectionGroup
                    self.penAndBrushSet(True)
                    return
            # end if
            else:
                # print "deselect", self.number(), self.parentObject(), self.group()
                self.penAndBrushSet(False)
                return
            # end else
        # end if
        elif change == QGraphicsItem.ItemSelectedChange and self.scene():
            selectionGroup = self._phg.phhSelectionGroup
            lock = selectionGroup.phg().selectionLock
            if value == True and (lock == None or lock == selectionGroup):
                self.penAndBrushSet(True)
                return True
            # end if
            else:
                self.penAndBrushSet(False)
                return False
            # end else
        # end elif
        return QGraphicsEllipseItem.itemChange(self, change, value)
    # end def

