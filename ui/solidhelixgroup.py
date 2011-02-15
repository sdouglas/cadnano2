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
solidhelixgroup.py

Created by Nick Conway on 2011-02-04.
For use controlling 3D solid models generated in Maya
"""
from PyQt4.QtCore import pyqtSignal, pyqtSlot, QObject
from string import *
import math
import random
import pymel.core as pc
import os
import sys
import styles
import maya.OpenMayaUI as mui
import maya.OpenMaya as mo	

X, Y, Z = range(3) # enumerate unit direction indices

class SolidHelixGroup(QObject):
    """
    A Solid Hinstance is meant to store helix data in Maya 
    representing a pathhelixgroup.
    
    column nodes all have the same X coordinate
    row nodes can have slightly different Y coordinates (offset) for convenience of data representation
    as is the case of the honeycomb representation
    
    Parameters
    ----------
    rows: rows grid size
    cols: columns grid size

    See Also
    --------

    Examples
    --------
    """

    # store slice nodes in hash accessible by "row,col" keys
    def __init__(self, dnaPartInst, htype="honeycomb", controller=None, parent=None):
        """
        Parameters
        ----------
        rows: rows grid size
        cols: columns grid size

        See Also
        --------

        Examples
        --------
        """
        super(SolidHelixGroup, self).__init__()
        
        self.number_hash = {}
        self.type = htype
        self.helix_diameter = 2.0
        self.pointscale = self.helix_diameter/(2*styles.SLICE_HELIX_RADIUS)
        
        # initialize the column direction stuff
        self.column_dir = X
        self.row_dir = Y
        self.helix_dir = Z

        # the limits of the indices of the output raster
        self.row_count = 0
        self.column_count = 0
        self.helix_count = 0
                
        self.h_axis = 'Z'
        self.row_axis = 'Y'

        # initialize the unit size of a base cell
        self.drow = 0       # the row direction
        self.dcolumn = 0    # the direction normal to the row direction and the helical axis 
        self.dhelix = 0     # the helical axis
        self.model_scale = 1
        self.unit_scale = 2
        self.N_bases = 1
        self.N_bases_default = 3
        # set up the above parameters
        self.calculateParameters()
        print "maya group created"
        self.group = pc.general.group(em=True,name='helixgroup0')
        
        # the coloring of the cylinders is set here 
        shdr, sg = pc.createSurfaceShader( 'blinn' )
        self.colorshader = sg
        colorfill = styles.orangefill
        # maya takes RGB component values from 0 to 1
        shdr.setAttr('color', colorfill.redF(),colorfill.greenF(),colorfill.blueF(), type='double3')
 
    # end def
    
    def calculateParameters(self):
        """ calculate the core values of the cylinders """
        if self.type == 'honeycomb':
            self.dcolumn = self.helix_diameter*math.sqrt(3)/self.unit_scale 
            self.drow = 1.5*self.helix_diameter/self.unit_scale
            self.dhelix = 0.34*self.N_bases/self.unit_scale
        # end if
        elif self.type == 'square':
            self.dcolumn = 2*self.helix_diameter/self.unit_scale
            self.drow = self.helix_diameter/self.unit_scale
            self.dhelix = 0.34*self.N_bases/self.unit_scale
        # end elif
        else:
            print "Undefined unit type\n"
            exit()
        # end else
    # end def
    
    def handleScaffoldChange(self,number):
        """"""
        self.number
        
    # end def
    
    @pyqtSlot('QPointF',int)
    def handleHelixAdded(self, pos, number):
        """
        Retrieve reference to new VirtualHelix vh based on number relayed
        by the signal event. Next, create a new PathHelix associated 
        with vh and draw it on the screen.
        
        pos: a QPointF identifying a slice views XY position for a helix
        
        """
        
        axis = [0,0,0]
        axis[self.helix_dir] = 1
        
        # draw the default length helix
        length= self.dhelix*self.N_bases_default
        
        # figure out starting position
        x = pos.x()*self.pointscale # scale input from slice view
        # scale input from slice view make negative to invert the fact that
        # Qt defines origins positve moving downscreen from the top left corner
        y = -pos.y()*self.pointscale + 29 
        print x, y
        origin = [x/self.unit_scale, y/self.unit_scale, 0]
        
        self.number_hash[number] = self.drawHelix(origin, length, axis,number)
    # end def
    
    def drawHexPair(self,start_point, end_point, orientation):

        originA = [[],[],[]]
        originB = [[],[],[]]

        if (orientation == True): 
            column_offset = self.dcolumn/4
            row_offset = self.drow/4
        # end if
        else:
            column_offset = -self.dcolumn/4
            row_offset = -self.drow/4
        # end else
        originA[self.column_dir] = start_point[self.column_dir]-column_offset
        originB[self.column_dir] = start_point[self.column_dir]+column_offset
        originA[self.row_dir] = start_point[self.row_dir]+row_offset
        originB[self.row_dir] = start_point[self.row_dir]-row_offset

        originA[self.helix_dir] = (start_point[self.helix_dir]+start_point[self.helix_dir])/2
        originB[self.helix_dir] = originA[self.helix_dir]

        #axisPair = [start_point[X]-end_point[X], start_point[Y]-end_point[Y],start_point[Z]-end_point[Z]]   
        axisPair = [0,0,0]
        axisPair[self.helix_dir] = 1

        cylinder_length = abs(start_point[self.helix_dir]-end_point[self.helix_dir])  

        self.drawHelix(originA, cylinder_length, axisPair)
        self.drawHelix(originB, cylinder_length, axisPair)
    # end def

    def drawCubePair(self,start_point, end_point, orientation):
        """
        
        orientation: True == , False, == 
        start_point: a vector list [X,Y,Z]
        end_point: a vector list [X,Y,Z]
        _____________
        """
        originA = [[],[],[]]
        originB = [[],[],[]]

        if (orientation == True): 
            column_offset = self.dcolumn/4
            row_offset = 0
        # end if
        else:
            column_offset = -self.dcolumn/4
            row_offset = 0
        # end else
        originA[self.column_dir] = start_point[self.column_dir]-column_offset
        originB[self.column_dir] = start_point[self.column_dir]+column_offset
        originA[self.row_dir] = start_point[self.row_dir]+row_offset
        originB[self.row_dir] = start_point[self.row_dir]-row_offset

        originA[self.helix_dir] = (start_point[self.helix_dir]+start_point[self.helix_dir])/2
        originB[self.helix_dir] = originA[self.helix_dir]

        #axisPair = [start_point[X]-end_point[X], start_point[Y]-end_point[Y],start_point[Z]-end_point[Z]]   
        axisPair = [0,0,0]
        axisPair[self.helix_dir] = 1

        cylinder_length = abs(start_point[self.helix_dir]-end_point[self.helix_dir])  

        self.drawHelix(originA, cylinder_length, axisPair)
        self.drawHelix(originB, cylinder_length, axisPair)
    # end def

    def drawHelix(self, origin, length, axis,number=None):
        """
        origin: defines the starting point of one end of the helix
        axis: vector defining the spatial direction of the helix
        height: length of the cylinder
        """
        temp = pc.polyCylinder(axis=axis,radius=(self.helix_diameter/self.unit_scale/2), height=length, name='helix0')[0]
        # set position
        temp.setTranslation(origin, space='object') 
        
        # apply coloring
        pc.general.sets(self.colorshader, edit=True, forceElement=temp)
        mypoint = (origin[0],origin[1],origin[2])
        if number != None:
            mynote = str(number)
        else:
            mynote = 'awesome'
        #pc.windows.annotate( temp.name(), tx=mynote, p=mypoint ) 
        # set up parent group
        pc.general.parent(temp.name(), self.group.name())
        return temp[0]
    # end def
# end class

