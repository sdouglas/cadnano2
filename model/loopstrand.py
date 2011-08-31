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

import util, sys
from model.strand import Strand
util.qtWrapImport('QtCore', globals(), ['QObject', 'pyqtSignal'] )
util.qtWrapImport('QtGui', globals(), ['QUndoCommand'] )
nextStrandDebugIdentifier = 0

class LoopStrand(Strand):
    """
    Represents multiple actual bases located at a single virtual base. It's
    called 'Loop' because in the limit where you have many bases that occupy
    a single virtual base they bulge outwards, forming a loop.
    """
    logger = None
    kind = 'loop'
    numBasesChanged = pyqtSignal(object)  # emitter passes self as the object
    def __init__(self, vBase, numberOfActualBases):
        Strand.__init__(self)
        self._vBase = vBase
        self._numBases = numberOfActualBases
    def assertConsistent(self):
        Strand.assertConsistent(self)
    def __repr__(self):
        return "LoopStrand(%s, %i)"%(self.vBase(), self.numBases())
    def vBase(self):    return self._vBase
    def vBaseL(self):   return self._vBase
    def vBaseR(self):   return self._vBase + 1
    def idxs(self):
        idx = self._vBase.vIndex()
        return (idx, idx + 1)

    def setVBase(self, newVBase, undoStack):
        com = SetVBaseCommand(self, newVBase)
        if undoStack != None:
            undoStack.push(com)
        else:
            com.redo()
    class SetVBaseCommand(QUndoCommand):
        def __init__(self, strand, newVBase):
            QUndoCommand.__init__(self)
            self.strand = strand
            self.newVBase, self.oldVBase = newVBase, strand.vBase
        def redo(self):
            self.strand.vBase = self.newVBase
        def undo(self):
            self.strand.vBase = self.oldVBase

    def numBases(self):
        return self._numBases
    def setNumBases(self, newNumBases, useUndoStack=True, undoStack=None):
        if useUndoStack == True and undoStack == None:
            undoStack = self.vBase().undoStack()
            com = self.SetNumBasesCommand(self, newNumBases)
        if useUndoStack:
            undoStack.push(com)
        else:
            com.redo()
    class SetNumBasesCommand(QUndoCommand):
        def __init__(self, strand, newNumBases):
            QUndoCommand.__init__(self)
            self.oldNumBases = strand._numBases
            self.newNumBases = newNumBases
            self.strand = strand
        def redo(self):
            self.strand._numBases = self.newNumBases
            self.strand.numBasesChanged.emit(self.strand)
        def undo(self):
            self.strand._numBases = self.oldNumBases
            self.strand.numBasesChanged.emit(self.strand)

    def vStrand(self):
        return self.vBase().vStrand()

    def removalWillBePushed(self, useUndoStack, undoStack):
        """Called before the command that causes removal of self to be pushed
        to the undoStack is pushed (in contrast to willBeRemoved which is called
        every time the undoStack decides to remove self). This is the place to
        push side effects of removal onto the undo stack."""
        if self.connL() != None:
            self.setConnL(None, useUndoStack, undoStack)
        if self.connR() != None:
            self.setConnR(None, useUndoStack, undoStack)

    def exposedEndsAt(self, vBase):
        """
        Returns a string containing some (possibly empty) combination of 'L',
        'R', '3', and '5' where each character is present if the corresponding
        end is exposed
        """
        ret = ''
        if vBase == self.vBase():
            drawn5To3 = vBase.vStrand().drawn5To3()
            if self.connL() == None:
                ret += 'L5' if drawn5To3 else 'L3'
            if self.connR() == None:
                ret += 'R3' if drawn5To3 else 'R5'
        return ret
