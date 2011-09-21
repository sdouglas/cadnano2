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
import bisect
from operator import itemgetter

# import Qt stuff into the module namespace with PySide, PyQt4 independence
util.qtWrapImport('QtCore', globals(), ['pyqtSignal', 'QObject', 'Qt'])
util.qtWrapImport('QtGui', globals(), ['QUndoStack', 'QUndoCommand'])

class VirtualStrand(QObject):
    
    def __init__(self, vhelix):
        super(VirtualStrand, self).__init__(vhelix)
        self._vhelix = vhelix
        self._strands = []
        self._undoStack = None
        self._lastSetIndex = None
    # end def
    
    ### SIGNALS ###
    strandAddedSignal = pyqtSignal(QObject)
    
    ### SLOTS ###
    
    
    
    ### Methods ###
    def undoStack(self):
        if self._undoStack == None:
            self._undoStack = self._vhelix.undoStack()
        return self._undoStack
        
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
    
    def beginCommmandMacro(self, commandDescription, useUndoStack):
        """Called as a prefix to every public mutation method. Ensures uniform
        handling of the useUndoStack+undoStack variables. Returns the
        undoStack that the mutator method should use."""
        self._lastSetIndex = None   # reset the index cache
        if useUndoStack:
            self.undoStack().beginMacro(commandDescription)
    # end def
    
    def endCommandMacro(self, useUndoStack):
        if useUndoStack:
            self.undoStack().endMacro()
    # end def

    def endCommand(self, command, useUndoStack):
        """Called at the end of every public mutation method"""
        if useUndoStack:
            self.undoStack().push(command) 
        else:
            command.redo()
    # end def
    
    def createStrand(self, idxLow, idxHigh, useUndoStack=True):
        """
        Assumes a strand is being created at a valid set of indices
        """
        strand = Strand(self, idxLow, idxHigh)
        if couldStrandInsertAtLastIndex(strand):
            idx = self._lastSetIdx
        else:
            raise IndexError("The cached index was invalid")
        self.beginCommandMacro('VirtualStrand.createStrand', useUndoStack)
        self.addStrand(strand, idx, useUndoStack)
        self.endCommandMacro(useUndoStack)
    # end def 
    
    def addStrand(self, strand, idx=None, useUndoStack=True):
        """
        use this method directly when deserializing model
        """
        if not idx:
            idx, isInSet = self.findIndexOfRangeFor(strand)
            if not isInSet:
                raise IndexError
        # end if
        command = AddStrandCommand(self._strands, strand, idx)
        self.endCommand(command, useUndoStack)
        return idx
    # end def
    
    class AddStrandCommand(QUndoCommand):
        def __init__(self, strands, strand, idx):
            super(AddStrandCommand, self).__init__()
            self.strands = strands
            self.strand = strand
            self.idx = idx            
        # end def
        
        def redo(self):
            self.strands.insert(self.idx, self.strand)
        # end def
        
        def undo(self):
            self.strands.pop(self.idx)
        # end def
    # end def
    
    def removeStrand(self, strand, idx=None, useUndoStack=True):
        if not idx:
            idx, isInSet = self.findIndexOfRangeFor(strand)
            if not isInSet:
                raise IndexError
        # end if
        command = RemoveStrandCommand(self._strands, strand, idx)
        self.endCommand(command, useUndoStack)
        return idx
    # end def
    
    class RemoveStrandCommand(QUndoCommand):
        def __init__(self, strands, strand, idx):
            super(RemoveStrandCommand, self).__init__()
            self.strands = strands
            self.strand = strand
            self.idx = idx            
        # end def
        
        def redo(self):
            self.strands.pop(self.idx)
        # end def
        
        def undo(self):
            self.strands.insert(self.idx, self.strand)
        # end def
    # end def
    
    def couldStrandInsertAtLastIndex(self, strand):
        """
        Verification of insertability based on cached last index
        """
        lastInd = self._lastSetIndex
        if lastInd == None:
            return False
        else:
            strands = self.strands
            sTestHigh = strands[lastInd ].lowIdx()
            sTestLow = strands[lastInd-1].highIdx() if lastInd  > 0 else -1
            sLow, sHigh = strand.idxs()
            if sTestLow < sLow and sHigh < sTestHigh:
                return True
            else:
                return False
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
        high = lenStrands
        
        sLow, sHigh = strand.idxs()
        
        while low < high:
            middle = low if low == high else (low + high) / 2
            currentStrand = strands[ middle ]
            
            # pre get indices from strands
            cLow, cHigh = currentStrand.idxs()
            
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
                if cLow <= sLow <= cHigh or cLow <= sHigh <= cHigh:
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
        
        This returns a non-Pythonic but intuitive range tuple, that is
        inclusive around the query index of the virtual array of bases
        as if to return (x, y) indicating strands[x:y+1] which includes 
        strands[x] and strands[y]
        
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
        high = lenStrands
        while low < high:
            middle = (low + high) / 2
            currentStrand = strands[ middle ]
            cLow, cHigh = currentStrand.idxs()
            if cLow > queryIdx:
                # adjust bounds down
                highIdx = cLow - 1
                high = middle
            # end if
            elif cHigh < queryIdx:
                # adjust bounds up
                lowIdx = cHigh + 1
                low = middle + 1
            #end elif
            else:
                # return this when the query is somehow invalid
                # like if it is called on an index with an 
                # existing strand
                return None
        # end while
        # set the last query index result
        self._lastSetIndex = (low + high) /2
        # return the tuple
        return lowIdx, highIdx
    # end def