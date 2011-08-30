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
from string import *
import math
import random
import os
import sys
from views import styles
from model.enum import LatticeType
from model.enum import StrandType
from model.normalstrand import NormalStrand
from model.xoverstrand import XOverStrand3, XOverStrand5

import maya.OpenMayaUI as mui
import maya.OpenMaya as mo
import maya.cmds as cmds
import util

# import Qt stuff into the module namespace with PySide, PyQt4 independence
util.qtWrapImport('QtCore', globals(), ['pyqtSignal', 'pyqtSlot', 'QObject'])

"""
solidhelix.py
Created by Simon Breslav on 2011-08-29.
"""


class SolidHelix(QObject):
    """
    SolidHelix is the 3D of the VirtualHelix.
    """
    baseWidth = styles.PATH_BASE_WIDTH

    def __init__(self, vhelix, solidHelixGroup, x, y):
        super(SolidHelix, self).__init__()
        self._solidHelixGroup = solidHelixGroup
        self._vhelix = None
        self.setVHelix(vhelix)
        self.x = x
        self.y = y
        self.row = vhelix.row()
        self.col = vhelix.col()
        # XXX - [SB] should not need to keep track of these IDs, should be
        # able to get it from the VH, but for now we use it when base count
        # changes
        self.strandIDs = []

    def pathHelixGroup(self):
        return self._solidHelixGroup

    def vhelix(self):
        return self._vhelix

    def setVHelix(self, newVH):
        vh = self._vhelix
        if vh:
            vh.basesModifiedSignal.disconnect(self.vhelixBasesModified)
            vh.dimensionsModifiedSignal.disconnect(\
                                             self.vhelixDimensionsModified)
            vh.scaf().didAddStrand.disconnect(self.strandAddedToVStrand)
            vh.stap().didAddStrand.disconnect(self.strandAddedToVStrand)
            vh.scaf().indicesModifiedSignal.disconnect(
                                        self.onIndicesModifiedSignal)
            vh.stap().indicesModifiedSignal.disconnect(
                                        self.onIndicesModifiedSignal)
        self._vhelix = newVH
        newVH.basesModifiedSignal.connect(self.vhelixBasesModified)
        newVH.dimensionsModifiedSignal.connect(self.vhelixDimensionsModified)
        newVH.scaf().didAddStrand.connect(self.strandAddedToVStrand)
        newVH.stap().didAddStrand.connect(self.strandAddedToVStrand)
        newVH.scaf().indicesModifiedSignal.connect(
                                            self.onIndicesModifiedSignal)
        newVH.stap().indicesModifiedSignal.connect(
                                            self.onIndicesModifiedSignal)

    def number(self):
        return self._vhelix.number()

    def row(self):
        return self._vhelix.row()

    def col(self):
        return self._vhelix.col()

    def evenParity(self):
        return self._vhelix.evenParity()

    def StrandIDs(self):
        return self.strandIDs

    def strandAddedToVStrand(self, strand):
        if isinstance(strand, NormalStrand):
            strand.didMove.connect(self.onStrandDidMove)
            strand.willBeRemoved.connect(self.onStrandWillBeRemoved)
            strand.apparentConnectivityChanged.connect(
                                    self.onStrandApparentConnectivityChanged)

            id = self._solidHelixGroup.strandMayaID(strand)
            self.strandIDs.append(id)
            #print "SolidHelix:strandAddedToVStrand-NormalStrand %s" % id
            if(strand.vStrand().isScaf()):
                self.createMayaHelixNodes(self.x, self.y,
                                          strand.color(),
                                          StrandType.Scaffold,
                                          id)
            else:
                self.createMayaHelixNodes(self.x, self.y,
                                          strand.color(),
                                          StrandType.Staple,
                                          id)
            self.onStrandDidMove(strand)
        elif isinstance(strand, XOverStrand3):
            #print "SolidHelix:strandAddedToVStrand-XOverStrand3"
            pass
        elif isinstance(strand, XOverStrand5):
            #print "SolidHelix:strandAddedToVStrand-XOverStrand5"
            pass
        else:
            raise NotImplementedError

    def onStrandDidMove(self, strand):
        id = self._solidHelixGroup.strandMayaID(strand)
        cylinderName = "HalfCylinderHelixNode%s" % id
        # XXX - [SB] why is there +1 in 2nd component of idxs?
        endpoints = strand.idxs()
        totalNumBases = self._vhelix.numBases()
        cmds.setAttr("%s.startBase" % cylinderName,
                             endpoints[0])

        cmds.setAttr("%s.endBase" % cylinderName,
                             endpoints[1] - 1)
        cmds.setAttr("%s.totalBases" % cylinderName, int(totalNumBases))

    def onStrandWillBeRemoved(self, strand):
        id = self._solidHelixGroup.strandMayaID(strand)
        #print "SolidHelix:onStrandWillBeRemoved %s" % id
        transformName = "DNAShapeTransform%s" % id
        if cmds.objExists(transformName):
            cmds.delete(transformName)
        self.strandIDs.remove(id)
        self._solidHelixGroup.deleteStrandMayaID(strand)
        #print strand

    def onStrandApparentConnectivityChanged(self, strand):
        pass

    def vhelixDimensionsModified(self):
        #print "SolidHelix:vhelixDimensionsModified"
        totalNumBases = self._vhelix.numBases()
        for starndID in self.strandIDs:
            cylinderName = "HalfCylinderHelixNode%s" % starndID
            cmds.setAttr("%s.totalBases" % cylinderName, int(totalNumBases))

    def vhelixBasesModified(self):
        pass

    def onIndicesModifiedSignal(self, endpoints):
        pass

    def createMayaHelixNodes(self, x, y, color, strandType, id):
        cylinderName = "HalfCylinderHelixNode%s" % id
        transformName = "DNAShapeTransform%s" % id
        meshName = "DNACylinderShape%s" % id
        shaderName = "DNAStrandShader%s" % id

        cmds.createNode("transform", name=transformName)
        cmds.setAttr("%s.rotateX" % transformName, 90)
        cmds.setAttr("%s.translateX" % transformName, x)
        cmds.setAttr("%s.translateY" % transformName, y)
        cmds.createNode("mesh", name=meshName, parent=transformName)

        cmds.createNode("spHalfCylinderHelixNode", name=cylinderName)
        cmds.connectAttr("%s.outputMesh" % cylinderName,
                         "%s.inMesh" % meshName)

        # XXX - [SB] This should go away and we will ask the model for
        # the right numbers...
        if self._solidHelixGroup.type() == LatticeType.Honeycomb:
            cmds.setAttr("%s.rotation" % cylinderName, 34.286)
            cmds.setAttr("%s.rotationOffset" % cylinderName, 30)
            cmds.setAttr("%s.parity" % cylinderName, self.evenParity())
        elif self._solidHelixGroup.type() == LatticeType.Square:
            cmds.setAttr("%s.rotation" % cylinderName, 33.75)
            cmds.setAttr("%s.rotationOffset" % cylinderName, 240)
            cmds.setAttr("%s.parity" % cylinderName, self.evenParity())
        else:
            raise NotImplementedError

        cmds.setAttr("%s.strandType" % cylinderName, strandType)
        colorval = "%d_%d_%d" % (color.red(), color.green(), color.blue())
        shaderName = "DNAStrandShader%d_%d_%d" % (color.red(),
                                                  color.green(),
                                                  color.blue())
        if not cmds.objExists(shaderName):
            # Shader does not exist create one
            cmds.shadingNode('lambert', asShader=True, name=shaderName)
            cmds.sets(n="%sSG" % shaderName, r=True, nss=True, em=True)
            cmds.connectAttr("%s.outColor" % shaderName,
                             "%sSG.surfaceShader" % shaderName)
            cmds.setAttr("%s.color" % shaderName,
                         color.redF(), color.greenF(), color.blueF(),
                         type="double3")
            cmds.sets(meshName, forceElement="%sSG" % shaderName)
        else:
            #shader exist connect
            cmds.sets(meshName, forceElement="%sSG" % shaderName)
