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
# from PyQt4.QtCore import QPointF, QRectF
# from PyQt4.QtCore import Qt, QObject, pyqtSignal, pyqtSlot
# from PyQt4.QtGui import QBrush, QFont
# from PyQt4.QtGui import QGraphicsItem
# from PyQt4.QtGui import QGraphicsSimpleTextItem
# from PyQt4.QtGui import QPen, QDrag, QUndoCommand
import ui.styles as styles
from util import *
# import Qt stuff into the module namespace with PySide, PyQt4 independence
qtWrapImport('QtCore', globals(), ['QPointF', 'QRectF', 'Qt', 'QtCore' \
                                    'QObject', 'pyqtSignal', 'pyqtSlot'])
qtWrapImport('QtGui', globals(), [ 'QBrush', 'QFont', 'QGraphicsItem' \
                                    'QGraphicsSimpleTextItem', 'QPen',\
                                    'QDrag', 'QUndoCommand'] )


class ActiveSliceHandle(QGraphicsItem):
    """docstring for ActiveSliceHandle"""
    _baseWidth = styles.PATH_BASE_WIDTH
    _brush = QBrush(styles.orangefill)
    _labelbrush = QBrush(styles.orangestroke)
    _pen = QPen(styles.orangestroke, styles.SLICE_HANDLE_STROKE_WIDTH)
    _myfont = QFont("Times", 12, QFont.Bold)

    def __init__(self, pathHelixGroup):
        super(ActiveSliceHandle, self).__init__(pathHelixGroup)
        self._pathHelixGroup = None
        self._activeSlice = 0
        self._dragMode = False
        self._label = QGraphicsSimpleTextItem("", parent=self)
        self._label.setPos(0, -18)
        self._label.setFont(self._myfont)
        self._label.setBrush(self._labelbrush)
        self._label.hide()
        self.setPathHelixGroup(pathHelixGroup)
        self.setFlag(QGraphicsItem.ItemIsMovable)
        self.setFlag(QGraphicsItem.ItemStacksBehindParent)
        self.setAcceptHoverEvents(True)
        self.setZValue(styles.ZACTIVESLICEHANDLE)

    def controller(self):
        return self._pathHelixGroup.controller()

    def part(self):
        return self._pathHelixGroup.part()

    def pathHelixGroup(self):
        return self._pathHelixGroup

    def setPathHelixGroup(self, newPHG):
        if self._pathHelixGroup:
            self._pathHelixGroup.geometryChanged.disconnect(\
                                                   self.prepareGeometryChange)
            self._pathHelixGroup.displayedVHsChanged.disconnect(self._hideIfEmptySelection)
        if self._pathHelixGroup and self._pathHelixGroup.part():
            self._pathHelixGroup.part().activeSliceWillChange.disconnect(\
                                                      self._updateActiveSlice)
        self._pathHelixGroup = newPHG
        newPHG.geometryChanged.connect(self.prepareGeometryChange)
        newPHG.part().activeSliceWillChange.connect(self._updateActiveSlice)
        newPHG.displayedVHsChanged.connect(self._hideIfEmptySelection)
        self._hideIfEmptySelection()
        self._updateActiveSlice(newPHG.part().activeSlice())

    def activeSlice(self):
        return self.part().activeSlice()

    def setActiveSlice(self, baseIndex):
        self.part().setActiveSlice(baseIndex)
    
    def _hideIfEmptySelection(self):
        self.setVisible(len(self.pathHelixGroup().displayedVHs())>0)
    
    def _updateActiveSlice(self, baseIndex):
        """The slot that receives active slice changed notifications from
        the part and changes the receiver to reflect the part"""
        bi = clamp(int(baseIndex), 0, self.part().numBases()-1)
        self.setPos(bi * self._baseWidth, -styles.PATH_HELIX_PADDING)
        self._activeSlice = bi
        if self._label:
            self._label.setText("%d" % bi)
            self._label.setX((self._baseWidth -\
                              self._label.boundingRect().width()) / 2)

    def boundingRect(self):
        return QRectF(0, 0, self._baseWidth,\
                      self.pathHelixGroup().boundingRect().height())

    def paint(self, painter, option, widget=None):
        if self.boundingRect().height() > 0:
            painter.setBrush(self._brush)
            painter.setPen(self._pen)
            painter.drawRect(self.boundingRect())
            self._label.show()
        else:
            self._label.hide()

    def resetBounds(self, maxBase):
        """Call after resizing virtualhelix canvas."""
        self.maxBase = maxBase
        self.maxX = (maxBase - 1) * self._baseWidth

    def hoverEnterEvent(self, event):
        self.setCursor(Qt.OpenHandCursor)
        QGraphicsItem.hoverEnterEvent(self, event)
    # end def

    # def hoverMoveEvent(self, event):
    #     if not self.controller().isSelectToolActive():
    #         # pass None, but if needed pass self for having a special
    #         # behavior for the slice helix
    #         self.controller().toolHoverMove(None, event, flag=True)
    #     QGraphicsItem.hoverMoveEvent(self, event)
    # end def

    def hoverLeaveEvent(self, event):
        self.setCursor(Qt.ArrowCursor)
        QGraphicsItem.hoverLeaveEvent(self, event)
    # end def

    def mouseMoveEvent(self, event):
        """Snaps handle into place when dragging."""
        if not self._dragMode:
            return
        x = event.scenePos().x()
        dx = int((x - self.pressX)/self._baseWidth)
        self.setActiveSlice(self.pressBaseIdx+dx)

    def mousePressEvent(self, event):
        if event.button() != Qt.LeftButton:
            event.ignore()
            QGraphicsItem.mousePressEvent(self, event)
            return
        self.scene().views()[0].addToPressList(self)
        self._dragMode = True
        self.pressX = event.scenePos().x()
        self.pressBaseIdx = self.activeSlice()

    def customMouseRelease(self, eventPosition):
        """Snaps to grid after mouse released. Updates vhelix data according
        to what movement took place."""
        self._dragMode = False

    def moveToLastSlice(self):
        """Moves to the last slice position."""
        self.setActiveSlice(self.part().numBases() - 1)

    def moveToFirstSlice(self):
        """Moves to the last slice position."""
        self.setActiveSlice(0)
