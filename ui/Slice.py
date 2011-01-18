# The MIT License
# 
# Copyright (c) 2010 Wyss Institute at Harvard University
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

#package edu.harvard.med.cadnano :
# from edu.harvard.med.cadnano.data.SliceNode import *
    
class Slice():
    """
        A Slice instance is meant to store a 2D array of helix data, in the form
        of SliceNodes.  This facilitates populating spatial relationships
        between helices in the honeycomb lattice.  Slice and SliceNode classes
        might be combined at some point, since we no longer need to store
        multiple slices.
    """
    
    # store slice nodes in hash accessible by "row,col" keys
    def __init__(self,rows, cols):
        self.index = '' 
        self.sliceHash =  Object() 
        
        # create a SliceNode at each position in the grid
        for col in range(cols):
            for row in range(rows):
                index = row + "," + col 
                self.sliceHash[index] = SliceNode(row, col) 
            # end for
        # end for
        
        # Populate neighbor linkages
        for col in range(cols):
            for row in range(rows):
                index = row + "," + col 
                node = self.sliceHash[index] 
                
                if node.parity: # odd parity
                    # if col-1 exists, set P0
                    if col > 0:
                        index = row + "," + (col-1) 
                        node.p0neighbor = self.sliceHash[index] 
                    # end if
                    # if row+1 exists, set P1
                    if row < rows-1:
                        index = (row+1) + "," + col 
                        node.p1neighbor = self.sliceHash[index] 
                    # end if
                    # if col+1 exists, set P2
                    if col < cols-1:
                        index = row + "," + (col+1) 
                        node.p2neighbor = self.sliceHash[index] 
                    # end if
                # end if
                else:         # even parity
                    # if col+1 exists, set P0
                    if col < cols-1:
                        index = row + "," + (col+1) 
                        node.p0neighbor = self.sliceHash[index] 
                    # end if
                    # if row-1 exists, set P1
                    if row > 0:
                        index = (row-1) + "," + col 
                        node.p1neighbor = self.sliceHash[index] 
                    # end if
                    # if col-1 exists, set P2
                    if col > 0:
                        index = row + "," + (col-1) 
                        node.p2neighbor = self.sliceHash[index] 
                    # end if
                # end else
            # end for
        # end for
    # end def
    
    def getSliceNode(self,row,col):
        """ 
            Called by DataTools 
        """
        index = row + "," + col 
        return self.sliceHash[index] 
    # end def
    
    def pairAllVstrands(self,path): 
        """ 
            Called by DataTools
            path = Path 
        """
        for node in self.sliceHash:
            if node.number != -1:
                # install Vstrand neighbor relationships
                if node.p0neighbor != null && node.p0neighbor.number != -1:
                    path.pairHelices(node.vstrand, node.p0neighbor.vstrand, 0) 
                # end if
                if node.p1neighbor != null && node.p1neighbor.number != -1:
                    path.pairHelices(node.vstrand, node.p1neighbor.vstrand, 1) 
                # end if
                if node.p2neighbor != null && node.p2neighbor.number != -1:
                    path.pairHelices(node.vstrand, node.p2neighbor.vstrand, 2) 
                # end if
            # end if
        # end for
    # end def
# end class

