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
import maya.cmds as cmds

# for controlling the nodes
from model.enum import StrandType
from controllers.mayacontrollers.mayaObjectManager import Mom


helixManipId = OpenMaya.MTypeId(0x00117702)
contextCmdName = "spHelixManipCtxCmd"
nodeName = "spHelixManip"


def project(a, b):
    c = OpenMaya.MVector()
    bn = b.normal()
    c.x = a.x * bn.x
    c.y = a.y * bn.y
    c.z = a.z * bn.z
    return c


class helixManip(OpenMayaMPx.MPxManipContainer):

    class helix():
        id = None
        helixName = ""
        newStrandSize = (0, 0)
        startBaseFloatAttr = OpenMaya.MObject()
        endBaseFloatAttr = OpenMaya.MObject()
        startBaseIntAttr = OpenMaya.MObject()
        endBaseIntAttr = OpenMaya.MObject()
        helixNode = OpenMaya.MObject()
        helixTransform = OpenMaya.MObject()
        sp = OpenMaya.MPoint()
        cp = OpenMaya.MPoint()

        def __str__(self):
            return self.helixName

    # I might need n of these...
    startBaseFloatAttr = OpenMaya.MObject()
    endBaseFloatAttr = OpenMaya.MObject()
    startBaseIntAttr = OpenMaya.MObject()
    endBaseIntAttr = OpenMaya.MObject()

    # I will not need n of these...
    frontDir = OpenMaya.MVector()
    backDir = OpenMaya.MVector()
    manipHandleOffset = 1
    fDistanceFrontManip = OpenMaya.MDagPath()
    fDistanceBackManip = OpenMaya.MDagPath()
    sp = OpenMaya.MPoint()
    cp = OpenMaya.MPoint()

    activeHelix = None
    helices = {}
    ffpIdxMap = {}
    epIdxMap = {}

    def __init__(self):
        OpenMayaMPx.MPxManipContainer.__init__(self)

    def addHelix(self, HNumber):

        m = Mom()

        h = self.helix()
        h.id = HNumber
        h.helixTransform = m.getNodeFromName(
                                    "%s%s" % (m.helixTransformName, HNumber))
        h.helixNode = m.getNodeFromName("%s%s" % (m.helixNodeName, HNumber))

        nodeFn = OpenMaya.MFnDependencyNode(h.helixNode)
        h.helixName = nodeFn.name()

        self.helices[HNumber] = h

        #if self.activeHelix is None:
        self.activeHelix = h
        self.connectToDependNode(h.helixNode)

    def createChildren(self):
        self.helices = {}
        #print "helixManip: createChildren being called..."
        # startPoint should correspond to the end of the helix
        # read the attribute to get the offset from the starting position
        self.fDistanceFrontManip = self.addDistanceManip(
                                                "distanceManip", "distance")
        distanceManipFn = OpenMayaUI.MFnDistanceManip(self.fDistanceFrontManip)
        startPoint = OpenMaya.MPoint(0.0, 0.0, 0.0)
        self.frontDir = OpenMaya.MVector(0.0, 0.0, 1.0)
        distanceManipFn.setStartPoint(startPoint)
        distanceManipFn.setDirection(self.frontDir)

        self.fDistanceBackManip = self.addDistanceManip(
                                                "distancgeteManip", "distance")
        distanceManipFn = OpenMayaUI.MFnDistanceManip(self.fDistanceBackManip)
        startPoint = OpenMaya.MPoint(0.0, 0.0, 0.0)
        self.backDir = OpenMaya.MVector(0.0, 0.0, -1.0)
        distanceManipFn.setStartPoint(startPoint)
        distanceManipFn.setDirection(self.backDir)

    def connectToDependNode(self, node):
        #print "connectToDependNode called"
        nodeFn = OpenMaya.MFnDependencyNode(node)
        self.activeHelix.helixNode = node
        self.activeHelix.helixName = nodeFn.name()

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

            idx = self.addManipToPlugConversion(frontPlug)
            self.ffpIdxMap[idx] = self.activeHelix
            idx = self.addManipToPlugConversion(backPlug)
            self.epIdxMap[idx] = self.activeHelix

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
            sys.stderr.write(
                        "helixManip: Error finding and connecting plugs\n")
            sys.stderr.write(sys.exc_info()[0])
            raise

    def computeDistance(self, helix, sp, cp, dirv):
        # sp - start point, cp - current point
        u = OpenMaya.MVector(sp)
        v = OpenMaya.MVector(cp)
        w = u - v
        m = self.getTransformMtxFromNode(helix.helixTransform)
        wm = w * m
        if(wm.normal() * dirv.normal() > 0):  # dotproduct
            dir = -1
        else:
            dir = 1
        distance = w.length() * dir
        return distance

    def doRelease(self):
        #print "RELEASED"
        for (id, helix) in self.helices.iteritems():
            if (helix.newStrandSize != (0, 0)):
                self.getStrand(helix).resize(helix.newStrandSize)
                helix.newStrandSize = (0, 0)
        return OpenMaya.kUnknownParameter

    def doDrag(self):
        #print "DRAGGING"
        for (id, helix) in self.helices.iteritems():
            if (helix.newStrandSize != (0, 0)):
                self.getStrand(helix).resize(helix.newStrandSize)
                helix.newStrandSize = (0, 0)
        return OpenMaya.kUnknownParameter

    def plugToManipConversion(self, manipIndex):

        helix = self.activeHelix

        # print "plugToManipCalled"
        manipData = OpenMayaUI.MManipData()
        try:
            frontManip = OpenMayaUI.MFnDistanceManip(self.fDistanceFrontManip)
            backManip = OpenMayaUI.MFnDistanceManip(self.fDistanceBackManip)

            # get the ws transform of the helix and transform the points
            m = self.getTransformMtxFromNode(helix.helixTransform)

            boundBoxCenter = OpenMaya.MVector()
            boundBoxScale = OpenMaya.MVector()
            mom = Mom()
            bbc = cmds.getAttr(mom.getSelectionBox() + ".translate")
            boundBoxCenter.x = float(bbc[0][0])
            boundBoxCenter.y = float(bbc[0][1])
            boundBoxCenter.z = float(bbc[0][2])
            bbs = cmds.getAttr(mom.getSelectionBox() + ".scale")
            boundBoxScale.x = float(bbs[0][0])
            boundBoxScale.y = float(bbs[0][1])
            boundBoxScale.z = float(bbs[0][2])

            nodeFn = OpenMaya.MFnDependencyNode(helix.helixNode)

            if(manipIndex == frontManip.currentPointIndex()):
                finalPoint = OpenMaya.MVector()
                finalPoint = OpenMaya.MVector(self.sp * m)
                finalPoint += self.frontDir * self.manipHandleOffset

                ws = boundBoxCenter
                nv = project(boundBoxScale / 2, self.frontDir)
                ws += nv + self.frontDir * self.manipHandleOffset
                finalPoint = ws

                numData = OpenMaya.MFnNumericData()
                numDataObj = numData.create(OpenMaya.MFnNumericData.k3Double)
                numData.setData3Double(
                                    finalPoint.x, finalPoint.y, finalPoint.z)
                manipData = OpenMayaUI.MManipData(numDataObj)

            elif(manipIndex == backManip.currentPointIndex()):
                finalPoint = OpenMaya.MVector()
                finalPoint = OpenMaya.MVector(self.ep * m)
                finalPoint += self.backDir * self.manipHandleOffset

                ws = boundBoxCenter
                nv = project(boundBoxScale / 2, self.backDir)
                ws += nv + self.backDir * self.manipHandleOffset
                finalPoint = ws

                numData = OpenMaya.MFnNumericData()
                numDataObj = numData.create(OpenMaya.MFnNumericData.k3Double)
                numData.setData3Double(
                                    finalPoint.x, finalPoint.y, finalPoint.z)
                manipData = OpenMayaUI.MManipData(numDataObj)

            elif(manipIndex == frontManip.startPointIndex()):

                ws = boundBoxCenter
                nv = project(boundBoxScale / 2, self.frontDir)
                ws += nv

                numData = OpenMaya.MFnNumericData()
                numDataObj = numData.create(OpenMaya.MFnNumericData.k3Float)
                numData.setData3Float(ws.x, ws.y, ws.z)
                manipData = OpenMayaUI.MManipData(numDataObj)

            elif(manipIndex == backManip.startPointIndex()):

                ws = boundBoxCenter
                nv = project(boundBoxScale / 2, self.backDir)
                ws += nv

                numData = OpenMaya.MFnNumericData()
                numDataObj = numData.create(OpenMaya.MFnNumericData.k3Float)
                numData.setData3Float(ws.x, ws.y, ws.z)
                manipData = OpenMayaUI.MManipData(numDataObj)
        except:
            sys.stderr.write("ERROR: helixManip.plugToManipConversion\n")
            raise

        return manipData

    def manipToPlugConversion(self, plugIndex):
        #print "manipToPlugConversion", plugIndex

        try:
            if plugIndex in self.ffpIdxMap:  # front float plug
                helix = self.ffpIdxMap[plugIndex]
                numData = OpenMaya.MFnNumericData()
                numDataObj = numData.create(OpenMaya.MFnNumericData.k3Double)

                sp = OpenMaya.MPoint()
                cp = OpenMaya.MPoint()

                frontManip = OpenMayaUI.MFnDistanceManip(
                                                    self.fDistanceFrontManip)

                self.getConverterManipValue(frontManip.startPointIndex(), sp)
                self.getConverterManipValue(frontManip.currentPointIndex(), cp)

                m2 = self.getTransformMtxFromNode(helix.helixTransform)
                m = m2.inverse()

                self.sp = sp * m
                self.cp = cp * m

                # distance is...
                distance = self.computeDistance(
                                        helix, self.sp, self.cp, self.frontDir
                                                ) - self.manipHandleOffset

                newIndex = self.getHelixDelta(helix, distance)
                self.dragDeltaFront = newIndex
                self.resizeCNHelixFront(helix, newIndex)

                numData.setData3Double(cp.x, cp.y, cp.z)
                returnData = OpenMayaUI.MManipData(numDataObj)

            if plugIndex in self.epIdxMap:
                helix = self.epIdxMap[plugIndex]
                numData = OpenMaya.MFnNumericData()
                numDataObj = numData.create(OpenMaya.MFnNumericData.k3Double)

                ep = OpenMaya.MPoint()
                ecp = OpenMaya.MPoint()

                backManip = OpenMayaUI.MFnDistanceManip(
                                                    self.fDistanceBackManip)

                self.getConverterManipValue(backManip.startPointIndex(), ep)
                self.getConverterManipValue(backManip.currentPointIndex(), ecp)

                m2 = self.getTransformMtxFromNode(helix.helixTransform)
                m = m2.inverse()

                self.ep = ep * m
                self.ecp = ecp * m

                # distance is...
                distance = self.computeDistance(
                                        helix, self.ep, self.ecp, self.backDir
                                                ) - self.manipHandleOffset

                newIndex = self.getHelixDelta(helix, distance)
                self.resizeCNHelixBack(helix, newIndex)

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
                                OpenMaya.MScriptUtil.getFloat(zPtr))

    def matchNodePosition(self, transformNode, helixNode):
        trans = self.getTranslation(transformNode)
        q = self.getRotation(transformNode)

        helixNodeFn = OpenMaya.MFnDependencyNode(helixNode)
        startPlug = helixNodeFn.findPlug("startPos")
        endPlug = helixNodeFn.findPlug("endPos")

        startPos = self.getFloat3PlugValue(startPlug)
        endPos = self.getFloat3PlugValue(endPlug)

        #print "matchNodePosition matching position..." \
                ## to (%f, %f, %f)" % (startPos[0], startpos[1], startpos[2[]])
        freePointManipFront = OpenMayaUI.MFnDistanceManip(
                                                    self.fDistanceFrontManip)
        freePointManipBack = OpenMayaUI.MFnDistanceManip(
                                                    self.fDistanceBackManip)
        vecZ = OpenMaya.MVector(0.0, 1.5, 0.0)
        vecMinusZ = OpenMaya.MVector(0.0, -1.5, 0.0)
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

    def getStrand(self, helix):
        m = Mom()
        return m.mayaToCn[helix.helixName]

    def getRise(self, helix):
        try:
            n = nodeFn = OpenMaya.MFnDependencyNode(helix.helixNode)
            risePlug = n.findPlug("rise")
            rise = risePlug.asDouble()
            return rise
        except:
            print "Failed to retrieve rise from node %s" % helix.helixName

    def getHelixDelta(self, helix, distance):
        try:
            ## given a distance from the origin of the strand,
            ## compute the change in bases

            rise = self.getRise(helix)
            delta = int(distance / rise)

            return delta
        except:
            print "getFrontHelixDelta failed!"

    def resizeCNHelixFront(self, helix, delta):
        #print "resizeCNHelixFront"
        try:
            strand = self.getStrand(helix)
            lowIdx, highIdx = strand.idxs()
            newLow = lowIdx - delta
            newLow = min(newLow, highIdx - 1)
            newLow = max(newLow, strand.part().minBaseIdx())
            if(newLow != lowIdx):
                helix.newStrandSize = (newLow, highIdx)
        except:
            print "resizeCNHelixFront failed!"

    def resizeCNHelixBack(self, helix, delta):
        #print "resizeCNHelixBack"
        try:
            strand = self.getStrand(helix)
            lowIdx, highIdx = strand.idxs()
            newHigh = highIdx + delta
            newHigh = min(newHigh, strand.part().maxBaseIdx())
            newHigh = max(newHigh, lowIdx + 1)
            if(newHigh != highIdx):
                helix.newStrandSize = (lowIdx, newHigh)
        except:
            print "resizeCNHelixBack failed!"


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
