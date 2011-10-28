# Copyright 2011 Autodesk, Inc.  All rights reserved.
#
# The MIT License
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
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#
# http://www.opensource.org/licenses/mit-license.php

"""
partitem.py

Created by Nick Conway on 2011-02-04.
Re-Created by Simon Breslav on 2011-07-21

For use controlling 3D solid models generated in Maya
"""

from string import *
import math
import random
import os
import sys
from views import styles
from model.enum import LatticeType
from model.enum import StrandType
from model.virtualhelix import VirtualHelix

import maya.OpenMayaUI as mui
import maya.OpenMaya as mo
import maya.cmds as cmds
import util

from controllers.mayacontrollers.mayaObjectManager import Mom
from controllers.itemcontrollers.partitemcontroller import PartItemController
from virtualhelixitem import VirtualHelixItem

# import Qt stuff into the module namespace with PySide, PyQt4 independence
util.qtWrapImport('QtCore', globals(), ['pyqtSignal', 'pyqtSlot', 'QObject'])


class PartItem(object):
    """
    Maya Based View: PartItem stores VirtualHelixItems for a given DNA Part
    For now parent should be a rootItem but in the future it could be
    an AssemblyItem
    """
    def __init__(self, modelPart, parent=None):
        """
        """
        self._parentItem = parent
        pluginPath = os.path.join(os.environ['CADNANO_PATH'],
                                  "views",
                                  "solidview")
        hchPath = os.path.join(pluginPath, "halfcylinderhelixnode.py")
        smiPath = os.path.join(pluginPath, "predecoratornode.py")

        if(not cmds.pluginInfo(hchPath, query=True, loaded=True)):
            cmds.loadPlugin(hchPath)

        if(not cmds.pluginInfo(smiPath, query=True, loaded=True)):
            cmds.loadPlugin(smiPath)

        if(not cmds.pluginInfo(hchPath, query=True, loaded=True)):
            print "HalfCylinderHelixNode failed to load"
            return

        #print "maya PartItem created"
        self._type = modelPart.crossSectionType()

        #self.mayaScale = 1.0
        #later updates using basecount from the VH
        # XXX [SB] - need to ask CandNano for rows and cols...
        # top left cornder of maya 3d scene X Y Z
        self.mayaOrigin = (-15 * 2.25, 16 * 2.25, 0.0)
        self.helixRadius = 1.125  # diamiter is 2.25nm
        self._virtualHelixItems = {}

        self._part = modelPart
        self._controller = PartItemController(self, modelPart)

        self.modifyState = False
    # end def
    
    def parentItem(self):
        return self._parentItem
    # end def

    def setModifyState(self, val):
        self.modifyState = val
        self.updateModifyState()
    # end def

    def updateModifyState(self):
        for sh in self.virtualHelixItems:
            sh.setModifyState(self.modifyState)
            sh.updateDecorators()
    # end def

    def isInModifyState(self):
        return self.modifyState
    # end def

    def type(self):
        return self._type
    # end def

    def part(self):
        return self._part
    # end def

    def setPart(self, p):
        self._part = p
    # end def

    ### SLOTS ###
    def partDestroyedSlot(self, part):
        """solidview.PartItem partDestroyedSlot"""
        pass
    # end def

    def partDimensionsChangedSlot(self, part):
        pass
    # end def

    def partParentChangedSlot(self, part):
        """solidview.PartItem partParentChangedSlot"""
        #print "solidview.PartItem.partParentChangedSlot"
        pass
    # end def

    def partRemovedSlot(self, part):
        """solidview.PartItem partRemovedSlot"""
        # print "solidview.PartItem.partRemovedSlot"
        self._virtualHelixItems = None
        self._parentItem.removePartItem(self)
        self._parentItem = None
        self._part = None
        self._controller.disconnectSignals()
        self._controller = None
    # end def

    def partPreDecoratorSelectedSlot(self, row, col, baseIdx):
        pass
    # end def

    def partVirtualHelixAddedSlot(self, virtualHelix):
        #print "solidview.PartItem.partVirtualHelixAddedSlot"
        sh = self.createNewVirtualHelixItem(virtualHelix)
        sh.setModifyState(self.modifyState)
    # end def

    @pyqtSlot(tuple)
    def partVirtualHelixRenumberedSlot(self, coord):
        pass
    # end def

    @pyqtSlot(tuple)
    def partVirtualHelixResizedSlot(self, coord):
        pass
    # end def

    @pyqtSlot(list)
    def partVirtualHelicesReorderedSlot(self, orderedCoordList):
        pass
    # end def

    def updatePreXoverItemsSlot(self, virtualHelix):
        #print "solidview.PartItem.updatePreXoverItemsSlot"
        pass
    # end def

    ### METHODS ###
    def cadnanoToMayaCoords(self, row, col):
        """
        """
        x, y = self.part().latticeCoordToPositionXY(row, col)
        return x + self.mayaOrigin[0], self.mayaOrigin[1] - y
    # end def

    def clearInternalDataStructures(self):
        self._virtualHelixItems = {}
        self.idStrandMapping.clear()
        self.strandCount = 0
    # end def

    def deleteAllNodes(self):
        m = Mom()
        # Delete Helicies in this group
        for vhelixItem in self.virtualHelixItems:
            strandIDs = vhelixItem.StrandIDs()
            for mID in strandIDs:
                transformName = "%s%s" % (m.helixTransformName, mID)
                if cmds.objExists(transformName):
                    cmds.delete(transformName)
        self.clearInternalDataStructures()
    # end def

    def createNewVirtualHelixItem(self, virtualHelix):
        coords = virtualHelix.coord()
        #print "solidview.PartItem.createNewVirtualHelixItem: %d %d" % \
        #                                                (coords[0], coords[1])
        # figure out Maya Coordinates
        x, y = self.cadnanoToMayaCoords(coords[0], coords[1])
        #print virtualHelix
        newHelix = VirtualHelixItem(self, virtualHelix, x, y)
        self._virtualHelixItems[newHelix] = True
        return newHelix
    # end def

    def removeVirtualHelixItem(self, vhelixItem):
        del self._virtualHelixItems[vhelixItem]
    # end def
# end class
