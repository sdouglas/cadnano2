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
from PyQt4.QtCore import QString, Qt
import ui.styles as styles
from model.virtualhelix import VirtualHelix
from model.enum import Parity, StrandType


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
    outOfSlicePen = QPen(styles.lightorangestroke, styles.SLICE_HELIX_STROKE_WIDTH)
    outOfSliceBrush = QBrush(styles.lightorangefill)
    rect = QRectF(0, 0, 2 * radius, 2 * radius)

    def __init__(self, row, col, position, parent=None):
        """docstring for __init__"""
        super(SliceHelix, self).__init__(parent)
        self._parent = parent
        self._row = row
        self._col = col
        # drawing related
        self.focusRing = None
        self.beingHoveredOver = False
        self.setAcceptsHoverEvents(True)
        self.setPos(position)
        self.undoStack = self._parent.sliceController.mainWindow.undoStack
        self.setFlag(QGraphicsItem.ItemIsSelectable)
        self.setZValue(styles.ZSLICEHELIX)
    
    def part(self):
        return self._parent.part()

    def virtualHelix(self):
        if not self.part():
            return None
        return self.part().getVirtualHelix((self._row, self._col), returnNoneIfAbsent=True)

    class FocusRingPainter(QGraphicsItem):
        """Draws a focus ring around helix in parent"""
        def __init__(self, helix, scene, parent=None):
            super(SliceHelix.FocusRingPainter, self).__init__(parent)
            self._parent = parent
            self.scene = scene
            self.helix = helix
            # returns a new QRect that is bigger all around by 1 pixel
            # but in the same spot as the original
            # good for getting rid of line width artifacts
            self.rect = helix.rect.adjusted(-1,-1,2,2)
            self.setPos(helix.pos())
            self.setZValue(styles.ZFOCUSRING)

        def paint(self, painter, option, widget=None):
            painter.setPen(SliceHelix.hovPen)
            painter.drawEllipse(self.helix.rect)

        def boundingRect(self):
             return self.rect
    # end class

    class AddHelixCommand(QUndoCommand):
        """docstring for AddHelixCommand"""
        def __init__(self, part, coords, shg):
            super(SliceHelix.AddHelixCommand, self).__init__()
            self.part = part
            self.coords = coords
            self.shg = shg
            
        def redo(self):
            vh = self.part.addVirtualHelixAt(self.coords)
            nb = vh.numBases()
            vh.connectStrand(StrandType.Scaffold, nb/2-1, nb/2+1)

        def undo(self):
            self.part.removeVirtualHelix(self.coords)
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
        return self.virtualHelix().number()

    def row(self):
        return self._row

    def col(self):
        return self._col

    def paint(self, painter, option, widget=None):
        vh = self.virtualHelix()
        if vh:
            if vh.hasScafAt(self.part().activeSlice()): 
                painter.setBrush(self.useBrush)
                painter.setPen(self.usePen)
            else:
                painter.setBrush(self.outOfSliceBrush)
                painter.setPen(self.outOfSlicePen)
            painter.drawEllipse(self.rect)
            num = QString(str(self.virtualHelix().number()))
            painter.setPen(Qt.SolidLine)
            painter.setBrush(Qt.NoBrush)
            painter.drawText(0, 0, 2*self.radius, 2*self.radius, Qt.AlignHCenter+Qt.AlignVCenter, num)
        else:  # We are virtualhelix-less
            painter.setBrush(self.defBrush)
            painter.setPen(self.defPen)
            painter.drawEllipse(self.rect)
        if self.beingHoveredOver:
            painter.setPen(self.hovPen)
            painter.setBrush(Qt.NoBrush)
            painter.drawEllipse(self.rect)
    # end def

    def boundingRect(self):
        return self.rect

    def hoverEnterEvent(self, event):
        """hoverEnterEvent changes the SliceHelix brush and pen from default
        to the hover colors if necessary."""
        if self.focusRing == None:
            self.focusRing = SliceHelix.FocusRingPainter(self,\
                                                         self._parent.scene,\
                                                         self._parent)
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
        self.createOrAddBasesToVirtualHelix()
        self.part().setSelection((self.virtualHelix(),))
    # end def

    def createOrAddBasesToVirtualHelix(self):
        coord = (self._row, self._col)
        vh = self.virtualHelix()
        index = self.part().activeSlice()
        if not vh:
            self.undoStack.push(SliceHelix.AddHelixCommand(self.part(), coord, self._parent))
        else:  # Just add more bases
            vh = self.virtualHelix()
            nb = vh.numBases()
            vh.connectBases(StrandType.Staple)
    # end def
    
    def itemChange(self, change, value):
        # for selection changes test against QGraphicsItem.ItemSelectedChange
        # if change == QGraphicsItem.ItemScenePositionHasChanged and self.scene():
        #     # value is the new position.
        #     newPos = value.toPointF()
        #     print "I moooooved", newPos.x(), newPos.y()
        #     # rect = self.scene().sceneRect()
        #     # if not rect.contains(newPos):
        #     #     # Keep the item inside the scene rect.
        #     #     newPos.setX(min(rect.right(), max(newPos.x(), rect.left())))
        #     #     newPos.setY(min(rect.bottom(), max(newPos.y(), rect.top())))
        #     #     return newPos
        #     # # end if
        # # end if
        if change == QGraphicsItem.ItemSelectedChange and self.scene():
            # print "I am slice selected ", self._number
            pass
        return QGraphicsItem.itemChange(self,change, value)
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
