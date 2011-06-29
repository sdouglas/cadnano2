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
slicehelix.py

Created by Shawn on 2010-06-15.
"""

import ui.styles as styles
from model.virtualhelix import VirtualHelix
from model.enum import Parity, StrandType

import util
# import Qt stuff into the module namespace with PySide, PyQt4 independence
util.qtWrapImport('QtCore', globals(), ['Qt', 'QEvent', 'QString', 'QRectF'])
util.qtWrapImport('QtGui', globals(), ['QGraphicsItem', 'QGraphicsObject',\
                                       'QGraphicsSimpleTextItem',\
                                       'QBrush', 'QPen', 'QDrag',\
                                       'QUndoCommand'])

class SliceHelix(QGraphicsItem):
    """
    The SliceHelix is an individual circle that gets drawn in the SliceView
    as a child of the SliceGraphicsItem. Taken as a group, many SliceHelix
    instances make up the crossection of the DNAPart. Clicking on a SliceHelix
    adds a VirtualHelix to the DNAPart. The SliceHelix then changes appearence
    and paints its corresponding VirtualHelix number.
    """
    # set up default, hover, and active drawing styles
    defBrush = QBrush(styles.grayfill)
    defPen = QPen(styles.graystroke, styles.SLICE_HELIX_STROKE_WIDTH)
    hovBrush = QBrush(styles.bluefill)
    hovPen = QPen(styles.bluestroke, styles.SLICE_HELIX_HILIGHT_WIDTH)
    useBrush = QBrush(styles.orangefill)
    usePen = QPen(styles.orangestroke, styles.SLICE_HELIX_STROKE_WIDTH)
    radius = styles.SLICE_HELIX_RADIUS
    outOfSlicePen = QPen(styles.lightorangestroke,\
                         styles.SLICE_HELIX_STROKE_WIDTH)
    outOfSliceBrush = QBrush(styles.lightorangefill)
    rect = QRectF(0, 0, 2 * radius, 2 * radius)

    def __init__(self, row, col, parent=None):
        """docstring for __init__"""
        super(SliceHelix, self).__init__(parent)
        self._parent = parent
        self._row = row
        self._col = col
        # drawing related
        self.focusRing = None
        self.beingHoveredOver = False
        self.setAcceptsHoverEvents(True)
        self.undoStack = self._parent.sliceController.mainWindow.undoStack
        self.setFlag(QGraphicsItem.ItemIsSelectable)
        self.setZValue(styles.ZSLICEHELIX)

    def part(self):
        return self._parent.part()

    def virtualHelix(self):
        if not self.part():
            return None
        return self.part().getVirtualHelix((self._row, self._col),\
                                            returnNoneIfAbsent=True)

    def number(self):
        return self.virtualHelix().number()

    def row(self):
        return self._row

    def col(self):
        return self._col

    def selected(self):
        return self.focusRing != None

    def setSelected(self, select):
        if select and not self.focusRing:
            self.focusRing = SliceHelix.FocusRingPainter(self.parentItem())
            self.focusRing.setPos(self.pos())
            self.focusRing.setZValue(styles.ZFOCUSRING)
        if not select and self.focusRing:
            self.focusRing.scene().removeItem(self.focusRing)
            self.focusRing = None

    ############################ Painting ############################
    class FocusRingPainter(QGraphicsItem):
        def paint(self, painter, option, widget=None):
            painter.setPen(SliceHelix.hovPen)
            painter.drawEllipse(SliceHelix.rect)

        def boundingRect(self):
            return SliceHelix.rect.adjusted(-1, -1, 2, 2)

    def paint(self, painter, option, widget=None):
        vh = self.virtualHelix()
        if vh:
            if vh.hasBaseAt(StrandType.Scaffold, self.part().activeSlice()):
                painter.setBrush(self.useBrush)
                painter.setPen(self.usePen)
            else:
                painter.setBrush(self.outOfSliceBrush)
                painter.setPen(self.outOfSlicePen)
            painter.drawEllipse(self.rect)
            num = QString(str(self.virtualHelix().number()))
            painter.setPen(Qt.SolidLine)
            painter.setBrush(Qt.NoBrush)
            painter.setFont(styles.SLICE_NUM_FONT)
            painter.drawText(0, 0, 2 * self.radius, 2 * self.radius,\
                             Qt.AlignHCenter + Qt.AlignVCenter, num)
        else:  # We are virtualhelix-less
            pass
            painter.setBrush(self.defBrush)
            painter.setPen(self.defPen)
            painter.drawEllipse(self.rect)
        if self.beingHoveredOver:
            painter.setPen(self.hovPen)
            painter.setBrush(Qt.NoBrush)
            painter.drawEllipse(self.rect)

    def boundingRect(self):
        return self.rect

    ############################ User Interaction ############################
    def mouseDoubleClickEvent(self, event):
        self.createOrAddBasesToVirtualHelix(\
            addBases=True,\
            addToScaffold=event.modifiers() & Qt.ShiftModifier > 0)

    def sceneEvent(self, event):
        """Included for unit testing in order to grab events that are sent
        via QGraphicsScene.sendEvent()."""
        if event.type() == QEvent.MouseButtonPress:
            self.mousePressEvent(event)
            return True
        QGraphicsItem.sceneEvent(self, event)
        return False

    def mousePressEvent(self, event):
        self.createOrAddBasesToVirtualHelix(\
            addBases=True,\
            addToScaffold=not (int(event.modifiers())==Qt.ShiftModifier))
        if event.modifiers() & Qt.ShiftModifier:
            self.virtualHelix().setSelected(True)
        else:
            self.part().setSelection((self.virtualHelix(),))

    def selectAllBehavior(self):
        # If the selection is configured to always select
        # everything, we don't draw a focus ring around everything,
        # instead we only draw a focus ring around the hovered obj.
        if self.part() == None:
            return False
        else:
            return self.part().selectAllBehavior()

    def hoverEnterEvent(self, event):
        # If the selection is configured to always select
        # everything, we don't draw a focus ring around everything,
        # instead we only draw a focus ring around the hovered obj.
        if self.selectAllBehavior():
            self.setSelected(True)

    def hoverLeaveEvent(self, event):
        if self.selectAllBehavior():
            self.setSelected(False)

    def createOrAddBasesToVirtualHelix(self, addBases=False,\
                                             addToScaffold=False):
        coord = (self._row, self._col)
        vh = self.virtualHelix()
        index = self.part().activeSlice()
        undoStack = self.part().undoStack()
        if not vh:
            undoStack.beginMacro("Add helix")
            vh = VirtualHelix(numBases=self.part().crossSectionStep())
            self.part().addVirtualHelixAt(coord, vh)
            vh.basesModified.connect(self.update)
        else:
            undoStack.beginMacro("Connect segment")
        if addBases and addToScaffold:
            vh.connectStrand(StrandType.Scaffold, index - 1, index + 1)
        elif addBases and not addToScaffold:
            vh.connectStrand(StrandType.Staple, index - 1, index + 1)
        self.undoStack().endMacro()
