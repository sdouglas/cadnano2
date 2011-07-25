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

"""
helixmetanode.py

Created by Simon Breslav on 2011-07-21

A Maya Node with metadate for SolidHelix
"""
import sys
import maya.OpenMaya as OpenMaya
import maya.OpenMayaMPx as OpenMayaMPx

nodeName = "spHelixMetaNode"
id = OpenMaya.MTypeId(0x3113)

class HelixMetaNode(OpenMayaMPx.MPxNode):
    
    scaleFrontAttr = OpenMaya.MObject()
    scaleBacktAttr = OpenMaya.MObject()
    
    scaleAttr = OpenMaya.MObject()
    translateAttr = OpenMaya.MObject()
    
    inputMesh = OpenMaya.MObject();
    outputMesh = OpenMaya.MObject()

    def __init__(self):
        OpenMayaMPx.MPxNode.__init__(self)

    def compute(self, plug, data):
        try:
            #if plug == HelixMetaNode.outputMesh:
            handle = data.inputValue(HelixMetaNode.inputMesh)
            meshObj = handle.data()
            fnMesh = OpenMaya.MFnMesh(meshObj)	
            fnMeshData = OpenMaya.MFnMeshData()
            outMeshDataObj = fnMeshData.create()
            outMeshObj = fnMesh.copy(meshObj, outMeshDataObj)
            
            
            #fnOutMesh = OpenMaya.MFnMesh(outMeshObj)
            handle = data.outputValue(HelixMetaNode.outputMesh)
            handle.setMObject(outMeshDataObj)
            handle.setClean()
            #data.setClean(plug)
            
            #elif plug == HelixMetaNode.scaleAttr:
            rightData = data.inputValue(HelixMetaNode.scaleFrontAttr)
            leftData = data.inputValue(HelixMetaNode.scaleBacktAttr)
            
            rightVal = rightData.asDouble()
            leftVal = leftData.asDouble()
            totalVal = rightVal + leftVal
            
            scaleHandle = data.outputValue(HelixMetaNode.scaleAttr)
            scaleHandle.setDouble(totalVal)
            
            totalTranslation = (rightVal - leftVal);
            
            translateHandle = data.outputValue(HelixMetaNode.translateAttr)
            translateHandle.setDouble(totalTranslation)            
            
            data.setClean(plug)
            #else:
            #    return OpenMaya.kUnknownParameter
        except:
            print "Error in %s\n" % nodeName
            raise

def nodeCreator():
    return OpenMayaMPx.asMPxPtr( HelixMetaNode() )

def nodeInitialize():
    #unitAttr = OpenMaya.MFnUnitAttribute()
    typedAttr = OpenMaya.MFnTypedAttribute()    
    HelixMetaNode.inputMesh = typedAttr.create( "inputMesh","im", OpenMaya.MFnData.kMesh)
    HelixMetaNode.outputMesh = typedAttr.create("outputMesh", "out", OpenMaya.MFnData.kMesh)

    nAttr = OpenMaya.MFnNumericAttribute()
    HelixMetaNode.scaleFrontAttr = nAttr.create('scaleFront', 'sr', OpenMaya.MFnNumericData.kDouble, 0.0)
    nAttr.setStorable(True)
    HelixMetaNode.scaleBacktAttr = nAttr.create('scaleBack', 'sl', OpenMaya.MFnNumericData.kDouble, 0.0)
    nAttr.setStorable(True)
    
    HelixMetaNode.scaleAttr = nAttr.create('scale', 's', OpenMaya.MFnNumericData.kDouble, 1.0)
    nAttr.setWritable(False)
    nAttr.setStorable(False)
    HelixMetaNode.translateAttr = nAttr.create('translate', 't', OpenMaya.MFnNumericData.kDouble, 1.0)
    nAttr.setWritable(False)
    nAttr.setStorable(False)


 
    HelixMetaNode.addAttribute(HelixMetaNode.inputMesh)    
    HelixMetaNode.addAttribute(HelixMetaNode.outputMesh)
    HelixMetaNode.addAttribute(HelixMetaNode.scaleFrontAttr)
    HelixMetaNode.addAttribute(HelixMetaNode.scaleBacktAttr)
    HelixMetaNode.addAttribute(HelixMetaNode.scaleAttr)
    HelixMetaNode.addAttribute(HelixMetaNode.translateAttr)
    
    HelixMetaNode.attributeAffects(HelixMetaNode.inputMesh, HelixMetaNode.outputMesh)
    
    HelixMetaNode.attributeAffects(HelixMetaNode.scaleBacktAttr, HelixMetaNode.scaleAttr)
    HelixMetaNode.attributeAffects(HelixMetaNode.scaleFrontAttr, HelixMetaNode.scaleAttr)
    HelixMetaNode.attributeAffects(HelixMetaNode.scaleBacktAttr, HelixMetaNode.translateAttr)
    HelixMetaNode.attributeAffects(HelixMetaNode.scaleFrontAttr, HelixMetaNode.translateAttr)
    
    HelixMetaNode.attributeAffects(HelixMetaNode.scaleAttr, HelixMetaNode.outputMesh)
    HelixMetaNode.attributeAffects(HelixMetaNode.scaleFrontAttr, HelixMetaNode.outputMesh)
    HelixMetaNode.attributeAffects(HelixMetaNode.scaleBacktAttr, HelixMetaNode.outputMesh)
    HelixMetaNode.attributeAffects(HelixMetaNode.translateAttr, HelixMetaNode.outputMesh)

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
        sys.stderr.write("Failed to deregister node %s\n" %    nodeName)
        raise
