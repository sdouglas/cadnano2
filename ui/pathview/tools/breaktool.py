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
from PyQt4.QtGui import QBrush, QFont
from PyQt4.QtGui import QGraphicsItem, QGraphicsSimpleTextItem
from PyQt4.QtGui import QPainterPath
from PyQt4.QtGui import QPen
from model.enum import HandleOrient, StrandType
import ui.styles as styles
from ui.pathview.pathhelix import PathHelix
from abstractpathtool import AbstractPathTool
class BreakTool(AbstractPathTool):
    _pen = QPen(styles.redstroke, 2)
    _brush = QBrush(styles.breakfill)
    _baseWidth = styles.PATH_BASE_WIDTH
    _halfbaseWidth = _baseWidth / 2
    _rectDown = QRectF(0, -_baseWidth, _baseWidth, _baseWidth*2)
    _rectUp   = QRectF(0, 0, _baseWidth, _baseWidth*2)

    def _polyGen(path, pointList):
        path.moveTo(pointList[0])
        for pt in pointList[1:]:
            path.lineTo(pt)
        path.lineTo(pointList[0])

    # define points for arrow
    _leftX = 0
    _leftCenterX = 0.25 * _baseWidth
    _rightCenterX = 0.75 * _baseWidth
    _rightX = _baseWidth
    _midY = _halfbaseWidth
    _topY = _baseWidth

    # Arrow pointing down
    _pathStart = QPointF(_halfbaseWidth, 0)
    _p2 = QPointF(_leftX, -_midY)
    _p3 = QPointF(_leftCenterX, -_midY)
    _p4 = QPointF(_leftCenterX, -_topY)
    _p5 = QPointF(_rightCenterX, -_topY)
    _p6 = QPointF(_rightCenterX, -_midY)
    _p7 = QPointF(_rightX, -_midY)
    _pathArrowDown = QPainterPath()
    _polyGen(_pathArrowDown, [_pathStart, _p2, _p3, _p4, _p5, _p6, _p7])
    #_pathArrowDown.translate(0, _baseWidth)

    # Arrow pointing up
    _pathArrowUp = QPainterPath()
    _pathStart = QPointF(_halfbaseWidth, _baseWidth)
    _p2 = QPointF(_leftX, _baseWidth + _midY)
    _p3 = QPointF(_leftCenterX, _baseWidth + _midY)
    _p4 = QPointF(_leftCenterX, _baseWidth + _topY)
    _p5 = QPointF(_rightCenterX, _baseWidth + _topY)
    _p6 = QPointF(_rightCenterX, _baseWidth + _midY)
    _p7 = QPointF(_rightX, _baseWidth + _midY)
    _polyGen(_pathArrowUp, [_pathStart, _p2, _p3, _p4, _p5, _p6, _p7])
    #_pathArrowUp.translate(0, -_baseWidth)

    def __init__(self, controller, parent=None):
        super(BreakTool, self).__init__(controller, parent)
        self.latestHoveredBaseWasTop = True
        self.setZValue(styles.ZPATHTOOL)
        self._rect = self._rectDown
    
    def orientedDown(self):
        return self._rect==self._rectDown
    
    def setOrientedDown(self, newOD):
        self._rect = self._rectDown if newOD else self._rectUp
        self.prepareGeometryChange()
    
    def paint(self, painter, option, widget=None):
        super(BreakTool, self).paint(painter, option, widget)
        painter.setPen(self._pen)
        painter.setBrush(self._brush)
        if self.orientedDown():
            painter.drawPath(self._pathArrowDown)
        else:
            painter.drawPath(self._pathArrowUp)
            
    def hoverMovePathHelix(self, item, event, flag=None):
        """
        flag is for the case where an item in the path also needs to
        implement the hover method
        """
        self.setParentItem(item)
        self.show()
        posItem = event.pos()
        if flag != None:
            posScene = event.scenePos()
            posItem = self.parentItem().mapFromScene(posScene)
        self.setOrientedDown(self.helixIndex(posItem)[1]==0)
        self.setPos(self.helixPos(posItem))

    def mousePressPathHelix(self, pathHelix, event):
        posScene = event.scenePos()
        posItem = self.parentItem().mapFromScene(posScene)
        strandType, idx = self.baseAtPoint(pathHelix, posItem)
        pathHelix.vhelix().clearStrand(strandType, idx, idx)
        