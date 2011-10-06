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

from exceptions import NotImplementedError
from math import floor
from controllers.itemcontrollers.strand.stranditemcontroller import StrandItemController
from endpointitem import EndpointItem
from views import styles
from xoveritem import XoverItem

import util
# import Qt stuff into the module namespace with PySide, PyQt4 independence
util.qtWrapImport('QtCore', globals(), ['pyqtSignal', 'QObject', 'Qt'])
util.qtWrapImport('QtGui', globals(), ['QGraphicsLineItem', 'QGraphicsPathItem',
                                       'QPen', 'QColor', 'QBrush'])

_baseWidth = styles.PATH_BASE_WIDTH

class StrandItem(QGraphicsLineItem):
    def __init__(self, modelStrand, virtualHelixItem):
        """The parent should be a VirtualHelixItem."""
        super(StrandItem, self).__init__(virtualHelixItem)
        self._modelStrand = modelStrand
        self._virtualHelixItem = virtualHelixItem
        self._activeTool = virtualHelixItem.activeTool()
        isDrawn5To3 = modelStrand.strandSet().isDrawn5to3()
        self._lowCap = EndpointItem(self, 'low', isDrawn5To3)
        self._highCap = EndpointItem(self, 'high', isDrawn5To3)
        self._dualCap = EndpointItem(self, 'dual', isDrawn5To3)
        self._controller = StrandItemController(self, modelStrand)
        self._update(modelStrand)
    # end def

    ### SIGNALS ###

    ### SLOTS ###
    def strandResizedSlot(self):
        """docstring for strandResizedSlot"""
        lowMoved = self._lowCap.updatePosIfNecessary(self.idxs()[0])
        highMoved = self._highCap.updatePosIfNecessary(self.idxs()[1])
        if lowMoved:
            self.updateLine(self._lowCap)
        if highMoved:
            self.updateLine(self._highCap)

    def sequenceAddedSlot(self, oligo):
        """docstring for sequenceAddedSlot"""
        pass

    def sequenceClearedSlot(self, oligo):
        """docstring for sequenceClearedSlot"""
        pass
    # end def

    def strandRemovedSlot(self, strand):
        self._modelStrand = None
        scene = self.scene()
        # scene.removeItem(self._highCap)
        # scene.removeItem(self._lowCap)
        self._highCap = None
        self._lowCap = None
        scene.removeItem(self)
        self._controller.disconnectSignals()
        self._controller = None
    # end def

    def strandDestroyedSlot(self, strand):
        pass
    # end def

    def strandXover3pAddedSlot(self, strand3p, strand5p):
        partItem = self._virtualHelixItem.partItem()
        xo = XoverItem(partItem, strand3p, strand5p)
        partItem.addXoverItem(xo)
        self._update(strand3p)
        partItem.updatePreXoverItems()
    # end def

    # def strandXover3pRemovedSlot(self, strand3p, strand5p):
    #     self._update(strand3p)
    # # end def
    
    # def strandXover5pAddedSlot(self, strand5p):
    #     self._update(strand5p)
    # # end def

    def strandUpdateSlot(self, strand):
        """
        Slot for just updating connectivity and color, and endpoint showing
        """
        self._update(strand)
    # end def

    def oligoAppeareanceChangedSlot(self, oligo):
        pass
    # end def

    def oligoSequenceAddedSlot(self, oligo):
        pass
    # end def

    def oligoSequenceClearedSlot(self, oligo):
        pass
    # end def

    def strandHasNewOligoSlot(self, strand):
        pass
    # end def

    def strandDecoratorAddedSlot(self, strand):
        pass
    # end def

    ### ACCESSORS ###
    def activeTool(self):
        return self._activeTool
    # end def

    def idxs(self):
        return self._modelStrand.idxs()
        
    def virtualHelixItem(self):
        return self._virtualHelixItem

    ### PUBLIC METHODS FOR DRAWING / LAYOUT ###
    def updateLine(self, movedCap):
        # setup
        halfBaseWidth = self._virtualHelixItem._baseWidth / 2.0
        line = self.line()
        # set new line coords
        if movedCap == self._lowCap:
            p1 = line.p1()
            p1.setX(self._lowCap.pos().x() + halfBaseWidth)
            line.setP1(p1)
        else:
            p2 = line.p2()
            p2.setX(self._highCap.pos().x() + halfBaseWidth)
            line.setP2(p2)
        self.setLine(line)

    ### PRIVATE SUPPORT METHODS ###
    def _update(self, strand):
        """
        Prepare NormalStrand for drawing:
        1. Show or hide caps depending on L and R connectivity.
        2. Determine line coordinates.
        3. Apply paint styles.
        """
        # 0. Setup
        vhi = self._virtualHelixItem
        bw = vhi._baseWidth
        halfBaseWidth = bw / 2.0
        lowIdx, highIdx = strand.lowIdx(), strand.highIdx()

        lUpperLeftX, lUpperLeftY = vhi.upperLeftCornerOfBase(lowIdx, strand)
        hUpperLeftX, hUpperLeftY = vhi.upperLeftCornerOfBase(highIdx, strand)

        lowCap = self._lowCap
        highCap = self._highCap
        dualCap = self._dualCap

        # 1. Cap visibilty
        if strand.lowConnection() != None:  # hide low cap if Low-connected
            lx = lUpperLeftX
            lowCap.hide()
        else:  # otherwise show left cap
            lx = lUpperLeftX + halfBaseWidth
            lowCap.setPos(lUpperLeftX, lUpperLeftY)
            lowCap.show()
        if strand.highConnection() != None:  # hide high cap if High-connected
            hx = hUpperLeftX + bw
            highCap.hide()
        else:  # otherwise show it
            hx = hUpperLeftX + halfBaseWidth
            highCap.setPos(hUpperLeftX, hUpperLeftY)
            highCap.show()
        # special case: single-base strand with no L or H connections,
        # (unconnected caps were made visible in previous block of code)
        if strand.length() == 1 and \
                  (lowCap.isVisible() and highCap.isVisible()):
            lowCap.hide()  # hide 
            highCap.hide()
            dualCap.setPos(lUpperLeftX, lUpperLeftY)
            dualCap.show()
        else:
            dualCap.hide()
        # 2. Line drawing
        hy = ly = lUpperLeftY + halfBaseWidth
        self.setLine(lx, ly, hx, hy)
        self._updatePensAndBrushes(strand)
    # end def

    def _updatePensAndBrushes(self, strand):
        lowIdx, highIdx = strand.lowIdx(), strand.highIdx()
        if strand.strandSet().isScaffold():
            pen = QPen(styles.scafstroke, styles.PATH_STRAND_STROKE_WIDTH)
            brush = QBrush(styles.handlefill)
        else:
            colr = QColor(self._modelStrand.oligo().color())
            pen = QPen(colr, styles.PATH_STRAND_STROKE_WIDTH)
            brush = QBrush(colr)
        pen.setCapStyle(Qt.FlatCap)
        self.setPen(pen)
        self._lowCap.setBrush(brush)
        self._highCap.setBrush(brush)
        self._dualCap.setBrush(brush)
    # end def

    ### EVENT HANDLERS ###
    def mousePressEvent(self, event):
        """
        Parses a mousePressEvent, calling the approproate tool method as
        necessary.
        """
        # lowIdx = self._modelStrand.lowIdx()
        idx = int(floor((event.pos().x()) / _baseWidth))
        toolMethodName = str(self._activeTool()) + "MousePress"
        if hasattr(self, toolMethodName):  # if the tool method exists
            getattr(self, toolMethodName)(idx)  # call it

    ### TOOL METHODS ###
    def breakToolMousePress(self, idx):
        """
        Set the _moveIdx for future comparison by mouseMoveEvent.
        Set the allowed drag bounds for use by selectToolMouseMove.
        """
        mStrand = self._modelStrand
        mStrand.split(idx)
    # end def



