###############################################################################
#  
# Copyright 2011 Autodesk, Inc.  All rights reserved.
#  
# The MIT License
#  
# Permission is hereby granted, free of charge, to any person obtaining a copy of
# this software and associated documentation files ( the "Software" ), to deal in
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


import sys
import maya.OpenMaya as OpenMaya
import maya.OpenMayaUI as OpenMayaUI
import maya.OpenMayaMPx as OpenMayaMPx

helixManipId = OpenMaya.MTypeId( 0x87009 )
contextCmdName = "spHelixManipCtxCmd"
nodeName = "spHelixManip"

class helixManip( OpenMayaMPx.MPxManipContainer ):
    fDistanceFrontManip = OpenMaya.MDagPath()
    fDistranceBackManip = OpenMaya.MDagPath()
    # startPos = OpenMaya.MObject()
    # endPos = OpenMaya.MObject()
    start3DPosAttr = OpenMaya.MObject()
    end3DPosAttr = OpenMaya.MObject()        
    
    #fFreePointManip = OpenMaya.MDagPath()

    def __init__( self ):
        #print "helixManip: constructor init called"
        OpenMayaMPx.MPxManipContainer.__init__( self )

    def createChildren( self ):
        #print "helixManip: createChildren being called..."
        # startPoint should correspond to the end of the helix
        # read the attribute to get the offset from the starting position
        self.fDistanceFrontManip = self.addDistanceManip( "distanceManip", "distance" )
        distanceManipFn = OpenMayaUI.MFnDistanceManip( self.fDistanceFrontManip )
        startPoint = OpenMaya.MPoint( 0.0, 0.0, 0.0 )
        direction = OpenMaya.MVector( 0.0, 1.0, 0.0 )
        distanceManipFn.setStartPoint( startPoint )
        distanceManipFn.setDirection( direction )
        # self.fFreePointManip = self.addFreePointTriadManip( "pointManip", "freePoint" )

        self.fDistanceBackManip = self.addDistanceManip( "distanceManip", "distance" )
        distanceManipFn = OpenMayaUI.MFnDistanceManip( self.fDistanceBackManip )
        startPoint = OpenMaya.MPoint( 0.0, 0.0, 0.0 )
        direction = OpenMaya.MVector( 0.0, -1.0, 0.0 )
        distanceManipFn.setStartPoint( startPoint )
        distanceManipFn.setDirection( direction )
        #print "helixManip createChildren called"

    def connectToDependNode( self, node ):
        #print "helixManip: connectToDependNode being called"
        #print "helixManip:connectToDependNode, type of node passed in is: %s" % node.apiTypeStr()
        #print "helixManip:connectToDependNode -- trying the cast this node as a dependency node"
        nodeFn = OpenMaya.MFnDependencyNode( node )
        #print nodeFn.name()

        try:
            frontPlug  = nodeFn.findPlug( "end" )
            backPlug = nodeFn.findPlug( "start" )
            frontPosPlug = nodeFn.findPlug( "startPos" )
            backPosPlug = nodeFn.findPlug( "endPos" )
            
            distanceManipFn = OpenMayaUI.MFnDistanceManip(  self.fDistanceFrontManip )
            distanceManipFn.connectToDistancePlug(  frontPlug )
            # freePointManipFn = OpenMayaUI.MFnFreePointTriadManip( self.fFreePointManip )
            # freePointManipFn.connectToPointPlug( tPlug )

            distanceManipFn = OpenMayaUI.MFnDistanceManip(  self.fDistanceBackManip )
            distanceManipFn.connectToDistancePlug(  backPlug )

            OpenMayaMPx.MPxManipContainer.finishAddingManips( self )
            OpenMayaMPx.MPxManipContainer.connectToDependNode( self,node )
            #print "helixManip connected to node " + nodeFn.name()
        except:
            sys.stderr.write(  "helixManip: Error finding and connecting plugs\n" )
            # raise
    #def compute( self, plug, data )
    #    try:
    #        print "helixManip computing data"
    #    except:
    #        print "Error in compute for helixManip node"
    #        raise

    def getRotation( self, nodePath ):
        dagFn = OpenMaya.MFnDagNode( nodePath )
        path = OpenMaya.MDagPath()
        dagFn.getPath( path )
        transformFn = OpenMaya.MFnTransform( path )
        q = OpenMaya.MQuaternion()
        transformFn.getRotation( q, OpenMaya.MSpace.kWorld )
        return q
    
    def getTranslation( self, nodePath ):
        dagFn = OpenMaya.MFnDagNode( nodePath )
        path = OpenMaya.MDagPath()
        dagFn.getPath( path )
        transformFn = OpenMaya.MFnTransform( path )
        return transformFn.translation( OpenMaya.MSpace.kWorld )
    
    def matchNodePosition( self, transformNode, helixNode ):
        trans = self.getTranslation( transformNode )
        q = self.getRotation( transformNode )
        
        #helixNodeFn = OpenMaya.MFnDependencyNode( helixNode )
        #startPos = OpenMaya.MPoint( helixNodeFn.attribute( "startPos" ) ); # TODO type checking
        #endPos = OpenMaya.MPoint( helixNodeFn.attribute( "endPos" ) );
        #print "startPos is"
        #print startPos
        #print "endPos is"
        #print endPos
        freePointManipFn1 = OpenMayaUI.MFnDistanceManip( self.fDistanceFrontManip  )
        freePointManipFn2 = OpenMayaUI.MFnDistanceManip( self.fDistanceBackManip )
        vecZ = OpenMaya.MVector( 0.0, 1.0, 0.0 )
        vecMinusZ = OpenMaya.MVector( 0.0, -1.0, 0.0 )
    
        # freePointManipFn1.setStartPoint( startPos )
        freePointManipFn1.setDirection( vecZ )
        freePointManipFn1.rotateBy( q )
        freePointManipFn1.setTranslation( trans, OpenMaya.MSpace.kWorld )
    
        # freePointManipFn2.setStartPoint( endPos )
        freePointManipFn2.setDirection( vecMinusZ )
        freePointManipFn2.rotateBy( q )
        freePointManipFn2.setTranslation( trans, OpenMaya.MSpace.kWorld )

