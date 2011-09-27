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
solidhelixgroup.py

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

import maya.OpenMayaUI as mui
import maya.OpenMaya as mo
import maya.cmds as cmds
import util

from solidhelix import SolidHelix

# import Qt stuff into the module namespace with PySide, PyQt4 independence
util.qtWrapImport('QtCore', globals(), ['pyqtSignal', 'pyqtSlot', 'QObject'])


class SolidHelixGroup(QObject):
    """
    A Solid Hinstance is meant to store helix data in Maya
    representing a pathhelixgroup.
    """
    def __init__(self, dnaPartInst, htype=LatticeType.Honeycomb,
                 controller=None, parent=None):
        """
        """
        super(SolidHelixGroup, self).__init__()
        pluginPath = os.path.join(os.environ['CADNANO_PATH'],
                                  "views",
                                  "solidview")
        hchPath = os.path.join(pluginPath, "halfcylinderhelixnode.py")
        smiPath = os.path.join(pluginPath, "stapleModIndicator.py")

        if(not cmds.pluginInfo(hchPath, query=True, loaded=True)):
            cmds.loadPlugin(hchPath)
            
        if(not cmds.pluginInfo(smiPath, query=True, loaded=True)):
            cmds.loadPlugin(smiPath)

        if(not cmds.pluginInfo(hchPath, query=True, loaded=True)):
            print "HalfCylinderHelixNode failed to load"
            return

        #print "maya SolidHelixGroup created"
        self._type = htype
        self._part = None
        #self.mayaScale = 1.0
        #later updates using basecount from the VH
        # XXX [SB] - need to ask CandNano for rows and cols...
        # top left cornder of maya 3d scene X Y Z
        self.mayaOrigin = (-15 * 2.25, 16 * 2.25, 0.0)
        self.helixRadius = 1.125  # diamiter is 2.25nm
        self.solidHelixes = []
        self.setPart(dnaPartInst)
        self.strandCount = 0
        # uses strand object as the key, stores stand id
        self.idStrandMapping = {}
        self.modifyState = False

    def setModifyState(self, val):
        self.modifyState = val
        for sh in self.solidHelixes:
            sh.upadateStapleModIndicators(val)

    def isInModifyState(self):
        return self.modifyState

    def strandMayaID(self, strand):
        if(strand in self.idStrandMapping):
            return self.idStrandMapping[strand]
        else:
            # XXX [SB+AT] NOT THREAD SAFE
            while cmds.objExists("DNAShapeTransform%s" % self.strandCount):
                self.strandCount += 1
            val = "%d" % self.strandCount
            self.idStrandMapping[strand] = val
            return val

    def deleteStrandMayaID(self, strand):
        del self.idStrandMapping[strand]

    def type(self):
        return self._type

    def part(self):
        # part
        return self._part

    def setPart(self, p):
        if self._part:
            self._part.dimensionsDidChange.disconnect(
                                        self.partDimensionsChanged)
            self._part.virtualHelixAtCoordsChanged.disconnect(
                                        self.onVirtualHelixAtCoordsChanged)
            self._past.activeSliceWillChange.disconnect(self.onActiveSliceWillChange)
        self._part = p
        if p != None:
            p.dimensionsDidChange.connect(self.partDimensionsChanged)
            p.virtualHelixAtCoordsChanged.connect(
                                        self.onVirtualHelixAtCoordsChanged)
            p.activeSliceWillChange.connect(self.onActiveSliceWillChange)

    @pyqtSlot()
    def partDimensionsChanged(self):
        #print "SolidHelixGroup:partDimensionsChanged"
        pass

    @pyqtSlot(object)
    def onActiveSliceWillChange(self, list):
        print "onSelectionWillChange"
        print list

    @pyqtSlot(int, int)
    def onVirtualHelixAtCoordsChanged(self, row, col):
        self.createNewHelix(row, col)

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
        self.solidHelixes = []
        self.idStrandMapping.clear()
        self.strandCount = 0

    def deleteAllNodes(self):
        # Delete Helicies in this group
        for solidhelix in self.solidHelixes:
            strandIDs = solidhelix.StrandIDs()
            for id in strandIDs:
                transformName = "DNAShapeTransform%s" % id
                if cmds.objExists(transformName):
                    cmds.delete(transformName)
        self.clearInternalDataStructures()

    def createNewHelix(self, row, col):
        #print "SolidHelixGroup.createNewHelix: %d %d" % (row, col)
        # figure out Maya Coordinates
        x, y = self.cadnanoToMayaCoords(row, col)
        vhelix = self._part.getVirtualHelix((row, col))
        newHelix = SolidHelix(vhelix, self, x, y)
        self.solidHelixes.append(newHelix)
