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
activeslicehandle.py
Created by Shawn on 2011-02-05.
"""

from exceptions import IndexError
from PyQt4.QtCore import QPointF, QRectF
from PyQt4.QtCore import Qt, QObject, pyqtSignal, pyqtSlot
from PyQt4.QtGui import QBrush
from PyQt4.QtGui import QGraphicsItem
from PyQt4.QtGui import QGraphicsSimpleTextItem
from PyQt4.QtGui import QPen, QDrag, QUndoCommand
import ui.styles as styles
from mmayacadnano.activeslicehandle3d import ActiveSliceHandle3D # For Campbell

class ActiveSliceHandle(QGraphicsItem):
    """docstring for ActiveSliceHandle"""
    baseWidth = styles.PATH_BASE_WIDTH
    brush = QBrush(styles.orangefill)
    pen = QPen(styles.orangestroke, styles.SLICE_HANDLE_STROKE_WIDTH)

    def __init__(self, pathHelixGroup):
        super(ActiveSliceHandle, self).__init__(pathHelixGroup)
        self._pathHelixGroup = None
        self.setPathHelixGroup(pathHelixGroup)
        self._activeSlice = 0
        self.setFlag(QGraphicsItem.ItemIsMovable)
        self.setAcceptHoverEvents(True)
        self.setZValue(styles.ZACTIVESLICEHANDLE)
        self._dragMode = False
    
    def controller(self):
        return self._pathHelixGroup.controller()
    
    def part(self):
        return self._pathHelixGroup.part()
    
    def pathHelixGroup(self):
        return self._pathHelixGroup
    
    def setPathHelixGroup(self, newPHG):
        if self._pathHelixGroup:
            self._pathHelixGroup.geometryChanged.disconnect(self.prepareGeometryChange)
        if self._pathHelixGroup and self._pathHelixGroup.part():
            self._pathHelixGroup.part().activeSliceWillChange.disconnect(self._updateActiveSlice)
        self._pathHelixGroup = newPHG
        newPHG.geometryChanged.connect(self.prepareGeometryChange)
        newPHG.part().activeSliceWillChange.connect(self._updateActiveSlice)
        self._updateActiveSlice(newPHG.part().activeSlice())

    def activeSlice(self):
        return self.part().activeSlice()
    
    def setActiveSlice(self, baseIndex):
        self.part().setActiveSlice(baseIndex)
    
    def _updateActiveSlice(self, baseIndex):
        """The slot that receives active slice changed notifications from
        the part and changes the receiver to reflect the part"""
        bi = int(baseIndex)
        if bi < 0 or bi >= self.part().dimensions()[2]:
            raise IndexError
        self.setPos(bi*self.baseWidth, -styles.PATH_HELIX_PADDING)
        self._activeSlice = bi
    
    def boundingRect(self):
        return QRectF(0, 0, self.baseWidth, self.pathHelixGroup().boundingRect().height()+50)

    def paint(self, painter, option, widget=None):
        painter.setBrush(self.brush)
        painter.setPen(self.pen)
        painter.drawRect(self.boundingRect())

    def resetBounds(self, maxBase):
        """Call after resizing virtualhelix canvas."""
        self.maxBase = maxBase
        self.maxX = (maxBase-1) * self.baseWidth

    def hoverEnterEvent(self,event):
        if self.controller().toolUse == False:
            self.setCursor(Qt.OpenHandCursor)
        QGraphicsItem.hoverEnterEvent(self,event)
    # end def
    
    def hoverMoveEvent(self,event):
        if self.controller().toolUse == True:
            # pass None, but if needed pass self for having a special 
            # behavior for the slice helix
            self.controller().toolHoverMove(None, event,flag=True)
        QGraphicsItem.hoverMoveEvent(self,event)
    # end def
    
    def hoverLeaveEvent(self,event):
        self.setCursor(Qt.ArrowCursor)
        QGraphicsItem.hoverLeaveEvent(self,event)
    # end def

    def mouseMoveEvent(self, event):
        """Snaps handle into place when dragging."""
        if self.controller().toolUse or not self._dragMode:
            return
        x = event.scenePos().x()-self.pos().x()
        dx = int((x - self.pressX)/self.baseWidth)
        if dx==0:
            return
        self.setActiveSlice(self.activeSlice()+dx)

    def mousePressEvent(self, event):
        if event.button() != Qt.LeftButton:
            event.ignore()
            QGraphicsItem.mousePressEvent(self, event)
            return
        if self.controller().toolUse:
            self.controller().toolPress(None, event)
            return
        self.scene().views()[0].addToPressList(self)
        self._dragMode = True
        self.pressX = event.scenePos().x()-self.pos().x()

    def customMouseRelease(self, eventPosition):
        """Snaps to grid after mouse released. Updates vhelix data according
        to what movement took place."""
        self._dragMode = False
        
    def moveToLastSlice(self):
        """Moves to the last slice position."""
        self.setActiveSlice(self.part().numBases()-1)
    
    def moveToFirstSlice(self):
        """Moves to the last slice position."""
        self.setActiveSlice(0)
