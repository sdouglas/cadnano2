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
util.qtWrapImport('QtCore', globals(), ['pyqtSignal', 'QObject'])
util.qtWrapImport('QtGui', globals(), [ 'QUndoCommand', 'QUndoStack'])

class Oligo(QObject):
    def __init__(self):
        super(Oligo, self).__init__()
        self._part = None
        self._strand5p = None
        self._length = 0
        self._isLoop = False
    # end def
    
    def shallowCopy(self):
        olg = Oligo()
        olg._part = self._part
        olg._strand5p = self._strand5p
        olg._length = self._length
        olg._isLoop = self._isLoop
        return olg
    # end def

    ### SIGNALS ###
    notifyMergedStrandsWithNewOligoSignal = pyqtSignal(QObject)  # new oligo
    appearanceChangedSignal = pyqtSignal(QObject)  # self
    sequenceAddedSignal = pyqtSignal(QObject)  # self
    sequenceClearedSignal = pyqtSignal(QObject)  # self

    ### SLOTS ###

    ### METHODS ###
    def undoStack(self):
        return self._part.undoStack()

    def destroy(self):
        # QObject also emits a destroyed() Signal
        self.setParent(None)
        self.deleteLater()
    # end def

    def part(self):
        return self._part

    def strand5p(self):
        return self._strand5p

    def setStrand5p(self, strand):
        self._strand5p = strand
    # end def

    def length(self):
        return self._length

    def setLength(self, length):
        return self._length = length

    def isLoop(self):
        return self._isLoop

    def add(self):
        self.part().addOligo(self)
    # end def

    def remove(self):
        """
        this method merely disconnects to object from the model
        it still lives on in the undoStack until clobbered
        """
        self.part().removeOligo(self)
    # end def

    def strandSplitUpdate(self, newStrandLow, newStrandHigh, oligoHigh, oldMergedStrand):
        """
        If the oligo is a loop, splitting the strand does nothing. If the
        oligo isn't a loop, a new oligo must be created and assigned to the
        newStrand and everything connected to it downstream.
        
        This always is called on a lower indexed half of a split strands
        oligo
        AKA strandLow --> oligoLow
        """
        # if you split it can't be a loop
        self._isLoop = False
        if oldMergedStrand.oligo().isLoop():
            # don't change the _strand5p cause it was  all the same
            # oligo
            return
        else:
            if newStrandLow.isDrawn5to3():
                self._strand5p = oldMergedStrand.oligo()._strand5p
                oligoHigh._strand5p = newStrandHigh
            else:
                self._strand5p = newStrandLow
                oligoHigh._strand5p = oldMergedStrand.oligo()._strand5p
        # end else
    # end def
            

    def strandMergeUpdate(self, oldStrandLow, oldStrandHigh):
        """
        This method correctly sets the isLoop status of the oligo and the
        oligo
        """
        # check loop status
        if oldStrandLow.oligo() == oldStrandHigh.oligo():
            self._isLoop = True
            # leave the _strand5p as is?
        # end if

        # Now get correct 5p end to oligo
        # there are four cases, two where it's already correctly set
        # and two where it needs to be changed, below are the two
        if oldStrandLow.isDrawn5to3() and self._strand5p == oldStrandHigh:
            """
            the oldStrandLow is more 5p than self._strand5p 
            and the self._strand5p was pointing to the oldHighstrand but 
            the high strand didn't have priority so make
            the new strands oligo
            """
            self._strand5p = oldStrandLow.oligo()._strand5p
        elif not oldStrandHigh.isDrawn5to3() and self._strand5p == oldStrandLow:
            """
            the oldStrandHigh is more 5p than self._strand5p 
            and the self._strand5p was pointing to the oldLowStrand but the 
            low strand didn't have priority so make
            the new strands oligo
            """ 
            self._strand5p = oldStrandHigh.oligo()._strand5p
        # end if
    # end def
    
    def strandResized(self, delta):
        """Called by a strand after resize. Delta is used to update the
        length, which may case an appearance change."""
        pass

    ### COMMANDS ###
    