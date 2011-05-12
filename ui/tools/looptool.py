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
from PyQt4.QtGui import QPen
from model.enum import HandleOrient
import ui.styles as styles
from ui.pathhelix import PathHelix


class BaseTool(QGraphicsItem):
        _toolRect = QRectF(0,0, \
                            styles.PATH_BASE_WIDTH, \
                            styles.PATH_BASE_WIDTH )
        _rect = QRectF(0,0, \
                            styles.PATH_BASE_WIDTH + \
                            styles.PATH_BASE_HL_STROKE_WIDTH/2, \
                            styles.PATH_BASE_WIDTH + \
                            styles.PATH_BASE_HL_STROKE_WIDTH/2 )
        _pen = QPen(styles.redstroke, styles.PATH_BASE_HL_STROKE_WIDTH)
        def __init__(self, pathcontroller=None, parent=None):
            """
            A base class, no pun intended to display a highlight tool for 
            selecting an individual base in the path view
            
            it's parent should be 
            """
            super(BaseTool, self).__init__(parent)
            
            # self.undoStack = pathcontroller.mainWindow.undoStack
            # self._enabled = False
            # self.setFlag(QGraphicsItem.ItemIsMovable)
            
            # self.x0 = baseIndex * baseWidth
            # self.y0 = self.getYoffset()
            # self.pressX = 0
            # self.pressXoffset = 0
            self.hide()
        # end def
        
        def paint(self, painter, option, widget=None):
            painter.setPen(self._pen)
            painter.drawRect(self._toolRect)
        # end def
        
        def boundingRect(self):
            return self._rect
        # end def
        
        def setEnableTool(self,mode):
            self._enabled = mode
        # end def
        
        def toolPress(self, item, event):
            pass
        #     if event.button() != Qt.LeftButton:
        #         QGraphicsItem.mousePressEvent(self, event)
        #     else:
        #         # if self.parentItem() == self.restoreParentItem:
        #         self.scene().views()[0].addToPressList(self)
        #         self._dragMode = True
        #         self.scene().clearSelection()
        #         self.pressX = event.scenePos().x()
        #         self.pressXoffset = self.pressX % baseWidth
        # end def
        
        def toolHoverEnter(self,item,event):
            self.setParentItem(item)
            self.show()
        # end def
        
        def toolHoverLeave(self,item,event):
            self.hide()
        # end def
        
        def toolHoverMove(self, item, event):
                posScene = event.scenePos()
                posItem = event.pos()
                # posItem = self.mapFromScene(posItem)
                
                self.setPos(posItem)
                # moveX = posScene.x()
                # deltaX = moveX - self.pressX
                # self.tempIndex = int((self.baseIndex * baseWidth +\
                #                       self.pressXoffset + deltaX) / baseWidth)
                # if self.tempIndex < self.minIndex:
                #     self.tempIndex = self.minIndex
                # elif self.tempIndex > self.maxIndex:
                #     self.tempIndex = self.maxIndex
                # self.x0 = self.tempIndex * baseWidth
                # 
                # self.setPos(self.x0, self.y0)
                
        # end def
        
        
# end class         


# class LoopTool(QGraphicsItem):
#     """
#     XoverHandlePair responds to mouse input and serves as an interface
#     for adding scaffold crossovers
# 
#     Each handle is created by the PathController. Its parent is a PathHelix
#     """
#     _pen = QPen(styles.bluestroke, 2)
# # end class