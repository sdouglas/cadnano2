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
squareslicegraphicsitem.py

Created by Nick Conway on 2010-06-23.
"""

from exceptions import NotImplementedError
from heapq import *
from ui.pathview.handles.activeslicehandle import ActiveSliceHandle
from model.enum import LatticeType, Parity, StrandType
from .slicehelix import SliceHelix
import ui.styles as styles

import util
# import Qt stuff into the module namespace with PySide, PyQt4 independence
util.qtWrapImport('QtCore', globals(), ['QRectF', 'QPointF', 'QEvent', 'Qt', \
                                        'pyqtSignal', 'pyqtSlot', 'QObject'] )
util.qtWrapImport('QtGui', globals(), [ 'QGraphicsItem', 'QBrush', \
                                        'QPainterPath', 'QPen'])

class SquareSliceGraphicsItem(QGraphicsItem):  # was a QGraphicsObject change for Qt 4.6
    """
    SquareSliceGraphicsItem
    """
    radius = styles.SLICE_HELIX_RADIUS
    
    def __init__(self, part, controller=None, parent=None):
        super(SquareSliceGraphicsItem, self).__init__()
        # data related
        self._part = None
        self.sliceController = controller
        self.parent = parent
        self.setParentItem(parent)
        self.setZValue(100)
        # The coords of the upper left corner of the slice being
        # hovered over

        # The deselector grabs mouse events that missed a slice
        # and clears the selection when it gets one
        self.deselector = SquareSliceGraphicsItem.Deselector(self)
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
        # connect destructor
        self._part.partRemoved.connect(self.destroy)
    # end def
    
    def destroy(self):
        self._part.partRemoved.disconnect(self.destroy)
        self.scene().removeItem(self)
        self.setPart(None)
    # end def
    
    def part(self):
        return self._part
    
    def setPart(self, newPart):
        if self._part:
            self._part.dimensionsWillChange.disconnect(self._setDimensions)
            self._part.selectionWillChange.disconnect(self.selectionWillChange)
            self._part.activeSliceWillChange.disconnect(self.activeSliceChanged)
            self._part.virtualHelixAtCoordsChanged.disconnect(self.vhAtCoordsChanged)
        if newPart != None:
            self._setDimensions(newPart.dimensions())
            newPart.dimensionsWillChange.connect(self._setDimensions)
            newPart.selectionWillChange.connect(self.selectionWillChange)
            newPart.activeSliceWillChange.connect(self.activeSliceChanged)
            newPart.virtualHelixAtCoordsChanged.connect(self.vhAtCoordsChanged)
        self._part = newPart
    
    def upperLeftCornerForCoords(self, row, col):
        x = col*2*self.radius
        y = row*2*self.radius
        return (x, y)
 
    def _spawnSliceAt(self, row, column):
        ul = QPointF(*self.upperLeftCornerForCoords(row, column))
        helix = SliceHelix(row, column, self)
        helix.setFlag(QGraphicsItem.ItemStacksBehindParent, True)
        helix.setPos(ul)
        self._helixhash[(row, column)] = helix

    def _killSliceAt(row, column):
        s = self._helixhash[(row, column)]
        s.scene().removeItem(s)
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
                           (newCols)*self.radius*2,\
                           (newRows)*self.radius*2)
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
        pass
    
    def selectionWillChange(self, newSel):
        if self.part().selectAllBehavior:
            return
        for sh in self._helixhash.itervalues():
            sh.setSelected(sh.virtualHelix() in newSel)

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
            
    def vhAtCoordsChanged(self, row, col):
        self._helixhash[(row, col)].update()

    class Deselector(QGraphicsItem):
        """The deselector lives behind all the slices
        and observes mouse press events that miss slices,
        emptying the selection when they do"""
        def __init__(self, parentHGI):
            super(SquareSliceGraphicsItem.Deselector, self).__init__()
            self.parentHGI = parentHGI
        def mousePressEvent(self, event):
            self.parentHGI.part().setSelection(())
            super(SquareSliceGraphicsItem.Deselector, self).mousePressEvent(event)
        def boundingRect(self):
            return self.parentHGI.boundingRect()
        def paint(self, painter, option, widget=None):
            pass

