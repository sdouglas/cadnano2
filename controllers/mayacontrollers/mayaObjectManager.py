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
mayaObjectManager.py
Created by Alex Tessier on 2011-08
"""
from cadnano import app
import maya.cmds as cmds
import util


class Mom(object):
    """
    A singleton manager for tracking maya to cadnano and reverse lookups of
    strand and pre-decorators
    """
    _instance = None
    strandCount = 0
    selectionCountCache = 0

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(Mom, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    def myId(self):
        return id(self)

    # uses DNACylinderShape as as the key, stores strand objects
    mayaToCn = {}
    # uses strand objects as the key, stores a list of maya nodes
    cnToMaya = {}
    # uses stapleModIndicatorMesh% objects as the key,
    # stores a object with (virualHelixItem object, baseNumber, strand object)
    decoratorToVirtualHelixItem = {}
    # uses strand object as the key, stores stand id
    idStrandMapping = {}
    
    # Selection boxes
    selectionBox = cmds.polyCube( constructionHistory=False, createUVs=0, object=True)[0]
    cmds.hide(selectionBox)
    cmds.setAttr(selectionBox + ".overrideEnabled", True)
    cmds.setAttr(selectionBox + ".overrideDisplayType", 2)
    #cmds.toggle(selectionBox, state=True, template=True)
    updatingSelectionBoxes = False
    selectionBoxShader = "SelectionBoxShader"
    
    selectionBoxShader = cmds.shadingNode('lambert', asShader=True, name=selectionBoxShader)
    cmds.sets(n="%sSG" % selectionBoxShader, r=True, nss=True, em=True)
    cmds.connectAttr("%s.outColor" % selectionBoxShader, "%sSG.surfaceShader" % selectionBoxShader)
    #cmds.setAttr("%s.color" % selectionBoxShader, 0, 0, 1, type="double3")
    cmds.setAttr("%s.transparency" % selectionBoxShader, 0.65, 0.65, 0.65, type="double3")
    cmds.setAttr("%s.incandescence" % selectionBoxShader, 0.5, 0.5, 0.5, type="double3")

    # MayaNames
    helixTransformName = "DNAShapeTransform_"
    helixNodeName = "HalfCylinderHelixNode_"
    helixMeshName = "DNACylinderShape_"
    helixShaderName = "DNAStrandShader_"
    decoratorTransformName = "stapleDecoratorTransform_"
    decoratorNodeName = "spStapleModIndicator_"
    decoratorMeshName = "stapleModIndicatorMesh_"
    decoratorShaderName = "stapleModeIndicatorShader_"

    def manipulator():
        return helixManipulator;
        
    def manipulatorObject():
        return manipulatorObject;
    
    def staplePreDecoratorSelected(self, listNames):
        """
        Callback function that is called from mayaSelectionContext when a
        PreDecorator geometry is called, notifies the Part Model of this
        event. XXX - [SB] In the future we should clean up this interaction.
        """
        selectionList = []
        for name in listNames:
            if name in self.decoratorToVirtualHelixItem:
                (virtualHelixItem, baseIdx, strand) = \
                                        self.decoratorToVirtualHelixItem[name]
                selectionList.append((virtualHelixItem.row(),
                                                virtualHelixItem.col(),
                                                baseIdx))
        if len(selectionList) == 0 and \
           self.selectionCountCache == 0:
            # a dumb cache check to prevent deselection to be broadcasted too
            # many times, but could cause problems
            return

        # XXX - [SB] we want to only send the signal to "active part" but
        # not sure how to get that
        for doc in app().documentControllers:
            if doc.win.actionModify.isChecked():
                for partItem in doc.win.solidroot.partItems():
                    partModel = partItem.part()
                    partModel.selectPreDecorator(selectionList)
        self.selectionCountCache = len(selectionList)

    def removeDecoratorMapping(self, id):
        """Remove all mappings related to Pre-Decorators"""
        key1 = "%s%s" % (self.decoratorMeshName, id)
        key2 = "%s%s" % (self.decoratorTransformName, id)
        if key1 in self.decoratorToVirtualHelixItem:
            del self.decoratorToVirtualHelixItem[key1]
        if key2 in self.decoratorToVirtualHelixItem:
            del self.decoratorToVirtualHelixItem[key2]

    def removeIDMapping(self, id, strand):
        """Remove all mappings related to Strands"""
        key1 = "%s%s" % (self.helixMeshName, id)
        key2 = "%s%s" % (self.helixNodeName, id)
        if key1 in self.mayaToCn:
            del self.mayaToCn[key1]
        if key2 in self.mayaToCn:
            del self.mayaToCn[key2]
        self.deleteStrandMayaID(strand)

    def strandMayaID(self, strand):
        """
        Get a Maya ID for a given strand, if one does not exits, it
        will create a new one.
        """
        if(strand in self.idStrandMapping):
            return self.idStrandMapping[strand]
        else:
            self.strandCount += 1
            # XXX [SB+AT] NOT THREAD SAFE
            while cmds.objExists("%s%s" %
                                 (self.helixTransformName,
                                  self.strandCount)):
                self.strandCount += 1
            val = "%d" % self.strandCount
            self.idStrandMapping[strand] = val
            # print self.idStrandMapping
            return val
    # end def

    def deleteStrandMayaID(self, strand):
        """
        Removes just the Cadnano -> Maya mapping.
        It is called from removeIDMapping function
        """
        if strand in self.cnToMaya:
            del self.cnToMaya[strand]
        if strand in self.idStrandMapping:
            del self.idStrandMapping[strand]

    def updateSelectionBoxes(self):
        selectedItems = cmds.ls( self.helixTransformName + "*", selection=True)
        if selectedItems:
            bbox = cmds.exactWorldBoundingBox(selectedItems)
            #cmds.polyCube( self.selectionBox, edit=True, width=bbox[3]-bbox[0], height=bbox[4]-bbox[1], depth=bbox[5]-bbox[2], constructionHistory=False, createUVs=0, object=True)
            cmds.setAttr( self.selectionBox + ".scale", bbox[3]-bbox[0], bbox[4]-bbox[1], bbox[5]-bbox[2], type="double3" )
            cmds.sets(self.selectionBox, forceElement="%sSG" % self.selectionBoxShader)
            cmds.setAttr( self.selectionBox + ".translate", (bbox[0] + bbox[3])/2, (bbox[1]+bbox[4])/2, (bbox[2]+bbox[5])/2, type="double3")
            cmds.showHidden( self.selectionBox )
        else:
            cmds.hide( self.selectionBox )