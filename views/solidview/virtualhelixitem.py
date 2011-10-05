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
#from model.strands.xoverstrand import XOverStrand3, XOverStrand5

from controllers.mayacontrollers.mayaObjectManager import Mom
from controllers.itemcontrollers.virtualhelixitemcontroller import VirtualHelixItemController

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
        coords = modelVirtualHelix.coords()
        self._row = coords[0]
        self._col = coords[1]
        self.strandIDs = []

        self.stapleIndicatorCount = 0
        self.stapleModIndicatorIDs = []
        
        self._controller = VirtualHelixItemController(self, modelVirtualHelix)

    def partItem(self):
        return self._partItem

    def vhelix(self):
        return self._vhelix

    def setVHelix(self, newVH):
        #vh = self._vhelix
        #if vh:
        #    vh.dimensionsModifiedSignal.disconnect(\
        #                                     self.vhelixDimensionsModified)
        #    vh.scaf().didAddStrand.disconnect(self.strandAddedToVStrand)
        #    vh.stap().didAddStrand.disconnect(self.strandAddedToVStrand)
        self._vhelix = newVH
      
        #newVH.dimensionsModifiedSignal.connect(self.vhelixDimensionsModified)
        #newVH.scaf().didAddStrand.connect(self.strandAddedToVStrand)
        #newVH.stap().didAddStrand.connect(self.strandAddedToVStrand)

    def number(self):
        return self._vhelix.number()

    def row(self):
        return self._vhelix.row()

    def col(self):
        return self._vhelix.col()
        
    def x(self):
        return self._x

    def y(self):
        return self._y

    def isEvenParity(self):
        return self._vhelix.isEvenParity()

    def StrandIDs(self):
        return self.strandIDs

    ### SLOTS ###
    @pyqtSlot(object)
    def strandAddedSlot(self, strand):
        """
        Instantiates a StrandItem upon notification that the model has a
        new Strand.  The StrandItem is responsible for creating its own
        controller for communication with the model, and for adding itself to
        its parent (which is *this* VirtualHelixItem, i.e. 'self').
        """
        print "solidview.VirtualHelixItem.strandAddedSlot"
        print strand
        #strand.didMove.connect(self.onStrandDidMove)
        #strand.willBeRemoved.connect(self.onStrandWillBeRemoved)
        id = self._partItem.strandMayaID(strand)
        self.strandIDs.append(id)
        #print "SolidHelix:strandAddedToVStrand-NormalStrand %s" % id
        StrandItem(id, strand, self)
    # end def

    @pyqtSlot(object)
    def decoratorAddedSlot(self, decorator):
        """
        Instantiates a DecoratorItem upon notification that the model has a
        new Decorator.  The Decorator is responsible for creating its own
        controller for communication with the model, and for adding itself to
        its parent (which is *this* VirtualHelixItem, i.e. 'self').
        """
        print "solidview.VirtualHelixItem.decoratorAddedSlot"
        pass

    @pyqtSlot(object)
    def virtualHelixNumberChangedSlot(self, virtualHelix):
        print "solidview.VirtualHelixItem.virtualHelixNumberChangedSlot"
        pass
    # end def

    @pyqtSlot(object)
    def virtualHelixRemovedSlot(self, virtualHelix):
        print "solidview.VirtualHelixItem.virtualHelixRemovedSlot"
        self._partItem.removeVirtualHelix(self)
        self._partItem = None
        self._modelVirtualHelix = None
        self._controller.disconnectSignals()
        self._controller = None
    # end def

    #old
    #@pyqtSlot(object)
    #def strandAddedToVStrand(self, strand):
    #    if isinstance(strand, NormalStrand):
    #        strand.didMove.connect(self.onStrandDidMove)
    #        strand.willBeRemoved.connect(self.onStrandWillBeRemoved)
    #        id = self._partItem.strandMayaID(strand)
    #        self.strandIDs.append(id)
    #        #print "SolidHelix:strandAddedToVStrand-NormalStrand %s" % id
    #        mayaNodeInfo = ()
    #        if(strand.vStrand().isScaf()):
    #            mayaNodeInfo = self.createMayaHelixNodes(self.x, self.y,
    #                                      strand.color(),
    #                                      StrandType.Scaffold,
    #                                      id)
    #        else:
    #            mayaNodeInfo = self.createMayaHelixNodes(self.x, self.y,
    #                                      strand.color(),
    #                                      StrandType.Staple,
    #                                      id)
    #        self.onStrandDidMove(strand)
    #        m = Mom()
    #        m.cnToMaya[ strand ] = mayaNodeInfo
    #        m.mayaToCn[ mayaNodeInfo[2] ] = strand
    #        m.mayaToCn[ mayaNodeInfo[0] ] = strand
    #    elif isinstance(strand, XOverStrand3):
    #        #print "SolidHelix:strandAddedToVStrand-XOverStrand3"
    #        pass
    #    elif isinstance(strand, XOverStrand5):
    #        #print "SolidHelix:strandAddedToVStrand-XOverStrand5"
    #        pass
    #    else:
    #        raise NotImplementedError
    #    if self.pathHelixGroup().isInModifyState():
    #        self.upadateStapleModIndicators(True)

    #@pyqtSlot(object)
    #def onStrandDidMove(self, strand):
    #    id = self._partItem.strandMayaID(strand)
    #    cylinderName = "HalfCylinderHelixNode%s" % id
    #    # XXX - [SB] why is there +1 in 2nd component of idxs?
    #    endpoints = strand.idxs()
    #    totalNumBases = self._vhelix.numBases()
    #    cmds.setAttr("%s.startBase" % cylinderName,
    #                         endpoints[0])
    #
    #    cmds.setAttr("%s.endBase" % cylinderName,
    #                         endpoints[1] - 1)
    #    cmds.setAttr("%s.totalBases" % cylinderName, int(totalNumBases))

    def upadateStapleModIndicators(self, on):
        self.clearStapleModIndicators()
        if on:
            m = Mom()
            for id in self.strandIDs:
                mayaNodeInfo = "DNACylinderShape%s" % id
                strand = m.mayaToCn[ mayaNodeInfo ]
                self.createStapleModIndicator(strand)

    #@pyqtSlot(object)
    #def onStrandWillBeRemoved(self, strand):
    #    id = self._partItem.strandMayaID(strand)
    #    strand.didMove.disconnect(self.onStrandDidMove)
    #    strand.willBeRemoved.disconnect(self.onStrandWillBeRemoved)
    #    #print "SolidHelix:onStrandWillBeRemoved %s" % id
    #    transformName = "DNAShapeTransform%s" % id
    #    mom = Mom()
    #    mom.removeIDMapping(id, strand)
    #    
    #    if cmds.objExists(transformName):
    #        cmds.delete(transformName)
    #    self.strandIDs.remove(id)
    #    self._partItem.deleteStrandMayaID(strand)
    #    #print strand
    #
    #@pyqtSlot()
    #def vhelixDimensionsModified(self):
    #    #print "SolidHelix:vhelixDimensionsModified"
    #    totalNumBases = self._vhelix.numBases()
    #    for strandID in self.strandIDs:
    #        cylinderName = "HalfCylinderHelixNode%s" % strandID
    #        cmds.setAttr("%s.totalBases" % cylinderName, int(totalNumBases))

    def cadnanoVBaseToMayaCoords(self, base, strand):
        id = self._partItem.strandMayaID(strand)
        cylinderName = "HalfCylinderHelixNode%s" % id
        if cmds.objExists(cylinderName):
            rise = cmds.getAttr("%s.rise" % cylinderName)
            startBase = cmds.getAttr("%s.startBase" % cylinderName)
            startPos = cmds.getAttr("%s.startPos" % cylinderName)
            base0Pos = startPos[0][1] + startBase*rise
            ourPos = base0Pos - (base*rise)
            zComp = ourPos#-rise*0.5 # center marker on the base
            
            rotation = cmds.getAttr("%s.rotation" % cylinderName)
            radius = cmds.getAttr("%s.radius" % cylinderName)
            parity = cmds.getAttr("%s.parity" % cylinderName)
            strandType = cmds.getAttr("%s.strandType" % cylinderName)
            rotationOffset = cmds.getAttr("%s.rotationOffset" % cylinderName)
            
            starting_rotation = (math.pi * (not parity)) + rotationOffset + \
                                (math.pi * strandType)
            
            fullrotation = -rotation * base * math.pi / 180
            #print fullrotation
            
            xComp = self._x + radius * math.cos(starting_rotation + fullrotation)
            yComp = self._y + radius * math.sin(starting_rotation + fullrotation)
            #print "%f %f %f" % (xComp, yComp, zComp)
            return (xComp, yComp, zComp)
            
        else:
            raise IndexError

    def clearStapleModIndicators(self):
        for id in self.stapleModIndicatorIDs:
            transformName = "stapleModIndicatorTransform%s" % id
            #print "delete %s" % transformName
            m = Mom()
            m.removeStapleModMapping(id)
            if cmds.objExists(transformName):
                cmds.delete(transformName)
        self.stapleModIndicatorIDs = []
        self.stapleIndicatorCount = 0

    def createStapleModIndicator(self, strand):
        #print "createStapleModIndicator"
        strandid = self._partItem.strandMayaID(strand)
        #mrow = self._row + 1
        #mcol = self._col + 1
        # XXX [SB] will use self._vhelix.getPreStapleModIndexList()
        totalNumBases = self._vhelix.numBases()
        stapleBases = []#[(0, mrow, mcol), (totalNumBases-1, mrow, mcol)]
        for b in range(totalNumBases):
            stapleBases.append(b)

        for stapleBase in stapleBases:
            # XXX [SB+AT] NOT THREAD SAFE
            while cmds.objExists("spStapleModIndicator%s_%s" % (strandid, self.stapleIndicatorCount)):
                self.stapleIndicatorCount += 1
            stapleId = "%s_%s" % (strandid, self.stapleIndicatorCount)
            #(targetX, targetY) = self.pathHelixGroup().cadnanoToMayaCoords(stapleBase[1], stapleBase[2])
            #vec = (targetX-self.x, targetY-self.y)
            #coords = (self.x+vec[0]/3.7, self.y+vec[1]/3.7, self.cadnanoVBaseToMayaZ(stapleBase, strand));
            coords = self.cadnanoVBaseToMayaCoords(stapleBase, strand)
            stapleModNodeInfo = self.createStapleModIndicatorNodes(coords,stapleId)
            #print "adding StapleID %s: " % stapleId
            #print self.cadnanoVBaseToMayaZ(stapleBase[0], strand)
            self.stapleModIndicatorIDs.append(stapleId)
            m = Mom()
            m.stapleModToSolidHelix[stapleModNodeInfo[2]] = (self, stapleBase, strand)
            m.stapleModToSolidHelix[stapleModNodeInfo[1]] = (self, stapleBase, strand)
            
    def createStapleModIndicatorNodes(self, coords, id):
        stapleModIndicatorName = "spStapleModIndicator%s" % id
        transformName = "stapleModIndicatorTransform%s" % id
        meshName = "stapleModIndicatorMesh%s" % id
        shaderName = "stapleModeIndicatorShader"
        
        cmds.createNode("transform", name=transformName)
        cmds.setAttr("%s.rotateX" % transformName, 90)
        cmds.setAttr("%s.translateX" % transformName, coords[0])
        cmds.setAttr("%s.translateY" % transformName, coords[1])
        cmds.setAttr("%s.translateZ" % transformName, coords[2])
        cmds.createNode("mesh", name=meshName, parent=transformName)
        cmds.createNode("spStapleModIndicator", name=stapleModIndicatorName)
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

        
    