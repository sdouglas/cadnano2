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

import views.pathview.pathselection as pathselection

import util
# import Qt stuff into the module namespace with PySide, PyQt4 independence
util.qtWrapImport('QtCore', globals(), ['pyqtSignal', 'QObject', 'Qt', 'QRectF'])
util.qtWrapImport('QtGui', globals(), ['QBrush', 'QColor', 'QFont', \
                                       'QFontMetricsF', 'QGraphicsLineItem', \
                                       'QGraphicsPathItem', 'QGraphicsItem', \
                                       'QGraphicsSimpleTextItem', \
                                       'QGraphicsRectItem', 'QPen'])

_baseWidth = styles.PATH_BASE_WIDTH
_defaultRect = QRectF(0,0, _baseWidth, _baseWidth)
_noPen = QPen(Qt.NoPen)


class StrandItem(QGraphicsLineItem):
    _filterName = "strand"
    
    def __init__(self, modelStrand, virtualHelixItem, viewroot):
        """The parent should be a VirtualHelixItem."""
        super(StrandItem, self).__init__(virtualHelixItem)
        self._modelStrand = modelStrand
        self._virtualHelixItem = virtualHelixItem
        self._viewroot = viewroot
        self._activeTool = virtualHelixItem.activeTool()

        self._controller = StrandItemController(self, modelStrand)
        isDrawn5to3 = modelStrand.strandSet().isDrawn5to3()

        self._strandFilter = modelStrand.strandFilter()

        self._insertionItems = {}
        # caps
        self._lowCap = EndpointItem(self, 'low', isDrawn5to3)
        self._highCap = EndpointItem(self, 'high', isDrawn5to3)
        self._dualCap = EndpointItem(self, 'dual', isDrawn5to3)

        # orientation
        self._isDrawn5to3 = isDrawn5to3
        # self._isOnTop = virtualHelixItem.isStrandOnTop(modelStrand)
        # label
        self._seqLabel = QGraphicsSimpleTextItem(self)
        self._updateSequenceText()

        # create a larger click area rect to capture mouse events
        self._clickArea = cA = QGraphicsRectItem(_defaultRect, self)
        cA.mousePressEvent = self.mousePressEvent
        cA.setPen(_noPen)
        self.setAcceptHoverEvents(True)
        cA.setAcceptHoverEvents(True)
        cA.hoverMoveEvent = self.hoverMoveEvent

        self.setZValue(styles.ZSTRANDITEM)

        # xover comming from the 3p end
        self._xover3pEnd = XoverItem(self, virtualHelixItem)
        # initial refresh
        self._updateColor(modelStrand)
        self._updateAppearance(modelStrand)

        self.setZValue(styles.ZSTRANDITEM)
        self.setFlag(QGraphicsItem.ItemIsSelectable)
    # end def

    ### SIGNALS ###

    ### SLOTS ###
    def strandResizedSlot(self, strand, indices):
        """docstring for strandResizedSlot"""
        lowMoved = self._lowCap.updatePosIfNecessary(self.idxs()[0])
        highMoved = self._highCap.updatePosIfNecessary(self.idxs()[1])
        group = self.group()
        self.tempReparent()  
        if lowMoved:
            self.updateLine(self._lowCap)
        if highMoved:
            self.updateLine(self._highCap)
        if strand.connection3p():
            self._xover3pEnd.update(strand)
        self.refreshInsertionItems(strand)
        self._updateSequenceText()
        if group:
            group.addToGroup(self)
    # end def

    def sequenceAddedSlot(self, oligo):
        """docstring for sequenceAddedSlot"""
        pass
    # end def

    def sequenceClearedSlot(self, oligo):
        """docstring for sequenceClearedSlot"""
        pass
    # end def

    def strandRemovedSlot(self, strand):
        # self._modelStrand = None
        self._controller.disconnectSignals()
        self._controller = None
        scene = self.scene()
        scene.removeItem(self._clickArea)
        scene.removeItem(self._highCap)
        scene.removeItem(self._lowCap)
        scene.removeItem(self._seqLabel)
        self._xover3pEnd.remove()
        self._xover3pEnd = None
        for insertionItem in self._insertionItems.itervalues():
            insertionItem.remove()
        self._insertionItems = None
        self._clickArea = None
        self._highCap = None
        self._lowCap = None
        self._seqLabel = None
        self._modelStrand = None
        self._virtualHelixItem = None
        scene.removeItem(self)
    # end def

    def strandUpdateSlot(self, strand):
        """
        Slot for just updating connectivity and color, and endpoint showing
        """
        self._updateAppearance(strand)
    # end def

    def oligoAppearanceChangedSlot(self, oligo):
        strand = self._modelStrand
        self._updateColor(strand)
        if strand.connection3p():
            self._xover3pEnd._updateColor(strand)
        for insertion in self.insertionItems().itervalues():
            insertion.updateItem()
    # end def

    def oligoSequenceAddedSlot(self, oligo):
        self._updateSequenceText()
    # end def

    def oligoSequenceClearedSlot(self, oligo):
        self._updateSequenceText()
    # end def

    def strandHasNewOligoSlot(self, strand):
        strand = self._modelStrand
        self._controller.reconnectOligoSignals()
        self._updateColor(strand)
        if strand.connection3p():
            self._xover3pEnd._updateColor(strand)
    # end def

    def strandInsertionAddedSlot(self, strand, insertion):
        self.insertionItems()[insertion.idx()] = \
                    InsertionItem(self._virtualHelixItem, strand, insertion)
    # end def
    def strandInsertionChangedSlot(self, strand, insertion):
        self.insertionItems()[insertion.idx()].updateItem()
    # end def

    def strandInsertionRemovedSlot(self, strand, index):
        instItem = self.insertionItems()[index]
        instItem.remove()
        del self.insertionItems()[index]
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

    def selectedChangedSlot(self, strand, indices):
        self.selectIfRequired(self.partItem().document(), indices)
    # end def

    ### ACCESSORS ###
    def activeTool(self):
        return self._activeTool
    # end def
    
    def viewroot(self):
        return self._viewroot
    # end def

    def insertionItems(self):
        return self._insertionItems
    # end def

    def strand(self):
        return self._modelStrand
    # end def

    def strandFilter(self):
        return self._strandFilter
    # end def

    def idxs(self):
        return self._modelStrand.idxs()
    # end def

    def virtualHelixItem(self):
        return self._virtualHelixItem
    # end def

    def partItem(self):
        return self._virtualHelixItem.partItem()
    # end def

    def window(self):
        return self._virtualHelixItem.window()

    ### PUBLIC METHODS FOR DRAWING / LAYOUT ###
    def refreshInsertionItems(self, strand):
        iItems = self.insertionItems()
        iModel = strand.insertionsOnStrand()
        # remove all in items
        for index, iItem in iItems.items():
            iItem.remove()
            del iItems[index]
        # end for
        # add in the ones supposed to be there
        for insertion in iModel:
            iItems[insertion.idx()] = \
                    InsertionItem(self._virtualHelixItem, strand, insertion)
        # end for
    # end def

    def resetStrandItem(self, virtualHelixItem, isDrawn5to3):
        self.setParentItem(virtualHelixItem)
        self._virtualHelixItem = virtualHelixItem
        self.resetEndPointItems(isDrawn5to3)
    # end def

    def resetEndPointItems(self, isDrawn5to3):
        self._isDrawn5to3 = isDrawn5to3
        self._lowCap.resetEndPoint(isDrawn5to3)
        self._highCap.resetEndPoint(isDrawn5to3)
        self._dualCap.resetEndPoint(isDrawn5to3)
    # end def

    def updateLine(self, movedCap):
        # setup
        bw = _baseWidth
        cA = self._clickArea
        line = self.line()
        # set new line coords
        if movedCap == self._lowCap:
            p1 = line.p1()
            newX = self._lowCap.pos().x() + bw
            p1.setX(newX)
            line.setP1(p1)
            temp = cA.rect()
            temp.setLeft(newX)
            cA.setRect(temp)
        else:
            p2 = line.p2()
            newX = self._highCap.pos().x()
            p2.setX(newX)
            line.setP2(p2)
            temp = cA.rect()
            temp.setRight(newX)
            cA.setRect(temp)
        self.setLine(line)
    # end def

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
        bw = _baseWidth
        halfBaseWidth = bw / 2.0
        lowIdx, highIdx = strand.lowIdx(), strand.highIdx()

        lUpperLeftX, lUpperLeftY = vhi.upperLeftCornerOfBase(lowIdx, strand)
        hUpperLeftX, hUpperLeftY = vhi.upperLeftCornerOfBase(highIdx, strand)
        lowCap = self._lowCap
        highCap = self._highCap
        dualCap = self._dualCap

        # 1. Cap visibilty
        lx = lUpperLeftX + bw  # draw from right edge of base
        lowCap.setPos(lUpperLeftX, lUpperLeftY)
        if strand.connectionLow() != None:  # has low xover
            # if we are hiding it, we might as well make sure it is reparented to the StrandItem
            # lowCap.tempReparent()
            lowCap.restoreParent()
            lowCap.hide()
        else:  # has low cap
            if not lowCap.isVisible():
                lowCap.show()

        hx = hUpperLeftX  # draw to edge of base
        highCap.setPos(hUpperLeftX, hUpperLeftY)
        if strand.connectionHigh() != None:  # has high xover
            # if we are hiding it, we might as well make sure it is reparented to the StrandItem
            # highCap.tempReparent()
            highCap.restoreParent()
            highCap.hide()
        else:  # has high cap
            if not highCap.isVisible():
                highCap.show()

        # special case: single-base strand with no L or H connections,
        # (unconnected caps were made visible in previous block of code)
        if strand.length() == 1 and \
                  (lowCap.isVisible() and highCap.isVisible()):
            lowCap.hide()
            highCap.hide()
            dualCap.setPos(lUpperLeftX, lUpperLeftY)
            dualCap.show()
        else:
            dualCap.hide()

        # 2. Xover drawing
        xo = self._xover3pEnd
        if strand.connection3p():
            xo.update(strand)
            xo.showIt()
        else:
            # xo.tempReparent()
            xo.restoreParent()
            xo.hideIt()

        # 3. Refresh insertionItems if necessary drawing
        self.refreshInsertionItems(strand)

        # 4. Line drawing
        hy = ly = lUpperLeftY + halfBaseWidth
        self.setLine(lx, ly, hx, hy)
        rectf = QRectF(lUpperLeftX+bw, lUpperLeftY, bw*(highIdx-lowIdx-1), bw)
        self._clickArea.setRect(rectf)
        self._updateHighlight(self.pen().color())
    # end def

    def _updateColor(self, strand):
        oligo = self._modelStrand.oligo()
        color = QColor(oligo.color())
        self._updateHighlight(color)
    # end def
    
    def _updateHighlight(self, color):
        """
        
        """
        oligo = self._modelStrand.oligo()
        penWidth = styles.PATH_STRAND_STROKE_WIDTH
        if oligo.shouldHighlight():
            color.setAlpha(128)
            penWidth = styles.PATH_STRAND_HIGHLIGHT_STROKE_WIDTH
        pen = QPen(color, penWidth)
        pen.setCosmetic(True)
        brush = QBrush(color)
        pen.setCapStyle(Qt.FlatCap)
        self.setPen(pen)
        self._lowCap.updateHighlight(brush)
        self._highCap.updateHighlight(brush)
        self._dualCap.updateHighlight(brush)
    # end def

    def _updateSequenceText(self):
        """
        docstring for _updateSequenceText
        """
        bw = _baseWidth
        seqLbl = self._seqLabel
        strand = self.strand()
        seqTxt = strand.sequence()
        isDrawn3to5 = not self._isDrawn5to3
        textXCenteringOffset = styles.SEQUENCETEXTXCENTERINGOFFSET

        if seqTxt == '':
            seqLbl.hide()
            for iItem in self.insertionItems().itervalues():
                iItem.hideSequence()
            return
        # end if

        strandSeqList = strand.getSequenceList()
        seqList = [x[1][0] for x in strandSeqList]
        insertSeqList = [(x[0], x[1][1]) for x in strandSeqList]
        iItems = self.insertionItems()
        for idx, seqTxt in insertSeqList:
            if seqTxt != '':
                iItems[idx].setSequence(seqTxt)

        if isDrawn3to5:
            seqList = seqList[::-1]
        seqTxt = ''.join(seqList)
        # seqLbl.setPen(QPen( Qt.NoPen))    # leave the Pen as None for unless required
        seqLbl.setBrush(QBrush(Qt.black))
        seqLbl.setFont(styles.SEQUENCEFONT)

        # this will always draw from the 5 Prime end!
        seqX = 2*textXCenteringOffset + bw*strand.idx5Prime()
        seqY = styles.SEQUENCETEXTYCENTERINGOFFSET

        if isDrawn3to5:
            # offset it towards the bottom
            seqY += bw * .8
            # offset X by the reverse centering offset and the string length
            seqX += textXCenteringOffset
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
        idx = int(floor((event.pos().x()) / _baseWidth))
        self._virtualHelixItem.setActive(idx)
        toolMethodName = str(self._activeTool()) + "MousePress"
        if hasattr(self, toolMethodName):
            getattr(self, toolMethodName)(event, idx)
    # end def

    def mouseMoveEvent(self, event):
        """
        Parses a mouseMoveEvent to extract strandSet and base index,
        forwarding them to approproate tool method as necessary.
        """
        toolMethodName = str(self._activeTool()) + "MouseMove"
        if hasattr(self, toolMethodName):
            idx = int(floor((event.pos().x()) / _baseWidth))
            getattr(self, toolMethodName)(idx)
    # end def

    def hoverLeaveEvent(self, event):
        self.partItem().updateStatusBar("")
    # end def

    def hoverMoveEvent(self, event):
        """
        Parses a mouseMoveEvent to extract strandSet and base index,
        forwarding them to approproate tool method as necessary.
        """
        vhiNum = self._virtualHelixItem.number()
        idx = int(floor((event.pos().x()) / _baseWidth))
        self.partItem().updateStatusBar("%d[%d]" % (vhiNum, idx))
        toolMethodName = str(self._activeTool()) + "HoverMove"
        if hasattr(self, toolMethodName):
            getattr(self, toolMethodName)(idx)
    # end def

    def customMouseRelease(self, event):
        """
        Parses a mouseReleaseEvent to extract strandSet and base index,
        forwarding them to approproate tool method as necessary.
        """
        toolMethodName = str(self._activeTool()) + "MouseRelease"
        if hasattr(self, toolMethodName):
            idx = int(floor((event.pos().x()) / _baseWidth))
            getattr(self, toolMethodName)(idx)
    # end def

    ### TOOL METHODS ###
    def breakToolMousePress(self, event, idx):
        """Break the strand is possible."""
        mStrand = self._modelStrand
        mStrand.split(idx)
    # end def

    def breakToolHoverMove(self, idx):
        pass
        # mStrand = self._modelStrand
        # vhi = self._virtualHelixItem
        # breakTool = self._activeTool()
        # breakTool.updateHoverRect(vhi, mStrand, idx, show=True)
    # end def

    def selectToolMousePress(self, event, idx):
        currentFilterDict = self._viewroot.selectionFilterDict()
        if self.strandFilter() in currentFilterDict and self._filterName in currentFilterDict:
            selectionGroup = self._viewroot.strandItemSelectionGroup()
            mod = Qt.MetaModifier
            if not (event.modifiers() & mod):
                 selectionGroup.clearSelection(False)
            selectionGroup.setSelectionLock(selectionGroup)
            # self.setSelectedColor(True)
            selectionGroup.pendToAdd(self)
            selectionGroup.pendToAdd(self._lowCap)
            selectionGroup.pendToAdd(self._highCap)
            selectionGroup.processPendingToAddList()
            return selectionGroup.mousePressEvent(event)
    # end def

    def pencilToolMousePress(self, event, idx):
        """Break the strand is possible."""
        mStrand = self._modelStrand
        vhi = self._virtualHelixItem
        partItem = vhi.partItem()
        activeTool = self._activeTool()
        if activeTool.isFloatingXoverBegin():
            if idx == mStrand.idx5Prime():
                return
            tempXover = activeTool.floatingXover()
            tempXover.updateBase(vhi, mStrand, idx)
            activeTool.setFloatingXoverBegin(False)
        else:
            activeTool.setFloatingXoverBegin(True)
            # install Xover
            activeTool.attemptToCreateXover(vhi, mStrand, idx)
    # end def

    def pencilToolHoverMove(self, idx):
        """Pencil the strand is possible."""
        mStrand = self._modelStrand
        vhi = self._virtualHelixItem
        activeTool = self._activeTool()
        if not activeTool.isFloatingXoverBegin():
            tempXover = activeTool.floatingXover()
            tempXover.updateFloatingFromStrandItem(vhi, mStrand, idx)
    # end def

    def eraseToolMousePress(self, event, idx):
        mStrand = self._modelStrand
        mStrand.strandSet().removeStrand(mStrand)
    # end def

    def insertionToolMousePress(self, event, idx):
        """Add an insert to the strand if possible."""
        mStrand = self._modelStrand
        mStrand.addInsertion(idx, 1)
    # end def

    def paintToolMousePress(self, event, idx):
        """Add an insert to the strand if possible."""
        mStrand = self._modelStrand
        if mStrand.isStaple():
            color = self.window().pathColorPanel.stapColorName()
        else:
            color = self.window().pathColorPanel.scafColorName()
        mStrand.oligo().applyColor(color)
    # end def

    def pencilToolHoverMove(self, idx):
        """Pencil the strand is possible."""
        mStrand = self._modelStrand
        vhi = self._virtualHelixItem
        activeTool = self._activeTool()

        if not activeTool.isFloatingXoverBegin():
            tempXover = activeTool.floatingXover()
            tempXover.updateFloatingFromStrandItem(vhi, mStrand, idx)
    # end def

    def pencilToolMousePress(self, event, idx):
        """Break the strand is possible."""
        mStrand = self._modelStrand
        vhi = self._virtualHelixItem
        partItem = vhi.partItem()
        activeTool = self._activeTool()

        if activeTool.isFloatingXoverBegin():
            # block xovers starting at a 5 prime end
            if mStrand.idx5Prime() == idx:
                return
            else:
                tempXover = activeTool.floatingXover()
                tempXover.updateBase(vhi, mStrand, idx)
                activeTool.setFloatingXoverBegin(False)
        else:
            activeTool.setFloatingXoverBegin(True)
            # install Xover
            activeTool.attemptToCreateXover(vhi, mStrand, idx)
    # end def

    def skipToolMousePress(self, event, idx):
        """Add an insert to the strand if possible."""
        mStrand = self._modelStrand
        mStrand.addInsertion(idx, -1)
    # end def
    
    def addSeqToolMousePress(self, event, idx):
        """
        Checks that a scaffold was clicked, and then calls apply sequence
        to the clicked strand via its oligo.
        """
        mStrand = self._modelStrand
        if mStrand.isScaffold():
            self._activeTool().applySequence(mStrand.oligo())
    # end def
    
    def restoreParent(self, pos=None):
        """
        Required to restore parenting and positioning in the partItem
        """
        # map the position
        # print "restoring parent si"
        self.tempReparent(pos)
        self.setSelectedColor(False)
        self.setSelected(False)
    # end def
    
    def tempReparent(self, pos=None):
        vhItem = self.virtualHelixItem()
        if pos == None:
            pos = self.scenePos()
        self.setParentItem(vhItem)
        tempP = vhItem.mapFromScene(pos)
        self.setPos(tempP)
    # end def

    def setSelectedColor(self, value):
        if value == True:
            color = QColor("#ff3333")
        else:
            oligo = self._modelStrand.oligo()
            color = QColor(oligo.color())
            if oligo.shouldHighlight():
                color.setAlpha(128)
        pen = self.pen()
        pen.setColor(color)
        self.setPen(pen)
    # end def

    def itemChange(self, change, value):
        # for selection changes test against QGraphicsItem.ItemSelectedChange
        # intercept the change instead of the has changed to enable features.
        if change == QGraphicsItem.ItemSelectedChange and self.scene():
            viewroot = self._viewroot
            currentFilterDict = viewroot.selectionFilterDict()
            selectionGroup = viewroot.strandItemSelectionGroup()
            
            # only add if the selectionGroup is not locked out
            if value == True and (self._filterName in currentFilterDict or not selectionGroup.isNormalSelect()):
                if self._strandFilter in currentFilterDict:
                    if self.group() != selectionGroup:
                        selectionGroup.pendToAdd(self)
                        selectionGroup.setSelectionLock(selectionGroup)
                        self.setSelectedColor(True)
                        selectionGroup.pendToAdd(self._lowCap)
                        selectionGroup.pendToAdd(self._highCap)
                    return True
                else:
                    return False
            # end if
            elif value == True:
                # Don't select
                return False
            else:
                # Deselect
                # print "Deselecting strand"
                selectionGroup.pendToRemove(self)
                self.setSelectedColor(False)
                selectionGroup.pendToRemove(self._lowCap)
                selectionGroup.pendToRemove(self._highCap)
                return False
            # end else
        # end if
        return QGraphicsItem.itemChange(self, change, value)
    # end def

    def selectIfRequired(self, document, indices):
        """
        Select self or xover item as necessary
        """
        strand5p = self._modelStrand
        con3p = strand5p.connection3p()
        selectionGroup = self._viewroot.strandItemSelectionGroup()
        # check this strand's xover
        if con3p:
            # perhaps change this to a direct call, but here are seeds of an 
            # indirect way of doing selection checks    
            if document.isModelStrandSelected(con3p) and document.isModelStrandSelected(strand5p):
                val3p = document.getSelectedStrandValue(con3p)
                # print "xover idx", indices
                test3p = val3p[0] if con3p.isDrawn5to3() else val3p[1]
                test5p = indices[1] if strand5p.isDrawn5to3() else indices[0]
                if test3p and test5p:
                    xoi = self._xover3pEnd
                    if not xoi.isSelected() or not xoi.group():
                        selectionGroup.setNormalSelect(False)
                        xoi.modelSelect(document)
                        selectionGroup.addToGroup(xoi)
                        selectionGroup.setNormalSelect(True)
                # end if
            # end if
        # end if
        # print "select if req", indices, self.isSelected(), self.group(), "normal select", selectionGroup.isNormalSelect()
        if indices[0] == True and indices[1] == True:
            if not self.isSelected() or not self.group():
                selectionGroup.setNormalSelect(False)
                self.modelSelect(document)
                selectionGroup.addToGroup(self)
                selectionGroup.setNormalSelect(True)
    # end def

    def modelDeselect(self, document):
        self.restoreParent()
        self._lowCap.modelDeselect(document)
        self._highCap.modelDeselect(document)
    # end def

    def modelSelect(self, document):
        self.setSelected(True)
        self.setSelectedColor(True)
    # end def
    
    def paint(self, painter, option, widget):
        painter.setPen(self.pen())
        painter.drawLine(self.line())
    # end def
