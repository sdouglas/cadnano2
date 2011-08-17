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
solidhelixgroup.py

Created by Nick Conway on 2011-02-04.
Re-Created by Simon Breslav on 2011-07-21
(old version can found at the end of the file)

For use controlling 3D solid models generated in Maya
"""

from string import *
import math
import random
import os
import sys
from views import styles
from model.enum import LatticeType
from model.enum import StrandType

import maya.OpenMayaUI as mui
import maya.OpenMaya as mo
import maya.cmds as cmds
import util

# import Qt stuff into the module namespace with PySide, PyQt4 independence
util.qtWrapImport('QtCore', globals(), ['pyqtSignal', 'pyqtSlot', 'QObject'])


class SolidHelixGroup(QObject):
    """
    A Solid Hinstance is meant to store helix data in Maya
    representing a pathhelixgroup.
    """
    def __init__(self, dnaPartInst, htype=LatticeType.Honeycomb,
                 controller=None, parent=None):
        """
        """
        super(SolidHelixGroup, self).__init__()
        self.setPart(dnaPartInst)
        pluginPath = os.path.join(os.environ['CADNANO_PATH'], "views",
                                  "solidview", "halfcylinderhelixnode.py")

        if (not cmds.pluginInfo(pluginPath, query=True, loaded=True)):
            cmds.loadPlugin(pluginPath)

        if (not cmds.pluginInfo(pluginPath, query=True, loaded=True)):
            print "HalfCylinderHelixNode failed to load"
            return

        print "maya SolidHelixGroup created"
        self.type = htype
        # self.mayaScale = 1.0
        # later updates using basecount from the VH
        # XXX [SB] - need to ask CandNano for rows and cols...
        # top left cornder of maya 3d scene X Y Z
        self.mayaOrigin = (-15 * 2.25, 16 * 2.25, 0.0)
        self.helixRadius = 1.125  # diamiter is 2.25nm
        self.solidHelicesIndices = {}
        self.solidHelicesIndicesCount = 0

    def part(self):
        # part
        return self._part

    def setPart(self, p):
        # setPart
        self._part = p
        self._part.persistentDataChanged.connect(self.onPersistentDataChanged)
        print "SolidHelixGroup.setPart: signals setup"

    def updateStrands(self, strandType):
        for vh in self._part.getVirtualHelices():
            myKey = '%d_%d_%d' % (vh.coord()[0], vh.coord()[1], strandType)

            if myKey not in self.solidHelicesIndices.keys():
                if strandType == StrandType.Scaffold:
                    self.createNewHelix(vh.coord()[0], vh.coord()[1],
                                        strandType, 1)
                else:
                    self.createNewHelix(vh.coord()[0], vh.coord()[1],
                                        strandType, 0)
            itemIndices = self.solidHelicesIndices[myKey]
            endpoints = vh.getSegmentsAndEndpoints(strandType)
            segmentsCount = len(endpoints[0])
            #print "%s %d %s" % (myKey, segmentsCount, endpoints)
            if (len(itemIndices) != segmentsCount):
                # Delete current itemIndices
                #print "Need to delete a strands"
                self.deleteHelix(vh.coord()[0], vh.coord()[1], strandType)
                # create new indeces
                self.createNewHelix(vh.coord()[0], vh.coord()[1],
                                    strandType, segmentsCount)

            if(segmentsCount < 1):
                continue
            itemIndices = self.solidHelicesIndices[myKey]
            parity = not self._part.virtualHelixParityEven(vh) # 0 -> even
            for seg in range(segmentsCount):
                cylinderName = "HalfCylinderHelixNode%d" % itemIndices[seg]
                #transformName = "DNAShapeTranform%d" % itemIndex
                totalNumBases = vh.numBases()
                cmds.setAttr("%s.startBase" % cylinderName,
                             endpoints[0][seg][0])
                cmds.setAttr("%s.endBase" % cylinderName,
                             endpoints[0][seg][1])
                cmds.setAttr("%s.totalBases" % cylinderName, totalNumBases)
                if self.type == LatticeType.Honeycomb:
                    cmds.setAttr("%s.rotation" % cylinderName, 34.286)
                    cmds.setAttr("%s.rotationOffset" % cylinderName, 30)
                    cmds.setAttr("%s.parity" % cylinderName, parity)
                elif self.type == LatticeType.Square:
                    cmds.setAttr("%s.rotation" % cylinderName, 33.75)
                    cmds.setAttr("%s.rotationOffset" % cylinderName, 60)
                    cmds.setAttr("%s.parity" % cylinderName, parity)
                else:
                    raise NotImplementedError
                cmds.setAttr("%s.strandType" % cylinderName, strandType)
                shaderName = "DNAStrandShader%d" % itemIndices[seg]
                color = vh.colorOfBase(strandType, int(endpoints[0][seg][0]))
                cmds.setAttr("%s.color" % shaderName,
                             color.redF(), color.greenF(), color.blueF(),
                             type="double3")

    def onPersistentDataChanged(self):
        # Update in the Model
        self.updateStrands(StrandType.Scaffold)
        self.updateStrands(StrandType.Staple)

    def cadnanoToMayaCoords(self, row, col):
        # cadnanoToMayaCoords
        if self.type == LatticeType.Honeycomb:
            #print "LatticeType.Honeycomb"
            x = self.mayaOrigin[0] + (col * math.sqrt(3) * self.helixRadius)
            if ((row % 2) ^ (col % 2)):  # odd parity
                y = self.mayaOrigin[1] - (row * self.helixRadius * 3.0 + \
                                          self.helixRadius)
            else:
                y = self.mayaOrigin[1] - (row * self.helixRadius * 3.0)
        # end if
        elif self.type == LatticeType.Square:
            #print "LatticeType.Square"
            x = self.mayaOrigin[0] + (col * 2.0 * self.helixRadius)
            y = self.mayaOrigin[1] - (row * 2.0 * self.helixRadius)
        return (x, y)

    def deleteAllMayaNodes(self):
        # Delete Transform Nodes
        #cylinders = cmds.ls("CylinderNode*")
        #transforms = cmds.ls("DNAShapeTransform*")
        #for t in transforms:
        #     cmds.delete(t)
        nodes = cmds.ls("DNAShapeTransform*", "DNAStrandShader*", "pfxToon*")
        for n in nodes:
            cmds.delete(n)
        transforms = cmds.ls("DNAToon*", et="transform")
        for t in transforms:
            cmds.delete(t)
        self.solidHelicesIndices = {}
        self.solidHelicesIndicesCount = 0

    def deleteHelix(self, row, col, strandType):
        # deleteHelix
        myKey = '%d_%d_%d' % (row, col, strandType)
        itemIndices = self.solidHelicesIndices[myKey]

        for i in itemIndices:
            toonName = "pfxToon%d" % i
            toonName2 = "DNAToon%d" % i
            transformName = "DNAShapeTransform%d" % i
            shaderName = "DNAStrandShader%d" % i
            items = cmds.ls(toonName, transformName, shaderName)
            for i in items:
                cmds.delete(i)
            items2 = cmds.ls(toonName2, et="transform")
            for i in items2:
                cmds.delete(i)
        self.solidHelicesIndices[myKey] = []

    def createNewHelix(self, row, col, strandType, count=1):
        # New Helix Added
        #print "SolidHelixGroup.onAtCoordsChanged: %d %d" % (row, col)
        # figure out Maya Coordinates
        x, y = self.cadnanoToMayaCoords(row, col)
        indexList = []
        for i in range(count):
            self.solidHelicesIndicesCount += 1
            indexList.append(self.solidHelicesIndicesCount)
            self.createCylinder(x, y, self.solidHelicesIndicesCount, self.type)
        self.solidHelicesIndices['%d_%d_%d' % \
                                 (row, col, strandType)] = indexList

    def createCylinder(self, x, y, count, htype):
        # createCylinder
        #cylinderName = "CylinderNode%d" % count
        cylinderName = "HalfCylinderHelixNode%d" % count
        transformName = "DNAShapeTransform%d" % count
        meshName = "DNACylinderShape%d" % count
        #metaName = "HelixMetaNode%d" % count
        toonName = "DNAToonShape%d" % count
        shaderName = "DNAStrandShader%d" % count

        #cmds.createNode("polyCylinder", name=cylinderName)
        #cmds.setAttr("%s.radius"%cylinderName, self.helixRadius)
        cmds.createNode("transform", name=transformName)
        cmds.setAttr("%s.rotateX" % transformName, 90)
        cmds.setAttr("%s.translateX" % transformName, x)
        cmds.setAttr("%s.translateY" % transformName, y)

        cmds.createNode("mesh", name=meshName, parent=transformName)

        cmds.sets(meshName, add="initialShadingGroup")

        #cmds.createNode("spHelixMetaNode", name=metaName)
        cmds.createNode("spHalfCylinderHelixNode", name=cylinderName)
        cmds.connectAttr("%s.outputMesh" % cylinderName,
                         "%s.inMesh" % meshName)
        # Create Crease and Profile Lines
        cmds.createNode("pfxToon", name=toonName)
        cmds.connectAttr("%s.outMesh" % meshName,
                         "%s.inputSurface[0].surface" % toonName)
        cmds.connectAttr("%s.worldMatrix[0]" % meshName,
                         "%s.inputSurface[0].inputWorldMatrix" % toonName)
        cmds.setAttr("%s.displayPercent" % toonName, 100)
        cmds.setAttr("%s.tighterProfile" % toonName, 1)
        cmds.setAttr("%s.profileLineWidth" % toonName, 0.613497)
        cmds.setAttr("%s.lineWidth" % toonName, 0.0245399)
        cmds.setAttr("%s.hardCreasesOnly" % toonName, 0)
        cmds.setAttr("%s.creaseAngleMin" % toonName, 30.920245)
        cmds.setAttr("%s.depthOffset" % toonName, 6.533742)

        # Create a separate shader for each strand so that it can be colored
        # in different colors
        # XXX [SB] - Need to refactor this, shuld group stands of the
        # same color into one shader
        cmds.shadingNode('lambert', asShader=True, name=shaderName)
        cmds.sets(n="%sSG" % shaderName, r=True, nss=True, em=True)
        cmds.connectAttr("%s.outColor" % shaderName,
                         "%sSG.surfaceShader" % shaderName)
        cmds.sets(meshName, forceElement="%sSG" % shaderName)
        cmds.setAttr("%s.color" % shaderName,
                     0.313725, 0.397089, 0.941176, type="double3")


#class SolidHelixGroup(QObject):
#    """
#    A Solid Hinstance is meant to store helix data in Maya
#    representing a pathhelixgroup.
#
#    column nodes all have the same X coordinate
#    row nodes can have slightly different Y coordinates
#    (offset) for convenience of data representation
#    as is the case of the honeycomb representation
#
#    Parameters
#    ----------
#    rows: rows grid size
#    cols: columns grid size
#
#    See Also
#    --------
#
#    Examples
#    --------
#    """
#
#    # store slice nodes in hash accessible by "row,col" keys
#    def __init__(self, htype=LatticeType.Honeycomb,
#                 controller=None, parent=None):
#        """
#        Parameters
#        ----------
#        rows: rows grid size
#        cols: columns grid size
#
#        See Also
#        --------
#
#        Examples
#        --------
#        """
#        super(SolidHelixGroup, self).__init__()
#
#        self.number_hash = {}
#        self.type = htype
#        self.helix_diameter = 2.0
#        self.pointscale = self.helix_diameter/(2*styles.SLICE_HELIX_RADIUS)
#
#        # initialize the column direction stuff
#        self.column_dir = X
#        self.row_dir = Y
#        self.helix_dir = Z
#
#        # the limits of the indices of the output raster
#        self.row_count = 0
#        self.column_count = 0
#        self.helix_count = 0
#
#        self.h_axis = 'Z'
#        self.row_axis = 'Y'
#
#        # initialize the unit size of a base cell
#        self.drow = 0       # the row direction
#        #the direction normal to the row direction and the helical axis
#        self.dcolumn = 0
#        self.dhelix = 0     # the helical axis
#        self.model_scale = 1
#        self.unit_scale = 2
#        self.N_bases = 1
#        self.N_bases_default = 3
#        # set up the above parameters
#        self.calculateParameters()
#        print "maya group created"
#        self.group = pc.general.group(em=True,name='helixgroup0')
#
#        # the coloring of the cylinders is set here
#        shdr, sg = pc.createSurfaceShader( 'blinn' )
#        self.colorshader = sg
#        colorfill = styles.orangefill
#        # maya takes RGB component values from 0 to 1
#        shdr.setAttr('color', colorfill.redF(),
#                     colorfill.greenF(),colorfill.blueF(), type='double3')
#
#        print  pc.language.scriptJob( event=[u'SelectionChanged',self.cool])
#        #fromBaseCenter.MEventMessage.addEventCallback(u'SelectionChanged',
#                                                       self.cool)
#    # end def
#
#    def cool(self,*args):
#        print "Who?"
#        if args != None:
#            print args
#        print "Awesome job"
#
#    def calculateParameters(self):
#        """ calculate the core values of the cylinders """
#        if self.type == 'honeycomb':
#            self.dcolumn = self.helix_diameter*math.sqrt(3)/self.unit_scale
#            self.drow = 1.5*self.helix_diameter/self.unit_scale
#            self.dhelix = 0.34*self.N_bases/self.unit_scale
#        # end if
#        elif self.type == 'square':
#            self.dcolumn = 2*self.helix_diameter/self.unit_scale
#            self.drow = self.helix_diameter/self.unit_scale
#            self.dhelix = 0.34*self.N_bases/self.unit_scale
#        # end elif
#        else:
#            print "Undefined unit type\n"
#            exit()
#        # end else
#    # end def
#
#    def handleScaffoldChange(self,number):
#        """"""
#        self.number
#
#    # end def
#
#    @pyqtSlot('QPointF',int)
#    def helixAddedSlot(self, pos, number):
#        """
#        Retrieve reference to new VirtualHelix vh based on number relayed
#        by the signal event. Next, create a new PathHelix associated
#        with vh and draw it on the screen.
#
#        pos: a QPointF identifying a slice views XY position for a helix
#
#        """
#
#        axis = [0,0,0]
#        axis[self.helix_dir] = 1
#
#        # draw the default length helix
#        length = self.dhelix*self.N_bases_default
#
#        # figure out starting position
#        x = pos.x()*self.pointscale # scale input from slice view
#        # scale input from slice view make negative to invert the fact that
#        # Qt defines origins positve movingdownscreen from the top left corner
#        y = -pos.y()*self.pointscale + 29
#        print x, y
#        origin = [x/self.unit_scale, y/self.unit_scale, 0]
#
#        self.number_hash[number] = self.drawHelix(origin, length, axis,number)
#    # end def
#
#    def drawHexPair(self,start_point, end_point, orientation):
#
#        originA = [[],[],[]]
#        originB = [[],[],[]]
#
#        if (orientation == True):
#            column_offset = self.dcolumn/4
#            row_offset = self.drow/4
#        # end if
#        else:
#            column_offset = -self.dcolumn/4
#            row_offset = -self.drow/4
#        # end else
#        originA[self.column_dir] = start_point[self.column_dir]-column_offset
#        originB[self.column_dir] = start_point[self.column_dir]+column_offset
#        originA[self.row_dir] = start_point[self.row_dir]+row_offset
#        originB[self.row_dir] = start_point[self.row_dir]-row_offset
#
#        originA[self.helix_dir] =
#           (start_point[self.helix_dir]+start_point[self.helix_dir])/2
#        originB[self.helix_dir] = originA[self.helix_dir]
#
#        #axisPair = [start_point[X]-end_point[X],
#                     start_point[Y]-end_point[Y],start_point[Z]-end_point[Z]]
#        axisPair = [0,0,0]
#        axisPair[self.helix_dir] = 1
#
#        cylinder_length = abs(start_point[self.helix_dir]- \
#                          end_point[self.helix_dir])
#
#        self.drawHelix(originA, cylinder_length, axisPair)
#        self.drawHelix(originB, cylinder_length, axisPair)
#    # end def
#
#    def drawCubePair(self,start_point, end_point, orientation):
#        """
#
#        orientation: True == , False, ==
#        start_point: a vector list [X,Y,Z]
#        end_point: a vector list [X,Y,Z]
#        _____________
#        """
#        originA = [[],[],[]]
#        originB = [[],[],[]]
#
#        if (orientation == True):
#            column_offset = self.dcolumn/4
#            row_offset = 0
#        # end if
#        else:
#            column_offset = -self.dcolumn/4
#            row_offset = 0
#        # end else
#        originA[self.column_dir] = start_point[self.column_dir]-column_offset
#        originB[self.column_dir] = start_point[self.column_dir]+column_offset
#        originA[self.row_dir] = start_point[self.row_dir]+row_offset
#        originB[self.row_dir] = start_point[self.row_dir]-row_offset
#
#        originA[self.helix_dir] = (start_point[self.helix_dir]+ \
#                                  start_point[self.helix_dir])/2
#        originB[self.helix_dir] = originA[self.helix_dir]
#
#        #axisPair = [start_point[X]-end_point[X], start_point[Y]- \
#                    end_point[Y],start_point[Z]-end_point[Z]]
#        axisPair = [0,0,0]
#        axisPair[self.helix_dir] = 1
#
#        cylinder_length = abs(start_point[self.helix_dir]- \
#                           end_point[self.helix_dir])
#
#        self.drawHelix(originA, cylinder_length, axisPair)
#        self.drawHelix(originB, cylinder_length, axisPair)
#    # end def
#
#    def drawHelix(self, origin, length, axis,number=None):
#        """
#        origin: defines the starting point of one end of the helix
#        axis: vector defining the spatial direction of the helix
#        height: length of the cylinder
#        """
#        # returns [nt.Transform(u'helix0'), nt.PolyCylinder(u'polyCylinder1')]
#        # modify the cylinder length with temp[1].setHeight()
#        # and temp[0].setTranslation([0,], space = 'object')
#        # so if you want to stretch in one direction only,
#        # the origin of a cylinder is it's geometric center
#        temp = pc.polyCylinder(axis=axis,radius= \
#                (self.helix_diameter/self.unit_scale/2), \
#                height=length, name='helix0')[0]
#        # set position in the Transform Node
#        temp.setTranslation(origin, space='object')
#
#        # apply coloring
#        pc.general.sets(self.colorshader, edit=True, forceElement=temp)
#        #mypoint = (origin[0],origin[1],origin[2])
#        # if number != None:
#        #     mynote = str(number)
#        # else:
#        #     mynote = 'awesome'
#        #pc.windows.annotate( temp[0].name(), tx=mynote, p=mypoint )
#        # set up parent group
#        pc.general.parent(temp.name(), self.group.name())
#        return temp
#
#    # end def
#
#    # def addbases(self, helix, end5prime, end3prime):
#    #     temp = helix[1].getHeight()
#    #     helix[1].setHeight()
#    #     # or we can do scale as N and start with 1 base
#    #     # the_scale = helix[0].getScale()[2],
#    #     #             helix[0].setScale(1.0,1.0,float)
#    #     helix[0].setTranslation([0, 0,temp-], space='object')
#    # # end def
## end class
