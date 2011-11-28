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
from math import floor

from controllers.itemcontrollers.activesliceitemcontroller import ActiveSliceItemController
from views import styles
import util

# import Qt stuff into the module namespace with PySide, PyQt4 independence
util.qtWrapImport('QtCore', globals(), ['QPointF', 'QRectF', 'Qt', 'QObject',\
                                        'pyqtSignal', 'pyqtSlot', 'QEvent'])
util.qtWrapImport('QtGui', globals(), ['QBrush', 'QFont', 'QGraphicsItem',\
                                       'QGraphicsSimpleTextItem', 'QPen',\
                                       'QDrag', 'QUndoCommand', 'QGraphicsRectItem'])


_baseWidth = styles.PATH_BASE_WIDTH
_brush = QBrush(styles.activeslicehandlefill)
_labelbrush = QBrush(styles.orangestroke)
_pen = QPen(styles.activeslicehandlestroke,\
            styles.SLICE_HANDLE_STROKE_WIDTH)
_font = QFont(styles.thefont, 12, QFont.Bold)


class ActiveSliceItem(QGraphicsRectItem):
    """ActiveSliceItem for the Path View"""

    def __init__(self, partItem, activeBaseIndex):
        super(ActiveSliceItem, self).__init__(partItem)
        self._partItem = partItem
        self._activeTool = partItem.activeTool()
        self._activeSlice = 0
        self._lowDragBound = 0
        self._highDragBound = self.part().maxBaseIdx()
        self._controller = ActiveSliceItemController(self, partItem.part())

        self._label = QGraphicsSimpleTextItem("", parent=self)
        self._label.setPos(0, -18)
        self._label.setFont(_font)
        self._label.setBrush(_labelbrush)
        self._label.hide()

        self.setFlag(QGraphicsItem.ItemIsMovable)
        self.setAcceptHoverEvents(True)
        self.setZValue(styles.ZACTIVESLICEHANDLE)
        self.setRect(QRectF(0, 0, _baseWidth,\
                      self._partItem.boundingRect().height()))
        self.setPos(activeBaseIndex*_baseWidth, 0)
        self.setBrush(_brush)
        self.setPen(_pen)

        # reuse select tool methods for other tools
        self.addSeqToolMousePress = self.selectToolMousePress
        self.addSeqToolMouseMove = self.selectToolMouseMove
        self.breakToolMousePress = self.selectToolMousePress
        self.breakToolMouseMove = self.selectToolMouseMove
        self.insertionToolMousePress = self.selectToolMousePress
        self.insertionToolMouseMove = self.selectToolMouseMove
        self.paintToolMousePress = self.selectToolMousePress
        self.paintToolMouseMove = self.selectToolMouseMove
        self.pencilToolMousePress = self.selectToolMousePress
        self.pencilToolMouseMove = self.selectToolMouseMove
        self.skipToolMousePress = self.selectToolMousePress
        self.skipToolMouseMove = self.selectToolMouseMove
    # end def

    ### SLOTS ###
    def strandChangedSlot(self, vh):
        pass
    # end def

    def updateRectSlot(self, part):
        bw = _baseWidth
        newRect = QRectF(0, 0, bw,\
                    self._partItem.virtualHelixBoundingRect().height())
        if newRect != self.rect():
            self.setRect(newRect)
        self._hideIfEmptySelection()
        self.updateIndexSlot(part, part.activeBaseIndex())
        return newRect
    # end def

    def updateIndexSlot(self, part, baseIndex):
        """The slot that receives active slice changed notifications from
        the part and changes the receiver to reflect the part"""
        label = self._label
        bw = _baseWidth
        bi = util.clamp(int(baseIndex), 0, self.part().maxBaseIdx())
        self.setPos(bi * bw, -styles.PATH_HELIX_PADDING)
        self._activeSlice = bi
        if label:
            label.setText("%d" % bi)
            label.setX((bw - label.boundingRect().width()) / 2)
    # end def

    ### ACCESSORS ###
    def activeBaseIndex(self):
        return self.part().activeBaseIndex()
    # end def

    def part(self):
        return self._partItem.part()
    # end def

    def partItem(self):
        return self._partItem
    # end def

    ### PUBLIC METHODS FOR DRAWING / LAYOUT ###
    def removed(self):
        scene = self.scene()
        scene.removeItem(self._label)
        scene.removeItem(self)
        self._partItem = None
        self._label = None
        self._controller.disconnectSignals()
        self.controller = None
    # end def

    def resetBounds(self):
        """Call after resizing virtualhelix canvas."""
        self._highDragBound = self.part().maxBaseIdx()
    # end def

    ### PRIVATE SUPPORT METHODS ###
    def _hideIfEmptySelection(self):
        vis = self.part().numberOfVirtualHelices() > 0
        self.setVisible(vis)
        self._label.setVisible(vis)
    # end def

    def _setActiveBaseIndex(self, baseIndex):
        self.part().setActiveBaseIndex(baseIndex)
    # end def

    ### EVENT HANDLERS ###
    def hoverEnterEvent(self, event):
        self.setCursor(Qt.OpenHandCursor)
        QGraphicsItem.hoverEnterEvent(self, event)
    # end def

    def hoverLeaveEvent(self, event):
        self.setCursor(Qt.ArrowCursor)
        QGraphicsItem.hoverLeaveEvent(self, event)
    # end def

    def mousePressEvent(self, event):
        """
        Parses a mousePressEvent, calling the approproate tool method as
        necessary. Stores _moveIdx for future comparison.
        """
        if event.button() != Qt.LeftButton:
            event.ignore()
            QGraphicsItem.mousePressEvent(self, event)
            return
        self.scene().views()[0].addToPressList(self)
        self._moveIdx = int(floor((self.x()+event.pos().x()) / _baseWidth))
        toolMethodName = str(self._activeTool()) + "MousePress"
        if hasattr(self, toolMethodName):  # if the tool method exists
            modifiers = event.modifiers()
            getattr(self, toolMethodName)(modifiers)  # call tool method

    def mouseMoveEvent(self, event):
        """
        Parses a mouseMoveEvent, calling the approproate tool method as
        necessary. Updates _moveIdx if it changed.
        """
        toolMethodName = str(self._activeTool()) + "MouseMove"
        if hasattr(self, toolMethodName):  # if the tool method exists
            idx = int(floor((self.x()+event.pos().x()) / _baseWidth))
            if idx != self._moveIdx:  # did we actually move?
                modifiers = event.modifiers()
                self._moveIdx = idx
                getattr(self, toolMethodName)(modifiers, idx)  # call tool method

    def mouseReleaseEvent(self, event):
        """
        Parses a mouseReleaseEvent, calling the approproate tool method as
        necessary. Deletes _moveIdx if necessary.
        """
        toolMethodName = str(self._activeTool()) + "MouseRelease"
        if hasattr(self, toolMethodName):  # if the tool method exists
            modifiers = event.modifiers()
            x = event.pos().x()
            getattr(self, toolMethodName)(modifiers, x)  # call tool method
        if hasattr(self, '_moveIdx'):
            del self._moveIdx

    ### TOOL METHODS ###
    def selectToolMousePress(self, modifiers):
        """
        Set the allowed drag bounds for use by selectToolMouseMove.
        """
        if (modifiers & Qt.AltModifier) and (modifiers & Qt.ShiftModifier):
            self.part().undoStack().beginMacro("Auto-drag Scaffold(s)")
            for vh in self.part().getVirtualHelices():
                # SCAFFOLD
                # resize 3' first
                for strand in vh.scaffoldStrandSet():
                    idx5p = strand.idx5Prime()
                    idx3p = strand.idx3Prime()
                    if not strand.hasXoverAt(idx3p):
                        lo, hi = strand.getResizeBounds(idx3p)
                        if strand.isDrawn5to3():
                            strand.resize((idx5p, hi))
                        else:
                            strand.resize((lo, idx5p))
                # resize 5' second
                for strand in vh.scaffoldStrandSet():
                    idx5p = strand.idx5Prime()
                    idx3p = strand.idx3Prime()
                    if not strand.hasXoverAt(idx5p):
                        lo, hi = strand.getResizeBounds(idx5p)
                        if strand.isDrawn5to3():
                            strand.resize((lo, idx3p))
                        else:
                            strand.resize((idx3p, hi))
                # STAPLE
                # resize 3' first
                for strand in vh.stapleStrandSet():
                    idx5p = strand.idx5Prime()
                    idx3p = strand.idx3Prime()
                    if not strand.hasXoverAt(idx3p):
                        lo, hi = strand.getResizeBounds(idx3p)
                        if strand.isDrawn5to3():
                            strand.resize((idx5p, hi))
                        else:
                            strand.resize((lo, idx5p))
                # resize 5' second
                for strand in vh.stapleStrandSet():
                    idx5p = strand.idx5Prime()
                    idx3p = strand.idx3Prime()
                    if not strand.hasXoverAt(idx3p):
                        lo, hi = strand.getResizeBounds(idx5p)
                        if strand.isDrawn5to3():
                            strand.resize((lo, idx3p))
                        else:
                            strand.resize((idx3p, hi))

            self.part().undoStack().endMacro()
    # end def

    def selectToolMouseMove(self, modifiers, idx):
        """
        Given a new index (pre-validated as different from the prev index),
        calculate the new x coordinate for self, move there, and notify the
        parent strandItem to redraw its horizontal line.
        """
        idx = util.clamp(idx, self._lowDragBound, self._highDragBound)
        x = int(idx * _baseWidth)
        self.setPos(x, self.y())
        self.updateIndexSlot(None, idx)
        self._setActiveBaseIndex(idx)
    # end def
