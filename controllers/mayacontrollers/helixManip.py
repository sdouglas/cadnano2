###############################################################################
#
# Copyright 2011 Autodesk, Inc.  All rights reserved.
#
# The MIT License
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of
# this software and associated documentation files (the "Software"), to deal in
# the Software without restriction, including without limitation the rights to
# use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies
# of the Software, and to permit persons to whom the Software is furnished to do
# so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#
###############################################################################

"""
helixManip.py
Created by Alex Tessier on 2011-08
A Maya manip for controlling Helix Shape similar to the selectTool
"""

import sys
import maya.OpenMaya as OpenMaya
import maya.OpenMayaUI as OpenMayaUI
import maya.OpenMayaMPx as OpenMayaMPx

# for controlling the nodes
from model.enum import StrandType
from controllers.mayacontrollers.mayaObjectManager import Mom


helixManipId = OpenMaya.MTypeId(0x00117702)
contextCmdName = "spHelixManipCtxCmd"
nodeName = "spHelixManip"


def dotproduct(a, b):
    return a.x * b.x + a.y * b.y + a.z * b.z


class helixManip(OpenMayaMPx.MPxManipContainer):
    fDistanceFrontManip = OpenMaya.MDagPath()
    fDistanceBackManip = OpenMaya.MDagPath()
    startBaseFloatAttr = OpenMaya.MObject()
    endBaseFloatAttr = OpenMaya.MObject()
    startBaseIntAttr = OpenMaya.MObject()
    endBaseIntAttr = OpenMaya.MObject()
    myNode = OpenMaya.MObject()
    helixTransform = OpenMaya.MObject()
    sp = OpenMaya.MPoint()
    cp = OpenMaya.MPoint()
    frontDir = OpenMaya.MVector()
    backDir = OpenMaya.MVector()
    helixName = ""
    #amResizing = False
    ffpIdx = 0  # front index in converter plug array
    epIdx = 0   # back index in converter plug array
    #fFreePointManip = OpenMaya.MDagPath()
    newStrandSize = (0, 0)
    manipHandleOffset = 1

    def __init__(self):
        OpenMayaMPx.MPxManipContainer.__init__(self)
        self.fNodePath = OpenMaya.MDagPath()

    def createChildren(self):
        #print "helixManip: createChildren being called..."
        # startPoint should correspond to the end of the helix
        # read the attribute to get the offset from the starting position
        self.fDistanceFrontManip = self.addDistanceManip("distanceManip", "distance")
        distanceManipFn = OpenMayaUI.MFnDistanceManip(self.fDistanceFrontManip)
        startPoint = OpenMaya.MPoint(0.0, 0.0, 0.0)
        self.frontDir = OpenMaya.MVector(0.0, 0.0, 1.0)
        distanceManipFn.setStartPoint(startPoint)
        distanceManipFn.setDirection(self.frontDir)
        #distanceManipFn.setScalingFactor(3.0)
        # self.fFreePointManip = self.addFreePointTriadManip("pointManip", "freePoint")

        self.fDistanceBackManip = self.addDistanceManip("distancgeteManip", "distance")
        distanceManipFn = OpenMayaUI.MFnDistanceManip(self.fDistanceBackManip)
        startPoint = OpenMaya.MPoint(0.0, 0.0, 0.0)
        self.backDir = OpenMaya.MVector(0.0, 0.0, -1.0)
        distanceManipFn.setStartPoint(startPoint)
        distanceManipFn.setDirection(self.backDir)

    def connectToDependNode(self, node):
        #print "connectToDependNode called"
        nodeFn = OpenMaya.MFnDependencyNode(node)
        self.myNode = node
        self.helixName = nodeFn.name()

        try:
            frontPlug = nodeFn.findPlug("startBaseFloat")
            backPlug = nodeFn.findPlug("endBaseFloat")

            frontManip = OpenMayaUI.MFnDistanceManip(self.fDistanceFrontManip)
            frontManip.connectToDistancePlug(frontPlug)

            backManip = OpenMayaUI.MFnDistanceManip(self.fDistanceBackManip)
            backManip.connectToDistancePlug(backPlug)

            # hookup the converter functions
            self.addPlugToManipConversion(frontManip.startPointIndex())
            self.addPlugToManipConversion(frontManip.currentPointIndex())
            self.addPlugToManipConversion(backManip.startPointIndex())
            self.addPlugToManipConversion(backManip.currentPointIndex())

            self.ffpIdx = self.addManipToPlugConversion(frontPlug)
            self.epIdx = self.addManipToPlugConversion(backPlug)

            # initially, current points and start/end points match
            startPos = nodeFn.findPlug("startPos")
            startPoint = self.getFloat3PlugValue(startPos)
            self.sp = startPoint
            self.cp = startPoint

            endPos = nodeFn.findPlug("endPos")
            endPoint = self.getFloat3PlugValue(endPos)
            self.ep = endPoint
            self.ecp = endPoint

            self.finishAddingManips()
            OpenMayaMPx.MPxManipContainer.connectToDependNode(self, node)
        except:
            sys.stderr.write("helixManip: Error finding and connecting plugs\n")
            sys.stderr.write(sys.exc_info()[0])
            # raise

    def setupTransform(self, node, path):
        self.helixTransform = node  # store the transform node
        nodeFn = OpenMaya.MFnDependencyNode(node)
        #print nodeFn.name()

        dagNodeFn = OpenMaya.MFnDagNode(node)
        dagNodeFn.getPath(self.fNodePath)

    def computeDistance(self, sp, cp, dirv):
        # sp - start point, cp - current point
        u = OpenMaya.MVector(sp)
        v = OpenMaya.MVector(cp)
        w = u - v
        m = self.getTransformMtxFromNode(self.helixTransform)
        wm = w * m
        if(dotproduct(wm.normal(), dirv.normal()) > 0):
            dir = -1
        else:
            dir = 1
        distance = w.length() * dir
        #print "start point is (%f, %f, %f)" % (sp.x, sp.y, sp.z)
        #print "current point is (%f, %f, %f)" % (cp.x, cp.y, cp.z)
        return distance

    def doRelease(self):
        #print "RELEASED"
        if (self.newStrandSize != (0, 0)):
            self.getStrand().resize(self.newStrandSize)
            self.newStrandSize = (0, 0)
        return OpenMaya.kUnknownParameter

    def doDrag(self):
        #print "DRAGGING"
        if (self.newStrandSize != (0, 0)):
            self.getStrand().resize(self.newStrandSize)
            self.newStrandSize = (0, 0)
        return OpenMaya.kUnknownParameter

    def plugToManipConversion(self, manipIndex):
        # print "plugToManipCalled"
        manipData = OpenMayaUI.MManipData()
        try:
            frontManip = OpenMayaUI.MFnDistanceManip(self.fDistanceFrontManip)
            backManip = OpenMayaUI.MFnDistanceManip(self.fDistanceBackManip)

            # get the ws transform of the helix and transform the points
            m = self.getTransformMtxFromNode(self.helixTransform)

            nodeFn = OpenMaya.MFnDependencyNode(self.myNode)

            if(manipIndex == frontManip.currentPointIndex()):
                #distance = self.computeDistance(self.sp, self.cp, self.frontDir)
                finalPoint = OpenMaya.MVector()
                finalPoint = OpenMaya.MVector(self.sp * m)
                finalPoint += self.frontDir * self.manipHandleOffset

                #self.checkHelixDelta(distance)

                #print "front manip final point is (%f, %f, %f)" % \
                #    (finalPoint.x, finalPoint.y, finalPoint.z)

                # is this the new position?
                #startPos  = nodeFn.findPlug("startPos")
                #startPoint = self.getFloat3PlugValue(startPos)
                #print "front p to m sp is (%f, %f, %f) vs final (%f, %f, %f)" \
                #% (startPoint.x, startPoint.y, startPoint.z,
                #   finalPoint.x, finalPoint.y, finalPoint.z)

                numData = OpenMaya.MFnNumericData()

                numDataObj = numData.create(OpenMaya.MFnNumericData.k3Double)
                numData.setData3Double(finalPoint.x, finalPoint.y, finalPoint.z)
                manipData = OpenMayaUI.MManipData(numDataObj)

            elif(manipIndex == backManip.currentPointIndex()):
                #distance = self.computeDistance(self.ep, self.ecp, self.backDir)
                finalPoint = OpenMaya.MVector()
                finalPoint = OpenMaya.MVector(self.ep * m)
                finalPoint += self.backDir * self.manipHandleOffset

                #endPos  = nodeFn.findPlug("endPos")
                #endPoint = self.getFloat3PlugValue(endPos)
                #ws = endPoint * m
                #
                numData = OpenMaya.MFnNumericData()

                numDataObj = numData.create(OpenMaya.MFnNumericData.k3Double)

                numData.setData3Double(finalPoint.x, finalPoint.y, finalPoint.z)
                manipData = OpenMayaUI.MManipData(numDataObj)

            elif(manipIndex == frontManip.startPointIndex()):
                startPos = nodeFn.findPlug("startPos")
                startPoint = self.getFloat3PlugValue(startPos)
                #startPoint = OpenMaya.MPoint(0., 0., 0.)
                ws = startPoint * m

                numData = OpenMaya.MFnNumericData()
                numDataObj = numData.create(OpenMaya.MFnNumericData.k3Float)
                numData.setData3Float(ws.x, ws.y, ws.z)
                #print "frontManip start to (%f, %f, %f)" % (ws.x, ws.y, ws.z)
                manipData = OpenMayaUI.MManipData(numDataObj)

            elif(manipIndex == backManip.startPointIndex()):
                endPos = nodeFn.findPlug("endPos")
                endPoint = self.getFloat3PlugValue(endPos)
                #endPoint = OpenMaya.MPoint(0., 0., 0.)
                ws = endPoint * m

                numData = OpenMaya.MFnNumericData()
                numDataObj = numData.create(OpenMaya.MFnNumericData.k3Float)
                numData.setData3Float(ws.x, ws.y, ws.z)
                #print "back Manip start to (%f, %f, %f)" % (ws.x, ws.y, ws.z)
                manipData = OpenMayaUI.MManipData(numDataObj)
        except:
            sys.stderr.write("ERROR: helixManip.plugToManipConversion\n")
            raise

        return manipData

    def manipToPlugConversion(self, plugIndex):
        #print "manipToPlugConversion", plugIndex
        try:
            if(plugIndex == self.ffpIdx):  # front float plug
                numData = OpenMaya.MFnNumericData()
                numDataObj = numData.create(OpenMaya.MFnNumericData.k3Double)

                sp = OpenMaya.MPoint()
                cp = OpenMaya.MPoint()

                frontManip = OpenMayaUI.MFnDistanceManip(self.fDistanceFrontManip)

                self.getConverterManipValue(frontManip.startPointIndex(), sp)
                self.getConverterManipValue(frontManip.currentPointIndex(), cp)

                m2 = self.getTransformMtxFromNode(self.helixTransform)
                m = m2.inverse()

                self.sp = sp * m
                self.cp = cp * m

                # distance is...
                distance = self.computeDistance(self.sp, self.cp, self.frontDir) - self.manipHandleOffset

                newIndex = self.getHelixDelta(distance)
                self.dragDeltaFront = newIndex
                self.resizeCNHelixFront(newIndex)

                #(remainder, intInc) = self.checkHelixDelta(distance)
                #print "manipToPlug front manip r, inc are (%f, %f)" % (remainder, intInc)
                ## tell the manip to move by intInc
                ## reset the distance to remainder, adjust start points
                ## accordingly

                numData.setData3Double(cp.x, cp.y, cp.z)
                returnData = OpenMayaUI.MManipData(numDataObj)

            elif(plugIndex == self.epIdx):
                numData = OpenMaya.MFnNumericData()
                numDataObj = numData.create(OpenMaya.MFnNumericData.k3Double)

                ep = OpenMaya.MPoint()
                ecp = OpenMaya.MPoint()

                backManip = OpenMayaUI.MFnDistanceManip(self.fDistanceBackManip)

                self.getConverterManipValue(backManip.startPointIndex(), ep)
                self.getConverterManipValue(backManip.currentPointIndex(), ecp)

                m2 = self.getTransformMtxFromNode(self.helixTransform)
                m = m2.inverse()

                self.ep = ep * m
                self.ecp = ecp * m

                # distance is...
                distance = self.computeDistance(self.ep, self.ecp, self.backDir) - self.manipHandleOffset

                newIndex = self.getHelixDelta(distance)
                self.resizeCNHelixBack(newIndex)

                numData.setData3Double(ecp.x, ecp.y, ecp.z)
                returnData = OpenMayaUI.MManipData(numDataObj)
        except:
            sys.stderr.write("ERROR: helixManip.manipToPlugConversion\n")
            raise
        return returnData

    def getTransformFromNode(self, trnsNode):
        try:
            dagFn = OpenMaya.MFnDagNode(trnsNode)
            path = OpenMaya.MDagPath()
            dagFn.getPath(path)
            transformFn = OpenMaya.MFnTransform(path)
            return transformFn
        except:
            print "getTransformFromNode -- unable to get transform from node"
            print trnsNode
            raise

    def getTransformMtxFromNode(self, trnsNode):
        mtx = OpenMaya.MMatrix()
        try:
            transformFn = self.getTransformFromNode(trnsNode)
            mm = transformFn.transformation()
            mtx = mm.asMatrix()
        except:
            print "Unable to get transformation matrix for node:"
            print trnsNode

        return mtx

    #def nodeTranslation(self):
            #dagFn = OpenMaya.MFnDagNode(self.fNodePath)
            #path = OpenMaya.MDagPath()

            #dagFn.getPath(path)

            # pop from the shape to the transform
            #path.pop()
            #print "nodeTranslation is"
            #print path
            #transformFn = OpenMaya.MFnTransform(path)
            #return transformFn.translation(OpenMaya.MSpace.kWorld)

    def getRotation(self, nodePath):
        dagFn = OpenMaya.MFnDagNode(nodePath)
        path = OpenMaya.MDagPath()
        dagFn.getPath(path)
        transformFn = OpenMaya.MFnTransform(path)
        q = OpenMaya.MQuaternion()
        transformFn.getRotation(q, OpenMaya.MSpace.kWorld)
        return q

    def getTranslation(self, nodePath):
        dagFn = OpenMaya.MFnDagNode(nodePath)
        path = OpenMaya.MDagPath()
        dagFn.getPath(path)
        transformFn = OpenMaya.MFnTransform(path)
        return transformFn.translation(OpenMaya.MSpace.kWorld)

    # Getting values out of references is a little crazy in the 1.0
    # Maya Python API....
    def getFloat3PlugValue(self, plug):
        # Retrieve the value as an MObject
        object = plug.asMObject()

        # TODO type checking that our plug is a float3 plug!
        # Convert the MObject to a float3
        numDataFn = OpenMaya.MFnNumericData(object)

        xParam = OpenMaya.MScriptUtil()
        xParam.createFromDouble(0.0)
        xPtr = xParam.asFloatPtr()

        yParam = OpenMaya.MScriptUtil()
        yParam.createFromDouble(0.0)
        yPtr = yParam.asFloatPtr()

        zParam = OpenMaya.MScriptUtil()
        zParam.createFromDouble(0.0)
        zPtr = zParam.asFloatPtr()

        numDataFn.getData3Float(xPtr, yPtr, zPtr)

        return OpenMaya.MPoint(OpenMaya.MScriptUtil.getFloat(xPtr),
                                OpenMaya.MScriptUtil.getFloat(yPtr),
                                OpenMaya.MScriptUtil.getFloat(zPtr) )
        

    def matchNodePosition( self, transformNode, helixNode ):
        trans = self.getTranslation( transformNode )
        q = self.getRotation( transformNode )
        
        helixNodeFn = OpenMaya.MFnDependencyNode( helixNode )
        startPlug = helixNodeFn.findPlug( "startPos")
        endPlug = helixNodeFn.findPlug( "endPos" )
        
        startPos = self.getFloat3PlugValue( startPlug )
        endPos = self.getFloat3PlugValue( endPlug )

        #print "matchNodePosition matching position..." ## to (%f, %f, %f)" % ( startPos[0], startpos[1], startpos[2[]])
        freePointManipFront = OpenMayaUI.MFnDistanceManip( self.fDistanceFrontManip  )
        freePointManipBack = OpenMayaUI.MFnDistanceManip( self.fDistanceBackManip )
        vecZ = OpenMaya.MVector( 0.0, 1.5, 0.0 )
        vecMinusZ = OpenMaya.MVector( 0.0, -1.5, 0.0 )
        scalingFactor = 1.0

        freePointManipFront.setStartPoint(startPos)
        freePointManipFront.setDrawStart(False)
        freePointManipFront.setScalingFactor(scalingFactor)
        freePointManipFront.setDirection(vecZ)
        freePointManipFront.rotateBy(q)
        freePointManipFront.setTranslation(trans, OpenMaya.MSpace.kWorld)

        freePointManipBack.setStartPoint(endPos)
        freePointManipBack.setDrawStart(False)
        freePointManipBack.setScalingFactor(scalingFactor)
        freePointManipBack.setDirection(vecMinusZ + vecMinusZ)
        freePointManipBack.rotateBy(q)
        freePointManipBack.setTranslation(trans, OpenMaya.MSpace.kWorld)

    def getStrand(self):
        m = Mom()
        return m.mayaToCn[self.helixName]

    #def getSide(self):
        #strand = self.getStrand()
        #return 0

    def getRise(self):
        try:
            n = nodeFn = OpenMaya.MFnDependencyNode(self.myNode)
            risePlug = n.findPlug("rise")
            rise = risePlug.asDouble()
            return rise
        except:
            print "Failed to retrieve rise from node %s" % self.helixName

    def getHelixDelta(self, distance):
        try:
            ## given a distance from the origin of the strand,
            ## compute the change in bases

            rise = self.getRise()
            delta = int(distance / rise)

            return delta
        except:
            print "getFrontHelixDelta failed!"

    #def checkHelixDelta(self, distance):
        #rise = self.getRise()
        #increment = int(distance / rise)
        #remainder = distance % rise
        #return (remainder, increment)

    def resizeCNHelixFront(self, delta):
        try:
            #if(self.amResizing):
               #return

            strand = self.getStrand()
            lowIdx, highIdx = strand.idxs()
            newLow = lowIdx - delta
            newLow = min(newLow, highIdx - 1)
            newLow = max(newLow, strand.part().minBaseIdx())
            if(newLow != lowIdx):
                #self.amResizing = True
                #strand.resize((newLow, highIdx))
                self.newStrandSize = (newLow, highIdx)
                #self.amResizing = False
            # to make smaller
            # strand.clearStrand(startIdx, endIdx)
        except:
            print "resizeCNHelixFront failed!"

    def resizeCNHelixBack(self, delta):
        try:
            #if(self.amResizing):
               #return

            strand = self.getStrand()
            lowIdx, highIdx = strand.idxs()
            newHigh = highIdx + delta
            newHigh = min(newHigh, strand.part().maxBaseIdx())
            newHigh = max(newHigh, lowIdx + 1)
            if(newHigh != highIdx):
                #self.amResizing = True
                #strand.resize((lowIdx, newHigh))
                self.newStrandSize = (lowIdx, newHigh)
                #self.amResizing = False
            # to make smaller
            # strand.clearStrand(startIdx, endIdx)
        except:
            print "resizeCNHelixBack failed!"


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

        # walk the dag on the transform, find the mesh and then the helixNode
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
            print funcSig + "Can't find inMesh plug on Mesh. \
                                            Not a helixNode mesh?"
            raise

        connectors = OpenMaya.MPlugArray()
        inMeshPlug.connectedTo(connectors, True, False)

        plug = OpenMaya.MPlug()
        if connectors.length() != 1:
            print funcSig + "Incorrect number of connectors \
                                    from Mesh to HelixNode, not a helixMesh?"
            raise

        helixNode = OpenMaya.MObject()
        for i in range(connectors.length()):
            plug = connectors[i]
            helixNode = plug.node()
            print funcSig + "found helix node plug, APItype string %s" \
                                                    % helixNode.apiTypeStr()

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
        print "helixManip:getHelixNodeFromTransform failed! \
                        unable to get the helix node from transform!"
        return None


