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
from decorators.insertionitem import InsertionItem

import util
# import Qt stuff into the module namespace with PySide, PyQt4 independence
util.qtWrapImport('QtCore', globals(), ['pyqtSignal', 'QObject', 'Qt'])
util.qtWrapImport('QtGui', globals(), ['QGraphicsLineItem', 'QGraphicsPathItem',
                                       'QPen', 'QColor', 'QBrush', 'QFont', \
                                       'QFontMetricsF', 'QGraphicsSimpleTextItem'])

_baseWidth = styles.PATH_BASE_WIDTH

class StrandItem(QGraphicsLineItem):
    
    def __init__(self, modelStrand, virtualHelixItem):
        """The parent should be a VirtualHelixItem."""
        super(StrandItem, self).__init__(virtualHelixItem)
        self._modelStrand = modelStrand
        self._virtualHelixItem = virtualHelixItem
        self._activeTool = virtualHelixItem.activeTool()

        isDrawn5to3 = modelStrand.strandSet().isDrawn5to3()
        self._lowCap = EndpointItem(self, 'low', isDrawn5to3)
        self._highCap = EndpointItem(self, 'high', isDrawn5to3)
        self._dualCap = EndpointItem(self, 'dual', isDrawn5to3)

        self._isDrawn5to3 = isDrawn5to3
        self._isOnTop = virtualHelixItem.isStrandOnTop(modelStrand)

        self._seqLabel = QGraphicsSimpleTextItem(self)
        self._updateSequenceText()

        self._controller = StrandItemController(self, modelStrand)
        self._updateAppearance(modelStrand)
        
        self._insertionItems = {}
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
        # self._modelStrand = None
        self._controller.disconnectSignals()
        self._controller = None
        scene = self.scene()
        # scene.removeItem(self._highCap)
        # scene.removeItem(self._lowCap)
        self._highCap = None
        self._lowCap = None
        scene.removeItem(self)
    # end def

    def strandDestroyedSlot(self, strand):
        pass
    # end def

    def strandXover3pAddedSlot(self, strand3p, strand5p):
        partItem = self._virtualHelixItem.partItem()
        xo = XoverItem(partItem, strand3p, strand5p)
        partItem.addXoverItem(xo)
        self._updateAppearance(strand3p)
        partItem.updatePreXoverItems()
    # end def

    def strandUpdateSlot(self, strand):
        """
        Slot for just updating connectivity and color, and endpoint showing
        """
        self._updateAppearance(strand)
    # end def

    def oligoAppeareanceChangedSlot(self, oligo):
        pass
    # end def

    def oligoSequenceAddedSlot(self, oligo):
        self._updateSequenceText()
    # end def

    def oligoSequenceClearedSlot(self, oligo):
        self._updateSequenceText()
    # end def

    def strandHasNewOligoSlot(self, strand):
        self._controller.reconnectOligoSignals()
    # end def

    def strandInsertionAddedSlot(self, strand, insertion):
        self._insertionItems[insertion.idx()] = InsertionItem(self._virtualHelixItem, strand, insertion)
    # end def
    def strandInsertionChangedSlot(self, strand, insertion):
        self._insertionItems[insertion.idx()].update()
    # end def
    def strandInsertionRemovedSlot(self, strand, index):
        instItem = self._decorators[insertion.idx()]
        instItem.remove()
        del self._insertionItems[insertion.idx()]
    # end def
    def strandDecoratorAddedSlot(self, strand, decorator):
        pass
    # end def
    def strandDecoratorChangedSlot(self, strand, decorator):
        pass
    # end def
    def strandDecoratorRemovedSlot(self, strand, index):
        pass
    # end def
    def strandModifierAddedSlot(self, strand, modifier):
        pass
    # end def
    def strandModifierChangedSlot(self, strand, modifier):
        pass
    # end def
    def strandModifierRemovedSlot(self, strand, index):
        pass
    # end def

    ### ACCESSORS ###
    def activeTool(self):
        return self._activeTool
    # end def

    def strand(self):
        return self._modelStrand
    # end def
    
    def idxs(self):
        return self._modelStrand.idxs()

    def virtualHelixItem(self):
        return self._virtualHelixItem

    ### PUBLIC METHODS FOR DRAWING / LAYOUT ###
    def updateLine(self, movedCap):
        # setup
        bw = self._virtualHelixItem._baseWidth
        line = self.line()
        # set new line coords
        if movedCap == self._lowCap:
            p1 = line.p1()
            p1.setX(self._lowCap.pos().x() + bw)
            line.setP1(p1)
        else:
            p2 = line.p2()
            p2.setX(self._highCap.pos().x())
            line.setP2(p2)
        self.setLine(line)

    ### PRIVATE SUPPORT METHODS ###
    def _updateAppearance(self, strand):
        """
        Prepare Strand for drawing, positions are relative to the VirtualHelixItem:
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
            lx = lUpperLeftX + halfBaseWidth
            lowCap.hide()
        else:  # otherwise show left cap
            lx = lUpperLeftX + halfBaseWidth
            lowCap.setPos(lUpperLeftX, lUpperLeftY)
            lowCap.show()
        if strand.highConnection() != None:  # hide high cap if High-connected
            hx = hUpperLeftX + halfBaseWidth
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

    def _updateSequenceText(self):
        """
        """
        bw = _baseWidth
        seqLbl = self._seqLabel
        strand = self.strand()
        seqTxt = strand.sequence()
        # seqTxt = "ACG"
        
        if seqTxt == None:
            seqLbl.hide()
            return
        # end if
        
        # seqLbl.setPen(QPen( Qt.NoPen))    # leave the Pen as None for unless required
        seqLbl.setBrush(QBrush(Qt.black))
        seqLbl.setFont(styles.SEQUENCEFONT)
        
        # this will always draw from the 5 Prime end!
        seqX = 2*styles.SEQUENCETEXTXCENTERINGOFFSET + bw*strand.idx5Prime()
        seqY = -styles.SEQUENCETEXTYCENTERINGOFFSET
        
        if not self._isOnTop:
            # offset it towards the bottom
            seqY += 3*bw
            # offset X by the reverse centering offset and the 
            # length of the string 
            seqX += styles.SEQUENCETEXTXCENTERINGOFFSET 
            
            # rotate the characters upside down this does not affect positioning
            # coordinate system, +Y is still Down, and +X is still Right
            seqLbl.setRotation(180)
            # draw the text and reverse the string to draw 5 prime to 3 prime
            # seqTxt = seqTxt[::-1]
        # end if
        
        seqLbl.setPos(seqX,seqY)
        seqLbl.setText(seqTxt)
        
        seqLbl.show()
    # end def

    ### EVENT HANDLERS ###
    def mousePressEvent(self, event):
        """
        Parses a mousePressEvent to extract strandSet and base index,
        forwarding them to approproate tool method as necessary.
        """
        self.scene().views()[0].addToPressList(self)
        toolMethodName = str(self._activeTool()) + "MousePress"
        if hasattr(self, toolMethodName):
            idx = int(floor((event.pos().x()) / _baseWidth))
            getattr(self, toolMethodName)(idx)

    def mouseMoveEvent(self, event):
        """
        Parses a mouseMoveEvent to extract strandSet and base index,
        forwarding them to approproate tool method as necessary.
        """
        toolMethodName = str(self._activeTool()) + "MouseMove"
        if hasattr(self, toolMethodName):
            idx = int(floor((event.pos().x()) / _baseWidth))
            getattr(self, toolMethodName)(idx)

    def customMouseRelease(self, event):
        """
        Parses a mouseReleaseEvent to extract strandSet and base index,
        forwarding them to approproate tool method as necessary.
        """
        toolMethodName = str(self._activeTool()) + "MouseRelease"
        if hasattr(self, toolMethodName):
            idx = int(floor((event.pos().x()) / _baseWidth))
            getattr(self, toolMethodName)(idx)

    ### TOOL METHODS ###
    def breakToolMousePress(self, idx):
        """Break the strand is possible."""
        mStrand = self._modelStrand
        mStrand.split(idx)
    # end def

    def insertionToolMousePress(self, idx):
        """Add an insert to the strand if possible."""
        mStrand = self._modelStrand
        # localIdx = idx - mStrand.lowIdx()
        # mStrand.addInsertion(self, localIdx, 1)
        mStrand.addInsertion(idx, 1)
