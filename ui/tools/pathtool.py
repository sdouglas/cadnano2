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


class PathTool(QGraphicsItem):
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
            
            it's parent should be *always* be a PathHelix
            """
            super(PathTool, self).__init__(parent)
            
            # self.undoStack = pathcontroller.mainWindow.undoStack
            self.baseWidth = styles.PATH_BASE_WIDTH
            self.hide()
            self.setZValue(styles.ZPATHTOOL)
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
            posScene = event.scenePos()
            posItem = self.parentItem().mapFromScene(posScene)
            indexp = self.helixIndex(posItem)
            print "PathTool clicked at: (%d, %d) on helix %d" % \
                (indexp[0], indexp[1], self.parentItem().number())
        # end def
        
        def toolHoverEnter(self,item,event):
            self.setParentItem(item)
            self.show()
        # end def
        
        def toolHoverLeave(self,item,event):
            self.hide()
        # end def
        
        def toolHoverMove(self, item, event, flag=None):
            """
            flag is for the case where an item in the path also needs to 
            implement the hover method
            """
            posItem = event.pos()
            if flag != None:
                posScene = event.scenePos()
                posItem = self.parentItem().mapFromScene(posScene)
            self.setPos(self.helixPos(posItem))
        # end def
        
        def helixIndex(self, point):
            x = int(point.x()/self.baseWidth)
            y = int(point.y()/self.baseWidth)
            return (x,y)
        # end def
        
        def helixPos(self, point):
            x = int(point.x()/self.baseWidth)*self.baseWidth
            y = int(point.y()/self.baseWidth)*self.baseWidth
            return QPointF(x,y)
        # end def
# end class         