def getHelixNodeFromTransform( transformNode ):
    funcSig = "helixManip:getHelixNodeFromTransform "
    # given a transform node, find the helix node attached to it
    try:
        #print funcSig + "calling getHelixNodeFromTransform with node"
        #print transformNode
        #print funcSig + "node type is %s" % transformNode.apiTypeStr()
        if transformNode.apiType() != OpenMaya.MFn.kTransform:
            #print funcSig + "incorrect node type passed in, need transform!"
            raise
        
        # walk the dag on the transform and find the mesh and then the helixNode
        dagNode = OpenMaya.MFnDagNode()
        dagComponentObjects = OpenMaya.MObject()
        dagNode = OpenMaya.MFnDagNode( transformNode )
        if dagNode.childCount() == 0:
            #print funcSig + "Incorrect number of dag children from transform"
            raise
        
        child = OpenMaya.MObject()
        child = dagNode.child( 0 )
        
        if child.apiType() != OpenMaya.MFn.kMesh:
            #print funcSig + "Unexpected child of transform, expected kMesh"
            raise
        
        helixMesh = OpenMaya.MFnMesh( child )
        inMeshPlug = OpenMaya.MPlug()
        try:
            inMeshPlug = helixMesh.findPlug( "inMesh" )
        except:
            #print funcSig + "Can't find inMesh plug on Mesh. Not a helixNode mesh?"
            raise
               
        connectors = OpenMaya.MPlugArray();
        inMeshPlug.connectedTo( connectors, True, False )
        
        plug = OpenMaya.MPlug()
        if connectors.length() != 1:
            #print funcSig + "Incorrect number of connectors from Mesh to HelixNode, not a helixMesh?"
            raise

        helixNode = OpenMaya.MObject()        
        for i in range( connectors.length() ):
            plug = connectors[ i ]
            helixNode = plug.node()
            #print funcSig + "found helix node plug, APItype string %s" % helixNode.apiTypeStr()
        
        if helixNode.apiType() == OpenMaya.MFn.kInvalid:
            #print funcSig + "failed to find connecting node!"
            helixNode = None
            raise
            
        return helixNode    
                       
    except:
        #print "helixManip:getHelixNodeFromTransform failed! unable to get the helix node from transform!"
        return None

