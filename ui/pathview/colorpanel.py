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
colorpanel.py
Created by Shawn on 2011-05-31.
"""

from PyQt4.QtCore import QRectF, Qt
from PyQt4.QtGui import QBrush, QGraphicsItem, QColorDialog
import ui.styles as styles

class ColorPanel(QGraphicsItem):
    """docstring for ColorPanel"""
    _colors = styles.stapleColors
    _pen = Qt.NoPen  # QPen(styles.bluestroke, 2)

    def __init__(self, parent=None):
        super(ColorPanel, self).__init__(parent)
        self.rect = QRectF(0, 0, 20, 20)
        self.setFlag(QGraphicsItem.ItemIgnoresTransformations)
        self.colordialog = QColorDialog()
        self._currentColor = self._colors[0]
        self._brush = QBrush(self._currentColor)
        self.hide()

    def boundingRect(self):
        return self.rect

    def paint(self, painter, option, widget=None):
        painter.setBrush(self._brush)
        painter.setPen(self._pen)
        painter.drawRect(self.boundingRect())

    def mousePressEvent(self, event):
        self._currentColor = self.colordialog.getColor(self._currentColor)
        self._brush = QBrush(self._currentColor)
