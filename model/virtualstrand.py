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
    
    def minmax(self):
        return self._vhelix.part().minmax()
    
    def bounds(self, queryIdx):
        """
        This is called when a virtualstrand is asked prior
        to put a new strand in what locations are free.
        
        if this is called, it probably is at either end of the strand. 
        so look at the limit indices and iterate in
        
        this should never be called on an index containing a strand
        """
        strands = self._strands
        
        # set the return limits to the maximum bounds of the vstrand
        leftIdx, rightIdx = self.minmax()
        temp = strands[0].idxs()
        lenstrand = len(strands)
        
        # check for zero length
        if  lenstrand == 0:
            return leftIdx, rightIdx
        # end if
        
        # check the far end first
        strand = strands[-1]
        lIdx, rIdx = strands.idxs()
        if queryIdx > rIdx:
            leftIdx = rIdx
            return leftIdx, rightIdx
        # end if
        # now just check two or less
        for strand in strands[0:-1]:
            lIdx, rIdx = strands.idxs()
            if leftIdx < queryIdx < lIdx:
                rightIdx = lIdx
                break
            elif queryIdx > rIdx:
                leftIdx = rIdx
                break
            else:
                leftIdx = rIdx
        # end for
        return leftIdx, rightIdx
    # end def