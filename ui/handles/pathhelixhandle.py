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
from PyQt4.QtGui import QBrush
from PyQt4.QtGui import QGraphicsItem
from PyQt4.QtGui import QGraphicsSimpleTextItem
from PyQt4.QtGui import QPen, QDrag, QUndoCommand
import ui.styles as styles


class PathHelixHandle(QGraphicsItem):
    """docstring for PathHelixHandle"""
    radius = styles.PATH_HELIX_RADIUS
    rect = QRectF(0, 0, 2*radius, 2*radius)
    defBrush = QBrush(styles.grayfill)
    defPen = QPen(styles.graystroke, styles.SLICE_HELIX_STROKE_WIDTH)
    hovBrush = QBrush(styles.bluefill)
    hovPen = QPen(styles.bluestroke, styles.SLICE_HELIX_HILIGHT_WIDTH)
    useBrush = QBrush(styles.orangefill)
    usePen = QPen(styles.orangestroke, styles.SLICE_HELIX_STROKE_WIDTH)

    def __init__(self, vhelix, position, parent):
        super(PathHelixHandle, self).__init__(parent)
        print vhelix
        self.vhelix = vhelix
        self.parent = parent
        self.number = self.vhelix.number()
        print "PathHelixHandle self.number:",self.number
        self.label = None
        self.focusRing = None
        self.beingHoveredOver = False
        self.setAcceptsHoverEvents(True)
        self.setPos(position)
        self.setNumber()

    def boundingRect(self):
        return self.rect

    def paint(self, painter, option, widget=None):
        if self.number >= 0:
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
            self.label.setParentItem(self)
        y_val = self.radius / 2
        if self.number < 10:
            self.label.setPos(self.radius / 1.3, y_val)
        elif self.number < 100:
            self.label.setPos(self.radius / 2, y_val)
        else:  # added for bigger than 100 by NC
            self.label.setPos(self.radius / 4, y_val)

    class FocusRingPainter(QGraphicsItem):
        """Draws a focus ring around helix in parent"""
        def __init__(self, helix, scene):
            super(PathHelixHandle.FocusRingPainter, self).__init__()
            self.scene = scene
            self.helix = helix
            self.setPos(helix.pos())
            scene.addItem(self)

        def paint(self, painter, option, widget=None):
            painter.setPen(PathHelixHandle.hovPen)
            painter.drawEllipse(self.helix.rect)
            bringToFront(self, self.scene)

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
                                                            self.parent.scene)
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

    def mousePressEvent(self, event):
        # self.setUsed(not self.number >= 0)
        QDrag(self.parent.parentWidget())
    # end def

    def dragEnterEvent(self, e):
        # self.setUsed(not self.number >= 0)
        e.acceptProposedAction()
        print "dee"
    # end def
    
def bringToFront(target, scene):
    """collidingItems gets a list of all items that overlap. sets
    this items zValue to one higher than the max."""
    zval = 1
    items = scene.items(target.boundingRect()) # the is a QList
    for item in items:
        temp = item.zValue()
        if temp >= zval:
            zval = item.zValue() + 1
        # end if
    # end for
    target.setZValue(zval)
