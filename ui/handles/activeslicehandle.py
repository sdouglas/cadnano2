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

from PyQt4.QtCore import QPointF, QRectF
from PyQt4.QtCore import Qt
from PyQt4.QtGui import QBrush
from PyQt4.QtGui import QGraphicsItem
from PyQt4.QtGui import QGraphicsSimpleTextItem
from PyQt4.QtGui import QPen, QDrag, QUndoCommand
import ui.styles as styles


class ActiveSliceHandle(QGraphicsItem):
    """docstring for ActiveSliceHandle"""
    width = styles.PATH_BASE_WIDTH
    brush = QBrush(styles.orangefill)
    pen = QPen(styles.orangestroke, styles.SLICE_HANDLE_STROKE_WIDTH)

    def __init__(self, helixCount, startBase):
        super(ActiveSliceHandle, self).__init__()
        self.setFlag(QGraphicsItem.ItemIsMovable)
        self.height = (helixCount + 2) * (styles.PATH_BASE_HEIGHT + \
                                          styles.PATH_HELIX_PADDING)
        self.rect = QRectF(0, 0, self.width, self.height)
        
        self.x0 = startBase * self.width
        self.y0 = -1 * (styles.PATH_HELIX_PADDING)
        self.setPos(QPointF(self.x0, self.y0))

    def boundingRect(self):
        """docstring for boundingRect"""
        return self.rect

    def paint(self, painter, option, widget=None):
        painter.setBrush(self.brush)
        painter.setPen(self.pen)
        painter.drawRect(self.rect)

    def resize(self, helixCount):
        """docstring for resize"""
        height = (helixCount + 2) * (styles.PATH_BASE_HEIGHT + \
                                     styles.PATH_HELIX_PADDING)
        self.rect.setHeight(height)
        self.update(self.rect)

    def mouseMoveEvent(self, event):
        """docstring for mouseMoveEvent"""
        xf = event.pos().x()
        self.translate(xf - self.x0, 0)
        self.x0 = xf