def updateManipulators( clientData ):
        #print "helixManip: updateManipulators called"
        clientData.deleteManipulators()
        selectionList = OpenMaya.MSelectionList()

        OpenMaya.MGlobal.getActiveSelectionList( selectionList )
        selectionIter = OpenMaya.MItSelectionList( selectionList, OpenMaya.MFn.kInvalid )
        # selectionIter.setFilter( OpenMaya.MFn.kPluginDependNode )
        while not selectionIter.isDone():
                #print "helixManip: walking a selecting node, should be kPluginDependNode type"
                dependNode = OpenMaya.MObject()
                try:
                        selectionIter.getDependNode( dependNode )
                except:
                        selectionIter.next()
                        continue
                #print "helixManip: walking selection and dependNode type is " + dependNode.apiTypeStr()

                if dependNode.isNull() or not dependNode.hasFn( OpenMaya.MFn.kDependencyNode ):
                        #print "helixManip: depend node is null"
                        selectionIter.next()
                        continue

                #print "helixManip: the selection iterator is of type : "
                #print selectionIter.itemType()
                
                helixNode = OpenMaya.MObject();
                helixNode = getHelixNodeFromTransform( dependNode )
                if helixNode is None:
                    #print "helixManip: helixNode not found!"
                    selectionIter.next()
                    continue
                
                
                manipObject = OpenMaya.MObject() # should this be helixmetanode() ?
                manipulator = OpenMayaMPx.MPxManipContainer.newManipulator( nodeName, manipObject )
                if manipulator is not None:
                    clientData.addManipulator( manipObject )
                    transformNodePath = OpenMaya.MDagPath()
                    # components = OpenMaya.MObject()
                    selectionIter.getDagPath( transformNodePath )
                    manipulator.connectToDependNode( helixNode )
                    manipulator.matchNodePosition( transformNodePath, helixNode )
                selectionIter.next()
                
    
def helixManipCreator():
    #print "helixManip: helixManipCreator called"
    return OpenMayaMPx.asMPxPtr( helixManip() )

def helixManipInitialize():
        #print "helixManip: helixManipInitialize called"
        OpenMayaMPx.MPxManipContainer.initialize()
        typedAttr = OpenMaya.MFnTypedAttribute()
        nAttr = OpenMaya.MFnNumericAttribute()

        helixManip.start3DPosAttr = nAttr.create( 'startPos',
                                                  'sp',
                                                  OpenMaya.MFnNumericData.k3Float,
                                                  0.0 )
        nAttr.setWritable(True)
        nAttr.setStorable(False)
        helixManip.end3DPosAttr = nAttr.create( 'endPos',
                                                'ep',
                                                OpenMaya.MFnNumericData.k3Float,
                                                0.0 )
        nAttr.setWritable(True)
        nAttr.setStorable(False)
        
        helixManip.addAttribute( helixManip.start3DPosAttr )
        helixManip.addAttribute( helixManip.end3DPosAttr )
        

class helixManipContext( OpenMayaMPx.MPxSelectionContext ):
    def __init__( self ):
        #print "helixManip: helixManipContext init called"
        OpenMayaMPx.MPxSelectionContext.__init__( self )
    def toolOnSetup( self,event ):
        #print "helixManip: helixManipContext toolOnSetup called"
        updateManipulators( self )
        OpenMaya.MModelMessage.addCallback(  OpenMaya.MModelMessage.kActiveListModified, 
                                            updateManipulators, self )
class helixManipCtxCmd( OpenMayaMPx.MPxContextCommand ):
    def __init__( self ):
        #print "helixManip: helixManipCtxCMd init called"
        OpenMayaMPx.MPxContextCommand.__init__( self )

    def makeObj( self ):
        #print "helixManipCtxCmd makeObj called"
        return OpenMayaMPx.asMPxPtr( helixManipContext() )


def contextCmdCreator():
    #print "helixManip: contextCmdCreator called"
    return OpenMayaMPx.asMPxPtr(  helixManipCtxCmd() )


# initialize the script plug-in
def initializePlugin( mobject ):
    #print "helixManip: initializePlugin for helixManip called"
    mplugin = OpenMayaMPx.MFnPlugin( mobject )

    try:
        mplugin.registerContextCommand( contextCmdName, contextCmdCreator )
    except:
        print "helixManip: Failed to register context command: %s" % contextCmdName
        raise
    
    try:
        mplugin.registerNode( nodeName, helixManipId, helixManipCreator, helixManipInitialize, OpenMayaMPx.MPxNode.kManipContainer )
    except:
        print "helixManip: Failed to register node: %s" % nodeName
        raise

# uninitialize the script plug-in
def uninitializePlugin( mobject ):
    #print "helixManip uninitializePlugin for helixManip called"
    mplugin = OpenMayaMPx.MFnPlugin( mobject )
    try:
        mplugin.deregisterContextCommand( contextCmdName )
    except:
        print "helixManip: Failed to deregister context command: %s" % contextCmdName
        raise
        
    try:
        mplugin.deregisterNode( helixManipId )
    except:
        print "helixManip: Failed to deregister node: %s" % nodeName
        raise
