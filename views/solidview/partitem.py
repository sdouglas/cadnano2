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


class PartItem(QObject):
    """
    Maya Based View: PartItem stores VirtualHelixItems for a given DNA Part
    """
    def __init__(self, modelPart, parent=None):
        """
        """
        super(PartItem, self).__init__()
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
        self.virtualHelixItems = []

        self._part = modelPart
        self._controller = PartItemController(self, modelPart)

        self.modifyState = False

    def setModifyState(self, val):
        self.modifyState = val
        for sh in self.virtualHelixItems:
            sh.upadateStapleModIndicators(val)

    def isInModifyState(self):
        return self.modifyState

    def type(self):
        return self._type

    def part(self):
        # part
        return self._part

    def setPart(self, p):
        self._part = p

    ### SLOTS ###

    @pyqtSlot()
    def parentChangedSlot(self):
        """solidview.PartItem parentChangedSlot"""
        print "solidview.PartItem.parentChangedSlot"
        pass

    @pyqtSlot()
    def removedSlot(self):
        """solidview.PartItem removedSlot"""
        print "solidview.PartItem.removedSlot"
        self._part = None
        self._controller.disconnectSignals()
        self._controller = None

    @pyqtSlot()
    def destroyedSlot(self):
        """solidview.PartItem destroyedSlot"""
        print "solidview.PartItem.destroyedSlot"
        pass

    @pyqtSlot(int)
    def movedSlot(self, pos):
        """solidviw.PartItem partMovedSlot"""
        print "solidview.PartItem.movedSlot"
        pass

    # @pyqtSlot(QObject, QObject, int, int, QObject, int, int)
    # def xoverAddedSlot(self, part, virtualHelix3p, strandType3p, idx3p, \
    #                                 virtualHelix5p, strandType5p, idx5p):
    #     """docstring for xover3pAddedSlot"""
    #     print "solidview.PartItem.xover3pAddedSlot"
    #     pass
    # 
    # @pyqtSlot(QObject, QObject, int, int, QObject, int, int)
    # def xoverRemovedSlot(self, part, virtualHelix3p, strandType3p, idx3p, \
    #                                 virtualHelix5p, strandType5p, idx5p):
    #     """docstring for xover3pDestroyedSlot"""
    #     print "solidview.PartItem.xover3pDestroyedSlot"
    #     pass

    @pyqtSlot(object)
    def virtualHelixAddedSlot(self, virtualHelix):
        print "solidview.PartItem.virtualHelixAddedSlot"
        self.createNewVirtualHelixItem(virtualHelix)

    @pyqtSlot(object)
    def updatePreXoverItemsSlot(self, virtualHelix):
        print "solidview.PartItem.updatePreXoverItemsSlot"

    ### METHODS ###
    def cadnanoToMayaCoords(self, row, col):
        # XXX - [SB] This should go away and we will ask the model for
        # the position
        if self._type == LatticeType.Honeycomb:
            #print "LatticeType.Honeycomb"
            x = self.mayaOrigin[0] + (col * math.sqrt(3) * self.helixRadius)
            if ((row % 2) ^ (col % 2)):  # odd parity
                y = self.mayaOrigin[1] - (row * self.helixRadius * 3.0 +
                                          self.helixRadius)
            else:
                y = self.mayaOrigin[1] - (row * self.helixRadius * 3.0)
        # end if
        elif self._type == LatticeType.Square:
            #print "LatticeType.Square"
            x = self.mayaOrigin[0] + (col * 2.0 * self.helixRadius)
            y = self.mayaOrigin[1] - (row * 2.0 * self.helixRadius)
        return (x, y)

    def clearInternalDataStructures(self):
        self.virtualHelixItems = []
        self.idStrandMapping.clear()
        self.strandCount = 0

    def deleteAllNodes(self):
        m = Mom()
        # Delete Helicies in this group
        for vhelixItem in self.virtualHelixItems:
            strandIDs = vhelixItem.StrandIDs()
            for id in strandIDs:
                transformName ="%s%s" % (m.helixTransformName, id)
                if cmds.objExists(transformName):
                    cmds.delete(transformName)
        self.clearInternalDataStructures()

    def createNewVirtualHelixItem(self, virtualHelix):
        coords = virtualHelix.coords()
        print "solidview.PartItem.createNewVirtualHelixItem: %d %d" % (coords[0], coords[1])
        # figure out Maya Coordinates
        x, y = self.cadnanoToMayaCoords(coords[0], coords[1])
        print virtualHelix
        newHelix = VirtualHelixItem(self, virtualHelix, x, y)
        self.virtualHelixItems.append(newHelix)

    def removeVirtualHelix(self, vhelixItem):
        self.virtualHelixItems.remove(vhelixItem)

