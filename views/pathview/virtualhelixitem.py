#!/usr/bin/env python
# encoding: utf-8

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

from math import floor
from views import styles
from virtualhelixhandleitem import VirtualHelixHandleItem
from controllers.itemcontrollers.virtualhelixitemcontroller import VirtualHelixItemController
from .strand.stranditem import StrandItem

from model.enum import StrandType

import util
# import Qt stuff into the module namespace with PySide, PyQt4 independence
util.qtWrapImport('QtCore', globals(), ['pyqtSignal', 'QObject', 'Qt', 'QRectF'])
util.qtWrapImport('QtGui', globals(), ['QBrush', 'QGraphicsItem',\
                                       'QGraphicsPathItem','QPen',\
                                       'QPainterPath'])

_baseWidth = styles.PATH_BASE_WIDTH


class VirtualHelixItem(QGraphicsPathItem):
    """VirtualHelixItem for PathView"""
    minorGridPen = QPen(styles.minorgridstroke, styles.MINOR_GRID_STROKE_WIDTH)
    majorGridPen = QPen(styles.majorgridstroke, styles.MAJOR_GRID_STROKE_WIDTH)
    minorGridPen.setCosmetic(True)
    majorGridPen.setCosmetic(True)

    def __init__(self, partItem, modelVirtualHelix, activeTool):
        super(VirtualHelixItem, self).__init__(partItem)
        self._partItem = partItem
        self._modelVirtualHelix = modelVirtualHelix
        self._activeTool = activeTool
        self.setAcceptHoverEvents(True)  # for pathtools
        self.setFlag(QGraphicsItem.ItemUsesExtendedStyleOption)
        self.setCacheMode(QGraphicsItem.DeviceCoordinateCache)
        self.setBrush(QBrush(Qt.NoBrush))
        self.setPen(self.minorGridPen)
        self._minorGridPainterPath = None
        self._majorGridPainterPath = None
        self._minorGridPainterPath = self.minorGridPainterPath()
        self._majorGridPainterPath = self.majorGridPainterPath()
        self.setPath(self._minorGridPainterPath)
        self._handle = VirtualHelixHandleItem(modelVirtualHelix, partItem)
        
        self._controller = VirtualHelixItemController(self, modelVirtualHelix)
        self.setAcceptHoverEvents(True)
    # end def

    ### SIGNALS ###

    ### SLOTS ###
    def strandAddedSlot(self, strand):
        """
        Instantiates a StrandItem upon notification that the model has a
        new Strand.  The StrandItem is responsible for creating its own
        controller for communication with the model, and for adding itself to
        its parent (which is *this* VirtualHelixItem, i.e. 'self').
        """
        StrandItem(strand, self)
    # end def

    def decoratorAddedSlot(self, decorator):
        """
        Instantiates a DecoratorItem upon notification that the model has a
        new Decorator.  The Decorator is responsible for creating its own
        controller for communication with the model, and for adding itself to
        its parent (which is *this* VirtualHelixItem, i.e. 'self').
        """
        pass

    def virtualHelixNumberChangedSlot(self, virtualHelix):
        pass
    # end def

    def virtualHelixRemovedSlot(self, virtualHelix):
        scene = self.scene()
        scene.removeItem(self._handle)
        scene.removeItem(self)
        self._partItem.removeVirtualHelixItem(self)
        self._partItem = None
        self._modelVirtualHelix = None
        self._activeTool = None
        self._minorGridPainterPath = None
        self._majorGridPainterPath = None
        self._handle = None
        self._controller.disconnectSignals()
        self._controller = None
    # end def

    ### ACCESSORS ###
    def activeTool(self):
        return self._activeTool

    def coord(self):
        return self._modelVirtualHelix.coord()
    # end def

    def handle(self):
        return self._handle
    # end def

    def part(self):
        return self._partItem.part()
    # end def

    def partItem(self):
        return self._partItem
    # end def

    def number(self):
        return self._modelVirtualHelix.number()
    # end def

    def virtualHelix(self):
        return self._modelVirtualHelix
    # end def

    def window(self):
        return self._partItem.window()
    # end def

    ### DRAWING METHODS ###
    def isStrandOnTop(self, strand):
        sS = strand.strandSet()
        isEvenParity = self._modelVirtualHelix.isEvenParity()
        return isEvenParity and sS.isScaffold() or\
               not isEvenParity and sS.isStaple()
    # end def

    def isStrandTypeOnTop(self, strandType):
        isEvenParity = self._modelVirtualHelix.isEvenParity()
        return isEvenParity and strandType == StrandType.Scaffold or \
               not isEvenParity and strandType == StrandType.Staple
    # end def

    def upperLeftCornerOfBase(self, idx, strand):
        x = idx * _baseWidth
        y = 0 if self.isStrandOnTop(strand) else _baseWidth
        return x, y
    # end def

    def upperLeftCornerOfBaseType(self, idx, strandType):
        x = idx * _baseWidth
        y = 0 if self.isStrandTypeOnTop(strandType) else _baseWidth
        return x, y
    # end def

    def minorGridPainterPath(self):
        """
        Returns a QPainterPath object for the minor grid lines.
        The path also includes a border outline and a midline for
        dividing scaffold and staple bases.
        """
        bw = _baseWidth
        part = self.part()

        if self._minorGridPainterPath:
            return self._minorGridPainterPath
        path = QPainterPath()
        canvasSize = part.maxBaseIdx()+1
        # border
        path.addRect(0, 0, bw * canvasSize, 2 * bw)
        # minor tick marks
        for i in range(canvasSize):
            x = round(bw * i) + .5
            path.moveTo(x, 0)
            path.lineTo(x, 2 * bw)
        # staple-scaffold divider
        path.moveTo(0, bw)
        path.lineTo(bw * canvasSize, bw)
        self._minorGridPainterPath = path
        return path

    def majorGridPainterPath(self):
        """
        Returns a QPainterPath object for the major grid lines.
        This is separated from the minor grid lines so different
        pens can be used for each.
        """
        bw = _baseWidth
        part = self.part()
        
        if self._majorGridPainterPath:
            return self._majorGridPainterPath
        path = QPainterPath()
        canvasSize = part.maxBaseIdx()
        # major tick marks
        for i in range(0, canvasSize + 1, part.subStepSize()):
            x = round(bw * i) + .5
            path.moveTo(x, .5)
            path.lineTo(x, 2 * bw - .5)
        self._majorGridPainterPath = path
        return path
    # end def

    def resize(self):
        """Called by part on resize."""
        print "resize", self
        self._minorGridPainterPath = None
        self._minorGridPainterPath = self.minorGridPainterPath()
        self.setPath(self._minorGridPainterPath)
    # end def

    ### EVENT HANDLERS ###
    def mousePressEvent(self, event):
        """
        Parses a mousePressEvent to extract strandSet and base index,
        forwarding them to approproate tool method as necessary.
        """
        self.scene().views()[0].addToPressList(self)
        self.part().setActiveVirtualHelix(self.virtualHelix())
        toolMethodName = str(self._activeTool()) + "MousePress"
        if hasattr(self, toolMethodName):
            strandSet, idx = self.baseAtPoint(event.pos())
            self._lastStrandSet, self._lastIdx = strandSet, idx
            getattr(self, toolMethodName)(strandSet, idx)
    # end def

    def mouseMoveEvent(self, event):
        """
        Parses a mouseMoveEvent to extract strandSet and base index,
        forwarding them to approproate tool method as necessary.
        """
        toolMethodName = str(self._activeTool()) + "MouseMove"
        if hasattr(self, toolMethodName):
            strandSet, idx = self.baseAtPoint(event.pos())
            if self._lastStrandSet != strandSet or self._lastIdx != idx:
                self._lastStrandSet, self._lastIdx = strandSet, idx
                getattr(self, toolMethodName)(strandSet, idx)
    # end def

    def customMouseRelease(self, event):
        """
        Parses a mouseReleaseEvent to extract strandSet and base index,
        forwarding them to approproate tool method as necessary.
        """
        toolMethodName = str(self._activeTool()) + "MouseRelease"
        if hasattr(self, toolMethodName):
            getattr(self, toolMethodName)(self._lastStrandSet, self._lastIdx)
    # end def

    ### COORDINATE UTILITIES ###
    def baseAtPoint(self, pos):
        """
        Returns the (strandType, index) under the location x,y or None.

        It shouldn't be possible to click outside a pathhelix and still call
        this function. However, this sometimes happens if you click exactly
        on the top or bottom edge, resulting in a negative y value.
        """
        x, y = pos.x(), pos.y()
        mVH = self._modelVirtualHelix
        baseIdx = int(floor(x / _baseWidth))
        minBase, maxBase = 0, mVH.part().maxBaseIdx()
        if baseIdx < minBase or baseIdx >= maxBase:
            baseIdx = util.clamp(baseIdx, minBase, maxBase)
        if y < 0:
            y = 0  # HACK: zero out y due to erroneous click
        strandIdx = floor(y * 1. / _baseWidth)
        if strandIdx < 0 or strandIdx > 1:
            strandIdx = int(util.clamp(strandIdx, 0, 1))
        strandSet = mVH.getStrandSetByIdx(strandIdx)
        return (strandSet, baseIdx)
    # end def

    def keyPanDeltaX(self):
        """How far a single press of the left or right arrow key should move
        the scene (in scene space)"""
        dx = self._partItem.part().stepSize() * _baseWidth
        return self.mapToScene(QRectF(0, 0, dx, 1)).boundingRect().width()
    # end def

    def hoverMoveEvent(self, event):
        """
        Parses a mouseMoveEvent to extract strandSet and base index,
        forwarding them to approproate tool method as necessary.
        """
        activeTool = self._activeTool()
        toolMethodName = str(activeTool) + "HoverMove"
        if hasattr(self, toolMethodName):
            strandType, idxX, idxY = activeTool.baseAtPoint(self, event.pos())
            getattr(self, toolMethodName)(strandType, idxX, idxY)
    # end def

    ### TOOL METHODS ###
    def selectToolMousePress(self, strandSet, idx):
        """strand.getDragBounds"""
        print "%s: %s[%s]" % (util.methodName(), strandSet, idx)
        pass
    # end def

    def selectToolMouseMove(self, strandSet, idx):
        """move endpoint to new location"""
        print "%s: %s[%s]" % (util.methodName(), strandSet, idx)
        pass
    # end def

    def selectToolMouseRelease(self, strandSet, idx):
        """if startIdx != end, vhelix.createNewStrand(startIdx, endIdx)"""
        print "%s: %s[%s]" % (util.methodName(), strandSet, idx)
        pass
    # end def

    def pencilToolMousePress(self, strandSet, idx):
        """strand.getDragBounds"""
        print "%s: %s[%s]" % (util.methodName(), strandSet, idx)
        activeTool = self._activeTool()
        if not activeTool.isDrawingStrand():
            activeTool.initStrandItemFromVHI(self, strandSet, idx)
            activeTool.setIsDrawingStrand(True)
    # end def

    def pencilToolMouseMove(self, strandSet, idx):
        """strand.getDragBounds"""
        print "%s: %s[%s]" % (util.methodName(), strandSet, idx)
        activeTool = self._activeTool()
        if activeTool.isDrawingStrand():
            activeTool.updateStrandItemFromVHI(self, strandSet, idx)
    # end def

    def pencilToolMouseRelease(self, strandSet, idx):
        """strand.getDragBounds"""
        print "%s: %s[%s]" % (util.methodName(), strandSet, idx)
        activeTool = self._activeTool()
        if activeTool.isDrawingStrand():
            activeTool.setIsDrawingStrand(False)
            activeTool.attemptToCreateStrand(self, strandSet, idx)
    # end def

    def pencilToolHoverMove(self, strandType, idxX, idxY):
        """Pencil the strand is possible."""
        partItem = self.partItem()
        activeTool = self._activeTool()
        if not activeTool.isFloatingXoverBegin():
            tempXover = activeTool.floatingXover()
            tempXover.updateFloatingFromVHI(self, strandType, idxX, idxY)
    # end def
