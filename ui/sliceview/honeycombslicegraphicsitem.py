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
slicehelixgroup.py

Created by Shawn Douglas on 2010-06-15.
"""

from exceptions import NotImplementedError
from heapq import *
from PyQt4.QtCore import QRectF, QPointF, QEvent, pyqtSignal, QObject, Qt
from PyQt4.QtCore import pyqtSignal, pyqtSlot
from PyQt4.QtGui import QBrush, QPainterPath, QPen
from PyQt4.QtGui import QGraphicsItem
from ui.pathview.handles.activeslicehandle import ActiveSliceHandle
from model.enum import LatticeType, Parity, StrandType
from .slicehelix import SliceHelix
import ui.styles as styles

root3 = 1.732051

class HoneycombSliceGraphicsItem(QGraphicsItem):  # was a QGraphicsObject change for Qt 4.6
    """
    SliceHelixGroup maintains data and state for a set of SliceHelix objects
    (the circles in the slice view) and serves as the root of their
    drawing tree.
    
    -reserveLabelForHelix and -recycleLabelForHelix maintain a pool
    of labels (these are the nonnegative integers that appear on them)
    for slices.
    """
    radius = styles.SLICE_HELIX_RADIUS
    sliceHelixRect = QRectF(0, 0, 2*radius, 2*radius)
    
    def __init__(self, part, controller=None, parent=None):
        super(HoneycombSliceGraphicsItem, self).__init__()
        # data related
        self._part = None
        self.sliceController = controller
        self.parent = parent
        self.setParentItem(parent)
        self.setZValue(100)
        # The coords of the upper left corner of the slice being
        # hovered over
        self._hoverCoords = None

        # The deselector grabs mouse events that missed a slice
        # and clears the selection when it gets one
        self.deselector = HoneycombSliceGraphicsItem.Deselector(self)
        self.deselector.setParentItem(self)
        self.deselector.setFlag(QGraphicsItem.ItemStacksBehindParent)
        self.deselector.setZValue(-1)
        
        # Invariant: keys in _helixhash = range(_nrows) x range(_ncols)
        # where x is the cartesian product
        self._helixhash = {}
        self._nrows, self._ncols = 0, 0
        self._rect = QRectF(0, 0, 0, 0)
        self.setPart(part)
        
        # drawing related
        self.handleSize = 15
                
        # Cache of VHs that were active as of last call to
        # activeSliceChanged. If None, all slices will be redrawn
        # and the cache will be filled.
        self._previouslyActiveVHs = None
        
        # Cache of PainterPath that draws the hilight rings around
        # the current selection
        self._selectionPath = None
    # end def
    
    def part(self):
        return self._part
    
    def setPart(self, newPart):
        if self._part:
            self._part.dimensionsWillChange.disconnect(self._setDimensions)
            self._part.activeSliceWillChange.disconnect(self.activeSliceWillChange)
        self._setDimensions(newPart.dimensions())
        newPart.dimensionsWillChange.connect(self._setDimensions)
        newPart.selectionWillChange.connect(self.selectionWillChange)
        newPart.activeSliceWillChange.connect(self.activeSliceChanged)
        self._part = newPart
    
    def upperLeftCornerForCoords(self, row, col):
        x = col*self.radius*root3
        if ((row % 2) ^ (col % 2)): # odd parity
            y = row*self.radius*3 + self.radius
        else:                          # even parity
            y = row*self.radius*3
        return (x, y)
 
    def _spawnSliceAt(self, row, column):
        ul = QPointF(*self.upperLeftCornerForCoords(row, column))
        helix = SliceHelix(row, column, self)
        helix.setFlag(QGraphicsItem.ItemStacksBehindParent, True)
        helix.setPos(ul)
        self._helixhash[(row, column)] = helix
    
    def hoverCoords(self):
        return self._hoverCoords
    
    def setHoverCoords(self, newCoords):
        self._selectionPath = None
        self._hoverCoords = newCoords
        self.update()
        
    def _killSliceAt(row, column):
        self._helixhash[(row, column)].setParentItem(None)
        del self._helixhash[(row, column)]

    def _setDimensions(self, newDims):
        """A private method used to change the number of rows,
        cols in response to a change in the dimensions of the
        part represented by the receiver"""
        newRows, newCols, ignore = newDims
        if self._nrows > newRows:
            for r in range(newRows, self._nrows):
                for c in range(self._ncols):
                    self._killSliceAt(r, c)
        elif newRows > self._nrows:
            for r in range(self._nrows, newRows):
                for c in range(self._ncols):
                    self._spawnSliceAt(r, c)
        self._nrows = newRows
        # We now have the right number of rows
        if self._ncols > newCols:
            for c in range(newCol, self._ncols):
                for r in range(self._nrows):
                    self._killSliceAt(r, c)
        elif newCols > self._ncols:
            for c in range(self._ncols, newCols):
                for r in range(self._nrows):
                    self._spawnSliceAt(r, c)
        self._ncols = newCols
        self._rect = QRectF(0, 0,\
                           (newCols)*self.radius*root3,\
                           (newRows)*self.radius*3)
        self.prepareGeometryChange()
        # the Deselector copies our rect so it changes too
        self.deselector.prepareGeometryChange()
        self.zoomToFit()

    def boundingRect(self):
        return self._rect

    def zoomToFit(self):
        # Auto zoom to center the scene
        thescene = self.scene()
        theview = thescene.views()[0]
        theview.zoomToFit()
    # end def

    def paint(self, painter, option, widget=None):
        painter.save()
        painter.setPen(QPen(styles.bluestroke, styles.SLICE_HELIX_HILIGHT_WIDTH))
        painter.drawPath(self.selectionPainterPath())
        painter.restore()
    
    def selectionPainterPath(self):
        if self._selectionPath:
            return self._selectionPath
        p = QPainterPath()
        if self.part().selectAllBehavior:
            # If the slice automatically selects everything, it makes
            # little sense to draw focus rings around all the helices.
            # Instead, we only draw focus rings around the helix being
            # hovered over.
            if self.hoverCoords():
                ul = self.upperLeftCornerForCoords(*self.hoverCoords())
                rect = self.sliceHelixRect.translated(*ul)
                p.addEllipse(rect)
        else:
            # If the slice has a selection, it makes sense to highlight
            # that selection.
            for vh in self.part().selection():
                ul = self.upperLeftCornerForCoords(*vh.coord())
                rect = self.sliceHelixRect.translated(*ul)
                p.addEllipse(rect)
        self._selectionPath = p
        return p
    
    def selectionWillChange(self):
        self._selectionPath = None
        self.update()

    def activeSliceChanged(self, newActiveSliceZIndex):
        newlyActiveVHs = set()
        part = self.part()
        activeSlice = part.activeSlice()
        if self._previouslyActiveVHs:
            for vh in part.getVirtualHelices():
                isActiveNow = vh.hasBaseAt(StrandType.Scaffold, activeSlice)
                if isActiveNow != (vh in self._previouslyActiveVHs):
                    self._helixhash[vh.coords()].update()
                if isActiveNow:
                    newlyActiveVHs.add(vh)
        else:
            for vh in part.getVirtualHelices():
                isActiveNow = vh.hasBaseAt(StrandType.Scaffold, activeSlice)
                if isActiveNow:
                    newlyActiveVHs.add(vh)
            self.update()

    def bringToFront(self):
        """collidingItems gets a list of all items that overlap. sets
        this items zValue to one higher than the max."""
        zval = 1
        items = self.collidingItems() # the is a QList
        for item in items:
            temp = item.zValue()
            if temp >= zval:
                zval = item.zValue() + 1
            # end if
        # end for
        self.setZValue(zval)
    # end def
    
    class Deselector(QGraphicsItem):
        """The deselector lives behind all the slices
        and observes mouse press events that miss slices,
        emptying the selection when they do"""
        def __init__(self, parentHGI):
            super(HoneycombSliceGraphicsItem.Deselector, self).__init__()
            self.parentHGI = parentHGI
        def mousePressEvent(self, event):
            self.parentHGI.part().setSelection(())
            super(HoneycombSliceGraphicsItem.Deselector, self).mousePressEvent(event)
        def boundingRect(self):
            return self.parentHGI.boundingRect()
        def paint(self, painter, option, widget=None):
            pass
    
    class SelectionPainter(QGraphicsItem):
        """The SelectionPainter lives above the children and
        paints their focus rings."""
        def __init__(parent):
            super(HoneycombSliceGraphicsItem.SelectionPainter, self).__init__()
        def boundingRect(self):
            pass
        
