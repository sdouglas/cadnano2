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

from controllers.mayacontrollers.mayaObjectManager import Mom
from controllers.itemcontrollers.strand.stranditemcontroller \
                                                import StrandItemController
from model.enum import StrandType
from model.enum import LatticeType

import maya.OpenMayaUI as mui
import maya.OpenMaya as mo
import maya.cmds as cmds
import util

util.qtWrapImport('QtCore', globals(), ['pyqtSignal', 'pyqtSlot', \
                                        'QObject', 'Qt'])
util.qtWrapImport('QtGui', globals(), ['QColor'])

"""
stranditem.py
Created by Simon Breslav on 2011-10-05.
"""


class StrandItem(object):
    """
    StrandItem is the strand item in the SolidView.
    """
    def __init__(self, mID, modelStrand, virtualHelixItem):
        """The parent should be a VirtualHelixItem."""
        self._modelStrand = modelStrand
        self._virtualHelixItem = virtualHelixItem
        mayaNodeInfo = ()
        if(modelStrand.strandSet().isScaffold()):
            mayaNodeInfo = self.createMayaHelixNodes(virtualHelixItem.x(),
                                                     virtualHelixItem.y(),
                                      modelStrand.oligo().color(),
                                      StrandType.Scaffold,
                                      mID)
        else:
            mayaNodeInfo = self.createMayaHelixNodes(virtualHelixItem.x(),
                                                     virtualHelixItem.y(),
                                      modelStrand.oligo().color(),
                                      StrandType.Staple,
                                      mID)
        #self.onStrandDidMove(strand)
        m = Mom()
        m.cnToMaya[modelStrand] = mayaNodeInfo
        m.mayaToCn[mayaNodeInfo[2]] = modelStrand
        m.mayaToCn[mayaNodeInfo[0]] = modelStrand
        self.updateSize()
        self._controller = StrandItemController(self, modelStrand)
    # end def

    ### SLOTS ###
    def strandResizedSlot(self, strand, indices):
        """strandResizedSlot"""
        print "solid.StrandItem.strandResizedSlot", self._modelStrand.idxs()
        self.updateSize()
        self._virtualHelixItem.updateDecorators()

    def strandUpdateSlot(self, strand):
        """strandUpdateSlot"""
        #print "solidview.StrandItem.strandUpdateSlot"
        pass

    def sequenceAddedSlot(self, oligo):
        """sequenceAddedSlot"""
        pass
        #print "solidview.StrandItem.sequenceAddedSlot"

    def sequenceClearedSlot(self, oligo):
        """sequenceClearedSlot"""
        pass
        #print "solidview.StrandItem.sequenceClearedSlot"
    
    def strandRemovedSlot(self, strand):
        mom = Mom()
        mID = mom.strandMayaID(strand)
        mom.removeIDMapping(mID, strand)
        #print "solidview.StrandItem.strandRemovedSlot %s" % mID
        transformName = "%s%s" % (mom.helixTransformName, mID)
        cylinderName = "%s%s" % (mom.helixNodeName, mID)
        meshName = "%s%s" % (mom.helixMeshName, mID)
        if cmds.objExists(transformName):
            cmds.delete(transformName)
        if cmds.objExists(cylinderName):
            cmds.delete(cylinderName)
        if cmds.objExists(meshName):
            cmds.delete(meshName)
        if mID in self._virtualHelixItem.StrandIDs():
            self._virtualHelixItem.StrandIDs().remove(mID)
        self._virtualHelixItem.updateDecorators()
        self._virtualHelixItem.removeStrandItem(self)
        self._virtualHelixItem = None

                                                  
        self._modelStrand = None
        self._controller.disconnectSignals()
        self._controller = None
    # end def

    def oligoAppearanceChangedSlot(self, oligo):
        mom = Mom()
        id = mom.strandMayaID(self._modelStrand)
        self.updateColor(id, oligo.color())
        #print "solidview.StrandItem.oligoAppeareanceChangedSlot"
        pass

    def oligoSequenceAddedSlot(self, oligo):
        #print "solidview.StrandItem.oligoSequenceAddedSlot"
        pass

    def oligoSequenceClearedSlot(self, oligo):
        #print "solidview.StrandItem.oligoSequenceClearedSlot"
        pass

    def strandHasNewOligoSlot(self, strand):
        #print "solidview.StrandItem.strandHasNewOligoSlot"
        mom = Mom()
        self._controller.reconnectOligoSignals()
        mID = mom.strandMayaID(strand)
        self.updateColor(mID, strand.oligo().color())

    def strandInsertionAddedSlot(self, strand, insertion):
        pass

    def strandInsertionChangedSlot(self, strand, insertion):
        pass

    def strandInsertionRemovedSlot(self, strand, index):
        pass

    def strandDecoratorAddedSlot(self, strand, decorator):
        pass

    def strandDecoratorChangedSlot(self, strand, decorator):
        pass

    def strandDecoratorRemovedSlot(self, strand, index):
        pass

    def strandModifierAddedSlot(self, strand, modifier):
        pass

    def strandModifierChangedSlot(self, strand, modifier):
        pass

    def strandModifierRemovedSlot(self, strand, index):
        pass

    ### METHODS ###
    def createMayaHelixNodes(self, x, y, colorname, strandType, mID):
        m = Mom()
        cylinderName = "%s%s" % (m.helixNodeName, mID)
        transformName = "%s%s" % (m.helixTransformName, mID)
        meshName = "%s%s" % (m.helixMeshName, mID)
        # shaderName = "%s%s" % (m.helixShaderName, mID)
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
        vhi = self._virtualHelixItem
        part = vhi.partItem().part()
        cSType = part.crossSectionType()
        cmds.setAttr("%s.rotation" % cylinderName, part.twistPerBase())
        cmds.setAttr("%s.parity" % cylinderName, vhi.isEvenParity())
        if cSType == LatticeType.Honeycomb:
            cmds.setAttr("%s.rotationOffset" % cylinderName, 240)
        elif cSType == LatticeType.Square:
            cmds.setAttr("%s.rotationOffset" % cylinderName, 115)
        else:
            raise NotImplementedError
        cmds.setAttr("%s.strandType" % cylinderName, strandType)
        self.updateColor(mID, colorname)
        return (cylinderName, transformName, meshName)

    def updateColor(self, mID, colorname):
        m = Mom()
        meshName = "%s%s" % (m.helixMeshName, mID)
        color = QColor(colorname)
        colorval = "%d_%d_%d" % (color.red(), color.green(), color.blue())
        shaderName = "%s%d_%d_%d" % (m.helixShaderName, color.red(),
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

    def updateSize(self):
        mom = Mom()
        mID = mom.strandMayaID(self._modelStrand)
        cylinderName = "%s%s" % (mom.helixNodeName, mID)
        endpoints = self._modelStrand.idxs()
        totalNumBases = self._virtualHelixItem.virtualHelix().part().maxBaseIdx()
        cmds.setAttr("%s.startBase" % cylinderName,
                             endpoints[0])

        cmds.setAttr("%s.endBase" % cylinderName,
                             endpoints[1])
        cmds.setAttr("%s.totalBases" % cylinderName, int(totalNumBases))
