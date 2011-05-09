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
crossoverhandle.py
Created by Shawn on 2011-05-03.
"""
from exceptions import AttributeError, NotImplementedError
from PyQt4.QtCore import QPointF, QRectF, Qt
from PyQt4.QtGui import QBrush, QFont
from PyQt4.QtGui import QGraphicsItem, QGraphicsSimpleTextItem
from PyQt4.QtGui import QPainterPath
from PyQt4.QtGui import QPolygonF
from PyQt4.QtGui import QPen, QUndoCommand
from model.enum import StrandType, Parity, BreakType, HandleOrient
import ui.styles as styles

class CrossoverHandle(QGraphicsItem):
    """
    CrossoverHandle responds to mouse input and serves as an interface
    for adding scaffold crossovers

    Each handle is created by the PathController. Its parent is a PathHelix
    """
    pen = QPen(styles.bluestroke , 2)
    pen.setCapStyle(Qt.RoundCap)
    pen.setJoinStyle(Qt.RoundJoin)
    baseWidth = styles.PATH_BASE_WIDTH
    

    def __init__(self, indexA, helixA, indexB, helixB, parent=None):
        """
        Initialize a CrossoverHandle
        
        parent should be the PathHelixGroup and not a PathHelix
        """
        super(CrossoverHandle, self).__init__(parent)
        self.undoStack = parent.parentItem().pathController.mainWindow.undoStack
        self.rect = QRectF()
        self.orientation = None     # Left or right
        self.pointA = CrossoverPoint(indexA, helixA)
        self.pointB = CrossbverPoint(indexB, helixB)
        self.painterpath = QPainterPath()
        self.setZValue(styles.ZCROSSOVERHANDLE)
        self.refreshPath = self.rightDrawConfig

    def configure(self, orientation, index):
        """
        sets up the PCH to be tied to a helix as its parent such that
            when a helix is repostioned, it will redraw correctly
        gives it a partner to know who it needs to be connected to
        figures out the orientation to draw the PCH on the helix
        
        """
        self.orientation = orientation
        self.label.setText("%d" % (self.partner.number()))
        self.setX(self.baseWidth*index) # the position on the helix to draw
        # self.setX(0) # the position on the helix to draw

        if orientation == HandleOrient.RightDown:
            self.setX(self.baseWidth*index+styles.PATH_BASE_WIDTH/2)
            self.refreshPath = self.rightDrawConfig
        elif orientation == HandleOrient.LeftDown:
            self.refreshPath = self.leftDrawConfig
        else:
            raise AttributeError("CH orientation not recognized")
    # end def

    def rightDrawConfig(self):
        
        pA = self.mapFromItem(self.pointA,self.pointA.pos())
        pB =self.mapFromItem(self.pointB,self.pointB.pos())
        c1 = QPointF( (pA.x()+pB.x()) /2,  (pA.y()+pB.y()) /2) 
        self.painterpath.moveTo(pA)
        self.painterpath.cubicTo(c1, c1, pB)
    # end def

    def leftDrawConfig(self):
        
        pA = self.mapFromItem(self.pointA,self.pointA.pos())
        pB = self.mapFromItem(self.pointB,self.pointB.pos())
        c1 = QPointF( (pA.x()+pB.x()) /2,  (pA.y()+pB.y()) /2) 
        self.painterpath.moveTo(pA)
        self.painterpath.cubicTo(c1, c1, pB)
    # end def

    def boundingRect(self):
        return self.rect

    def paint(self, painter, option, widget=None):
        painter.setPen(self.pen)
        self.refreshPath()
        painter.drawPath(self.painterpath)
        # self.handlePainter(painter)
    # end def

    def mousePressEvent(self, event):
        """
        This handles installing crossovers
        """
        if event.button() != Qt.LeftButton:
            QGraphicsItem.mousePressEvent(self,event)
        # end else
        else:
            pass
            # install crossover
            # FILL IN
        # end else
    # end def
# end class

class CrossoverPoint(QGraphicsItem):
    _myfont = QFont("Times", 10, QFont.Bold)
    _myRect = QRectF(0, 0, styles.PATH_BASE_WIDTH, styles.PATH_BASE_WIDTH)    
    def __init__(self, orientation, index, xhandle, parent=None):
        """
        Merely initialize a CrossoverPoint
        This is a shell class that provides a lable and can be parented
        to a PathHelix to allow easy redrawing of a crossover when a pathhelix
        is repositioned
        
        orientation specs the where the label is above or below the helix
        index is the the helix index the crossover is at
        parent should be the path helix it is on
        """
        super(CrossoverPoint, self).__init__(parent)
        self.setPos(index*styles.PATH_BASE_WIDTH, 0)
        self._xoverhandle = xhandle
        self._label = QGraphicsSimpleTextItem("", parent=self)
        self._label.setParentItem(self)
        self._label.setPos(0, 0)
        self.label.setFont(self._myfont)
        self.endPoint = QPointF()
        # self.label.hide()
    # end def
    
    def boundingRect(self):
        return self._myRect

    def paint(self, painter, option, widget=None):
        pass
    # end def
# end class
