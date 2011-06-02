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
import ui.styles as styles
from PyQt4.QtGui import QGraphicsItem, QGraphicsItemGroup
from PyQt4.QtCore import QPointF, QRectF, Qt
from PyQt4.QtGui import QBrush, QFont, QPen
from model.enum import StrandType
# There's a bug where C++ will free orphaned
# graphics items out from under pyqt. To avoid
# this, "mother" adopts orphaned graphics items.
mother = QGraphicsItemGroup()

class AbstractPathTool(QGraphicsItem):
    """
    Abstract base class to be subclassed by all other pathview tools.

    AbstractPathTool is an abstract class for tools that can handle events
    forwarded in the style of util.defineEventForwardingMethodsForClass.
    
    In other words, the activeTool() gets events from various graphics objects
    in the pathview and then makes the corresponding changes to the model.
    
    The displayed content then updates automatically via notifications from
    the model.
    * the activeTool gets events from graphics items and does the work
      (changes the model). Possible future configuration of the activeTool()
      can be done on the instances of various tools kept in the controller,
      like selectTool.
    * graphics items that make up the view sit back and watch the model,
      updating when it changes
    """

    _baseWidth = styles.PATH_BASE_WIDTH
    _toolRect = QRectF(0, 0,\
                       _baseWidth, _baseWidth)
    _rect = QRectF(0, 0,\
                   _baseWidth +\
                   styles.PATH_BASE_HL_STROKE_WIDTH / 2,\
                   _baseWidth +\
                   styles.PATH_BASE_HL_STROKE_WIDTH / 2)
    _pen = QPen(styles.redstroke, styles.PATH_BASE_HL_STROKE_WIDTH)
    _brush = QBrush(Qt.NoBrush)
    
    def __init__(self, controller, parent=None):
        super(AbstractPathTool, self).__init__(parent)
        self._active = False
        self._controller = controller

    def paint(self, painter, option, widget=None):
        painter.setPen(self._pen)
        painter.setBrush(self._brush)
        painter.drawRect(self._toolRect)
    # end def
    
    def boundingRect(self):
        return self._rect
    # end def
    
    def hoverEnterPathHelix(self, pathHelix, event):
        self.setParentItem(pathHelix)
        self.show()
    # end def

    def hoverLeavePathHelix(self, pathHelix, event):
        self.hide()
    # end def
    
    def hoverMovePathHelix(self, pathHelix, event, flag=None):
        """
        Flag is for the case where an item in the path also needs to
        implement the hover method.
        """
        self.setParentItem(pathHelix)
        self.show()       
        posItem = event.pos()
        if flag != None:
            posScene = event.scenePos()
            posItem = self.parentItem().mapFromScene(posScene)
        self.setPos(self.helixPos(posItem))
    # end def

    def setActive(self, willBeActive):
        """
        Called by PathController.setActiveTool when the tool becomes
        active. Used, for example, to show/hide tool-specific ui elements.
        """
        if self.isActive() and not willBeActive:
            self.setParentItem(mother)

    def isActive(self):
        """Returns isActive"""
        return self._active!=mother
    
    def baseAtPoint(self, pathHelix, pt):
        """Returns the (strandType, baseIdx) corresponding
        to pt in pathHelix."""
        x, strandIdx = self.helixIndex(pt)
        vh = pathHelix.vhelix()
        if vh.evenParity():
            strandType = (StrandType.Scaffold, StrandType.Staple)[strandIdx]
        else:
            strandType = (StrandType.Staple, StrandType.Scaffold)[strandIdx]
        return (strandType, x)
    
    def helixIndex(self, point):
        """Returns the (row, col) of the base which point
        lies within."""
        x = int(point.x() / self._baseWidth)
        y = int(point.y() / self._baseWidth)
        return (x, y)
    # end def

    def helixPos(self, point):
        """Snaps a point to the upper left corner of the base
        it is within."""
        x = int(point.x() / self._baseWidth) * self._baseWidth
        y = int(point.y() / self._baseWidth) * self._baseWidth
        return QPointF(x, y)
    # end def
# end class
