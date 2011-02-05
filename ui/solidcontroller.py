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
solidcontroller.py

Created by Nick Conway on 2011-02-04.
For use controlling 3D solid models generated in Maya
"""

class SolidController():
    """
    Manages interactions between the slice widgets/UI and the model.
    """
    
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
        
        temp = polyCylinder(axis = axisPair,radius = (self.helix_diameter/2), height = cylinder_length)[0]
        temp.setTranslation(originA, space = 'object')
        temp = polyCylinder(axis = axisPair,radius = (self.helix_diameter/2), height = cylinder_length)[0]
        temp.setTranslation(originB,space = 'object')
    # end def
    
    def drawCubePair(self,start_point, end_point, orientation):
        
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
        
        temp = polyCylinder(axis = axisPair,radius = (self.helix_diameter/2), height = cylinder_length)[0]
        temp.setTranslation(originA, space = 'object')
        temp = polyCylinder(axis = axisPair,radius = (self.helix_diameter/2), height = cylinder_length)[0]
        temp.setTranslation(originB,space = 'object')
    # end def
# end class
