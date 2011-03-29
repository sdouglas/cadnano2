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
activeslicehandle.py
Created by Shawn on 2011-02-05.
"""

from exceptions import IndexError
from PyQt4.QtCore import QPointF, QRectF
from PyQt4.QtCore import Qt
from PyQt4.QtGui import QBrush
from PyQt4.QtGui import QGraphicsItem
from PyQt4.QtGui import QGraphicsSimpleTextItem
from PyQt4.QtGui import QPen, QDrag, QUndoCommand
import ui.styles as styles


class ActiveSliceHandle(QGraphicsItem):
    """docstring for ActiveSliceHandle"""
    baseWidth = styles.PATH_BASE_WIDTH
    brush = QBrush(styles.orangefill)
    pen = QPen(styles.orangestroke, styles.SLICE_HANDLE_STROKE_WIDTH)

    def __init__(self, part, startBase, parent=None):
        super(ActiveSliceHandle, self).__init__(parent)
        self.setFlag(QGraphicsItem.ItemIsMovable)
        self.part = part
        helixCount = self.part.getVirtualHelixCount()
        self.height = (helixCount + 2) * (styles.PATH_BASE_HEIGHT + \
                                          styles.PATH_HELIX_PADDING)
        self.rect = QRectF(0, 0, self.baseWidth, self.height)
        self.baseIndex = startBase
        self.tempIndex = startBase
        self.x0 = startBase * self.baseWidth
        self.y0 = -1 * (styles.PATH_HELIX_PADDING)
        self.minIndex = 0
        self.maxIndex = part.getCanvasSize()-1
        self.setPos(QPointF(self.x0, self.y0))
        self.setZValue(-10)
        self.pressX = 0
        self.pressXoffset = 0

    def boundingRect(self):
        """docstring for boundingRect"""
        return self.rect

    def paint(self, painter, option, widget=None):
        painter.setBrush(self.brush)
        painter.setPen(self.pen)
        painter.drawRect(self.rect)

    def getPosition(self):
        """Returns the base position"""
        return int(self.x0 / self.baseWidth)

    def setPosition(self, pos):
        """Returns the base position"""
        if pos >= 0 and pos <= self.maxBase:
            xf = pos * self.baseWidth
            self.translate(xf - self.x0, 0)
            self.x0 = xf
        else:
            raise IndexError

    def resize(self, helixCount):
        """Call after adding or removing a virtualhelix"""
        height = (helixCount + 2) * (styles.PATH_BASE_HEIGHT + \
                                     styles.PATH_HELIX_PADDING)
        self.rect.setHeight(height)
        self.update(self.rect)

    def resetBounds(self, maxBase):
        """Call after resizing virtualhelix canvas."""
        self.maxBase = maxBase
        self.maxX = (maxBase-1) * self.baseWidth

    def mouseMoveEvent(self, event):
        """Snaps handle into place when dragging."""
        moveX = event.scenePos().x()
        delta = moveX-self.pressX
        self.tempIndex = int((self.baseIndex*self.baseWidth+\
                          self.pressXoffset+delta) / self.baseWidth)
        if self.tempIndex < self.minIndex:
            self.tempIndex = self.minIndex
        elif self.tempIndex > self.maxIndex:
            self.tempIndex = self.maxIndex
        self.x0 = self.tempIndex * self.baseWidth
        self.setPos(self.x0, self.y0)

    def mousePressEvent(self, event):
        self.pressX = event.scenePos().x()
        self.pressXoffset = self.pressX % self.baseWidth

    def mouseReleaseEvent(self, event):
        """Snaps to grid after mouse released. Updates vhelix data according
        to what movement took place."""
        if self.tempIndex == self.baseIndex:
            return
        delta = int(self.tempIndex - self.baseIndex)
        self.baseIndex = self.tempIndex

