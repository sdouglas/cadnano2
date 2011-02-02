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

from PyQt4.QtCore import QRectF
from PyQt4.QtGui import QBrush
from PyQt4.QtGui import QGraphicsItem
from PyQt4.QtGui import QGraphicsSimpleTextItem
from PyQt4.QtGui import QPen, QDrag, QUndoCommand
import styles
from model.virtualhelix import VirtualHelix


class PathHelix(QGraphicsItem):
    """docstring for PathHelix"""
    def_brush = QBrush(styles.grayfill)
    def_pen = QPen(styles.graystroke, styles.SLICE_HELIX_STROKE_WIDTH)
    hov_brush = QBrush(styles.bluefill)
    hov_pen = QPen(styles.bluestroke, styles.SLICE_HELIX_HILIGHT_WIDTH)
    use_brush = QBrush(styles.orangefill)
    use_pen = QPen(styles.orangestroke, styles.SLICE_HELIX_STROKE_WIDTH)
    radius = styles.SLICE_HELIX_RADIUS
    rect = QRectF(0, 0, 2 * radius, 2 * radius)
    
    def __init__(self, vhelix, position, parent):
        super(PathHelix, self).__init__()
        self.parent = parent
        self.vhelix = vhelix
        self.number = self.vhelix.number()
        self.label = None
        self.focusRing = None
        self.beingHoveredOver = False
        self.setAcceptsHoverEvents(True)
        self.setPos(position)
        self.setNumber()

    def paint(self, painter, option, widget=None):
        if self.number >= 0:
            painter.setBrush(self.use_brush)
            painter.setPen(self.use_pen)
        else:
            painter.setBrush(self.def_brush)
            painter.setPen(self.def_pen)
        if self.beingHoveredOver:
            painter.setPen(self.hov_pen)
        painter.drawEllipse(self.rect)

    class FocusRingPainter(QGraphicsItem):
        """Draws a focus ring around helix in parent"""
        def __init__(self, helix, parent):
            super(PathHelix.FocusRingPainter, self).__init__()
            self.helix = helix
            self.setPos(helix.pos())
            parent.addItem(self)

        def paint(self, painter, option, widget=None):
            painter.setPen(PathHelix.hov_pen)
            painter.drawEllipse(self.helix.rect)

        def boundingRect(self):
            return self.helix.rect
        # end def
    # end class

    def boundingRect(self):
        return self.rect

    def hoverEnterEvent(self, event):
        """hoverEnterEvent changes the PathHelix brush and pen from default
        to the hover colors if necessary."""
        if self.focusRing == None:
            self.focusRing = PathHelix.FocusRingPainter(self, \
                                                         self.parent.scene)
        self.update(self.rect)
    # end def

    def hoverLeaveEvent(self, event):
        """hoverEnterEvent changes the PathHelix brush and pen from hover
        to the default colors if necessary."""
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

    def setNumber(self):
        """docstring for setNumber"""
        if self.label == None:
            self.label = QGraphicsSimpleTextItem("%d" % self.number)
            self.label.setParentItem(self)
        if self.number < 10:
            self.label.setX(self.radius / 1.3)
        elif self.number < 100:
            self.label.setX(self.radius / 2)
        else:   # added for bigger than 100 by NC
            self.label.setX(self.radius / 4)
        self.label.setY(self.radius / 2)
        
