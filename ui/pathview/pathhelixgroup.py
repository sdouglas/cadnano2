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
pathhelixgroup.py

Created by Shawn on 2011-01-27.
"""

from PyQt4.QtCore import QRectF, QPointF, QEvent, pyqtSlot, QObject, Qt
from PyQt4.QtCore import pyqtSignal
from PyQt4.QtGui import QBrush, QPen, qApp, QGraphicsTextItem, QFont
from PyQt4.QtGui import QGraphicsItem, QGraphicsItemGroup, QUndoCommand
from .pathhelix import PathHelix
from handles.activeslicehandle import ActiveSliceHandle
from handles.breakpointhandle import BreakpointHandle
from handles.pathhelixhandle import PathHelixHandle
from handles.precrossoverhandle import PreXoverHandleGroup
from model.enum import EndType, LatticeType, StrandType
import ui.styles as styles
from handles.pathhelixhandle import PathHelixHandle



class PathHelixGroup(QGraphicsItem):
    """
    PathHelixGroup maintains data and state for a set of object that provide
    an interface to the schematic view of a DNA part. These objects include
    the PathHelix, PathHelixHandles, and ActiveSliceHandle.
    """
    handleRadius = styles.SLICE_HELIX_RADIUS

    def __init__(self, part, activeslicehandle,\
                       controller=None,\
                       parent=None):
        super(PathHelixGroup, self).__init__(parent)
        self.pathHelixList = []  # Primary property
        self._part = part
        self.pathController = controller
        self.activeslicehandle = activeslicehandle
        self.rect = QRectF()
        self.font = QFont("Times", 30, QFont.Bold)
        self.label = QGraphicsTextItem("Part 1")
        self.label.setVisible(True)
        self.label.setFont(self.font)
        self.label.setParentItem(self)
        self.label.setPos(0, 0)
        self.label.setTextInteractionFlags(Qt.TextEditorInteraction)
        self.label.inputMethodEvent = None
    
    def part(self):
        return self._part
    
    def setPart(self, newPart):
        if self.part:
            self.part.helixAdded.disconnect(self.helixAddedSlot)
            self.part.helixWillBeRemoved.disconnect(self.helixRemovedSlot)
        newPart.helixAdded.connect(self.helixAddedSlot)
        newPart.helixWillBeRemoved.connect(self.helixRemovedSlot)
        self.part = newPart
    
    def displayedVHs(self):
        """Returns the list (ordered top to bottom) of VirtualHelix
        that the receiver is displaying"""
        return [ph.vhelix() for ph in self.pathHelixList]
    
    def setDisplayedVHs(self, vhrefs):
        """Spawns or destroys PathHelix such that displayedVHs
        has the same VirtualHelix in the same order as vhrefs
        (though displayedVHs always returns a list of VirtualHelix
        while setDisplayedVHs can take any vhref)"""
        newPathHelixList = []
        vhToPH = dict(((ph.vhelix(), ph) for ph in self.pathHelixList))
        for vhref in vhrefs:
            vh = self.part().getVirtualHelix(vhref)
            ph = vhToPH.get(vh, None)
            if ph == None:
                ph = PathHelix(vh, self.pathController)
            newPathHelixList.append(ph)
        self._setPathHelixList(newPathHelixList)
        
    def _pathHelixList(self):
        return self.pathHelixList
    
    def _setPathHelixList(self, newList):
        """Give me a list of PathHelix and I'll parent them
        to myself if necessary, position them in a column, adopt
        their handles, and position them as well."""
        y = 0  # How far down from the top the next PH should be
        leftmostExtent = 0
        rightmostExtent = 0
        for ph in newList:
            ph.setParentItem(self)
            ph.setPos(0, y)
            h = ph.boundingRect().height()
            y += h
            phh = ph.handle()
            phh.setParentItem(self)
            phhr = phh.boundingRect()
            phh.setPos(-2*phhr.width(), y-h/2-phhr.height()/2)
            leftmostExtent = min(leftmostExtent, -2*phhr.width())
            rightmostExtent = max(rightmostExtent, ph.boundingRect().width())
        self.rect = QRectF(leftmostExtent, 0, -leftmostExtent+rightmostExtent, y)
        self.pathHelixList = newList
        self.vhToPathHelix = dict(((ph.vhelix(), ph) for ph in newList))
        self.scene().views()[0].zoomToFit()

    def paint(self, painter, option, widget=None):
        pass

    def boundingRect(self):
        return self.rect
    
    def moveHelixNumToIdx(self, num, idx):
        """Reinserts helix with number() num such that
        it's at position idx in pathHelixList"""
        vhs = [vh.number() for vh in self.displayedVHs()]
        vhs.remove(num)
        vhs.insert(idx, num)
        self.setDisplayedVHs(vhs)

    @pyqtSlot(int)
    def helixAddedSlot(self, vhref):
        vhs = self.displayedVHs()
        vhs.append(vhref)
        self.setDisplayedVHs(vhs)

    @pyqtSlot(int)
    def helixRemovedSlot(self, vh):
        vhs = self.displayedVHs()
        vhs.remove(vh)
        self.setDisplayedVHs(vh)

    # Slot called when the part's selection changes
    def selectionWillChange(self, newSelection):
        pass

    def getPathHelix(self, vhref):
        """Given the helix number, return a reference to the PathHelix."""
        vh = self.part.getVirtualHelix(vhref)
        for ph in self.pathHelixList:
            if ph.vhelix() == vh:
                return ph
        return None

    def notifyPreCrossoverGroupAfterUpdate(self, virtualhelix):
        """Called by PathHelix.mousePressEvent after the vhelix has calculated
        its new PreXoverHandle positions."""
        self.pchGroup.updateActiveHelix(virtualhelix)

    def reorderHelices(self, first, last, indexDelta):
        """
        Reorder helices by moving helices pathHelixList[first:last]
        by a distance delta in the list. Notify each PathHelix and
        PathHelixHandle of its new location.
        """
        vhs = self.displayedVHs()
        vhsToMove = vhs[first:last]
        del vhs[first:last]
        self.setDisplayedVHs(vhs[0:first+indexDelta]+vhsToMove+vhs[first+indexDelta:-1])

    def bringToFront(self):
        """collidingItems gets a list of all items that overlap. sets
        this items zValue to one higher than the max."""
        zval = 1
        items = self.collidingItems()  # the is a QList
        for item in items:
            temp = item.zValue()
            if temp >= zval:
                zval = item.zValue() + 1
            # end if
        # end for
        self.setZValue(zval)
    # end def
