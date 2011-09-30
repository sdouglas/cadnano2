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

from strandset import StrandSet
import util
from enum import StrandType

# import Qt stuff into the module namespace with PySide, PyQt4 independence
util.qtWrapImport('QtCore', globals(), ['pyqtSignal', 'QObject', 'Qt'])
util.qtWrapImport('QtGui', globals(), ['QUndoStack'])

class VirtualHelix(QObject):
    def __init__(self, part, row, col, idnum=0):
        """
        VirtualHelix is a container class for two StrandSet objects (one scaffold
        and one staple). The Strands all share the same helix axis. It is called
        "virtual" because many different Strands (i.e. sub-oligos) combine to
        form the "helix", just as many fibers may be braided together to 
        form a length of rope.
        """
        super(VirtualHelix, self).__init__(part)
        self._coords = (row, col) # col, row
        self._part = part
        self._scafStrandSet = StrandSet('scaffold', self)
        self._stapStrandSet = StrandSet('staple', self)
        # If self._part exists, it owns self._number
        # in that only it may modify it through the
        # private interface. The public interface for
        # setNumber just routes the call to the parent
        # dnapart if one is present. If self._part == None
        # the virtualhelix owns self._number and may modify it.
        self._number = idnum
    # end def

    ### SIGNALS ###
    virtualhelixRemovedSignal = pyqtSignal(QObject) # self
    virtualhelixNumberChangedSignal = pyqtSignal(QObject, object) # self, num

    ### SLOTS ###

    ### Methods ###
    def undoStack(self):
        return self._part.undoStack()
    # end def

    def destroy(self):
        # QObject also emits a destroyed() Signal
        self.setParent(None)
        self.deleteLater()
    # end def

    def part(self):
        return self._part
    # end def

    def number(self):
        return self._number

    def setPart(self, newPart):
        self._part = newPart
        self.setParent(newPart)
    # end def
    
    def coords(self):
        return self._coords
    # end def
    
    def translateCoords(self, deltaCoords):
        """
        for expanding a helix
        """
        deltaRow, deltaCol = deltaCoords
        row, col = self._coords
        self._coords = row + deltaRow, col + deltaCol
    # end def
    
    def number(self):
        return self._number
    # end def

    def setNumber(self, number):
        self._number = number
    # end def

    def isEvenParity(self):
        return self._part.isEvenParity(*self._coords)
    # end def
    
    def isDrawn5to3(self, strandSet):
        isScaf = strandSet == self._scafStrandSet
        isEven = self.isEvenParity()
        return isEven == isScaf
    # end def

    def getStrandSetByIdx(self, idx):
        """
        This is a path-view-specific accessor
        idx == 0 means top strand
        idx == 1 means bottom strand
        """
        if idx == 0:
            if self.isEvenParity():
                return self._scafStrandSet
            else:
                return self._stapStrandSet
        else:
            if self.isEvenParity():
                return self._stapStrandSet
            else:
                return self._scafStrandSet
    # end def

    def getStrandSetByType(self, strandType):
        if strandType == StrandType.Scaffold:
            return self._scafStrandSet
        else:
            return self._stapStrandSet
    # end def

    def getStrandSets(self):
        """
        return a tuple of the scaffold and staple StrandSets
        """
        return self._scafStrandSet, self._stapStrandSet

    def strandSetBounds(self, indexHelix, indexType):
        """
        forwards the query to the strandSet
        """
        return self.strandSet(indexHelix, indexType).bounds()
    # end def

    def shallowCopy(self):
        pass
    # end def

    def deepCopy(self, part):
        """
        This only copies as deep as the VirtualHelix
        strands get copied at the oligo and added to the Virtual Helix
        """
        vh = VirtualHelix(part, self._number)
        vh._coords = (self._coords[0], self._coords[1])
        # If self._part exists, it owns self._number
        # in that only it may modify it through the
        # private interface. The public interface for
        # setNumber just routes the call to the parent
        # dnapart if one is present. If self._part == None
        # the virtualhelix owns self._number and may modify it.
        self._number = idnum
    # end def
