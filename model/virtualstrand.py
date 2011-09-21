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

import util

# import Qt stuff into the module namespace with PySide, PyQt4 independence
util.qtWrapImport('QtCore', globals(), ['pyqtSignal', 'QObject', 'Qt'])
util.qtWrapImport('QtGui', globals(), ['QUndoStack'])

class VirtualStrand(QObject):
    
    def __init__(self, vhelix):
        super(VirtualStrand, self).__init__(vhelix)
        self._vhelix = vhelix
        self._strands = []
        
    # end def
    
    ### SIGNALS ###
    strandAddedSignal = pyqtSignal(QObject)
    
    ### SLOTS ###
    
    
    
    ### Methods ###
    def undoStack(self):
        return self._vhelix.undoStack()
        
    def destroy(self):
        # QObject also emits a destroyed() Signal
        self.setParent(None)
        self.deleteLater()
    # end def
    
    def vhelix(self):
        return self._vhelix
    # end def
    
    def strandToBeDestroy(self, strand):
        strands = self.strands
        del strands[strand.idx]
    # end def
    
    def minmax(self):
        """
        return the bounds of the virtualstrand as defined in the part
        """
        return self._vhelix.part().minmax()
    # end def
    
    def addStrand(self, strand):
        idx, isInSet = self.findIndexOfRangeFor(strand)
        if not isInSet:
            self._strands[idx] = strand
        else:
            raise Exception
    # end def
    
    def removeStrand(self, strand):
        idx, isInSet = self.findIndexOfRangeFor(strand)
        if isInSet:
            del self._strands[idx]
        else:
            raise Exception
    # end def
    
    def findIndexOfRangeFor(self, strand):
        """
        a binary search for a strand in self._strands
        
        returns a tuple (int, bool) 
        
        returns a positive value index in self._strands
        if the element is in the set
        
        returns a negative value index in self._strands
        if the element is not in the set, to be used as an insertion point
        
        returns True if the strand is in range
        
        returns False if the strand is not in range
            in this case, if a strand is for some reason passed to this 
            method that overlaps an existing range, it will return 
            a positive 1 in addition to False rather than raise an exception
        """
        strands = self._strands
        lenStrands = len(strands)
        if lenStrands == 0:
            return None
        # end if

        low = 0
        high = lenStrands - 1
        while low <= high:
            middle = low if low == high else (low + high) / 2
            currentStrand = strands[ middle ]
            
            # pre get indices from strands
            cLow, cHigh = currentStrand.idxs()
            sLow, sHigh = strand.idxs()
            
            if currentStrand == strand:
                # strand is an existing range
                return middle, True
            # end if
            elif cLow > sHigh:
                high = middle - 1
            # end elif
            elif cHigh < sLow:
                low = middle + 1
            #end elif
            else:
                if cLow <= sLow <= cHigh:
                    # strand is within an existing range
                    # but is not that range
                    return 1, False
                else:
                # object not in set, here's where you'd insert it
                    return -middle, False
            # end else
        return -low, False
    # end def
    
    def bounds(self, queryIdx):
        """
        This is called when a virtualstrand is asked prior
        to put a new strand in what locations are free.
        
        if this is called, it probably is at either end of the strand. 
        so look at the limit indices and iterate in
        
        this should never be called on an index containing a strand
        
        This returns the Pythonic range that is open around the query index
        this is like strands[x:y]
        which includes strands[x] but not strands[y]
        
        Again this is a binary search on the range
        """
        strands = self._strands
        
        # set the return limits to the maximum bounds of the vstrand
        lowIdx, highIdx = self.minmax()
        lenStrands = len(strands)
        # check for zero length
        if  lenStrands == 0:
            return lowIdx, highIdx
        # end if
        low = 0
        high = lenStrands - 1
        while low <= high:
            middle = low if low == high else (low + high) / 2
            currentStrand = strands[ middle ]
            cLow, cHigh = currentStrand.idxs()
            if cLow > queryIdx:
                # adjust bounds down
                highIdx = cLow
                high = middle - 1
            # end if
            elif cHigh < queryIdx:
                # adjust bounds up
                lowIdx = cHigh + 1
                low = middle + 1
            #end elif
            else:
                return 0, 0
        # end while
        return lowIdx, highIdx
    # end def