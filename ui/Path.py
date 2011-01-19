#!/usr/bin/env python
# encoding: utf-8

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
Path.py

Created by Nick Conway on 2010-11-23.
Copyright (c) 2010 __Wyss Institute__. All rights reserved.
ported from Shawn Douglas's actionscript version Path.AS
"""

"""
The Path class is used to create and maintain VHelices.
DrawPath uses a Path instance to draw the user interface,
as well as to update the VHelices with changes as the user
interacts with the interface.

The main "vhList" object is a doubly-linked list, in which each element 
is a VHelix (virtual strand), corresponding to a DNA helix in the
nanostructure.
"""

#from collections import deque
    
# cadnano
import edu.harvard.med.cadnano.data.VHelix 
import edu.harvard.med.cadnano.data.SliceNode 
import edu.harvard.med.cadnano.drawing.* 

    
class Path(self):
    """
    
    """
    def __init__(self):
        """
        
        """
        self.PREPEND = "prepend" 
        self.APPEND = "append"
        
        self.drawPath = DrawPath()
        self.vhList = []
        #self.vhDeq = deque()
        self.vhHash = {} #pointers to VHelices independent of vhList order # this becomes a dictionary
        
        self.loadedData = False
    # end def
        
    def resetPathData(self):
        """
        Parameters
        ----------
        node: SliceNode

        See Also
        --------

        Examples
        --------
        """
        self.drawPath.clearActiveVHelix()
        vh = self.vhList.remove(0)
        #vh = self.vhDeq.popLeft()
        while vh != None:
            del vh
            vh = self.vhList.remove(0) 
            #vh = self.vhDeq.popLeft()
    # end def

    def addHelix(self,node):
        """
        Add newly clicked helix from SlicePanel to Path Panel.  Install
        some initial scaffold bases.
        
        Parameters
        ----------
        node: SliceNode

        See Also
        --------

        Examples
        --------
        """ 
        gridwidth
        if self.vhList.size == 0: # use default size for first vhtrand
            gridwidth = 42
        # end if
        else: # use calculated size of existing vhtrand
            gridwidth = self.vhList.head.data.scaf.length
        
        # Add virtual strand data structure
        vh = VHelix(node,gridwidth)
        self.vhHash[vh.number] = vh
        
        self.vhList.append(vh)
        #self.vhDeq.append(vh)
        
        node.vhtrand = vh # link node to its vhtrand
        self.addBases(self.drawPath.currentSlice,vh) # populate new vhtrand
        
        # Add virtual strand drawing methods
        dv = DrawVHelix(self.drawPath, vh, node, self.vhList.size-1)
        self.drawPath.addDrawVHelix(dv)
        
        self.drawPath.addHelixHandle(node,self.vhList.size-1)
        self.drawPath.addGridLines(self.vhList.size-1, vh.scaf.length)
        
        dv.addScafBreakpoints() # add initial breakpoints
        dv.updateScafBreakBounds()
    # end def
        
    def addBases(self,i, vh):
        """
        Update pointer pairs to create a few bases
        Parameters
        ----------
        i: integer
        vh: VHelix

        See Also
        --------

        Examples
        --------
        """
        # get away from edge
        if i == 0:
            self.drawPath.currentSlice = i + 1
            self.drawPath.redrawSliceBar()
        # end if
        elif self.drawPath.currentSlice == vh.scaf.length-1:
            self.drawPath.currentSlice = i - 1
            self.drawPath.redrawSliceBar()
        # end elif
        
        # add some scaffold bases
        vh.scaf[i].prev_strand = vh.number 
        vh.scaf[i].next_strand = vh.number 
        
        if vh.number % 2 == 0 : # even parity
            # update upstream next pointer to point to this
            vh.scaf[int(i-1)].next_strand = vh.number 
            vh.scaf[int(i-1)].next_pos = i 
            
            # update this prev to point upstream
            vh.scaf[i].prev_pos = i - 1 
            # update this next to point downstream
            vh.scaf[i].next_pos = i + 1 
            
            # update downstream prev to point to this
            vh.scaf[i+1].prev_strand = vh.number 
            vh.scaf[i+1].prev_pos = i 
        # end if 
        else:
            # update upstream prev to point to this
            vh.scaf[int(i-1)].prev_strand = vh.number 
            vh.scaf[int(i-1)].prev_pos = i 
            
            # update this prev to point downstram
            vh.scaf[i].prev_pos = i + 1 
            # update this next to point upstream
            vh.scaf[i].next_pos = i - 1 
            
            # update downstream next to point to this
            vh.scaf[i+1].next_strand = vh.number 
            vh.scaf[i+1].next_pos = i 
        # end else
    # end def
        

    def addStapleBases(self,i,vh):
        """
        Update pointer pairs to create a few staple bases

        Parameters
        ----------
        i: integer
        vh: VHelix

        See Also
        --------

        Examples
        --------
        """
        # get away from edge
        if i == 0:
            self.drawPath.currentSlice = i + 1 
            self.drawPath.redrawSliceBar() 
        # end if
        elif self.drawPath.currentSlice == vh.stap.length-1:
            self.drawPath.currentSlice = i - 1 
            self.drawPath.redrawSliceBar() 
        # end elif
        
        # add some stapfold bases
        vh.stap[i].prev_strand = vh.number 
        vh.stap[i].next_strand = vh.number 
        
        if vh.number % 2 == 1: # odd parity
            # update upstream next pointer to point to this
            vh.stap[int(i-1)].next_strand = vh.number 
            vh.stap[int(i-1)].next_pos = i 
            
            # update this prev to point upstream
            vh.stap[i].prev_pos = i - 1 
            # update this next to point downstream
            vh.stap[i].next_pos = i + 1 
            
            # update downstream prev to point to this
            vh.stap[i+1].prev_strand = vh.number 
            vh.stap[i+1].prev_pos = i 
        # end if
        else:
            # update upstream prev to point to this
            vh.stap[int(i-1)].prev_strand = vh.number 
            vh.stap[int(i-1)].prev_pos = i 
            
            # update this prev to point downstram
            vh.stap[i].prev_pos = i + 1 
            # update this next to point upstream
            vh.stap[i].next_pos = i - 1 
            
            # update downstream next to point to this
            vh.stap[i+1].next_strand = vh.number 
            vh.stap[i+1].next_pos = i 
        # end else
    # end def

    def extendVHelices(self,type_arg, segments=1):
        """

        Parameters
        ----------
        type_arg: string
        segments: integer

        See Also
        --------

        Examples
        --------
        """
        for vh in self.vhList:
            vh.extend(type_arg, segments)  # extend every vhtrand
            if type_arg == PREPEND:
                vh.drawVHelix.shiftHandles(segments)  # shift all handles (xo, loop, skip)
            # end if
        # end for
        
        if type_arg == PREPEND:
            # snap to end by default
            self.drawPath.currentSlice = 0 
            # keep canvas centered
            self.drawPath.x = self.drawPath.x - segments*21*DrawPath.baseWidth 
        # end if
        elif type_arg == APPEND:
            self.drawPath.currentSlice += segments*21 
        # end elif
        self.drawPath.update() 
    # end def
    
    def renumberHelices(self):
        """ 
        Renumber helices in ascending order according to position in vhList.
    
        Parameters
        ----------

        See Also
        --------

        Examples
        --------     
        """
        transform = {} # dictionary
        helixNum =None
        i = None 
        even = -2 
        odd = -1 
        
        # "sort" and decorate
        for vh in self.vhList:
            helixNum = vh.number 
            if helixNum % 2 == 0:
                even += 2 
                transform[helixNum] = 1000 + even
            # end if 
            else :
                odd += 2 
                transform[helixNum] = 1000 + odd 
            # end else
        # end for
        
        for vh in self.vhList:
            vh.reNumber(transform) 
        # end for
        
        # undecorate
        for vh in self.vhList:
            helixNum = vh.number 
            transform[helixNum] = helixNum - 1000 
        # end for
        
        for key in self.vhHash:  # reset vhHash
            del self.vhHash[key] 
        # end
        
        for item in self.vhList:
            vh = item.data 
            vh.reNumber(transform) 
            self.vhHash[vh.number] = vh 
        # end for
        self.drawPath.reNumberHelixLabels() 
    # end
    
    def pairHelices(self,vh1, vh2, p):
        """ 
        When SliceNodes are updated by clicking in the slice panel
        it is necessary to link the corresponding VHelices that are
        created so stage coordinates can be easily determined when
        crossovers are drawn.
        
        Parameters
        ----------
        vh1: VHelix
        vh2: VHelix
        p: integer

        See Also
        --------

        Examples
        --------
        """
        if p == 0:
            vh1.p0 = vh2 
            vh2.p0 = vh1 
        # end if
        if p == 1:
            vh1.p1 = vh2 
            vh2.p1 = vh1 
        # end if
        if p == 2:
            vh1.p2 = vh2 
            vh2.p2 = vh1 
        # end if
    # end def
    
    def importVHelices(self,vhl):
        """
        Parameters
        ----------
        vhl: VHelix

        See Also
        --------

        Examples
        --------    
        """
        rank = 0 
        
        self.vhList = vhl 
        for key in self.vhHash:  # reset vhHash
            del self.vhHash[key] 
        # end
        
        for item in self.vhList:
            vh = item.node.data 
            self.vhHash[vh.number] = vh 
            dv = DrawVHelix(self.drawPath, vh, vh.sliceNode, rank, false) 
            self.drawPath.addDrawVHelix(dv) 
            self.drawPath.addHelixHandle(vh.sliceNode, rank) 
            rank += 1 
        # end
        
        self.loadedData = True 
    # end def
# end class



def main():
    pass


if __name__ == '__main__':
    main()
