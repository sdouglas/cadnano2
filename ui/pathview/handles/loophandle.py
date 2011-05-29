# The MIT License
#
# Copyright (c) 2011 Wyss Institute at Harvard University
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of self software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and self permission notice shall be included in
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
# http:#www.opensource.org/licenses/mit-license.php
"""
loophandle.py
Created by Shawn on 2011-05-03.
"""

from PyQt4.QtCore import QPointF, QRectF, Qt
from PyQt4.QtGui import QBrush, QFont
from PyQt4.QtGui import QGraphicsItem, QGraphicsSimpleTextItem
from PyQt4.QtGui import QPainterPath
from PyQt4.QtGui import QPen
import ui.styles as styles
from ui.pathview.pathhelix import PathHelix

class LoopItem(QGraphicsItem):
    """
    This is just the shape of the Loop item
    """
    _myRect = QRectF(0, 0, styles.PATH_BASE_WIDTH, styles.PATH_BASE_WIDTH)
    _pen = QPen(styles.bluestroke, 2)
    baseWidth = styles.PATH_BASE_WIDTH
    halfbaseWidth = baseWidth/2
    dx = 0#0.25*baseWidth # shift to right for even parity scaffold
    
    def _loopGen(path, start, c1, p1, c2):
        path.moveTo(start)
        path.quadTo(c1, p1)
        path.quadTo(c2, start)
    # end def

    _pathStart = QPointF(halfbaseWidth+dx,halfbaseWidth)
    _pathMidUp = QPointF(halfbaseWidth+dx, -baseWidth)
    _pathUpUpCtrlPt = QPointF(-halfbaseWidth+dx, -baseWidth)
    _pathUpDownCtrlPt = QPointF(1.5*baseWidth+dx, -baseWidth)
    _pathMidDown = QPointF(halfbaseWidth+dx,2*baseWidth)
    _pathDownDownCtrlPt = QPointF(-halfbaseWidth+dx,2*baseWidth)
    _pathDownUpCtrlPt = QPointF(1.5*baseWidth+dx,2*baseWidth)
    
    _loopPathUp = QPainterPath()
    _loopGen(_loopPathUp, _pathStart, _pathUpUpCtrlPt, _pathMidUp, _pathUpDownCtrlPt)
    _loopPathDown = QPainterPath()
    _loopGen(_loopPathDown, _pathStart, _pathDownDownCtrlPt, _pathMidDown, _pathDownUpCtrlPt)
    def __init__(self, orient, parent=None):
        super(LoopItem, self).__init__(parent)
        self.setOrient(orient)
        self.setZValue(styles.ZLOOPHANDLE)
    # end def
    
    def setOrient(self, orient):
        if orient == "Up":
            self.painterPath = self._loopPathUp
        else:
            self.painterPath = self._loopPathDown
    # end def
        
    def boundingRect(self):
        return self._myRect

    def paint(self, painter, option, widget=None):
        painter.setPen(self._pen)
        painter.drawPath(self.painterPath)
    # end def
# end class

class LoopHandle(QGraphicsItem):
    """
    Loop handle consists of the LoopItem and the QLabel and manages loop 
    manipulation
    """
    def __init__(self, vstrand, pos, loopSize, parent=None):
        super(LoopHandle, self).__init__(parent)
        # bookkeeping
        self.vstrand = vstrand
        self.setPos(pos)
        self.name = pos.toString()
        if vstrand.number % 2 == 0: 
            self.loopItem = LoopItem(orient="Up",parent=self)
        # end end if
        else:
            self.loopItem = LoopItem(orient="Down",parent=self)
            
        # data
        self.vstrand.addLoop(pos,loopSize);
    
        # appearance

        self._label = QGraphicsSimpleTextItem("%d" % loopSize, parent=self)
        # self._label.setFont(self._myfont)
        
        self.setZValue(styles.ZLOOPHANDLE)
    # end def
        
