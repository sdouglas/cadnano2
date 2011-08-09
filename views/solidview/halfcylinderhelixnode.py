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
# http://www.opensource.org/licenses/mit-license.php

"""
halfcylinderhelixnode.py

Created by Simon Breslav on 2011-08-04

A Maya Node for creating Half-Cylinder Helix Shape 
"""
import sys
import maya.OpenMaya as OpenMaya
import maya.OpenMayaMPx as OpenMayaMPx
import math

nodeName = "spHalfCylinderHelixNode"
id = OpenMaya.MTypeId(0x3114)


class HalfCylinderHelixNode(OpenMayaMPx.MPxNode):
    outputMesh = OpenMaya.MObject()
    startAttr = OpenMaya.MObject()
    endAttr = OpenMaya.MObject()    
    angleAttr = OpenMaya.MObject()
    spacingAttr = OpenMaya.MObject()
    mayaScaleAttr = OpenMaya.MObject()
    start3DPosAttr = OpenMaya.MObject()
    end3DPosAttr = OpenMaya.MObject()        
    
    def __init__(self):
        OpenMayaMPx.MPxNode.__init__(self)
        self.start3DPos = OpenMaya.MFloatPoint()
        self.end3DPos = OpenMaya.MFloatPoint()

    def compute(self, plug, data):
        try:      
            fnMeshData = OpenMaya.MFnMeshData()
            outMeshDataObj = fnMeshData.create()
            endData = data.inputValue(HalfCylinderHelixNode.endAttr)
            startData = data.inputValue(HalfCylinderHelixNode.startAttr)
            startVal = startData.asDouble()
            totalVal = startVal+endData.asDouble()
            angleData = data.inputValue(HalfCylinderHelixNode.angleAttr)
            spacingData = data.inputValue(HalfCylinderHelixNode.spacingAttr)
            mayaScaleData = data.inputValue(HalfCylinderHelixNode.mayaScaleAttr)
            self.createMesh(startVal, totalVal, angleData.asDouble(), 
                            spacingData.asDouble(), 
                            mayaScaleData.asInt(), 
                            outMeshDataObj)   
                            
            startPosHandle = data.outputValue(HalfCylinderHelixNode.start3DPosAttr)
            startPosHandle.set3Float (self.start3DPos[0], self.start3DPos[1], self.start3DPos[2])
            endPosHandle = data.outputValue(HalfCylinderHelixNode.start3DPosAttr)
            endPosHandle.set3Float (self.end3DPos[0], self.end3DPos[1], self.end3DPos[2])
            
            handle = data.outputValue(HalfCylinderHelixNode.outputMesh)
            handle.setMObject(outMeshDataObj)
            handle.setClean()
            data.setClean(plug)
        except:
            print "Error in %s\n" % nodeName
            raise

    def createMesh(self, start, size, angleAttr, spacingAttr, mayaScale, outData):
        # These parameters need refactoring...
        maya_scale = mayaScale
        numVerticesEnds = 20 
        numMiddleSections = int(size*maya_scale)
        dist_offset = spacingAttr  
        start_pos = -start * dist_offset * maya_scale
        numVerticesTotal = (numVerticesEnds * 2) + numMiddleSections*numVerticesEnds
        radius = 0.5
        rot_ang = angleAttr 

        numFacesEnds = numVerticesEnds-2
        numFacesTotal = (numVerticesEnds-2)*2 +  (numVerticesEnds)* (numMiddleSections+1)
        numFaceConnects = ((numVerticesEnds-2) * 2 * 3) + (numVerticesEnds * (numMiddleSections+1) * 4)

        vtx = []
        angle = 0    
        # Create Endpice verts       
        vtx.append( OpenMaya.MFloatPoint(0.0, start_pos, 0.0) )
        self.start3DPos = OpenMaya.MFloatPoint(0.0, start_pos, 0.0)         
        for i in range(1,numVerticesEnds):
            val = i*(180/(numFacesEnds))
            rad = (val*math.pi)/180
            vtx.append( OpenMaya.MFloatPoint( radius * math.cos(rad), start_pos, radius*math.sin(rad)) )
        # Create Middle verts
        for i in range(0,numMiddleSections):
            angle = rot_ang * (i+1)
            pos = dist_offset* (i+1)
            vtx.append( OpenMaya.MFloatPoint(0.0, start_pos+pos, 0.0) )                
            for i in range(1,numVerticesEnds):
                val = i*(180/(numFacesEnds))
                rad = (val*math.pi)/180
                #print "vrt %d, %f %f" % (i, val, rad) 
                x = radius * math.cos(rad+angle)
                y = radius*math.sin(rad+angle)     
                vtx.append( OpenMaya.MFloatPoint( x, start_pos+pos, y) )        

        # Create EndPiece verts
        vtx.append( OpenMaya.MFloatPoint(0.0, start_pos+(numMiddleSections+1)*dist_offset, 0.0) )
        self.end3DPos = OpenMaya.MFloatPoint(0.0, start_pos+(numMiddleSections+1)*dist_offset, 0.0)
        for i in range(1,numVerticesEnds):
            angle = rot_ang * (1+numMiddleSections)
            val = i*(180/(numFacesEnds))
            rad = (val*math.pi)/180
            #print "vrt %d, %f %f" % (i, val, rad) 
            x = radius * math.cos(rad+angle)
            y = radius*math.sin(rad+angle)
            vtx.append( OpenMaya.MFloatPoint( x, start_pos+(numMiddleSections+1)*dist_offset, y) )
        #print "vtx length %d"  % len(vtx)
        points = OpenMaya.MFloatPointArray()
        points.setLength(numVerticesTotal)

        for i in range(0,numVerticesTotal):
            points.set(vtx[i], i)

        faceConnects = OpenMaya.MIntArray()
        faceConnects.setLength(numFaceConnects)
        #print "numFaceConnects %d" % numFaceConnects
        offset = 1
        count = 0
        for i in range(0,numFacesEnds):
            faceConnects.set(0, count)
            count +=1
            faceConnects.set(offset, count)
            offset += 1
            count +=1
            faceConnects.set(offset, count)
            count +=1

        for k in range(0,numMiddleSections+1):
            for i in range(0, numVerticesEnds):
                if i < numVerticesEnds-1:
                    v1 = (k*numVerticesEnds)+i
                    v2 = (k*numVerticesEnds)+1+i
                    v3 = ((k+1)*numVerticesEnds)+i
                    v4 = ((k+1)*numVerticesEnds)+1+i
                else:
                    v1 = (k*numVerticesEnds)+i
                    v2 = (k*numVerticesEnds)
                    v3 = ((k+1)*numVerticesEnds)+i
                    v4 = ((k+1)*numVerticesEnds)

                faceConnects.set(v1, count)
                count +=1
                faceConnects.set(v2, count)
                count +=1
                faceConnects.set(v4, count)
                count +=1
                faceConnects.set(v3, count)
                count +=1

        offset = numVerticesTotal-numVerticesEnds+1
        for i in range(numFacesTotal-numFacesEnds, numFacesTotal):
            #print numVerticesTotal-numVerticesEnds
            #print offset 
            faceConnects.set(numVerticesTotal-numVerticesEnds, count)
            count +=1
            faceConnects.set(offset, count)
            offset += 1
            count +=1
            #print offset 
            faceConnects.set(offset, count)
            count +=1

        #print "face connect ended at %d" % count
        faceCounts = OpenMaya.MIntArray()
        faceCounts.setLength(numFacesTotal)
        count = 0
        for i in range(0,numFacesEnds):
            #print count            
            faceCounts.set(3, count)
            count += 1
        for i in range(numFacesEnds, numFacesTotal-numFacesEnds):
            #print count    
            faceCounts.set(4, count)
            count += 1
        for i in range(numFacesTotal-numFacesEnds, numFacesTotal):
            #print count    
            faceCounts.set(3, count)
            count += 1
        #print "face count ended at %d" % count
        meshFS = OpenMaya.MFnMesh()
        meshFS.create(numVerticesTotal, numFacesTotal, points, faceCounts, faceConnects, outData)

