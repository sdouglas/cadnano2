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

from PyQt4.QtCore import QRectF
from PyQt4.QtGui import QBrush
from PyQt4.QtGui import QGraphicsItem
from PyQt4.QtGui import QGraphicsSimpleTextItem
from PyQt4.QtGui import QPen, QDrag, QUndoCommand
import styles
from model.virtualhelix import VirtualHelix


class SliceHelix(QGraphicsItem):
    """docstring for SliceHelix"""
    # set up default, hover, and active drawing styles
    defBrush = QBrush(styles.grayfill)
    defPen = QPen(styles.graystroke, styles.SLICE_HELIX_STROKE_WIDTH)
    hovBrush = QBrush(styles.bluefill)
    hovPen = QPen(styles.bluestroke, styles.SLICE_HELIX_HILIGHT_WIDTH)
    useBrush = QBrush(styles.orangefill)
    usePen = QPen(styles.orangestroke, styles.SLICE_HELIX_STROKE_WIDTH)
    radius = styles.SLICE_HELIX_RADIUS
    rect = QRectF(0, 0, 2 * radius, 2 * radius)

    def __init__(self, row, col, position, parent=None):
        """docstring for __init__"""
        super(SliceHelix, self).__init__(parent)
        self.parent = parent
        # data related
        self.part = parent.dnaPartInst.part()
        self._number = -1
        self._row = row
        self._col = col
        self.parity = (row % 2) ^ (col % 2)
        self.p0neighbor = None
        self.p1neighbor = None
        self.p2neighbor = None
        self.label = None
        # drawing related
        self.focusRing = None
        self.beingHoveredOver = False
        self.setAcceptsHoverEvents(True)
        self.setPos(position)
        self.undoStack = self.parent.sliceController.mainWindow.undoStack

    class FocusRingPainter(QGraphicsItem):
        """Draws a focus ring around helix in parent"""
        def __init__(self, helix, scene, parent=None):
            super(SliceHelix.FocusRingPainter, self).__init__(parent)
            self.parent = parent
            self.scene = scene
            self.helix = helix
            self.setPos(helix.pos())

        def paint(self, painter, option, widget=None):
            painter.setPen(SliceHelix.hovPen)
            painter.drawEllipse(self.helix.rect)
            bringToFront(self)

        def boundingRect(self):
            return self.helix.rect
    # end class

    class RenumberCommand(QUndoCommand):
        """docstring for RenumberCommand"""
        def __init__(self, slicehelix, fromNum):
            super(SliceHelix.RenumberCommand, self).__init__()
            self.slicehelix = slicehelix
            self.fromNum = fromNum

        def redo(self):
            self.toNum = self.slicehelix.parent.reserveLabelForHelix(self.slicehelix)
            self.slicehelix.setNumber(self.toNum)
            self.slicehelix.update(self.slicehelix.rect)

        def undo(self):
            self.slicehelix.setNumber(self.fromNum) # will recycle
            self.slicehelix.update(self.slicehelix.rect)
    # end class

    class AddHelixCommand(QUndoCommand):
        """docstring for AddHelixCommand"""
        def __init__(self, slicehelix, number):
            super(SliceHelix.AddHelixCommand, self).__init__()
            self.slicehelix = slicehelix
            self._number = number

        def redo(self):
            self.slicehelix.part.addVirtualHelix(self.slicehelix)
            self.slicehelix.parent.addHelixToPathGroup(self._number)

        def undo(self):
            self.slicehelix.part.removeVirtualHelix(self._number)
            self.slicehelix.parent.removeHelixFromPathGroup(self._number)
    # end class

    class AddBasesToHelixCommand(QUndoCommand):
        """docstring for AddBasesToHelixCommand"""
        def __init__(self, slicehelix, number, index):
            super(SliceHelix.AddBasesToHelixCommand, self).__init__()
            self.slicehelix = slicehelix
            self._number = number
            self._index = index

        def redo(self):
            self.slicehelix.parent.addBasesToDnaPart(self._number, self._index)

        def undo(self):
            self.slicehelix.parent.removeBasesFromDnaPart(self._number, self._index)
    # end class

    class DeleteHelixCommand(QUndoCommand):
        """docstring for DeleteHelixCommand"""
        def __init__(self, slicehelix, position, number):
            super(SliceHelix.DeleteHelixCommand, self).__init__()
            self.slicehelix = slicehelix
            self._pos = position
            self._num = number

        def redo(self):
            pass
            
        def undo(self):
            pass
    # end class

    def number(self):
        """docstring for number"""
        return self._number

    def row(self):
        """returns SliceHelix row"""
        return self._row

    def col(self):
        """returns SliceHelix column"""
        return self._col

    def paint(self, painter, option, widget=None):
        if self._number >= 0:
            painter.setBrush(self.useBrush)
            painter.setPen(self.usePen)
        else:
            painter.setBrush(self.defBrush)
            painter.setPen(self.defPen)
        if self.beingHoveredOver:
            painter.setPen(self.hovPen)
        painter.drawEllipse(self.rect)
    # end def

    def boundingRect(self):
        return self.rect

    def hoverEnterEvent(self, event):
        """hoverEnterEvent changes the SliceHelix brush and pen from default
        to the hover colors if necessary."""
        if self.focusRing == None:
            self.focusRing = SliceHelix.FocusRingPainter(self,\
                                                         self.parent.scene,\
                                                         self.parent)
        self.update(self.rect)
    # end def

    def hoverLeaveEvent(self, event):
        """hoverEnterEvent changes the SliceHelix brush and pen from hover
        to the default colors if necessary."""
        if self.focusRing != None:
            self.focusRing.setParentItem(None)
            self.focusRing = None
        self.update(self.rect)
    # end def

    def mousePressEvent(self, event):
        self.setUsed(not self._number >= 0)
        QDrag(self.parent.parentWidget())
    # end def

    def dragEnterEvent(self, e):
        self.setUsed(not self._number >= 0)
        e.acceptProposedAction()
    # end def

    def setNumber(self, n):
        """
        If n!=slice.number the caller should have already reserved n with
        the parent SliceHelixGroup (from self.parent.reserveLabelForHelix).
        The callee tells the SliceHelixGroup to recycle the old value.
        """
        if n != self._number and self._number >= 0:
            self.parent.recycleLabelForHelix(self._number, self)
        if n < 0:
            if self.label:
                self.label.setParentItem(None)
                self.label = None
            self._number = -1
            return
        self._number = n
        if self.label == None:
            self.label = QGraphicsSimpleTextItem("%d" % self._number)
            self.label.setParentItem(self)
        y_val = self.radius / 2
        if self._number < 10:
            self.label.setPos(self.radius/1.3, y_val)
        elif self._number < 100:
            self.label.setPos(self.radius/2, y_val)
        else:
            self.label.setPos(self.radius/4, y_val)
        bringToFront(self)
    # end def

    def setUsed(self, u):
        """
        Handles user click on SliceHelix in two possible ways:

        1. If the SliceHelix has never been used, reserve a new label
        from the parent SliceHelixGroup, create a new VirtualHelix vhelix,
        and notify the PathHelixGroup that it should create a new
        PathHelix that points to vhelix.

        2. If the SliceHelix has been used previously, try to add some
        scaffold at the currently selected position in the path view.
        """
        if (self._number >= 0) == u:
            # self.parent.addBasesToDnaPart(self._number)
            pass
        if self._number < 0:  # Initiate
            self.undoStack.beginMacro("Add new SliceHelix")
            self.undoStack.push(SliceHelix.RenumberCommand(self, self._number))
            self.undoStack.push(SliceHelix.AddHelixCommand(self, self._number))
            index = self.parent.activeslicehandle.getPosition()
            self.undoStack.push(SliceHelix.AddBasesToHelixCommand(self, self._number, index))
            self.undoStack.endMacro()
        else:  # Just add more bases
            index = self.parent.activeslicehandle.getPosition()
            self.undoStack.beginMacro("Add scaf at %d[%d]" % (self._number, index))
            self.undoStack.push(SliceHelix.AddBasesToHelixCommand(self, self._number, index))
            self.undoStack.endMacro()
    # end def
# end class

def bringToFront(self):
    """collidingItems gets a list of all items that overlap. sets
    this items zValue to one higher than the max."""
    zval = 1
    items = self.scene().items(self.boundingRect()) # the is a QList
    for item in items:
        temp = item.zValue()
        if temp >= zval:
            zval = item.zValue() + 1
        # end if
    # end for
    self.setZValue(zval)
