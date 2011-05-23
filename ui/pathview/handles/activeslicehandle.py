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

    def __init__(self, part, controller=None, parent=None):
        super(ActiveSliceHandle, self).__init__(parent)
        self._activeSlice = 0
        self._part = None
        if part:
            helixCount = part.getVirtualHelixCount()
        else:
            helixCount = 0
        self.height = (helixCount + 2) * (styles.PATH_HELIX_HEIGHT + \
                                          styles.PATH_HELIX_PADDING)
        self.rect = QRectF(0, 0, self.baseWidth, self.height)
        self.setParentItem(parent)
        self.setFlag(QGraphicsItem.ItemIsMovable)
        self.pathController = controller
        self.setAcceptHoverEvents(True)
        self.setZValue(styles.ZACTIVESLICEHANDLE)
        self.setPart(part)
        self._dragMode = False
    
    def part(self):
        return self._part
    
    def setPart(self, newPart):
        if self._part:
            self._part.activeSliceWillChange.disconnect(self._updateActiveSlice)
        self._part = newPart
        self._part.activeSliceWillChange.connect(self._updateActiveSlice)
        self._updateActiveSlice(self._part.activeSlice())

    def activeSlice(self):
        return self._part.activeSlice()
    
    def setActiveSlice(self, baseIndex):
        self._part.setActiveSlice(baseIndex)
    
    def _updateActiveSlice(self, baseIndex):
        """The slot that receives active slice changed notifications from
        the part and changes the receiver to reflect the part"""
        bi = int(baseIndex)
        if bi < 0 or bi >= self._part.dimensions()[2]:
            raise IndexError
        self.setPos(bi*self.baseWidth, -styles.PATH_HELIX_PADDING)
        self._activeSlice = bi
    
    def boundingRect(self):
        """docstring for boundingRect"""
        return self.rect

    def paint(self, painter, option, widget=None):
        painter.setBrush(self.brush)
        painter.setPen(self.pen)
        painter.drawRect(self.rect)

    def resize(self, helixCount):
        """Call after adding or removing a virtualhelix"""
        height = (helixCount + 2) * (styles.PATH_HELIX_HEIGHT + \
                                     styles.PATH_HELIX_PADDING)
        self.rect.setHeight(height)
        self.update(self.rect)

    def resetBounds(self, maxBase):
        """Call after resizing virtualhelix canvas."""
        self.maxBase = maxBase
        self.maxX = (maxBase-1) * self.baseWidth

    def hoverEnterEvent(self,event):
        if self.pathController.toolUse == False:
            self.setCursor(Qt.OpenHandCursor)
        QGraphicsItem.hoverEnterEvent(self,event)
    # end def
    
    def hoverMoveEvent(self,event):
        if self.pathController.toolUse == True:
            # pass None, but if needed pass self for having a special 
            # behavior for the slice helix
            self.pathController.toolHoverMove(None, event,flag=True)
        QGraphicsItem.hoverMoveEvent(self,event)
    # end def
    
    def hoverLeaveEvent(self,event):
        self.setCursor(Qt.ArrowCursor)
        QGraphicsItem.hoverLeaveEvent(self,event)
    # end def

    def mouseMoveEvent(self, event):
        """Snaps handle into place when dragging."""
        if self.pathController.toolUse or not self._dragMode:
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
        if self.pathController.toolUse:
            self.pathController.toolPress(None, event)
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
        self.setActiveSlice(self._part.dimensions()[2]-1)
    
    def moveToFirstSlice(self):
        """Moves to the last slice position."""
        self.setActiveSlice(0)
