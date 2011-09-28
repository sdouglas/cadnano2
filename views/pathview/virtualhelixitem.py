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
                                       'QGraphicsPathItem','QPen',])

class VirtualHelixItem(QGraphicsPathItem):
    baseWidth = styles.PATH_BASE_WIDTH
    minorGridPen = QPen(styles.minorgridstroke, styles.MINOR_GRID_STROKE_WIDTH)
    majorGridPen = QPen(styles.majorgridstroke, styles.MAJOR_GRID_STROKE_WIDTH)
    minorGridPen.setCosmetic(True)
    majorGridPen.setCosmetic(True)
    nobrush = QBrush(Qt.NoBrush)

    def __init__(self, parent, modelVirtualHelix):
        super(VirtualHelixItem, self).__init__(parent)
        self._partItem = parent
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

    ### DRAWING ##
    def paint(self, painter, option, widget=None):
        # Note that the methods that fetch the paths
        # cache the paths and that those caches are
        # invalidated as the primary mechanism
        # of updating after a change in vhelix's bases
        if option != None and \
           not self.boundingRect().intersects(option.exposedRect):
            return
        painter.save()
        painter.setBrush(self.nobrush)
        painter.setPen(self.minorGridPen)
        painter.drawPath(self.minorGridPainterPath())  # Minor grid lines
        painter.setPen(self.majorGridPen)
        painter.drawPath(self.majorGridPainterPath())  # Major grid lines
        painter.setBrush(Qt.NoBrush)
        segmentPaths, endptPths = self.segmentAndEndptPaths()
        for sp in segmentPaths:
            pen, path = sp
            strandRect = path.controlPointRect().adjusted(0, 0, 5, 5)
            if option != None and not strandRect.intersects(option.exposedRect):
                continue
            painter.setPen(pen)
            painter.drawPath(path)
        painter.setPen(Qt.NoPen)
        for ep in endptPths:
            brush, path = ep
            if option != None and\
               not path.controlPointRect().intersects(option.exposedRect):
                continue
            painter.setBrush(brush)
            painter.drawPath(path)
        self.paintHorizontalBaseText(painter)
        painter.restore()
    #end def

    def minorGridPainterPath(self):
        """
        Returns a QPainterPath object for the minor grid lines.
        The path also includes a border outline and a midline for
        dividing scaffold and staple bases.
        """
        if self._minorGridPainterPath:
            return self._minorGridPainterPath
        path = QPainterPath()
        canvasSize = self._vhelix.part().numBases()
        # border
        path.addRect(0, 0, self.baseWidth * canvasSize, 2 * self.baseWidth)
        # minor tick marks
        for i in range(canvasSize):
            if (i % self._vhelix.part().majorGrid() != 0):
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
        canvasSize = self._vhelix.part().numBases()
        # major tick marks  FIX: 7 is honeycomb-specific
        for i in range(0, canvasSize + 1, self._vhelix.part().majorGrid()):
            x = round(self.baseWidth * i) + .5
            path.moveTo(x, .5)
            path.lineTo(x, 2 * self.baseWidth - .5)
        self._majorGridPainterPath = path
        return path
    