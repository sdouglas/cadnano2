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


class AshObject(QObject):
    """
    A placeholder class until QGraphicsObject is available to allow signaling
    """
    activeSliceMovedSignal = pyqtSignal(int)
    def __init__(self):
        super(AshObject, self).__init__()
# end class


class ActiveSliceHandle(QGraphicsItem):
    """docstring for ActiveSliceHandle"""
    baseWidth = styles.PATH_BASE_WIDTH
    brush = QBrush(styles.orangefill)
    pen = QPen(styles.orangestroke, styles.SLICE_HANDLE_STROKE_WIDTH)

    def __init__(self, dnaPartInst, startBase, controller=None, parent=None):
        super(ActiveSliceHandle, self).__init__(parent)
        self.dnaPartInst = dnaPartInst
        self.part = dnaPartInst.part()
        helixCount = self.part.getVirtualHelixCount()
        self.height = (helixCount + 2) * (styles.PATH_HELIX_HEIGHT + \
                                          styles.PATH_HELIX_PADDING)
        self.rect = QRectF(0, 0, self.baseWidth, self.height)
        self.baseIndex = startBase
        self.tempIndex = startBase
        
        self.x0 = (startBase * self.baseWidth)
        self.y0 = -1 * (styles.PATH_HELIX_PADDING)
        self.minIndex = 0
        self.maxIndex = self.part.getNumBases()-1
        self.setPos(QPointF(self.x0, self.y0))
        self.setZValue(-10)
        self.pressX = 0
        self.pressXoffset = 0
        self.setParentItem(parent)
        # self.setCursor(Qt.OpenHandCursor)
        self.setFlag(QGraphicsItem.ItemIsMovable)
        self.qObject = AshObject()
        self.activeSliceMovedSignal = self.qObject.activeSliceMovedSignal
        self.activeslicehandle3D = ActiveSliceHandle3D(self) # for Campbell
        
        self.pathController = controller
        self.setAcceptHoverEvents(True)
        
        self.setZValue(styles.ZACTIVESLICEHANDLE)

    def boundingRect(self):
        """docstring for boundingRect"""
        return self.rect

    def paint(self, painter, option, widget=None):
        painter.setBrush(self.brush)
        painter.setPen(self.pen)
        painter.drawRect(self.rect)

    def getPosition(self):
        """Returns the base position"""
        return int(self.x0 / self.baseWidth)

    def setPosition(self, pos):
        """Returns the base position"""
        if pos >= 0 and pos <= self.maxBase:
            xf = pos * self.baseWidth
            self.translate(xf - self.x0, 0)
            self.x0 = xf
        else:
            raise IndexError

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
        if self.pathController.toolUse == False:
            moveX = event.scenePos().x()
            delta = moveX-self.pressX
            self.tempIndex = int((self.baseIndex*self.baseWidth+\
                              self.pressXoffset+delta) / self.baseWidth)
            if self.tempIndex < self.minIndex:
                self.tempIndex = self.minIndex
            elif self.tempIndex > self.maxIndex:
                self.tempIndex = self.maxIndex
            self.x0 = self.tempIndex * self.baseWidth
            self.setPos(self.x0, self.y0)
            # this should be fixed on only notify on changes
            self.activeslicehandle3D.dragFrom2D(self.tempIndex)

    def mousePressEvent(self, event):
        if event.button() != Qt.LeftButton:
            event.ignore()
            QGraphicsItem.mousePressEvent(self, event)
        else:
            if self.pathController.toolUse == False:
                self.scene().views()[0].addToPressList(self)
                self._dragMode = True
                self.pressX = event.scenePos().x()
                self.pressXoffset = self.pressX % self.baseWidth
            else:
                self.pathController.toolPress(None, event)

    def customMouseRelease(self, eventPosition):
        """Snaps to grid after mouse released. Updates vhelix data according
        to what movement took place."""
        if self.tempIndex == self.baseIndex:
            return
        delta = int(self.tempIndex - self.baseIndex)
        self.baseIndex = self.tempIndex
        self.activeSliceMovedSignal.emit(self.baseIndex)
        self._dragMode = False
        
    @pyqtSlot()
    def activeSliceLastSlot(self):
        """Moves to the last slice position. Updates vhelix data according
        to what movement took place."""
        self.tempIndex = self.maxIndex
        self.x0 = self.tempIndex * self.baseWidth
        self.setPos(self.x0, self.y0)
        self.baseIndex = self.tempIndex
        self.activeSliceMovedSignal.emit(self.baseIndex)
    # end def
    
    @pyqtSlot()
    def activeSliceFirstSlot(self):
        """Moves to the first slice position. Updates vhelix data according
        to what movement took place."""
        self.tempIndex = self.minIndex
        self.x0 = self.tempIndex * self.baseWidth
        self.setPos(self.x0, self.y0)
        self.baseIndex = self.tempIndex
        self.activeSliceMovedSignal.emit(self.baseIndex)
    # end def

    def updateFrom3D(self, newIndex):
        """Called by BreakpointHandle3D to notify cadnano that the
        ActiveSliceHandle has moved to a new location. All updates to the data
        structure are then handled by cadnano."""
        # not tested
        if self.baseIndex == newIndex:
            return
        self.baseIndex = newIndex
        self.x0 = self.baseIndex*self.baseWidth
        self.setPos(self.x0, self.y0)
        self.activeSliceMovedSignal.emit(self.baseIndex)