def nodeCreator():
    return OpenMayaMPx.asMPxPtr(HalfCylinderHelixNode())

def nodeInitialize():
    #unitAttr = OpenMaya.MFnUnitAttribute()
    typedAttr = OpenMaya.MFnTypedAttribute()
    HalfCylinderHelixNode.outputMesh = typedAttr.create("outputMesh",
                                                "out",
                                                OpenMaya.MFnData.kMesh)

    nAttr = OpenMaya.MFnNumericAttribute()

    HalfCylinderHelixNode.startAttr = nAttr.create('start',
                                    'st',
                                    OpenMaya.MFnNumericData.kDouble,
                                    0.0)
    nAttr.setStorable(True)       
    HalfCylinderHelixNode.endAttr = nAttr.create('end',
                                    'sa',
                                    OpenMaya.MFnNumericData.kDouble,
                                    0.0)
    nAttr.setStorable(True)
    
    HalfCylinderHelixNode.spacingAttr = nAttr.create('scale',
                                    's',
                                    OpenMaya.MFnNumericData.kDouble,
                                    0.1)
    nAttr.setMin(0.01)
    nAttr.setMax(1.0)
    nAttr.setStorable(True)
    HalfCylinderHelixNode.mayaScaleAttr = nAttr.create('mayaMapping',
                                    'mm',
                                    OpenMaya.MFnNumericData.kInt,
                                    3)
    nAttr.setMin(1)
    nAttr.setMax(20)
    nAttr.setStorable(True)
    
    HalfCylinderHelixNode.start3DPosAttr = nAttr.create('startPos',
                                            'sp',
                                            OpenMaya.MFnNumericData.k3Float,
                                            0.0)
    nAttr.setWritable(False)
    nAttr.setStorable(False)
    HalfCylinderHelixNode.end3DPosAttr = nAttr.create('endPos',
                                            'ep',
                                            OpenMaya.MFnNumericData.k3Float,
                                            0.0)
    nAttr.setWritable(False)
    nAttr.setStorable(False)

    unitFn = OpenMaya.MFnUnitAttribute() 
    HalfCylinderHelixNode.angleAttr = unitFn.create('angle',
                                    'a',
                                    OpenMaya.MFnUnitAttribute.kAngle,
                                    10.0 * math.pi / 180)
    unitFn.setMin(0.0)
    unitFn.setMax(math.pi)
    unitFn.setStorable(True)
    
    

    HalfCylinderHelixNode.addAttribute(HalfCylinderHelixNode.outputMesh)
    HalfCylinderHelixNode.addAttribute(HalfCylinderHelixNode.startAttr)    
    HalfCylinderHelixNode.addAttribute(HalfCylinderHelixNode.endAttr)
    HalfCylinderHelixNode.addAttribute(HalfCylinderHelixNode.angleAttr)
    HalfCylinderHelixNode.addAttribute(HalfCylinderHelixNode.spacingAttr)
    HalfCylinderHelixNode.addAttribute(HalfCylinderHelixNode.mayaScaleAttr)
    HalfCylinderHelixNode.addAttribute(HalfCylinderHelixNode.start3DPosAttr)
    HalfCylinderHelixNode.addAttribute(HalfCylinderHelixNode.end3DPosAttr)
    HalfCylinderHelixNode.attributeAffects(HalfCylinderHelixNode.endAttr, HalfCylinderHelixNode.outputMesh)
    HalfCylinderHelixNode.attributeAffects(HalfCylinderHelixNode.startAttr, HalfCylinderHelixNode.outputMesh)
    HalfCylinderHelixNode.attributeAffects(HalfCylinderHelixNode.angleAttr, HalfCylinderHelixNode.outputMesh)
    HalfCylinderHelixNode.attributeAffects(HalfCylinderHelixNode.spacingAttr, HalfCylinderHelixNode.outputMesh)
    HalfCylinderHelixNode.attributeAffects(HalfCylinderHelixNode.mayaScaleAttr, HalfCylinderHelixNode.outputMesh)
    
    HalfCylinderHelixNode.attributeAffects(HalfCylinderHelixNode.endAttr, HalfCylinderHelixNode.start3DPosAttr)
    HalfCylinderHelixNode.attributeAffects(HalfCylinderHelixNode.startAttr, HalfCylinderHelixNode.start3DPosAttr)
    HalfCylinderHelixNode.attributeAffects(HalfCylinderHelixNode.spacingAttr, HalfCylinderHelixNode.start3DPosAttr)
    HalfCylinderHelixNode.attributeAffects(HalfCylinderHelixNode.mayaScaleAttr, HalfCylinderHelixNode.start3DPosAttr)
    
    HalfCylinderHelixNode.attributeAffects(HalfCylinderHelixNode.endAttr, HalfCylinderHelixNode.end3DPosAttr)
    HalfCylinderHelixNode.attributeAffects(HalfCylinderHelixNode.startAttr, HalfCylinderHelixNode.end3DPosAttr)
    HalfCylinderHelixNode.attributeAffects(HalfCylinderHelixNode.spacingAttr, HalfCylinderHelixNode.end3DPosAttr)
    HalfCylinderHelixNode.attributeAffects(HalfCylinderHelixNode.mayaScaleAttr, HalfCylinderHelixNode.start3DPosAttr)
   
    HalfCylinderHelixNode.attributeAffects(HalfCylinderHelixNode.outputMesh, HalfCylinderHelixNode.start3DPosAttr)
    HalfCylinderHelixNode.attributeAffects(HalfCylinderHelixNode.outputMesh, HalfCylinderHelixNode.end3DPosAttr)

def initializePlugin(obj):
    plugin = OpenMayaMPx.MFnPlugin(obj)

    try:
        plugin.registerNode(nodeName, id, nodeCreator, nodeInitialize)
    except:
        sys.stderr.write("Failed to register node %s\n" % nodeName)
        raise

def uninitializePlugin(obj):
    plugin = OpenMayaMPx.MFnPlugin(obj)

    try:
        plugin.deregisterNode(id)
    except:
        sys.stderr.write("Failed to deregister node %s\n" % nodeName)
        raise
