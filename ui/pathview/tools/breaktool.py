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
breaktool.py

Created by Nick on 2011-05-18
"""

from exceptions import AttributeError, NotImplementedError
from PyQt4.QtCore import QPointF, QRectF, Qt
from PyQt4.QtGui import QBrush, QFont, QPolygonF
from PyQt4.QtGui import QGraphicsItem, QGraphicsSimpleTextItem
from PyQt4.QtGui import QPainterPath
from PyQt4.QtGui import QPen
from model.enum import HandleOrient, StrandType
import ui.styles as styles
from ui.pathview.pathhelix import PathHelix
from abstractpathtool import AbstractPathTool


class BreakTool(AbstractPathTool):
    _pen = QPen(styles.redstroke, 1)
    _baseWidth = styles.PATH_BASE_WIDTH
    _halfbaseWidth = _baseWidth / 2
    _rect = QRectF(0, 0, _baseWidth, _baseWidth )
    _pathArrowLeft = QPainterPath()
    _l3poly = QPolygonF()
    _l3poly.append(QPointF(_baseWidth, 0))
    _l3poly.append(QPointF(0.25 * _baseWidth, 0.5 * _baseWidth))
    _l3poly.append(QPointF(_baseWidth, _baseWidth))
    _pathArrowLeft.addPolygon(_l3poly)
    _pathArrowRight = QPainterPath()
    _r3poly = QPolygonF()
    _r3poly.append(QPointF(0, 0))
    _r3poly.append(QPointF(0.75 * _baseWidth, 0.5 * _baseWidth))
    _r3poly.append(QPointF(0, _baseWidth))
    _pathArrowRight.addPolygon(_r3poly)

    def __init__(self, controller, parent=None):
        super(BreakTool, self).__init__(controller, parent)
        self.latestHoveredBaseWasTop = True
        self.setZValue(styles.ZPATHTOOL)
        self._isTopStrand = True

    def setTopStrand(self, isTop):
        """
        Called in hoverMovePathHelix to set whether breaktool is hovering
        over a top strand (goes 5' to 3' left to right) or bottom strand.
        """
        self._isTopStrand = isTop

    def paint(self, painter, option, widget=None):
        super(BreakTool, self).paint(painter, option, widget)
        painter.setPen(self._pen)
        if self._isTopStrand:
            painter.drawPath(self._pathArrowRight)
        else:
            painter.drawPath(self._pathArrowLeft)

    def hoverMovePathHelix(self, item, event, flag=None):
        """
        flag is for the case where an item in the path also needs to
        implement the hover method
        """
        self.updateLocation(item, event.scenePos())
        posScene = event.scenePos()
        posItem = self.parentItem().mapFromScene(posScene)
        self.setTopStrand(self.helixIndex(posItem)[1] == 0)
        self.setPos(self.helixPos(posItem))

    def mousePressPathHelix(self, pathHelix, event):
        posScene = event.scenePos()
        posItem = self.parentItem().mapFromScene(posScene)
        strandType, idx = self.baseAtPoint(pathHelix, posItem)
        if pathHelix.vhelix().hasEndAt(strandType, idx):
            return  # don't try to break endpoints
        if pathHelix.vhelix().directionOfStrandIs5to3(strandType):
            pathHelix.vhelix().clearStrand(strandType, idx + 1, idx + 1)
        else:
            pathHelix.vhelix().clearStrand(strandType, idx, idx)