# end class


class SelectionItemGroup(QGraphicsItemGroup):
    """
    SelectionItemGroup
    """
    def __init__(self, boxtype, constraint='y', parent=None):
        super(SelectionItemGroup, self).__init__(parent)
        self.parent = parent
        self.setParentItem(parent)
        self.setFiltersChildEvents(True)
        self.setFlag(QGraphicsItem.ItemIsSelectable)
        self.pen = QPen(styles.bluestroke, styles.PATH_SELECTBOX_STROKE_WIDTH)
        self.drawMe = False
        self.drawn = False
        self.selectionbox = boxtype(self)
        self.dragEnable = False
        self._r0 = 0  # save original mousedown
        self._r = 0  # latest position for moving

        if constraint == 'y':
            self.getR = self.getY
            self.translateR = self.translateY
        else:
            self.getR = self.getX
            self.translateR = self.translateX
    # end def

    def getY(self, pos):
        return pos.y()
    # end def

    def getX(self, pos):
        return pos.x()
    # end def

    def translateY(self, yf):
        self.selectionbox.translate(0, (yf - self._r))
    # end def

    def translateX(self, xf):
        self.selectionbox.translate((xf - self._r), 0)
    # end def

    def paint(self, painter, option, widget=None):
        pass
    # end def

    def bringToFront(self):
        """collidingItems gets a list of all items that overlap. sets
        this items zValue to one higher than the max."""
        zval = 1
        items = self.scene().items(self.boundingRect())  # the is a QList
        for item in items:
            temp = item.zValue()
            if temp >= zval:
                zval = item.zValue() + 1
            # end if
        # end for
        self.setZValue(zval)
    # end def

    def mousePressEvent(self, event):
        if event.button() != Qt.LeftButton:
            QGraphicsItemGroup.mousePressEvent(self, event)
        else:
            self.dragEnable = True
            self.selectionbox.resetTransform()

            # this code block is a HACK to update the boundingbox of the group
            if self.childItems()[0] != None:
                item = self.childItems()[0]
                self.removeFromGroup(item)
                item.restoreParent()
                self.addToGroup(item)

            self.selectionbox.setRect(self.boundingRect())
            self.selectionbox.drawMe = True
            self._r0 = self.getR(event.scenePos())
            self._r = self._r0
            self.scene().views()[0].addToPressList(self)
    # end def

    def mouseMoveEvent(self, event):
        if self.dragEnable == True:
            rf = self.getR(event.scenePos())
            self.translateR(rf)
            self._r = rf
        else:
            QGraphicsItemGroup.mouseMoveEvent(self, event)
    # end def

    def customMouseRelease(self, event):
        """docstring for customMouseRelease"""
        if self.isSelected():
            self.selectionbox.processSelectedItems(self._r0, self._r)
        # end if
        self.selectionbox.drawMe = False
        self.selectionbox.resetTransform()
        self.dragEnable = False
    # end def

    def itemChange(self, change, value):
        """docstring for itemChange"""
        if change == QGraphicsItem.ItemSelectedHasChanged:
            if value == False:
                # self.drawMe = False
                self.selectionbox.drawMe = False
                self.selectionbox.resetTransform()
                self.removeSelectedItems()
                self.parentItem().selectionLock = None
            # end if
            else:
                pass
            self.update(self.boundingRect())
        return QGraphicsItemGroup.itemChange(self, change, value)
    # end def

    def removeSelectedItems(self):
        """docstring for removeSelectedItems"""
        for item in self.childItems():
            if not item.isSelected():
                self.removeFromGroup(item)
                try:
                    item.restoreParent()
                except:
                    pass
                item.setSelected(False)
            # end if
        # end for
    # end def
