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
from model.enum import HandleOrient
import ui.styles as styles

class CrossoverHandle(QGraphicsItem):
    """
    CrossoverHandle responds to mouse input and serves as an interface
    for adding scaffold crossovers

    Each handle is created by the PathController. Its parent is a PathHelix
    """
    _pen = QPen(styles.bluestroke , 2)
    _pen.setCapStyle(Qt.RoundCap)
    _pen.setJoinStyle(Qt.RoundJoin)
    baseWidth = styles.PATH_BASE_WIDTH
    

    def __init__(self, preXoverA, preXoverB, parent=None):
        """
        Initialize a CrossoverHandle
        
        parent should be the PathHelixGroup and not a PathHelix
        """
        super(CrossoverHandle, self).__init__(parent)
        self.setParentItem(parent)
        # self.undoStack = parent.parentItem().pathController.mainWindow.undoStack
        
        # generate the points where the action happens
        
        self.pointA = CrossoverPoint(preXoverA.orientation(),\
                                        preXoverA.index(), \
                                        self, \
                                        preXoverA.helix())
        self.pointB = CrossoverPoint(preXoverB.orientation(),\
                                        preXoverB.index(), \
                                        self, \
                                        preXoverB.helix())
        self.pointA.setLabel(preXoverB.helix().number())
        self.pointB.setLabel(preXoverA.helix().number())
        
        rectA = self.mapRectFromItem(self.pointA, self.pointA.boundingRect())
        rectB = self.mapRectFromItem(self.pointB, self.pointB.boundingRect())
        self.rect = rectA.united(rectB)
        
        # handle drawing the cubic spline linker
        self.painterpath = None
        self.setZValue(styles.ZCROSSOVERHANDLE)
    # end def

    def refreshPath(self):
        self.painterpath = QPainterPath()
        # if we need to speed this up, we could keep track if pA changed?
        pA = self.mapFromItem(self.pointA,self.pointA.endPoint)
        pB = self.mapFromItem(self.pointB,self.pointB.endPoint)
        
        rectA = self.mapRectFromItem(self.pointA, self.pointA.boundingRect())
        rectB = self.mapRectFromItem(self.pointB, self.pointB.boundingRect())
        self.rect = rectA.united(rectB)
        
        c1 = QPointF( 0.35*pA.x()+0.65*pB.x(),  0.5*pA.y()+0.5*pB.y() ) 
        self.painterpath.moveTo(pA)
        self.painterpath.cubicTo(c1, c1, pB)
    # end def

    def boundingRect(self):
        return self.rect

    def paint(self, painter, option, widget=None):
        painter.setPen(self._pen)
        self.refreshPath()
        painter.drawPath(self.painterpath)
        # self.handlePainter(painter)
    # end def

    def mousePressEvent(self, event):
        """
        This handles manipulating crossovers somehow
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
    _pen = QPen(styles.bluestroke , 2)
    
    def _hashMarkGen(path, p1, p2, p3):
        path.moveTo(p1)
        path.lineTo(p2)
        path.lineTo(p3)
    # end
    
    _pathCenter = QPointF(styles.PATH_BASE_WIDTH/2, styles.PATH_BASE_WIDTH/2)
    _pathLeft = QPointF(0, styles.PATH_BASE_WIDTH/2)
    _pathUp = QPointF(styles.PATH_BASE_WIDTH/2, 0)
    _pathRight = QPointF(styles.PATH_BASE_WIDTH, styles.PATH_BASE_WIDTH/2)
    _pathDown = QPointF(styles.PATH_BASE_WIDTH/2, styles.PATH_BASE_WIDTH)
    _ppathLU = QPainterPath()
    _hashMarkGen(_ppathLU, _pathLeft, _pathCenter, _pathUp)
    _ppathRU = QPainterPath()
    _hashMarkGen(_ppathRU, _pathRight, _pathCenter, _pathUp)
    _ppathRD = QPainterPath()
    _hashMarkGen(_ppathRD, _pathRight, _pathCenter, _pathDown)
    _ppathLD = QPainterPath()
    _hashMarkGen(_ppathLD, _pathLeft, _pathCenter, _pathDown)
    
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
        
        self._xoverhandle = xhandle
        self._label = QGraphicsSimpleTextItem("", parent=self)
        self._label.setParentItem(self)
        self._label.setFont(self._myfont)
        self._painterpath = None
        self.configure(orientation, index)
        self.setZValue(styles.ZCROSSOVERHANDLE)
    # end def
    
    def configure(self, orientation, index):
        """
        Configure has for options for displaying hash marks
        """
        if orientation  == HandleOrient.LeftUp:
            # set postion to the top grid box
            self._painterpath = self._ppathLU
            self.configUp(index)
        elif orientation  == HandleOrient.RightUp:
            # set postion to the bottom grid box for down
            self._painterpath = self._ppathRU
            self.configUp(index)
        elif orientation  == HandleOrient.LeftDown:
            # set postion to the bottom grid box for down
            self._painterpath = self._ppathLD
            self.configDown(index)
        elif orientation  == HandleOrient.RightDown:
            # set postion to the bottom grid box for down
            self._painterpath = self._ppathRD
            self.configDown(index)
    # end def
    
    
    def configUp(self,index):
        self.setPos(index*styles.PATH_BASE_WIDTH, 0)
        self.endPoint = self._pathUp
        self._label.setPos(0.3*styles.PATH_BASE_WIDTH,-0.9*styles.PATH_BASE_WIDTH) # label on top
    # end def
    
    def configDown(self,index):
        self.setPos(index*styles.PATH_BASE_WIDTH, styles.PATH_BASE_WIDTH)
        self.endPoint = self._pathDown
        self._label.setPos(0.3*styles.PATH_BASE_WIDTH, 1.27*styles.PATH_BASE_WIDTH) # label below 
    # end def
    
    def setLabel(self,number):
        self._label.setText("%d" % number)
    # end def
    
    def boundingRect(self):
        return self._myRect

    def paint(self, painter, option, widget=None):
        painter.setPen(self._pen)
        painter.drawPath(self._painterpath)
    # end def
    
    def mousePressEvent(self, event):
        """
        This handles manipulating crossovers
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
