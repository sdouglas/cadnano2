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

from controllers.itemcontrollers.partitemcontroller import PartItemController
from virtualhelixitem import VirtualHelixItem

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
        super(PartItem, self).__init__(parent)
        self._modelPart = modelPart
        self._virtualHelixHash = {}
        self._virtualHelixList = []
        self._activeTool = activeTool
        self._activeSliceItem = ActiveSliceItem(self, modelPart.activeBaseIndex())
        self._controller = PartItemController(self, modelPart)
        self._vhiHSelectionGroup = SelectionItemGroup(\
                                                 boxtype=PathHelixHandleSelectionBox,\
                                                 constraint='y',\
                                                 parent=self)
        self._selectionLock = None
        self._vHRect = QRectF()
    # end def
        
    ### SIGNALS ###

    ### SLOTS ###
    def parentChangedSlot(self):
        """docstring for partParentChangedSlot"""
        print "PartItem.partParentChangedSlot"
        pass

    def removedSlot(self):
        """docstring for partDestroyedSlot"""
        self._activeSliceItem.removed()
        self.parentItem().removePartItem(self)
        scene = self.scene()
        scene.removeItem(self)
        self._modelPart = None
        self._virtualHelixHash = None
        self._virtualHelixList = None
        self._controller.disconnectSignals()
        self._controller = None
    # end def

    def destroyedSlot(self):
        """docstring for partDestroyedSlot"""
        print "PartItem.partDestroyedSlot"
        pass

    def movedSlot(self, pos):
        """docstring for partMovedSlot"""
        print "PartItem.partMovedSlot"
        pass

    def virtualHelixAddedSlot(self, modelVirtualHelix):
        """
        When a virtual helix is added to the model, this slot handles
        the instantiation of a virtualhelix item.
        """
        # print "PartItem.virtualHelixAddedSlot"
        vh = modelVirtualHelix
        vhi = VirtualHelixItem(self, modelVirtualHelix, self._activeTool)
        vhi.setPos
        self._virtualHelixHash[vh.coords()] = vhi
        self._virtualHelixList.append(vhi)
        self._setVirtualHelixItemList(self._virtualHelixList)
    # end def

    def updatePreXOverHandlesSlot(self, virtualHelix):
        if self.activeVirtualHelix().isNeighbor(virtualHelix):
            self.setPreXOverHandlesVisible(self.activeVirtualHelix)
    # end def
    
    def xover3pCreatedSlot(self, strand, idx):
        """docstring for xover3pCreatedSlot"""
        print "PartItem.xover3pCreatedSlot"
        pass

    def xover3pDestroyedSlot(self, strand, idx):
        """docstring for xover3pDestroyedSlot"""
        print "PartItem.xover3pDestroyedSlot"
        pass


    ### METHODS ###
    def part(self):
        """Return a reference to the model's part object"""
        return self._modelPart
        
    def removeVirtualHelix(self, virtualHelix):
        self._virtualHelixItemList.remove(virtualHelix)
        self._setVirtualHelixItemList(self._virtualHelixList)
    # end

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
            # self.updatePreXOverHandles()
        # end for
        self._vHRect = QRectF(leftmostExtent,\
                           -40,\
                           -leftmostExtent + rightmostExtent,\
                           y + 40)
        self._virtualHelixItemList = newList
        if zoomToFit:
            self.scene().views()[0].zoomToFit()
    # end def
    
    def virtualHelixBoundingRect(self):
        return self._vHRect
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
    
    def activeVirtualHelixItem(self):
        return self._activeVirtualHelixItem
    
    def setActiveVirtualHelixItem(self, newActiveVHI):
        if newActiveVHI != self._activeVirtualHelixItem:
            self._modelPart.setActiveVirtualHelix(newActiveVHI.virtualHelix())
            self.setPreXOverHandlesVisible(newActiveVHI, True)
    # end def
    
    def numberOfVirtualHelices(self):
        return len(self._virtualHelixList)
    # end def
    
    def vhiHandleSelectionGroup(self):
        return self._vhiHSelectionGroup
    # end def
    
    def selectionLock(self):
        return self._selectionLock
    # end def
    
    def setSelectionLock(self, locker):
        self._selectionLock = locker
    # end def
    
    def preXOverHandlesVisible(self):
        return self._preXOverHandles != None
    # end def
    
    def setPreXOverHandlesVisible(self, virtualHelixItem, shouldBeVisible):
        """
        self._preXoverHandles list references prexovers parented to other
        PathHelices such that only the activeHelix maintains the list of
        visible prexovers
        
        A possible more efficient solution is to maintain the list _preXoverHandles
        in pathhelixgroup, in fact this method should live in pathhelixgroup
        """
        vhi = virtualHelixItem
        if vhi == None:
            return
        # end if
        areVisible = self._preXOverHandles != None
        vh = vhi.virtualHelix()
        partItem = self
        part = self.part()
        
        # clear visible PCHs
        # for pch in self._preXOverHandles:
        #     if pch.scene():
        #         pch.scene().removeItem(pch)
        if areVisible:
            map(lambda pch: pch.remove() if pch.scene() else None, self._preXOverHandles)

            self._preXOverHandles = None

        if shouldBeVisible:
            self._preXOverHandles = []
            for strandType, facingRight in \
                    product(('vStrandScaf', 'vStrandStap'), (True, False)):
                # Get potential crossovers in (fromVBase, toVBase) format
                potentialXOvers = vh.potentialCrossoverList(facingRight, getattr(vh,strandType)())
                numBases = vh.numBases()
                # assert(all(index < numBases for neighborVH, index in potentialXOvers))
                
                for (fromVBase, toVBase) in potentialXOvers:
                    # create one half
                    pch = PreXoverItem(ph, fromVBase, toVBase, not facingRight)
                    # add to list
                    self._preXOverHandles.append(pch)
                    # create the complement
                    otherPH = phg.pathHelixForVHelix(toVBase.vHelix())
                    pch = PreXoverItem(otherPH, toVBase, fromVBase, not facingRight)
                    # add to list
                    self._preXOverHandles.append(pch)
                # end for
            # end for
        self._XOverCacheEnvironment = (vh.neighbors(), vh.numBases())
    # end def

    def updatePreXOverHandles(self):
        cacheConstructionEnvironment = self._XOverCacheEnvironment
        vhi = self.activeVirtualHelixItem()
        if vhi == None:
            return
        vh = vhi.virtualHelix()
        currentEnvironment = (vh.neighbors(), vh.numBases())
        if cacheConstructionEnvironment != currentEnvironment and\
           self.preXOverHandlesVisible():
            self.setPreXOverHandlesVisible(vhi, False)
            self.setPreXOverHandlesVisible(vhi, True)
    # end def
