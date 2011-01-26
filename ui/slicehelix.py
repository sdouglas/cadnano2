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
slicehelix.py

Created by Shawn on 2010-06-15.
"""

from PyQt4.QtCore import QRectF
from PyQt4.QtGui import QBrush
from PyQt4.QtGui import QGraphicsItem
from PyQt4.QtGui import QGraphicsSimpleTextItem
from PyQt4.QtGui import QPen, QDrag

import styles


class SliceHelix(QGraphicsItem):
    """docstring for SliceHelix"""
    # set up default, hover, and active drawing styles
    def_brush = QBrush(styles.grayfill)
    def_pen = QPen(styles.graystroke, styles.SLICE_HELIX_STROKE_WIDTH)
    hov_brush = QBrush(styles.bluefill)
    hov_pen = QPen(styles.bluestroke, styles.SLICE_HELIX_HILIGHT_WIDTH)
    use_brush = QBrush(styles.orangefill)
    use_pen = QPen(styles.orangestroke, styles.SLICE_HELIX_STROKE_WIDTH)
    radius = styles.SLICE_HELIX_RADIUS
    rect = QRectF(0, 0, 2*radius, 2*radius)

    def __init__(self, row, col, position, parent):
        super(SliceHelix, self).__init__()
        self.parent = parent
        # data related
        self.row = row
        self.col = col
        self.parity = (row % 2) ^ (col % 2)
        self.p0neighbor = None
        self.p1neighbor = None
        self.p2neighbor = None
        self.number = -1 
        self.vhelix = None
        self.label = None
        # drawing related
        self.beingHoveredOver = False
        self.setAcceptsHoverEvents(True)
        self.setPos(position)
    
    def paint(self, painter, option, widget=None):
        if self.number >= 0:
            painter.setBrush(self.use_brush)
            painter.setPen(self.use_pen)
        else:
            painter.setBrush(self.def_brush)
            painter.setPen(self.def_pen)
        if self.beingHoveredOver:
            #Focus ring will be drawn beneath 2 neighboring SliceHelix if we do it here
            #painter.setBrush(self.hov_brush)
            painter.setPen(self.hov_pen)
        painter.drawEllipse(self.rect)
    
    class FocusRingPainter(QGraphicsItem):
        def __init__(self,helix):
            super(FocusRingPainter,self).__init__()
            self.helix=helix       
            self.setPos(helix.pos())
        def paint(self,painter,option,widget=None):
            painter.setPen(self.hov_pen)
            painter.drawEllipse(self.rect)
        def boundingRect(self):
            return self.helix.rect

    def boundingRect(self):
        return self.rect

    def hoverEnterEvent(self, event):
        """hoverEnterEvent changes the SliceHelix brush and pen from default to the hover colors if necessary."""
        self.beingHoveredOver = True
        self.update(self.rect)
    # end def

    def hoverLeaveEvent(self, event):
        """hoverEnterEvent changes the SliceHelix brush and pen from hover to the default colors if necessary."""
        self.beingHoveredOver = False
        self.update(self.rect)
    # end def

    def mousePressEvent(self, event):
        self.setUsed(not self.number>=0)
        QDrag(self.parent.parentWidget())
   
    def dragEnterEvent(self,e):
        self.setUsed(not self.number>=0)
        e.acceptProposedAction()
        print "dee"
        
    def setNumber(self,n):
        """If n!=slice.number the caller should have already reserved n with the parent SliceHelixGroup (get it from self.parent.newNumberForHelix). The callee tells the SliceHelixGroup to recycle the old value."""
        self.update(self.rect)
        if n!=self.number and self.number>=0:
            self.parent.recycleNumberForHelix(self.number,self)
        if n < 0:
            if self.label:
                self.label.setParentItem(None)
                self.label = None
            self.number = -1
            return
        self.number = n
        if self.label == None:
            self.label = QGraphicsSimpleTextItem("%d" % self.number)
            self.label.setParentItem(self)
        if self.number < 10:
            self.label.setX(self.radius/1.3)
        else:
            self.label.setX(self.radius/2)
        self.label.setY(self.radius/2)
     
    def setUsed(self,u):
        if (self.number>=0) == u:
            return
        if self.number < 0: #Use
            self.setNumber(self.parent.newNumberForHelix(self))
        else: #Unuse
            self.setNumber(-1)
