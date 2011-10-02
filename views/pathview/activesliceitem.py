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
from controllers.itemcontrollers.activesliceitemcontroller import ActiveSliceItemController
from views import styles
import util

# import Qt stuff into the module namespace with PySide, PyQt4 independence
util.qtWrapImport('QtCore', globals(), ['QPointF', 'QRectF', 'Qt', 'QObject',\
                                        'pyqtSignal', 'pyqtSlot', 'QEvent'])
util.qtWrapImport('QtGui', globals(), ['QBrush', 'QFont', 'QGraphicsItem',\
                                       'QGraphicsSimpleTextItem', 'QPen',\
                                       'QDrag', 'QUndoCommand', 'QGraphicsRectItem'])


class ActiveSliceItem(QGraphicsRectItem):
    """ActiveSliceItem for the Path View"""
    _baseWidth = styles.PATH_BASE_WIDTH
    _brush = QBrush(styles.activeslicehandlefill)
    _labelbrush = QBrush(styles.orangestroke)
    _pen = QPen(styles.activeslicehandlestroke,\
                styles.SLICE_HANDLE_STROKE_WIDTH)
    _font = QFont(styles.thefont, 12, QFont.Bold)

    def __init__(self, partItem, activeBaseIndex):
        super(ActiveSliceItem, self).__init__(partItem)
        self._partItem = partItem
        self._activeSlice = 0
        self._dragMode = False
        self._label = QGraphicsSimpleTextItem("", parent=self)
        self._label.setPos(0, -18)
        self._label.setFont(self._font)
        self._label.setBrush(self._labelbrush)
        self._label.hide()

        self.setFlag(QGraphicsItem.ItemIsMovable)
        # self.setFlag(QGraphicsItem.ItemNegativeZStacksBehindParent)
        # self.setFlag(QGraphicsItem.ItemStacksBehindParent)
        self.setAcceptHoverEvents(True)
        self.setZValue(styles.ZACTIVESLICEHANDLE)
        
        self.setRect(QRectF(0, 0, self._baseWidth,\
                      self._partItem.boundingRect().height()))
        self.setPos(activeBaseIndex*self._baseWidth, 0)
        self.setBrush(self._brush)
        self.setPen(self._pen)
        self._label.show()
        
        self._controller = ActiveSliceItemController(self, partItem.part())
    # end def
    
    ### SLOTS ###
    
    def updateRectSlot(self, part):
        bw = self._baseWidth
        newRect = QRectF(0, 0, bw,\
                    self._partItem.virtualHelixBoundingRect().height())
        if newRect != self.rect():
            self.setRect(newRect)
        self._hideIfEmptySelection()
        # print "updating activesliceitem", self._partItem.virtualHelixBoundingRect().height()
        self.updateIndexSlot(part, part.activeBaseIndex())  
        return newRect
    # end def
    
    def updateIndexSlot(self, part, baseIndex):
        """The slot that receives active slice changed notifications from
        the part and changes the receiver to reflect the part"""
        label = self._label
        bw = self._baseWidth

        bi = util.clamp(int(baseIndex), 0, self.part().maxBaseIdx()-1)
        self.setPos(bi * bw, -styles.PATH_HELIX_PADDING)
        self._activeSlice = bi
        if label:
            label.setText("%d" % bi)
            label.setX((bw - label.boundingRect().width()) / 2)
    # end def
    
    def strandChangedSlot(self, vh):
        pass
    # end def
    
    ### METHODS ###

    def part(self):
        return self._partItem.part()

    def partItem(self):
        return self._partItem
        
    def removed(self):
        self._partItem = None
        self._label = None
        self._controller.disconnectSignals()
        self.controller = None
    # end def

    def activeBaseIndex(self):
        return self.part().activeBaseIndex()

    def setActiveBaseIndex(self, baseIndex):
        self.part().setActiveBaseIndex(baseIndex)
    
    def _hideIfEmptySelection(self):
        self.setVisible(self._partItem.numberOfVirtualHelices() > 0)

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

    # def sceneEvent(self, event):
    #     """Included for unit testing in order to grab events that are sent
    #     via QGraphicsScene.sendEvent()."""
    #     if self._partItem.controller().testRecorder:
    #         self._partItem.controller().testRecorder.ashSceneEvent(event)
    #     if event.type() == QEvent.MouseButtonPress:
    #         self.mousePressEvent(event)
    #         return True
    #     # Uncomment next 3 lines if mouseReleaseEvent is ever implemented
    #     # elif event.type() == QEvent.MouseButtonRelease:
    #     #     self.mouseReleaseEvent(event)
    #     #     return True
    #     elif event.type() == QEvent.MouseMove:
    #         self.mouseMoveEvent(event)
    #         return True
    #     QGraphicsRectItem.sceneEvent(self, event)
    #     return False

    def mouseMoveEvent(self, event):
        """Snaps handle into place when dragging."""
        if not self._dragMode:
            return
        x = self.mapToScene(QPointF(event.pos())).x()
        dx = int((x - self.pressX)/self._baseWidth)
        # Modified to update this view in real time instead of with signalign
        self.updateIndexSlot(None, self._pressBaseIdx+dx)
        self.setActiveBaseIndex(self._pressBaseIdx+dx)

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
                for strand in vh.scaffoldStrandSet():
                    
                    # INSERT code to expand to FILL SPACE
                    indx3p = strand.idx3Prime()
                    indx3p = strand.idx3Prime()
                # end for
                for strand in vh.stapleStrandSet():
                    # INSERT code to expand to FILL SPACE
                    indx3p = strand.idx3Prime()
                    indx3p = strand.idx3Prime()
                # end for
            self.part().undoStack().endMacro()

        # try here because event passed from sceneEvent has no scenePos()
        try:
            self.scene().views()[0].addToPressList(self)
            self._dragMode = True
            self.pressX = self.mapToScene(QPointF(event.pos())).x()
            self._pressBaseIdx = self.activeBaseIndex()
            self._controller.disconnectSignals()
        except AttributeError, e:
            # print e
            pass
    # end def
    
    def customMouseRelease(self, eventPosition):
        """Snaps to grid after mouse released. Updates vhelix data according
        to what movement took place."""
        self._dragMode = False
        self._controller.connectSignals()

    def moveToLastSlice(self):
        """Moves to the last slice position."""
        self.setActiveSlice(self.part().numBases() - 1)

    def moveToFirstSlice(self):
        """Moves to the last slice position."""
        self.setActiveSlice(0)