def helixManipCreator():
    #print "helixManip: helixManipCreator called"
    return OpenMayaMPx.asMPxPtr(helixManip())


def helixManipInitialize():
        #print "helixManip: helixManipInitialize called"
        OpenMayaMPx.MPxManipContainer.initialize()
        typedAttr = OpenMaya.MFnTypedAttribute()
        nAttr = OpenMaya.MFnNumericAttribute()

        helixManip.startBaseFloatAttr = \
            nAttr.create('helixManipStartPos',
            'hmsp',
            OpenMaya.MFnNumericData.kFloat,
            0.0)

        nAttr.setWritable(True)
        nAttr.setStorable(False)
        helixManip.endBaseFloatAttr = \
            nAttr.create('helixManipEndPos',
            'hmep',
            OpenMaya.MFnNumericData.kFloat,
            0.0)

        nAttr.setWritable(True)
        nAttr.setStorable(False)

        helixManip.addAttribute(helixManip.startBaseFloatAttr)
        helixManip.addAttribute(helixManip.endBaseFloatAttr)


# initialize the script plug-in
def initializePlugin(mobject):
    #print "helixManip: initializePlugin for helixManip called"
    mplugin = OpenMayaMPx.MFnPlugin(mobject)
    try:
        mplugin.registerNode(nodeName, helixManipId, helixManipCreator,
                    helixManipInitialize, OpenMayaMPx.MPxNode.kManipContainer)
    except:
        print "helixManip: Failed to register node: %s" % nodeName
        raise


# uninitialize the script plug-in
def uninitializePlugin(mobject):
    #print "helixManip uninitializePlugin for helixManip called"
    mplugin = OpenMayaMPx.MFnPlugin(mobject)

    try:
        mplugin.deregisterNode(helixManipId)
    except:
        print "helixManip: Failed to deregister node: %s" % nodeName
        raise
