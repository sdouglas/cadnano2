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
from views import styles

from controllers.itemcontrollers.partitemcontroller import PartItemController
from virtualhelixitem import VirtualHelixItem
from prexoveritem import PreXoverItem

from .pathselection import SelectionItemGroup
from .pathselection import PathHelixHandleSelectionBox
from .pathselection import BreakpointHandleSelectionBox
from activesliceitem import ActiveSliceItem

import util
# import Qt stuff into the module namespace with PySide, PyQt4 independence
util.qtWrapImport('QtCore', globals(), ['pyqtSignal', 'QObject', 'QRectF'])
util.qtWrapImport('QtGui', globals(), ['QUndoCommand', 'QUndoStack',
                                       'QGraphicsPathItem'])

class PartItem(QGraphicsPathItem):
    def __init__(self, modelPart, activeTool, parent):
        """parent should always be pathrootitem"""
        super(PartItem, self).__init__(parent)
        self._modelPart = modelPart
        self._activeTool = activeTool
        self._activeSliceItem = ActiveSliceItem(self, modelPart.activeBaseIndex())
        self._activeVirtualHelixItem = None
        self._controller = PartItemController(self, modelPart)
        self._virtualHelixHash = {}
        self._virtualHelixItemList = []
        self._vHRect = QRectF()
        # crossover-related
        self._preXoverItems = []
        self._xoverItems = defaultdict(dict)  # key: [coord][idx,strandtype]
        # selection-related
        self._selectionLock = None
        self._vhiHSelectionGroup = SelectionItemGroup(\
                                         boxtype=PathHelixHandleSelectionBox,\
                                         constraint='y',\
                                         parent=self)
    # end def

    ### SIGNALS ###

    ### SLOTS ###
    def parentChangedSlot(self):
        """docstring for partParentChangedSlot"""
        # print "PartItem.partParentChangedSlot"
        pass
    # end def

    def removedSlot(self):
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

    def destroyedSlot(self):
        """docstring for partDestroyedSlot"""
        # print "PartItem.partDestroyedSlot"
        pass
    # end def

    def movedSlot(self, pos):
        """docstring for partMovedSlot"""
        # print "PartItem.partMovedSlot"
        pass
    # end def

    def virtualHelixAddedSlot(self, modelVirtualHelix):
        """
        When a virtual helix is added to the model, this slot handles
        the instantiation of a virtualhelix item.
        """
        # print "PartItem.virtualHelixAddedSlot"
        vh = modelVirtualHelix
        vhi = VirtualHelixItem(self, modelVirtualHelix, self._activeTool)
        vhi.setPos
        self._virtualHelixHash[vh.coord()] = vhi
        self._virtualHelixItemList.append(vhi)
        self._setVirtualHelixItemList(self._virtualHelixItemList)
    # end def

    def updatePreXoverItemsSlot(self, virtualHelix):
        part = self.part()
        if part.areVirtualHelicesNeighbors(part.activeVirtualHelix(), virtualHelix):
            vhi = self.itemForVirtualHelix(virtualHelix)
            self.setActiveVirtualHelixItem(vhi)
            self.setPreXoverItemsVisible(self.activeVirtualHelixItem())
    # end def

    # def xoverAddedSlot(self, part, virtualHelix3p, strandType3p, idx3p, \
    #                                 virtualHelix5p, strandType5p, idx5p):
    #     """docstring for xover3pAddedSlot"""
    #     print "PartItem.xover3pAddedSlot"
    #     pass

    # def xoverRemovedSlot(self, part, virtualHelix3p, strandType3p, idx3p, \
    #                                 virtualHelix5p, strandType5p, idx5p):
    #     """docstring for xover3pDestroyedSlot"""
    #     print "PartItem.xover3pDestroyedSlot"
    #     pass

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
    # end

    def itemForVirtualHelix(self, virtualHelix):
        return self._virtualHelixHash[virtualHelix.coord()]


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

    ### PUBLIC METHODS ###

    def numberOfVirtualHelices(self):
        return len(self._virtualHelixItemList)
    # end def
    
    def addXoverItem(self, xoverItem):
        # use xoverItems twice! once for each end of the xover
        vhi3p, vhi5p = xoverItem.virtualHelixItems()
        iAST3P, iAST5P = xoverItem.indicesAndStrandTypes()
        self._xoverItems[vhi3p.coord()][iAST3P] = xoverItem
        self._xoverItems[vhi5p.coord()][iAST5P] = xoverItem
    # end def

    def removeXoverItem(self, xoverItem):
        # use xoverItems twice! once for each end of the xover
        vhi3p, vhi5p = xoverItem.virtualHelixItems()
        iAST3P, iAST5P = xoverItem.indicesAndStrandTypes()
        del self._xoverItems[vhi3p.coord()][iAST3P]
        del self._xoverItems[vhi5p.coord()][iAST5P]
    # end def

    def updateXoverItems(self, virtualHelixItem):
         coord = virtualHelixItem.coord()
         for xoveritem in self._xoverItems[coord].itervalues():
             xoveritem.updatePath()
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

    ### COORDINATE METHODS ###
    def keyPanDeltaX(self):
        """How far a single press of the left or right arrow key should move
        the scene (in scene space)"""
        vhs = self._virtualHelixItemList
        return vhs[0].keyPanDeltaX() if vhs else 5

    def keyPanDeltaY(self):
        """How far an an arrow key should move the scene (in scene space)
        for a single press"""
        vhs = self._virtualHelixItemList
        if not len(vhs) > 1:
            return 5
        dy = vhs[0].pos().y() - vhs[1].pos().y()
        dummyRect = QRectF(0, 0, 1, dy)
        return self.mapToScene(dummyRect).boundingRect().height()

