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
skiphandle.py
Created by Shawn on 2011-05-03.
"""

from PyQt4.QtCore import QPointF, QRectF, Qt
from PyQt4.QtGui import QBrush, QFont
from PyQt4.QtGui import QGraphicsItem, QGraphicsSimpleTextItem
from PyQt4.QtGui import QPainterPath
from PyQt4.QtGui import QPen
import ui.styles as styles
from ui.pathhelix import PathHelix

class SkipItem(QGraphicsItem):
    """
    This is just the shape of the Loop item
    """
    _myRect = QRectF(0, 0, styles.PATH_BASE_WIDTH, styles.PATH_BASE_WIDTH)
    _pen = QPen(styles.redstroke, 2)
    baseWidth = styles.PATH_BASE_WIDTH
    halfbaseWidth = baseWidth/2
    
    def _xGen(path, p1, p2, p3, p4):
        path.moveTo(p1)
        path.lineTo(p2)
        path.moveTo(p3)
        path.lineTo(p4)
    # end def

    _pathStart = QPointF(halfbaseWidth,halfbaseWidth)
    
    _skipPath = QPainterPath()
    _xGen(_skipPath, _myRect.bottomLeft(), _myRect.topRight(), \
                        _myRect.topLeft(), _myRect.bottomRight())

    def __init__(self, parent=None):
        super(SkipItem, self).__init__(parent)
        self.setZValue(styles.ZSKIPHANDLE)
    # end def
        
    def boundingRect(self):
        return self._myRect

    def paint(self, painter, option, widget=None):
        painter.setPen(self._pen)
        painter.drawPath(self._skipPath)
    # end def
# end class

class SkipHandle(QGraphicsItem):
    """
    Loop handle consists of the LoopItem and the QLabel and manages loop 
    manipulation
    """
    def __init__(self, vstrand, pos, skipSize, parent=None):
        super(SkipHandle, self).__init__(parent)
        # bookkeeping
        self.vstrand = vstrand
        self.setPos(pos)
        self.name = pos.toString()
        self.skipItem = SkipItem(parent=self)
            
        # data
        self.vstrand.addLoop(pos,skipSize);
    
        # appearance

        self._label = QGraphicsSimpleTextItem("%d" % skipSize, parent=self)
        # self._label.setFont(self._myfont)
        
        self.setZValue(styles.ZSKIPHANDLE)
    # end def