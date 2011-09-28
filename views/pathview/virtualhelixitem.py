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
import util
# import Qt stuff into the module namespace with PySide, PyQt4 independence
util.qtWrapImport('QtCore', globals(), ['pyqtSignal', 'QObject', 'Qt'])
util.qtWrapImport('QtGui', globals(), ['QBrush', 'QGraphicsItem',\
                                       'QGraphicsPathItem','QPen',\
                                       'QPainterPath'])

class VirtualHelixItem(QGraphicsPathItem):
    baseWidth = styles.PATH_BASE_WIDTH
    minorGridPen = QPen(styles.minorgridstroke, styles.MINOR_GRID_STROKE_WIDTH)
    majorGridPen = QPen(styles.majorgridstroke, styles.MAJOR_GRID_STROKE_WIDTH)
    minorGridPen.setCosmetic(True)
    majorGridPen.setCosmetic(True)

    def __init__(self, parent, modelVirtualHelix):
        super(VirtualHelixItem, self).__init__(parent)
        self._partItem = parent
        self._modelPart = parent.modelPart()
        self._modelVirtualHelix = modelVirtualHelix
        self.setAcceptHoverEvents(True)  # for pathtools
        self.setFlag(QGraphicsItem.ItemUsesExtendedStyleOption)
        self.setCacheMode(QGraphicsItem.DeviceCoordinateCache)
        self._minorGridPainterPath = None
        self._majorGridPainterPath = None

    ### SIGNALS ###

    ### SLOTS ###
    def strandAddedSlot(self, strand):
        """docstring for sequenceAddedSlot"""
        pass

    def decoratorAddedSlot(self, decorator):
        """docstring for sequenceClearedSlot"""
        pass

    ### DRAWING METHODS ###
    def paint(self, painter, option, widget=None):
        painter.setBrush(Qt.NoBrush)
        painter.setPen(self.minorGridPen)
        painter.drawPath(self.minorGridPainterPath())  # Minor grid lines
        painter.setPen(self.majorGridPen)
        painter.drawPath(self.majorGridPainterPath())  # Major grid lines

    def minorGridPainterPath(self):
        """
        Returns a QPainterPath object for the minor grid lines.
        The path also includes a border outline and a midline for
        dividing scaffold and staple bases.
        """
        if self._minorGridPainterPath:
            return self._minorGridPainterPath
        path = QPainterPath()
        canvasSize = self._modelPart.maxBaseIdx()
        # border
        path.addRect(0, 0, self.baseWidth * canvasSize, 2 * self.baseWidth)
        # minor tick marks
        for i in range(canvasSize):
            if (i % self._modelPart.subStepSize() != 0):
                x = round(self.baseWidth * i) + .5
                path.moveTo(x, 0)
                path.lineTo(x, 2 * self.baseWidth)
        # staple-scaffold divider
        path.moveTo(0, self.baseWidth)
        path.lineTo(self.baseWidth * canvasSize, self.baseWidth)
        self._minorGridPainterPath = path
        return path

    def majorGridPainterPath(self):
        """
        Returns a QPainterPath object for the major grid lines.
        This is separated from the minor grid lines so different
        pens can be used for each.
        """
        if self._majorGridPainterPath:
            return self._majorGridPainterPath
        path = QPainterPath()
        canvasSize = self._modelPart.maxBaseIdx()
        # major tick marks
        for i in range(0, canvasSize + 1, self._modelPart.subStepSize()):
            x = round(self.baseWidth * i) + .5
            path.moveTo(x, .5)
            path.lineTo(x, 2 * self.baseWidth - .5)
        self._majorGridPainterPath = path
        return path

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
