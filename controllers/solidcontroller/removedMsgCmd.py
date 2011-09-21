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

# Example Code:
# from maya import cmds
# cmds.loadPlugin("removedMsgCmd.py")
# cmds.spRemovedMsg()

"""
removedMsgCmd.py
Created by Simon Breslav on 2011/09/06
A command that adds a callback function when a node is deleted
"""

import sys
import maya.OpenMaya as OpenMaya
import maya.OpenMayaMPx as OpenMayaMPx

from controllers.solidcontroller.mayaObjectManager import Mom
from controllers.erasetooloperation import EraseToolOperation

kPluginCmdName = "spRemovedMsg"

messageId = 0
messageIdSet = False

def removeCallback(id):
    try:
        OpenMaya.MMessage.removeCallback( id )
    except:
        sys.stderr.write( "Failed to remove callback\n" )
        raise

def dagParentRemovedCallback( child, parent, clientData ):
    #print "dagParentRemovedCallback..."
    #print "\tchild %s" % child.fullPathName()
    #print "\tparent %s" % parent.fullPathName()
    #print "\tclient data %s" % clientData
    
    mom = Mom()
    children = child.fullPathName().split("|")
    for c in children:
        if c.startswith("DNACylinderShape"):
            if mom.mayaToCn.has_key(c):
                strand = mom.mayaToCn[ c ]
                if strand:
                    print "Strand %s : %s needs removal" % (c, strand)
                    mom.removeIDMapping(c, strand)
                    startVBase = strand.vBase3
                    undoStack = strand.vStrand().vHelix.undoStack()
                    eraseOp  = EraseToolOperation(startVBase, undoStack)
                    eraseOp.actionEraseVstrandAt(strand)
                    eraseOp.end()
                else:
                    print "Error: no Strand inside mayaObjectModel"
            else:
                pass
                #print "dagParentRemovedCallback: %s already deleted" % c
        elif c.startswith("stapleModIndicatorMesh"):
            if mom.stapleModToSolidHelix.has_key(c):
                stapleModObject = mom.stapleModToSolidHelix[ c ]
                solidHelix = stapleModObject[0]
                solidHelix.upadateStapleModIndicators(True)

def createParentAddedCallback(stringData):
    # global declares module level variables that will be assigned
    global messageIdSet
    try:
        id = OpenMaya.MDagMessage.addParentRemovedCallback( dagParentRemovedCallback, stringData )
    except:
        sys.stderr.write( "Failed to install dag parent removed callback\n" )
        messageIdSet = False
    else:
        messageIdSet = True
    return id

# command
class scriptedCommand(OpenMayaMPx.MPxCommand):
    def __init__(self):
        OpenMayaMPx.MPxCommand.__init__(self)
    def doIt(self,argList):
        global messageId
        if ( messageIdSet ):
            print "Message callaback already installed"
        else:
            print "Installing parent removed callback message"
            messageId = createParentAddedCallback( "_noData_" )

# Creator
def cmdCreator():
    return OpenMayaMPx.asMPxPtr( scriptedCommand() )
    
# Initialize the script plug-in
def initializePlugin(mobject):
    mplugin = OpenMayaMPx.MFnPlugin(mobject)
    try:
        mplugin.registerCommand( kPluginCmdName, cmdCreator )
    except:
        sys.stderr.write( "Failed to register command: %s\n" % name )
        raise

# Uninitialize the script plug-in
def uninitializePlugin(mobject):
    # Remove the callback
    if ( messageIdSet ):
        removeCallback( messageId )
    # Remove the plug-in command
    mplugin = OpenMayaMPx.MFnPlugin(mobject)
    try:
        mplugin.deregisterCommand( kPluginCmdName )
    except:
        sys.stderr.write( "Failed to unregister command: %s\n" % kPluginCmdName )
        raise

    
