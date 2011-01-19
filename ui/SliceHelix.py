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
SliceHelix.py

Created by Shawn on 2010-06-15.
"""

from PyQt4.QtCore import QRectF
from PyQt4.QtGui import QBrush
from PyQt4.QtGui import QGraphicsItem
from PyQt4.QtGui import QGraphicsSimpleTextItem
from PyQt4.QtGui import QPen

import Styles


class SliceHelix(QGraphicsItem):
    """docstring for SliceHelix"""
    # set up default, hover, and active drawing styles
    def_brush = QBrush(Styles.grayfill)
    def_pen = QPen(Styles.graystroke, Styles.SLICE_HELIX_STROKE_WIDTH)
    hov_brush = QBrush(Styles.bluefill)
    hov_pen = QPen(Styles.bluestroke, Styles.SLICE_HELIX_STROKE_WIDTH)
    use_brush = QBrush(Styles.orangefill)
    use_pen = QPen(Styles.orangestroke, Styles.SLICE_HELIX_STROKE_WIDTH)

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
        self.marked = False
        self.number = -1 
        self.vhelix = None
        self.label = None
        # drawing related
        self.setAcceptsHoverEvents(True);
        self.brush = SliceHelix.def_brush
        self.pen = SliceHelix.def_pen
        self.radius = Styles.SLICE_HELIX_RADIUS
        self.diameter = 2 * self.radius
        self.rect = QRectF(0, 0, self.diameter, self.diameter)
        self.setPos(position)
    # end def

    def paint(self, painter, option, widget=None):
        painter.setBrush(self.brush)
        painter.setPen(self.pen)
        painter.drawEllipse(self.rect)
    # end def    

    def boundingRect(self):
        return self.rect
    # end def

    def hoverEnterEvent(self, event):
        """hoverEnterEvent changes the SliceHelix brush and pen from default to the hover colors if necessary."""
        if self.marked:
            self.brush = SliceHelix.use_brush
            self.pen = SliceHelix.use_pen
        else:
            self.brush = SliceHelix.hov_brush
            self.pen = SliceHelix.hov_pen
            self.update()
    # end def

    def hoverLeaveEvent(self, event):
        """hoverEnterEvent changes the SliceHelix brush and pen from hover to the default colors if necessary."""
        if self.marked:
            self.brush = SliceHelix.use_brush
            self.pen = SliceHelix.use_pen
        else:
            self.brush = SliceHelix.def_brush
            self.pen = SliceHelix.def_pen
            self.update()
    # end def

    def mousePressEvent(self, event):
        pass

    def mouseReleaseEvent(self, event):
        """docstring for mousePressEvent"""
        # notify parent 
        self.parent.parseHelixClick(self)

    def useHelix(self):
        """useHelix adds displays the number after it has been clicked."""
        if self.label == None:
            self.label = QGraphicsSimpleTextItem("%d" % self.number)
            if self.number < 10:
                self.label.setX(self.radius/1.3)
            else:
                self.label.setX(self.radius/2)
            self.label.setY(self.radius/2)
            self.label.setParentItem(self)
        self.brush = SliceHelix.use_brush
        self.pen = SliceHelix.use_pen
        # update() is handled in SliceHelixGroup

# end class