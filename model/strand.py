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
from operator import attrgetter

# import Qt stuff into the module namespace with PySide, PyQt4 independence
util.qtWrapImport('QtCore', globals(), ['pyqtSignal', 'QObject', 'Qt'])
util.qtWrapImport('QtGui', globals(), ['QUndoStack'])

class Strand(QObject):
    
    def __init__(self, vStrand, indexLow, indexHigh):
        super(Strand, self).__init__(vstrand)
        self._oligo = None
        self._vStrand = vStrand
        
        self._strand5p = None
        self._strand3p = None
        self._vBaseIndices = (indexLow, indexHigh)
        
        
        self._decorators = {}
        self._sequence = None
        self._note = None
    # end def
    
    def shallowCopy(self):
        nS = Strand(self._vStrand, self.idxs())
        nS._oligo = self._oligo
        nS._strand5p = self._strand5p
        nS._strand3p = self._strand3p
        # required to shallow copy the dictionary
        nS._decorators = dict(self._decorators.items())
        nS._sequence = self._sequence
        nS._note = self._note
        return nS
    # end def

    def __iter__(self):
        """
        iterate from self to the final _strand3p == None
        5prime to 3prime
        
        Includes originalCount to check for circular linked list
        
        """
        originalCount = 0
        node = self
        f = attrgetter('_strand3p')
        while node and originalCount == 0:
            yield node
            # node = node._strand3p
            node = f(node)
            if node == self:
                originalCount += 1
        # end while
    # end def
    
    def __eq__(self, strand):
        return self is strand
        
    def __ne__(self, strand):
        return not self is strand

    def __lt__(self, strand):
        return self._vBaseIndices[1] < strand._vBaseIndices[0]

    def __gt__(self, strand):
        return self._vBaseIndices[0] > strand._vBaseIndices[1]

    def __le__(self, strand):
        return self.__eq__(strand) or self.__lt__(strand)

    def __ge__(self, strand):
        return self.__eq__(strand) or self.__gt__(strand)
    # end def
    
    ### SIGNALS ###
    hasNewOligoSignal = pyqtSignal(QObject)
    destroyedSignal = pyqtSignal(QObject)
    resizedSignal = pyqtSignal(QObject, tuple)
    xover3pCreatedSignal = pyqtSignal(QObject, int)
    xover3pDestroyedSignal = pyqtSignal(QObject, int)
    decoratorCreatedSignal = pyqtSignal(QObject, QObject, int)
    decoratorDestroyedSignal = pyqtSignal(QObject, int)
    
    ### SLOTS ###
    
    
    ### Methods ###
    def undoStack(self):
        return self._vStrand.undoStack()
    
    def vStrand(self):
        return self._vStrand
    # end def
    
    def oligo(self):
        return self._oligo
    # end def
    
    def setOligo(self, newOligo):
        self._oligo = newOligo
        self.hasNewOligoSignal.emit(self)
    # end def
    
    def decorators(self):
        return self.decorators
    #end def
    
    def addDecorators(self, additionalDecorators):
        """
        used in adding additional decorators during a merge operation
        """
        self._decorators.update(additionalDecorators)
    # def
    
    def destroy(self):
        # QObject also emits a destroyed() Signal
        self.setParent(None)
        self.deleteLater()
    # end def
    
    def idxs(self):
        return self._vBaseIndices
    # end def
    
    def setIdxs(self, idxs):
        self._vBaseIndices = idxs
    # end def
        
    def lowIdx(self):
        return self._vBaseIndices[0]
    # end def
    
    def highIdx(self):
        return self._vBaseIndices[1]
    # end def
    
    def isDrawn5to3(self):
        return self._vStrand.isDrawn5to3()
    # end def

    def lowConnection(self):
        if self.isDrawn5to3():
            return self._strand5p
        else:
            return self._strand3p
    # end def
    
    def setLowConnection(self, strand):
        if self.isDrawn5to3():
            self._strand5p = strand
        else:
            self._strand3p = strand
    # end def
    
    def highConnection(self):
        if self.isDrawn5to3():
            return self._strand3p
        else:
            return self._strand5p
    # end def
    
    def setHighConnection(self, strand):
        if self.isDrawn5to3():
            self._strand3p = strand
        else:
            self._strand5p = strand
    # end def
    
    def resize(self):
    
    # end def
    
    class ResizeCommand(QUndoCommand):
        def __init__(self, strand, newIndices):
            super(ResizeCommand, self).__init__()
            self.strand = strand
            self.oldIndices = strand.idxs()
            self.newIndices = newIndices
        # end def
        
        def redo(self):
            std = self.strand
            nI = self.newIndices
            std.setIdxs(nI)
            std.resizedSignal(std, nI)
        # end def
        
        def undo(self):
            std = self.strand
            oI = self.oldIndices
            std.setIdxs(oI)
            std.resizedSignal(std, oI)
        # end def
        
    # end class
    
    def split(self, idx):
        
    # end def
    
    def copy(self):
        
    # end def
    
    def addSequence(self):
        
    # end def
    
    