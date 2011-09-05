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
from model.strands.normalstrand import NormalStrand
from controllers.selecttooloperation import SelectToolOperation
from views import styles
import util

# import Qt stuff into the module namespace with PySide, PyQt4 independence
util.qtWrapImport('QtCore', globals(), ['QPointF', 'QRectF', 'Qt', 'QObject',\
                                        'pyqtSignal', 'pyqtSlot', 'QEvent'])
util.qtWrapImport('QtGui', globals(), ['QBrush', 'QFont', 'QGraphicsItem',\
                                       'QGraphicsSimpleTextItem', 'QPen',\
                                       'QDrag', 'QUndoCommand', 'QGraphicsRectItem'])


class ActiveSliceHandle(QGraphicsRectItem):
    """docstring for ActiveSliceHandle"""
    _baseWidth = styles.PATH_BASE_WIDTH
    _brush = QBrush(styles.activeslicehandlefill)
    _labelbrush = QBrush(styles.orangestroke)
    _pen = QPen(styles.activeslicehandlestroke,\
                styles.SLICE_HANDLE_STROKE_WIDTH)
    _myfont = QFont(styles.thefont, 12, QFont.Bold)

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
        # self.setFlag(QGraphicsItem.ItemNegativeZStacksBehindParent)
        # self.setFlag(QGraphicsItem.ItemStacksBehindParent)
        self.setAcceptHoverEvents(True)
        self.setZValue(styles.ZACTIVESLICEHANDLE)
        
        self.setRect(QRectF(0, 0, self._baseWidth,\
                      self.pathHelixGroup().boundingRect().height()))
        self.setBrush(self._brush)
        self.setPen(self._pen)
        self._label.show()

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
            newPHG.geometryChanged.disconnect(self.updateRect)
            self._pathHelixGroup.displayedVHsChanged.disconnect(self._hideIfEmptySelection)
        # uncomment if you want to resignal position changes
        # if self._pathHelixGroup and self._pathHelixGroup.part():
        #     self._pathHelixGroup.part().activeSliceWillChange.disconnect(\
        #                                                self._updateActiveSlice)
        # uncomment if you want to resignal position changes
        self._pathHelixGroup = newPHG
        newPHG.geometryChanged.connect(self.prepareGeometryChange)
        newPHG.geometryChanged.connect(self.updateRect)
        #
        # newPHG.part().activeSliceWillChange.connect(self._updateActiveSlice)
        newPHG.displayedVHsChanged.connect(self._hideIfEmptySelection)
        self._hideIfEmptySelection()
        self._updateActiveSlice(newPHG.part().activeSlice())

    def activeSlice(self):
        return self.part().activeSlice()

    def setActiveSlice(self, baseIndex):
        self.part().setActiveSlice(baseIndex)
    
    def _hideIfEmptySelection(self):
        self.setVisible(len(self.pathHelixGroup().displayedVHs()) > 0)
    
    def _updateActiveSlice(self, baseIndex):
        """The slot that receives active slice changed notifications from
        the part and changes the receiver to reflect the part"""
        bi = util.clamp(int(baseIndex), 0, self.part().numBases()-1)
        self.setPos(bi * self._baseWidth, -styles.PATH_HELIX_PADDING)
        self._activeSlice = bi
        if self._label:
            self._label.setText("%d" % bi)
            self._label.setX((self._baseWidth -\
                              self._label.boundingRect().width()) / 2)
    # end def
    
    def updateRect(self):
        newRect = QRectF(0, 0, self._baseWidth,\
                    self.pathHelixGroup().boundingRect().height())
        if newRect != self.rect():
            self.setRect(newRect)
        return newRect

    # def boundingRect(self):
    #     newRect = QRectF(0, 0, self._baseWidth,\
    #                   self.pathHelixGroup().boundingRect().height())
    #     if newRect != self.rect():
    #         self.setRect(newRect)
    #     return newRect

    # def paint(self, painter, option, widget=None):
    #     if self.boundingRect().height() > 0:
    #         painter.setBrush(self._brush)
    #         painter.setPen(self._pen)
    #         painter.drawRect(self.boundingRect())
    #         self._label.show()
    #     else:
    #         self._label.hide()

    def resetBounds(self, maxBase):
        """Call after resizing virtualhelix canvas."""
        self.maxBase = maxBase
        self.maxX = (maxBase - 1) * self._baseWidth

    def hoverEnterEvent(self, event):
        self.setCursor(Qt.OpenHandCursor)
        QGraphicsItem.hoverEnterEvent(self, event)
    # end def

    def hoverLeaveEvent(self, event):
        self.setCursor(Qt.ArrowCursor)
        QGraphicsItem.hoverLeaveEvent(self, event)
    # end def

    def sceneEvent(self, event):
        """Included for unit testing in order to grab events that are sent
        via QGraphicsScene.sendEvent()."""
        if self._pathHelixGroup.controller().testRecorder:
            self._pathHelixGroup.controller().testRecorder.ashSceneEvent(event)
        if event.type() == QEvent.MouseButtonPress:
            self.mousePressEvent(event)
            return True
        # Uncomment next 3 lines if mouseReleaseEvent is ever implemented
        # elif event.type() == QEvent.MouseButtonRelease:
        #     self.mouseReleaseEvent(event)
        #     return True
        elif event.type() == QEvent.MouseMove:
            self.mouseMoveEvent(event)
            return True
        QGraphicsRectItem.sceneEvent(self, event)
        return False

    def mouseMoveEvent(self, event):
        """Snaps handle into place when dragging."""
        if not self._dragMode:
            return
        x = self.mapToScene(QPointF(event.pos())).x()
        dx = int((x - self.pressX)/self._baseWidth)
        # Modified to update this view in real time instead of with signalign
        self._updateActiveSlice(self.pressBaseIdx+dx)
        self.setActiveSlice(self.pressBaseIdx+dx)

    def mousePressEvent(self, event):
        if event.button() != Qt.LeftButton:
            event.ignore()
            QGraphicsItem.mousePressEvent(self, event)
            return

        altClick = event.modifiers() & Qt.AltModifier
        shiftClick = event.modifiers() & Qt.ShiftModifier
        if altClick and shiftClick:
            self.part().undoStack().beginMacro("Auto-drag Scaffold(s)")
            for vh in self.part().getVirtualHelices():
                for vStr in vh.scaf():
                    if not isinstance(vStr, NormalStrand):
                        continue
                    end3 = vStr.vBase3
                    sto = SelectToolOperation(end3, None, self.part().undoStack())
                    sto.actionExpandStrandToFillAvailableSpace(end3)
                    sto.end()
                for vStr in vh.scaf():
                    if not isinstance(vStr, NormalStrand):
                        continue
                    end3 = vStr.vBase5
                    sto = SelectToolOperation(end3, None, self.part().undoStack())
                    sto.actionExpandStrandToFillAvailableSpace(end3)
                    sto.end()
            self.part().undoStack().endMacro()

        # try here because event passed from sceneEvent has no scenePos()
        try:
            self.scene().views()[0].addToPressList(self)
            self._dragMode = True
            self.pressX = self.mapToScene(QPointF(event.pos())).x()
            self.pressBaseIdx = self.activeSlice()
        except AttributeError, e:
            # print e
            pass

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
