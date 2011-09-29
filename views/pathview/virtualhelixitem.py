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

from views import styles
from itemhandle import VirtualHelixItemHandle
import util
# import Qt stuff into the module namespace with PySide, PyQt4 independence
util.qtWrapImport('QtCore', globals(), ['pyqtSignal', 'QObject', 'Qt'])
util.qtWrapImport('QtGui', globals(), ['QBrush', 'QGraphicsItem',\
                                       'QGraphicsPathItem','QPen',\
                                       'QPainterPath'])

class VirtualHelixItem(QGraphicsPathItem):
    _baseWidth = styles.PATH_BASE_WIDTH
    minorGridPen = QPen(styles.minorgridstroke, styles.MINOR_GRID_STROKE_WIDTH)
    majorGridPen = QPen(styles.majorgridstroke, styles.MAJOR_GRID_STROKE_WIDTH)
    minorGridPen.setCosmetic(True)
    majorGridPen.setCosmetic(True)

    def __init__(self, partItem, modelVirtualHelix):
        super(VirtualHelixItem, self).__init__(partItem)
        self._partItem = partItem
        self._modelVirtualHelix = modelVirtualHelix
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
        self._handle = VirtualHelixItemHandle(modelVirtualHelix, partItem)
    # end def
    ### SIGNALS ###

    ### SLOTS ###
    def strandAddedSlot(self, strand):
        """docstring for sequenceAddedSlot"""
        pass

    def decoratorAddedSlot(self, decorator):
        """docstring for sequenceClearedSlot"""
        pass

    # ### DRAWING METHODS ###
    # def paint(self, painter, option, widget=None):
    #     painter.setBrush(Qt.NoBrush)
    #     painter.setPen(self.minorGridPen)
    #     painter.drawPath(self.minorGridPainterPath())  # Minor grid lines
    #     painter.setPen(self.majorGridPen)
    #     painter.drawPath(self.majorGridPainterPath())  # Major grid lines

    def minorGridPainterPath(self):
        """
        Returns a QPainterPath object for the minor grid lines.
        The path also includes a border outline and a midline for
        dividing scaffold and staple bases.
        """
        bw = self._baseWidth
        part = self.part()
        
        if self._minorGridPainterPath:
            return self._minorGridPainterPath
        path = QPainterPath()
        canvasSize = part.maxBaseIdx()
        # border
        path.addRect(0, 0, bw * canvasSize, 2 * bw)
        # minor tick marks
        for i in range(canvasSize):
            if (i % part.subStepSize() != 0):
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
        bw = self._baseWidth
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
    
    def handle(self):
        return self._handle
    # end def
    
    def number(self):
        return self._modelVirtualHelix.number()
    # end def
    
    def part(self):
        return self._partItem.modelPart()
    # end def

    ### TOOL METHODS ###
    def selectToolMousePress(self, event):
        """virtualhelix.getVStrandAndDragBounds(pos), store startIdx"""
        pass
    # end def

    def selectToolMouseMove(self, event):
        """draw pseudoStrandGraphicsItem from startIdx to endIdx"""
        pass
    # end def

    def selectToolMouseRelease(self, event):
        """if startIdx != end, vhelix.createNewStrand(startIdx, endIdx)"""
        pass
    # end def

    ### COORDINATE UTILITIES ###
    def baseAtPoint(self, pt):
        """Returns the (strandType, baseIdx) corresponding
        to pt in virtualhelix."""
