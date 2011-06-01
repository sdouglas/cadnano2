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
from model.enum import HandleOrient
import ui.styles as styles
from ui.pathview.pathhelix import PathHelix
from abstractpathtool import AbstractPathTool


class BreakItem(QGraphicsItem):
    """
    This is just the shape of the Loop item
    """
    _myRect = QRectF(0, 0, styles.PATH_BASE_WIDTH, styles.PATH_BASE_WIDTH)
    _pen = QPen(styles.redstroke, 2)
    _brush = QBrush(styles.breakfill)
    _baseWidth = styles.PATH_BASE_WIDTH
    _halfbaseWidth = _baseWidth / 2

    # using this method instead of QPolygonF...
    def _polyGen(path, pointList):
        path.moveTo(pointList[0])
        for pt in pointList[1:]:
            path.lineTo(pt)
        path.lineTo(pointList[0])
    # end def

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

    def __init__(self, parent=None):
        super(BreakItem, self).__init__(parent)
        self.painterPath = self._pathArrowDown
        self.setZValue(styles.ZBREAKITEM)
    # end def

    def setOrient(self, orient):
        if orient == "Up":
            self.painterPath = self._pathArrowDown
        else:
            self.painterPath = self._pathArrowUp
    # end def

    def boundingRect(self):
        return self._myRect

    def paint(self, painter, option, widget=None):
        painter.setPen(self._pen)
        painter.setBrush(self._brush)
        painter.drawPath(self.painterPath)
    # end def
# end class


class BreakTool(AbstractPathTool):
    def __init__(self, parent=None):
        """
        This class inherits from the AbstractPathTool class for the majority of
        methods/behaviours.  Essentially it adds merely decorator graphics
        custimazation of behaviour and data structure access particular to
        loop insertion on a mouseclick.

        Its parent should be *always* be a PathHelix.
        """
        super(BreakTool, self).__init__(parent)
        self._breakItem = BreakItem(parent=self)
        self.hide()
        self.setZValue(styles.ZPATHTOOL)
    # end def

    def hoverMovePathHelix(self, item, event, flag=None):
        pass
    def mousePressPathHelix(self, ph, event):
        print "mp"
    
    def hoverEnterPathHelix(self, ph, event):
        if not self._graphic:
            g = self._graphic = BreakItem(ph)
        self.hoverMovePathHelix(self, ph, event)
    
    def hoverLeavePathHelix(self, ph, event):
        if self._graphic:
            pass
    
    def hoverMovePathHelix(self, ph, event):
        pass
    
    def toolHoverMove(self, item, event, flag=None):
        """
        flag is for the case where an item in the path also needs to
        implement the hover method
        """
        posItem = event.pos()
        if flag != None:
            posScene = event.scenePos()
            posItem = self.parentItem().mapFromScene(posScene)
        if self.helixIndex(posItem)[1] == 1:
            self._breakItem.setOrient("Down")
        else:
            self._breakItem.setOrient("Up")
        self.setPos(self.helixPos(posItem))
    # end def

    def mousePressPathHelix(self, item, event):
        posScene = event.scenePos()
        posItem = self.parentItem().mapFromScene(posScene)
        indexp = self.helixIndex(posItem)
        print "BreakTool clicked at: (%d, %d) on helix %d" % \
            (indexp[0], indexp[1], self.parentItem().number())
        # create a new LoopHandle by adding through the     parentItem
    # end def
# end class
