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
from PyQt4.QtCore import Qt
from PyQt4.QtGui import QBrush
from PyQt4.QtGui import QGraphicsItem
from PyQt4.QtGui import QGraphicsSimpleTextItem
from PyQt4.QtGui import QPainterPath
from PyQt4.QtGui import QPen, QDrag, QUndoCommand
import styles
from model.virtualhelix import VirtualHelix


class PathHelix(QGraphicsItem):
    """docstring for PathHelix"""
    minorGridPen = QPen(styles.minorgridstroke, styles.PATH_GRID_STROKE_WIDTH)
    majorGridPen = QPen(styles.majorgridstroke, styles.PATH_GRID_STROKE_WIDTH)
    nobrush = QBrush(Qt.NoBrush)
    baseWidth = styles.PATH_BASE_WIDTH
    
    def __init__(self, vhelix, position, parent):
        super(PathHelix, self).__init__()
        self.vhelix = vhelix
        self.parent = parent
        self.setPos(position)
        self.minorGridPainterPath = self.getMinorGridPainterPath()
        self.majorGridPainterPath = self.getMajorGridPainterPath()
        self.rect = QRectF()
        self.updateRect()

    def updateRect(self):
        """Sets rect width to reflect number of bases in vhelix. Sets
        rect height to the width of two bases (one for scaffold and
        one for staple)"""
        canvasSize = self.vhelix.part().getCanvasSize()
        self.rect.setWidth(self.baseWidth*canvasSize)
        self.rect.setHeight(2*self.baseWidth)

    def boundingRect(self):
        return self.rect

    def paint(self, painter, option, widget=None):
        # Minor grid lines
        painter.setBrush(self.nobrush)
        painter.setPen(self.minorGridPen)
        painter.drawPath(self.minorGridPainterPath)
        # Major grid lines
        painter.setPen(self.majorGridPen)
        painter.drawPath(self.majorGridPainterPath)

    def getMinorGridPainterPath(self):
        """
        Returns a QPainterPath object for the minor grid lines.
        The path also includes a border outline and a midline for
        dividing scaffold and staple bases.
        """
        path = QPainterPath()
        canvasSize = self.vhelix.part().getCanvasSize()
        # border
        path.addRect(0,0,self.baseWidth*canvasSize, 2*self.baseWidth)
        # minor tick marks
        for i in range(canvasSize):
            if (i % 7 != 0):
                path.moveTo(self.baseWidth*i,0)
                path.lineTo(self.baseWidth*i,2*self.baseWidth)
        # staple-scaffold divider
        path.moveTo(0, self.baseWidth)
        path.lineTo(self.baseWidth*canvasSize, self.baseWidth)
        return path

    def getMajorGridPainterPath(self):
        """
        Returns a QPainterPath object for the major grid lines.
        This is separated from the minor grid lines so different
        pens can be used for each.
        """
        path = QPainterPath()
        canvasSize = self.vhelix.part().getCanvasSize()
        # major tick marks
        for i in range(0,canvasSize+1,7):
                path.moveTo(self.baseWidth*i,0)
                path.lineTo(self.baseWidth*i,2*self.baseWidth)
        return path