# end class


class PathHelixHandleSelectionBox(QGraphicsItem):
    """
    docstring for PathHelixHandleSelectionBox
    """
    helixHeight = styles.PATH_HELIX_HEIGHT + styles.PATH_HELIX_PADDING
    radius = styles.PATHHELIXHANDLE_RADIUS
    penWidth = styles.SLICE_HELIX_HILIGHT_WIDTH

    def __init__(self, itemGroup, parent=None):
        super(PathHelixHandleSelectionBox, self).__init__(parent)
        self.itemGroup = itemGroup
        self.rect = itemGroup.boundingRect()
        self.parent = itemGroup.parent
        self.setParentItem(self.parent)
        self.drawMe = False
        self.pen = QPen(styles.bluestroke, self.penWidth)
    # end def

    def paint(self, painter, option, widget=None):
        if self.drawMe == True:
            painter.setPen(self.pen)
            painter.drawRoundedRect(self.rect, self.radius, self.radius)
            painter.drawLine(self.rect.right(),\
                             self.rect.center().y(),\
                             self.rect.right() + self.radius / 2,\
                             self.rect.center().y())
    # end def

    def boundingRect(self):
        return self.rect
    # end def

    def setRect(self, rect):
        self.rect = rect

    def processSelectedItems(self, rStart, rEnd):
        """docstring for processSelectedItems"""
        margin = styles.PATHHELIXHANDLE_RADIUS
        delta = (rEnd - rStart)  # r delta
        midHeight = (self.boundingRect().height()) / 2 - margin
        if abs(delta) < midHeight:  # move is too short for reordering
            return
        if delta > 0:  # moved down, delta is positive
            indexDelta = int((delta - midHeight) / self.helixHeight)
        else:  # moved up, delta is negative
            indexDelta = int((delta + midHeight) / self.helixHeight)
        # sort on y to determine the extremes of the selection group
        items = sorted(self.itemGroup.childItems(), key=lambda phh: phh.y())
        self.parent.reorderHelices(items[0].number(),\
                                   items[-1].number(),\
                                   indexDelta)
    # end def
# end class


class BreakpointHandleSelectionBox(QGraphicsItem):
    def __init__(self, itemGroup, parent=None):
        super(BreakpointHandleSelectionBox, self).__init__(parent)
        self.itemGroup = itemGroup
        self.rect = itemGroup.boundingRect()
        self.parent = itemGroup.parent
        self.setParentItem(self.parent)
        self.drawMe = False
        self.pen = QPen(styles.bluestroke, styles.PATH_SELECTBOX_STROKE_WIDTH)
    # end def

    def paint(self, painter, option, widget=None):
        if self.drawMe == True:
            painter.setPen(self.pen)
            painter.drawRect(self.boundingRect())
    # end def

    def boundingRect(self):
        return self.rect
    # end def

    def setRect(self, rect):
        self.prepareGeometryChange()
        self.rect = rect

    def processSelectedItems(self, rStart, rEnd):
        """docstring for processSelectedItems"""
        pass
# end class
