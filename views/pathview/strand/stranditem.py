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
from controllers.itemcontrollers.strand.stranditemcontroller import StrandItemController
from endpointitem import EndPointItem

import util
# import Qt stuff into the module namespace with PySide, PyQt4 independence
util.qtWrapImport('QtCore', globals(), ['pyqtSignal', 'QObject'])
util.qtWrapImport('QtGui', globals(), ['QGraphicsLineItem', 'QGraphicsPathItem'])

class StrandItem(QGraphicsLineItem):
    def __init__(self, modelStrand, virtualHelixItem):
        """The parent should be a VirtualHelixItem."""
        super(StrandItem, self).__init__(virtualHelixItem)
        self._modelStrand = modelStrand
        self._virtualHelixItem = virtualHelixItem
        isDrawn5To3 = modelStrand.drawn5To3()
        lowCap = EndPointItem(self, 'low', isDrawn5To3)
        lowCap.setPen(NoPen)
        highCap = EndPointItem(self, 'high', isDrawn5To3)
        highCap.setPen(NoPen)
        dualCap = EndPointItem(self, 'dual', isDrawn5To3)
        dualCap.setPen(NoPen)
        
        self._lowCap = lowCap
        self._highCap = highCap
        self._dualCap = dualCap
        self._controller = StrandItemController(self, modelStrand)

        self.update(modelStrand)
    # end def

    ### SIGNALS ###

    ### SLOTS ###
    def strandResizedSlot(self):
        """docstring for strandResizedSlot"""
        pass

    def sequenceAddedSlot(self, oligo):
        """docstring for sequenceAddedSlot"""
        pass

    def sequenceClearedSlot(self, oligo):
        """docstring for sequenceClearedSlot"""
        pass

    ### METHODS ###


    def update(self, strand):
        """
        Prepare NormalStrand for drawing:
        1. Show or hide caps depending on L and R connectivity.
        2. Determine line coordinates.
        3. Apply paint styles.
        """
        # 0. Setup
        vhi = self._virtualHelixItem
        halfBaseWidth = vhi.baseWidth / 2.0
        lowIdx, highIdx = strand.lowIdx(), strand.highIdx()
        
        lUpperLeftX, lUpperLeftY = vhi.upperLeftCornerOfBase(lowIdx)
        hUpperLeftX, hUpperLeftY = vhi.upperLeftCornerOfBase(highIdx)
        
        lowCap = self._lowCap
        highCap = self._highCap
        dualCap = self._dualCap
        
        # 1. Cap visibilty
        if strand.apparentlyConnectedL():  # hide left cap if L-connected
            lx = lUpperLeftX
            leftCap.hide()
        else:  # otherwise show left cap
            lx = lUpperLeftX + halfBaseWidth
            leftCap.setPos(lUpperLeftX, lUpperLeftY)
            leftCap.show()
        if strand.apparentlyConnectedR():  # hide right cap if R-connected
            hx = rUpperLeftX + vhi.baseWidth
            highCap.hide()
        else:  # otherwise show it
            hx = rUpperLeftX + halfBaseWidth
            highCap.setPos(rUpperLeftX, rUpperLeftY)
            highCap.show()
        # special case: single-base strand with no L or R connections,
        # (unconnected caps were made visible in previous block of code)
        if strand.numBases() == 1 and \
                  (self.leftCap.isVisible() and self.rightCap.isVisible()):
            lowCap.hide()  # hide 
            highCap.hide()
            dualCap.setPos(lUpperLeftX, lUpperLeftY)
            dualCap.show()
        else:
            dualCap.hide()
        # 2. Line drawing
        hy = ly = lUpperLeftY + halfBaseWidth
        self.setLine(lx, ly, hx, hy)
        self.updatePensAndBrushes(strand)

    def updatePensAndBrushes(self, strand):
        lowIdx, highIdx = strand.lowIdx(), strand.highIdx()
        
        if strand.isScaf():
            pen = QPen(styles.scafstroke, styles.PATH_STRAND_STROKE_WIDTH)
            brush = QBrush(styles.handlefill)
        else:
            colr = self._modelStrand.oligo().color()
            pen = QPen(colr, styles.PATH_STRAND_STROKE_WIDTH)
            brush = QBrush(colr)
        pen.setCapStyle(Qt.FlatCap)
        self.setPen(pen)
        self._lowCap.setBrush(brush)
        self._highCap.setBrush(brush)
        self._dualCap.setBrush(brush)

    def remove(self, strand):
        ns = self.normalStrand
        ns.didMove.disconnect(self.update)
        ns.apparentConnectivityChanged.disconnect(self.update)
        ns.willBeRemoved.disconnect(self.remove)
        scene = self.scene()
        scene.removeItem(self.rightCap)
        self.scene().removeItem(self.leftCap)
        self.rightCap = None
        self.leftCap = None
        scene.removeItem(self)
    # end def
    

    ### COMMANDS ###
    
