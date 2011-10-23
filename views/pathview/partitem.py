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

from collections import defaultdict
from math import ceil
from activesliceitem import ActiveSliceItem
from controllers.itemcontrollers.partitemcontroller import PartItemController
from pathselection import SelectionItemGroup
from pathselection import PathHelixHandleSelectionBox
from pathselection import BreakpointHandleSelectionBox
from prexoveritem import PreXoverItem
from strand.xoveritem import XoverNode3
from ui.mainwindow.svgbutton import SVGButton
from views import styles
from virtualhelixitem import VirtualHelixItem
import util

# import Qt stuff into the module namespace with PySide, PyQt4 independence
util.qtWrapImport('QtCore', globals(), ['pyqtSlot', 'QRectF', 'Qt'])
util.qtWrapImport('QtGui', globals(), ['QBrush', 'QGraphicsPathItem',
                                       'QGraphicsRectItem', 'QInputDialog',
                                        'QPen'])


class PartItem(QGraphicsRectItem):
    def __init__(self, modelPart, activeTool, parent):
        """parent should always be pathrootitem"""
        super(PartItem, self).__init__(parent)
        self._modelPart = mP = modelPart
        self._activeTool = activeTool
        self._activeSliceItem = ActiveSliceItem(self, mP.activeBaseIndex())
        self._activeVirtualHelixItem = None
        self._controller = PartItemController(self, mP)
        self._preXoverItems = []  # crossover-related
        self._virtualHelixHash = {}
        self._virtualHelixItemList = []
        self._vHRect = QRectF()
        self._initSelections()
        self._initResizeButtons()
        self.setAcceptHoverEvents(True)
    # end def

    def _initSelections(self):
        """Initialize anything related to multiple selection."""
        self._selectionLock = None
        bType = PathHelixHandleSelectionBox
        self._vhiHSelectionGroup = SelectionItemGroup(boxtype=bType,\
                                                      constraint='y',\
                                                      parent=self)
    # end def

    def _initResizeButtons(self):
        """Instantiate the buttons used to change the canvas size."""
        self._addBasesButton = SVGButton(":/pathtools/add-bases", self)
        self._addBasesButton.clicked.connect(self._addBasesClicked)
        self._addBasesButton.hide()
        self._removeBasesButton = SVGButton(":/pathtools/remove-bases", self)
        self._removeBasesButton.clicked.connect(self._removeBasesClicked)
        self._removeBasesButton.hide()
    # end def

    # def paint(self, painter, option, widget=None):
    #     painter.setPen(QPen(styles.redstroke))
    #     painter.drawRect(self._vHRect)
    # # end def

    ### SIGNALS ###

    ### SLOTS ###
    def partParentChangedSlot(self):
        """docstring for partParentChangedSlot"""
        # print "PartItem.partParentChangedSlot"
        pass
    # end def

    def partDimensionsChangedSlot(self, part):
        print "partDimensionsChangedSlot"
        if len(self._virtualHelixItemList) > 0:
            vhi = self._virtualHelixItemList[0]
            vhiRect = vhi.boundingRect()
            vhiHRect = vhi.handle().boundingRect()
            self._vHRect.setLeft(vhiHRect.left())
            self._vHRect.setRight(vhiRect.right())
        self.scene().views()[0].zoomToFit()
        self._activeSliceItem.resetBounds()
        self._updateBoundingRect()
    # end def

    def partRemovedSlot(self):
        """docstring for partDestroyedSlot"""
        self._activeSliceItem.removed()
        self.parentItem().removePartItem(self)
        scene = self.scene()
        scene.removeItem(self)
        self._modelPart = None
        self._virtualHelixHash = None
        self._virtualHelixItemList = None
        self._controller.disconnectSignals()
        self._controller = None
    # end def

    def partDestroyedSlot(self):
        """docstring for partDestroyedSlot"""
        # print "PartItem.partDestroyedSlot"
        pass
    # end def

    def partPreDecoratorSelectedSlot(self, row, col, baseIdx):
        """docstring for partPreDecoratorSelectedSlot"""
        # determine where rootitem (self) is currently centered
        # compute deltaX from baseIdx and baseWidth
        # compute deltaY from virtualhelix position
        # self.translate(deltaX, deltaY)
        pass
    # end def

    def partVirtualHelixAddedSlot(self, modelVirtualHelix):
        """
        When a virtual helix is added to the model, this slot handles
        the instantiation of a virtualhelix item.
        """
        # print "PartItem.partVirtualHelixAddedSlot"
        vh = modelVirtualHelix
        vhi = VirtualHelixItem(self, modelVirtualHelix, self._activeTool)
        vhi.setPos
        self._virtualHelixHash[vh.coord()] = vhi
        self._virtualHelixItemList.append(vhi)
        self._setVirtualHelixItemList(self._virtualHelixItemList)
        self._updateBoundingRect()
    # end def

    def partVirtualHelixRenumberedSlot(self, coord):
        """Notifies the virtualhelix at coord to change its number"""
        vh = self._virtualHelixHash[coord]
        # check for new number
        # notify VirtualHelixHandleItem to update its label
        # notify VirtualHelix to update its xovers
        # if the VirtualHelix is active, refresh prexovers
        pass
    # end def

    def partVirtualHelixResizedSlot(self, coord):
        """Notifies the virtualhelix at coord to resize."""
        vh = self._virtualHelixHash[coord]
        vh.resize()
    # end def

    def partVirtualHelicesReorderedSlot(self, orderedCoordList):
        """docstring for partVirtualHelicesReorderedSlot"""
        newList = self._virtualHelixItemList
        decorated = [(orderedCoordList.index(vhi.coord()), vhi)\
                        for vhi in self._virtualHelixItemList]
        decorated.sort()
        newList = [vhi for idx, vhi in decorated]
        self._setVirtualHelixItemList(newList)
    # end def

    def updatePreXoverItemsSlot(self, virtualHelix):
        part = self.part()
        if part.areVirtualHelicesNeighbors(part.activeVirtualHelix(), virtualHelix):
            vhi = self.itemForVirtualHelix(virtualHelix)
            self.setActiveVirtualHelixItem(vhi)
            self.setPreXoverItemsVisible(self.activeVirtualHelixItem())
    # end def

    ### ACCESSORS ###
    def activeTool(self):
        return self._activeTool
    # end def

    def activeVirtualHelixItem(self):
        return self._activeVirtualHelixItem
    # end def

    def part(self):
        """Return a reference to the model's part object"""
        return self._modelPart
    # end def

    def removeVirtualHelixItem(self, virtualHelixItem):
        vh = virtualHelixItem.virtualHelix()
        self._virtualHelixItemList.remove(virtualHelixItem)
        del self._virtualHelixHash[vh.coord()]
        self._setVirtualHelixItemList(self._virtualHelixItemList)
        self._updateBoundingRect()

    # end def

    def itemForVirtualHelix(self, virtualHelix):
        return self._virtualHelixHash[virtualHelix.coord()]
    # end def

    def virtualHelixBoundingRect(self):
        return self._vHRect
    # end def

    def vhiHandleSelectionGroup(self):
        return self._vhiHSelectionGroup
    # end def

    def window(self):
        return self.parentItem().window()
    # end def

    ### PRIVATE METHODS ###
    def _addBasesClicked(self):
        part = self._modelPart
        step = part.stepSize()
        self._addBasesDialog = dlg = QInputDialog(self.window())
        dlg.setInputMode(QInputDialog.IntInput)
        dlg.setIntMinimum(0)
        dlg.setIntValue(step)
        dlg.setIntMaximum(100000)
        dlg.setIntStep(step)
        dlg.setLabelText(( "Number of bases to add to the existing"\
                         + " %i bases\n(must be a multiple of %i)")\
                         % (part.maxBaseIdx(), step))
        dlg.intValueSelected.connect(self._addBasesCallback)
        dlg.open()
    # end def

    @pyqtSlot(int)
    def _addBasesCallback(self, n):
        part = self._modelPart
        self._addBasesDialog.intValueSelected.disconnect(self._addBasesCallback)
        del self._addBasesDialog
        maxDelta = int(n) / part.stepSize() * part.stepSize()
        part.resizeVirtualHelices(0, maxDelta)
    # end def

    def _removeBasesClicked(self):
        part = self._modelPart
        idx = part.indexOfRightmostNonemptyBase()
        idx = int(ceil(float(idx)/part.stepSize()))*part.stepSize()
        idx = util.clamp(idx, part.stepSize(), 10000)
        delta = idx - part.maxBaseIdx()
        if delta < 0:
            part.resizeVirtualHelices(0, delta)
    # end def

    def _setVirtualHelixItemList(self, newList, zoomToFit=True):
        """
        Give me a list of VirtualHelixItems and I'll parent them to myself if
        necessary, position them in a column, adopt their handles, and
        position them as well.
        """
        y = 0  # How far down from the top the next PH should be
        leftmostExtent = 0
        rightmostExtent = 0

        scene = self.scene()
        vhiRect = None
        vhiHRect = None

        for vhi in newList:
            vhi.setPos(0, y)
            if not vhiRect:
                vhiRect = vhi.boundingRect()
                step = vhiRect.height() + styles.PATH_HELIX_PADDING
            # end if

            # get the VirtualHelixHandleItem
            vhiH = vhi.handle()
            if vhiH.parentItem() != self._vhiHSelectionGroup:
                vhiH.setParentItem(self)

            if not vhiHRect:
                vhiHRect = vhiH.boundingRect()

            vhiH.setPos(-2 * vhiHRect.width(), y + (vhiRect.height() - vhiHRect.height()) / 2)

            leftmostExtent = min(leftmostExtent, -2 * vhiHRect.width())
            rightmostExtent = max(rightmostExtent, vhiRect.width())
            y += step
            self.updateXoverItems(vhi)
        # end for
        self._vHRect = QRectF(leftmostExtent, -40, -leftmostExtent + rightmostExtent, y + 40)
        self._virtualHelixItemList = newList
        if zoomToFit:
            self.scene().views()[0].zoomToFit()
    # end def

    def _updateBoundingRect(self):
        """
        Updates the bounding rect to the size of the childrenBoundingRect,
        and refreshes the addBases and removeBases buttons accordingly.

        Called by partVirtualHelixAddedSlot, partDimensionsChangedSlot, or
        removeVirtualHelixItem.
        """
        self.setPen(QPen(Qt.NoPen))
        self.setRect(self.childrenBoundingRect())
        # move and show or hide the buttons if necessary
        addButton = self._addBasesButton
        rmButton = self._removeBasesButton
        if len(self._virtualHelixItemList) > 0:
            addRect = addButton.boundingRect()
            rmRect = rmButton.boundingRect()
            x = self._vHRect.right()
            y = -styles.PATH_HELIX_PADDING
            addButton.setPos(x, y)
            rmButton.setPos(x-rmRect.width(), y)
            addButton.show()
            rmButton.show()
        else:
            addButton.hide()
            rmButton.hide()
    # end def

    ### PUBLIC METHODS ###
    def getOrderedVirtualHelixList(self):
        """Used for encoding."""
        ret = []
        for vhi in self._virtualHelixItemList:
            ret.append(vhi.coord())
        return ret
    # end def

    def numberOfVirtualHelices(self):
        return len(self._virtualHelixItemList)
    # end def

    def reorderHelices(self, first, last, indexDelta):
        """
        Reorder helices by moving helices _pathHelixList[first:last]
        by a distance delta in the list. Notify each PathHelix and
        PathHelixHandle of its new location.
        """
        vhiList = self._virtualHelixItemList
        helixNumbers = [vhi.number() for vhi in vhiList]
        firstIndex = helixNumbers.index(first)
        lastIndex = helixNumbers.index(last) + 1

        if indexDelta < 0:  # move group earlier in the list
            newIndex = max(0, indexDelta + firstIndex)
            newList = vhiList[0:newIndex] +\
                                vhiList[firstIndex:lastIndex] +\
                                vhiList[newIndex:firstIndex] +\
                                vhiList[lastIndex:]
        # end if
        else:  # move group later in list
            newIndex = min(len(vhiList), indexDelta + lastIndex)
            newList = vhiList[:firstIndex] +\
                                 vhiList[lastIndex:newIndex] +\
                                 vhiList[firstIndex:lastIndex] +\
                                 vhiList[newIndex:]
        # end else

        # call the method to move the items and store the list
        self._setVirtualHelixItemList(newList, zoomToFit=False)
    # end def

    def setActiveVirtualHelixItem(self, newActiveVHI):
        if newActiveVHI != self._activeVirtualHelixItem:
            self._activeVirtualHelixItem = newActiveVHI
            self._modelPart.setActiveVirtualHelix(newActiveVHI.virtualHelix())
    # end def

    def selectionLock(self):
        return self._selectionLock
    # end def

    def setSelectionLock(self, locker):
        self._selectionLock = locker
    # end def

    def setPreXoverItemsVisible(self, virtualHelixItem):
        """
        self._preXoverItems list references prexovers parented to other
        PathHelices such that only the activeHelix maintains the list of
        visible prexovers
        
        A possible more efficient solution is to maintain the list _preXoverItems
        in pathhelixgroup, in fact this method should live in pathhelixgroup
        """
        vhi = virtualHelixItem
        if vhi == None:
            return
        # end if

        vh = vhi.virtualHelix()
        partItem = self
        part = self.part()

        # clear all PreXoverItems
        map(PreXoverItem.remove, self._preXoverItems)
        self._preXoverItems = []

        potentialXovers = part.potentialCrossoverList(vh)
        for neighbor, index, strandType, isLowIdx in potentialXovers:
            # create one half
            neighborVHI = self.itemForVirtualHelix(neighbor)
            pxi = PreXoverItem(vhi, neighborVHI, index, strandType, isLowIdx)
            # add to list
            self._preXoverItems.append(pxi)
            # create the complement
            pxi = PreXoverItem(neighborVHI, vhi, index, strandType, isLowIdx)
            # add to list
            self._preXoverItems.append(pxi)
        # end for
    # end def

    def updatePreXoverItems(self):
        self.setPreXoverItemsVisible(self.activeVirtualHelixItem())
    # end def

    def updateXoverItems(self, virtualHelixItem):
        for item in virtualHelixItem.childItems():
            if isinstance(item, XoverNode3):
                item.refreshXover()
     # end def

    ### COORDINATE METHODS ###
    def keyPanDeltaX(self):
        """How far a single press of the left or right arrow key should move
        the scene (in scene space)"""
        vhs = self._virtualHelixItemList
        return vhs[0].keyPanDeltaX() if vhs else 5
    # end def

    def keyPanDeltaY(self):
        """How far an an arrow key should move the scene (in scene space)
        for a single press"""
        vhs = self._virtualHelixItemList
        if not len(vhs) > 1:
            return 5
        dy = vhs[0].pos().y() - vhs[1].pos().y()
        dummyRect = QRectF(0, 0, 1, dy)
        return self.mapToScene(dummyRect).boundingRect().height()
    # end def

    ### TOOL METHODS ###
    def hoverMoveEvent(self, event):
        """
        Parses a mouseMoveEvent to extract strandSet and base index,
        forwarding them to approproate tool method as necessary.
        """
        activeTool = self._activeTool()
        toolMethodName = str(activeTool) + "HoverMove"
        if hasattr(self, toolMethodName):
            getattr(self, toolMethodName)(event.pos())
    # end def

    def pencilToolHoverMove(self, pt):
        """Pencil the strand is possible."""
        partItem = self
        activeTool = self._activeTool()
        if not activeTool.isFloatingXoverBegin():
            tempXover = activeTool.floatingXover()
            tempXover.updateFloatingFromPartItem(self, pt)
    # end def
