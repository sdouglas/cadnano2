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
mayaSelectionContex.py
Created by Simon Breslav on 2011-09-27
Maya Selection Context, generates callbacks when things are selected
in Maya 3D view
"""

import sys
import maya.OpenMaya as OpenMaya
import maya.OpenMayaUI as OpenMayaUI
import maya.OpenMayaMPx as OpenMayaMPx
from controllers.mayacontrollers.mayaObjectManager import Mom

contextCmdName = "spMayaCtxCmd"


def getHelixNodeFromTransform(transformNode):
    funcSig = "helixManip:getHelixNodeFromTransform "
    # given a transform node, find the helix node attached to it
    try:
        print funcSig + "calling getHelixNodeFromTransform with node"
        print transformNode
        print funcSig + "node type is %s" % transformNode.apiTypeStr()
        if transformNode.apiType() != OpenMaya.MFn.kTransform:
            print funcSig + "incorrect node type passed in, need transform!"
            raise

        # walk the dag on the transform and find the mesh and then the helixNode
        dagNode = OpenMaya.MFnDagNode()
        dagComponentObjects = OpenMaya.MObject()
        dagNode = OpenMaya.MFnDagNode(transformNode)
        if dagNode.childCount() == 0:
            print funcSig + "Incorrect number of dag children from transform"
            raise

        child = OpenMaya.MObject()
        child = dagNode.child(0)

        if child.apiType() != OpenMaya.MFn.kMesh:
            print funcSig + "Unexpected child of transform, expected kMesh"
            raise

        helixMesh = OpenMaya.MFnMesh(child)
        inMeshPlug = OpenMaya.MPlug()
        try:
            inMeshPlug = helixMesh.findPlug("inMesh")
        except:
            print funcSig + "Can't find inMesh plug on Mesh. Not a helixNode mesh?"
            raise

        connectors = OpenMaya.MPlugArray()
        inMeshPlug.connectedTo(connectors, True, False)

        plug = OpenMaya.MPlug()
        if connectors.length() != 1:
            print funcSig + "Incorrect number of connectors from Mesh to HelixNode, not a helixMesh?"
            raise

        helixNode = OpenMaya.MObject()
        for i in range(connectors.length()):
            plug = connectors[i]
            helixNode = plug.node()
            print funcSig + "found helix node plug, APItype string %s" % helixNode.apiTypeStr()

        if helixNode.apiType() == OpenMaya.MFn.kInvalid:
            print funcSig + "failed to find connecting node!"
            helixNode = None
            raise

        try:
            nodeFn = OpenMaya.MFnDependencyNode(helixNode)
            spPlug = nodeFn.findPlug("startBaseFloat")
        except:
            print "NOT A HELIX NODE!"
            helixNode = None
            raise

        return helixNode

    except:
        print "helixManip:getHelixNodeFromTransform failed! unable to get the helix node from transform!"
        return None


def selectionCallback(clientData):
    """
    Callback function that is called when the selection changes in Maya.
    Currently only used for Pre-Decorators.
    """
    clientData.deleteManipulators()
    #print "mayaSelcectionContex: selectionCallback called"
    selectionList = OpenMaya.MSelectionList()
    OpenMaya.MGlobal.getActiveSelectionList(selectionList)
    selectionIter = OpenMaya.MItSelectionList(selectionList)
    decoratorList = []
    m = Mom()
    while not selectionIter.isDone():
            dependNode = OpenMaya.MObject()
            dagNode = OpenMaya.MFnDagNode()
            try:
                    selectionIter.getDependNode(dependNode)
                    if dependNode.isNull() or not dependNode.hasFn( \
                                            OpenMaya.MFn.kDependencyNode):
                        selectionIter.next()
                        continue
                    dagNode = OpenMaya.MFnDagNode(dependNode)
            except:
                    selectionIter.next()
                    continue
            if dagNode.name().startswith(m.decoratorTransformName):
                if dagNode.name() not in decoratorList:
                    decoratorList.append(dagNode.name())
            elif dagNode.name().startswith(m.helixTransformName):
                helixNode = getHelixNodeFromTransform(dependNode)
                manipObject = OpenMaya.MObject()
                manipulator = \
                        OpenMayaMPx.MPxManipContainer.newManipulator("spHelixManip", manipObject)
                if manipulator is not None:
                    clientData.addManipulator(manipObject)
                    transformNodePath = OpenMaya.MDagPath()
                    selectionIter.getDagPath(transformNodePath)
                    distanceManipFn = OpenMayaUI.MFnDistanceManip(manipulator.fDistanceFrontManip)
                    startPointIndex = distanceManipFn.startPointIndex()
                    # OpenMayaMPx.MPxManipContainer.addPlugToManipConversion( manipulator, startPointIndex )
                    manipulator.setupTransform(dependNode, transformNodePath)  # attempt to set up the manip xform to match the helix node xform

                    # workaround for when a strand is added, and somehow triggers this event, even though it's not selected
                    if(helixNode):
                        manipulator.connectToDependNode(helixNode)
                print "selectionCallback ", dagNode.name(), helixNode
            selectionIter.next()
    m.staplePreDecoratorSelected(decoratorList)


class mayaSelectionContext(OpenMayaMPx.MPxSelectionContext):
    """
    Maya Command that adds a callback function when something is selected
    """
    def __init__(self):
        """Initialize the commands"""
        OpenMayaMPx.MPxSelectionContext.__init__(self)

    def toolOnSetup(self, event):
        """Add the callback"""
        OpenMaya.MModelMessage.addCallback( \
                        OpenMaya.MModelMessage.kActiveListModified,
                                            selectionCallback, self)


class mayaSelctionCtxCmd(OpenMayaMPx.MPxContextCommand):
    def __init__(self):
        OpenMayaMPx.MPxContextCommand.__init__(self)

    def makeObj(self):
        return OpenMayaMPx.asMPxPtr(mayaSelectionContext())


def contextCmdCreator():
    """Wrapper function that created the command"""
    return OpenMayaMPx.asMPxPtr(mayaSelctionCtxCmd())


# initialize the script plug-in
def initializePlugin(mobject):
    """Register the context command with Maya"""
    mplugin = OpenMayaMPx.MFnPlugin(mobject)
    try:
        mplugin.registerContextCommand(contextCmdName, contextCmdCreator)
    except:
        print "Failed to register context command: %s" % contextCmdName
        raise


# uninitialize the script plug-in
def uninitializePlugin(mobject):
    """Remove the context command"""
    mplugin = OpenMayaMPx.MFnPlugin(mobject)
    try:
        mplugin.deregisterContextCommand(contextCmdName)
    except:
        print "Failed to deregister context command: %s" % contextCmdName
        raise
