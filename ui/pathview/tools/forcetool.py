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
forcetool.py

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

class ForceTool(AbstractPathTool):
    
    _pen1 = QPen(styles.bluestroke, 2)
    _pen1.setCapStyle(Qt.RoundCap)
    _pen1.setJoinStyle(Qt.RoundJoin)
    _brush1 = QBrush(styles.forcefill)
    _pen2 = QPen(styles.orangestroke, 2)
    _pen2.setCapStyle(Qt.RoundCap)
    _pen2.setJoinStyle(Qt.RoundJoin)
    _brush2 = QBrush(styles.orangefill)
    
    def __init__(self, parent=None):
        super(ForceTool, self).__init__(parent)
        self.hide()
        self.setZValue(styles.ZPATHTOOL)
        self.base1 = None
    
    def paint(self, painter, option, widget=None):
        if self.base1:
            p, b = self._pen2, self._brush2
        else:
            p, b = self._pen1, self._brush1
        painter.setPen(p)
        painter.setBrush(b)
        painter.drawRect(self._toolRect)
    
    def mousePressPathHelix(self, pathHelix, event):
        posScene = event.scenePos()
        posItem = self.parentItem().mapFromScene(posScene)
        if self.base1==None:
            strandType, idx = self.baseAtPoint(pathHelix, posItem)
            vh = pathHelix.vhelix()
            self.base1 = (vh, strandType, idx)
            vh.setFloatingXover(strandType, idx, posScene)
        else:
            vh1, strand1, idx1 = self.base1
            vh1.setFloatingXover(None)
            vh2, idx2 = pathHelix.vhelix(), self.baseAtPoint(pathHelix, posItem)[1]
            vh1.installXoverFrom3To5(strand1, idx1, vh2, idx2)
            self.base1 = None
    
    def hoverMovePathHelix(self, pathHelix, event):
        super(ForceTool, self).hoverMovePathHelix(pathHelix, event)
        posScene = event.scenePos()
        self.updateFloatingXoverLocation(posScene)
    
    def hoverMovePathHelixGroup(self, pathHelixGroup, event):
        posScene = event.scenePos()
        self.updateFloatingXoverLocation(posScene)
    
    def updateFloatingXoverLocation(self, posScene):
        if self.base1:
            vh, strandType, idx = self.base1
            vh.setFloatingXover(strandType, idx, posScene)
    
    #def mouseReleasePathHelix(self, pathHelix, event):
    #    super(ForceTool, self).mouseReleasePathHelix(pathHelix, event)
    #    if self.base1:
    #        vh, strandType, idx = self.base1
    #        vh.setFloatingXover(strandType, idx, posScene)
    #        self.base1 = None