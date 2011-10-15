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

from string import *
import math
import random
import os
import sys
from views import styles
from model.enum import LatticeType
from model.enum import StrandType
from model.virtualhelix import VirtualHelix
#from model.strands.normalstrand import NormalStrand
#from model.strands.xoverstrand import XoverStrand3, XoverStrand5

from controllers.mayacontrollers.mayaObjectManager import Mom
from controllers.itemcontrollers.virtualhelixitemcontroller \
                                            import VirtualHelixItemController

import maya.OpenMayaUI as mui
import maya.OpenMaya as mo
import maya.cmds as cmds
import util

from .stranditem import StrandItem

# import Qt stuff into the module namespace with PySide, PyQt4 independence
util.qtWrapImport('QtCore', globals(), ['pyqtSignal', 'pyqtSlot', 'QObject'])
util.qtWrapImport('QtGui', globals(), ['QColor'])

"""
virtualhelixitem.py
Created by Simon Breslav on 2011-08-29.
"""


class VirtualHelixItem(QObject):
    """
    VirtualHelixItem is the 3D visualization of VirtualHelix, it contains
    strandItems
    """
    baseWidth = styles.PATH_BASE_WIDTH

    def __init__(self, partItem, modelVirtualHelix, x, y):
        super(VirtualHelixItem, self).__init__()
        self._partItem = partItem
        self._vhelix = modelVirtualHelix
        self._x = x
        self._y = y
        coords = modelVirtualHelix.coord()
        self._row = coords[0]
        self._col = coords[1]
        self.strandIDs = []
        self._modState = False

        self.stapleIndicatorCount = 0
        self.stapleModIndicatorIDs = []

        self._controller = VirtualHelixItemController(self, modelVirtualHelix)

    def partItem(self):
        return self._partItem

    def vhelix(self):
        return self._vhelix

    def setVHelix(self, newVH):
        self._vhelix = newVH

    def number(self):
        return self._vhelix.number()

    def row(self):
        return self._row

    def col(self):
        return self._col

    def x(self):
        return self._x

    def y(self):
        return self._y

    def isEvenParity(self):
        return self._vhelix.isEvenParity()

    def StrandIDs(self):
        return self.strandIDs

    def setModifyState(self, val):
        self._modState = val

    ### SLOTS ###
    @pyqtSlot(object)
    def strandAddedSlot(self, strand):
        """
        Instantiates a StrandItem upon notification that the model has a
        new Strand.  The StrandItem is responsible for creating its own
        controller for communication with the model, and for adding itself to
        its parent (which is *this* VirtualHelixItem, i.e. 'self').
        """
        #print "solidview.VirtualHelixItem.strandAddedSlot"
        #strand.didMove.connect(self.onStrandDidMove)
        #strand.willBeRemoved.connect(self.onStrandWillBeRemoved)
        m = Mom()
        id = m.strandMayaID(strand)
        self.strandIDs.append(id)
        StrandItem(id, strand, self)
        self.updateDecorators()
        #print "solidview.VirtualHelixItem.strandAddedSlot done %s" % id
    # end def

    @pyqtSlot(object)
    def decoratorAddedSlot(self, decorator):
        """
        Instantiates a DecoratorItem upon notification that the model has a
        new Decorator.  The Decorator is responsible for creating its own
        controller for communication with the model, and for adding itself to
        its parent (which is *this* VirtualHelixItem, i.e. 'self').
        """
        #print "solidview.VirtualHelixItem.decoratorAddedSlot"
        pass

    @pyqtSlot(object)
    def virtualHelixNumberChangedSlot(self, virtualHelix):
        print "solidview.VirtualHelixItem.virtualHelixNumberChangedSlot"
        pass
    # end def

    @pyqtSlot(object)
    def virtualHelixRemovedSlot(self, virtualHelix):
        #print "solidview.VirtualHelixItem.virtualHelixRemovedSlot"
        self._partItem.removeVirtualHelix(self)
        self._partItem = None
        self._modelVirtualHelix = None
        self._controller.disconnectSignals()
        self._controller = None
    # end def

    def updateDecorators(self):
        #print "solidview.VirtualHelixItem.upadateStapleModIndicators"
        self.clearDecorators()
        if self._modState:
            m = Mom()
            for id in self.strandIDs:
                mayaNodeInfo = "%s%s" % (m.helixMeshName, id)
                #print "mayaNodeInfo: %s" % mayaNodeInfo
                strand = m.mayaToCn[mayaNodeInfo]
                if(strand.strandSet().isStaple()):
                    self.createDecorators(strand)

    def cadnanoVBaseToMayaCoords(self, base, strand):
        m = Mom()
        id = m.strandMayaID(strand)
        cylinderName = "%s%s" % (m.helixNodeName, id)
        if cmds.objExists(cylinderName):
            rise = cmds.getAttr("%s.rise" % cylinderName)
            startBase = cmds.getAttr("%s.startBase" % cylinderName)
            startPos = cmds.getAttr("%s.startPos" % cylinderName)
            base0Pos = startPos[0][1] + startBase * rise
            ourPos = base0Pos - (base * rise)
            zComp = ourPos

            rotation = cmds.getAttr("%s.rotation" % cylinderName)
            radius = cmds.getAttr("%s.radius" % cylinderName)
            parity = cmds.getAttr("%s.parity" % cylinderName)
            strandType = cmds.getAttr("%s.strandType" % cylinderName)
            rotationOffset = cmds.getAttr("%s.rotationOffset" % cylinderName)
            starting_rotation = (math.pi * (not parity)) + rotationOffset + \
                                (math.pi * strandType)
            fullrotation = -rotation * base * math.pi / 180
            #print fullrotation
            xComp = self._x + radius * \
                    math.cos(starting_rotation + fullrotation)
            yComp = self._y + radius * \
                    math.sin(starting_rotation + fullrotation)
            #print "%f %f %f" % (xComp, yComp, zComp)
            return (xComp, yComp, zComp)
        else:
            raise IndexError

    def clearDecorators(self):
        m = Mom()
        for id in self.stapleModIndicatorIDs:
            transformName = "%s%s" % (m.decoratorTransformName, id)
            #print "delete %s" % transformName
            m = Mom()
            m.removeDecoratorMapping(id)
            if cmds.objExists(transformName):
                cmds.delete(transformName)
        self.stapleModIndicatorIDs = []
        self.stapleIndicatorCount = 0

    def createDecorators(self, strand):
        #print "createStapleModIndicator"
        m = Mom()
        strandid = m.strandMayaID(strand)
        # XXX [SB] will use self._vhelix.getPreStapleModIndexList()
        totalNumBases = self._vhelix.part().maxBaseIdx()
        stapleBases = strand.getPreDecoratorIdxList()
        #for b in range(totalNumBases):
        #    stapleBases.append(b)

        for stapleBase in stapleBases:
            # XXX [SB+AT] NOT THREAD SAFE
            while cmds.objExists("%s%s_%s" % (m.decoratorNodeName,
                                              strandid,
                                              self.stapleIndicatorCount)):
                self.stapleIndicatorCount += 1
            stapleId = "%s_%s" % (strandid, self.stapleIndicatorCount)
            coords = self.cadnanoVBaseToMayaCoords(stapleBase, strand)
            stapleModNodeInfo = self.createDecoratorNodes(coords, stapleId)
            self.stapleModIndicatorIDs.append(stapleId)
            m = Mom()
            m.decoratorToVirtualHelixItem[stapleModNodeInfo[2]] = (self,
                                                                   stapleBase,
                                                                   strand)
            m.decoratorToVirtualHelixItem[stapleModNodeInfo[1]] = (self,
                                                                   stapleBase,
                                                                   strand)

    def createDecoratorNodes(self, coords, id):
        m = Mom()
        stapleModIndicatorName = "%s%s" % (m.decoratorNodeName, id)
        transformName = "%s%s" % (m.decoratorTransformName, id)
        meshName = "%s%s" % (m.decoratorMeshName, id)
        shaderName = "%s" % m.decoratorShaderName

        cmds.createNode("transform", name=transformName)
        cmds.setAttr("%s.rotateX" % transformName, 90)
        cmds.setAttr("%s.translateX" % transformName, coords[0])
        cmds.setAttr("%s.translateY" % transformName, coords[1])
        cmds.setAttr("%s.translateZ" % transformName, coords[2])
        cmds.createNode("mesh", name=meshName, parent=transformName)
        cmds.createNode("spPreDecoratorNode", name=stapleModIndicatorName)
        cmds.setAttr("%s.radius" % stapleModIndicatorName, .25)
        cmds.connectAttr("%s.outputMesh" % stapleModIndicatorName,
                         "%s.inMesh" % meshName)

        if not cmds.objExists(shaderName):
            # Shader does not exist create one
            cmds.shadingNode('lambert', asShader=True, name=shaderName)
            cmds.sets(n="%sSG" % shaderName, r=True, nss=True, em=True)
            cmds.connectAttr("%s.outColor" % shaderName,
                             "%sSG.surfaceShader" % shaderName)
            cmds.setAttr("%s.color" % shaderName,
                         0.85, 0.2, 0.2,
                         type="double3")
            cmds.sets(meshName, forceElement="%sSG" % shaderName)
        else:
            #shader exist connect
            cmds.sets(meshName, forceElement="%sSG" % shaderName)
        return (stapleModIndicatorName, transformName, meshName, shaderName)
