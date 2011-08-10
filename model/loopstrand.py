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
util.qtWrapImport('QtCore', globals(), ['QObject', 'pyqtSignal'] )
util.qtWrapImport('QtGui', globals(), ['QUndoCommand'] )
nextStrandDebugIdentifier = 0
logger = None  # Tracing will be written by calling traceDest.write
logger = sys.stdout

class LoopStrand(Strand):
    """
    Represents multiple actual bases located at a single virtual base. It's
    called 'Loop' because in the limit where you have many bases that occupy
    a single virtual base they bulge outwards, forming a loop.
    """
    def __init__(self, vBase, numberOfActualBases):
        NormalStrand.__init__(self)
        self.vBase = vBase
        self.numBases = numberOfActualBases
    def assertConsistent(self):
        Strand.assertConsistent(self)
    def __repr__(self):
        return "LoopStrand(%s, %i)"%(self.vBase, self.numBases)
    def numBases(self): return self.numBases
    def vBase(self):    return self.vBase
    def vBaseL(self):   return self.vBase
    def vBaseR(self):   return self.vBase + 1

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

    def vStrand(self):
        return self.vBase().vStrand

    def exposedEndAt(self, vStrand, vIdx):
        """
        Returns 'L' or 'R' if a segment exists at vStrand, idx and it
        exposes an unbound endpoint on its 3' or 5' end. Otherwise returns None.
        """
        assert(vStrand == self.vStrand)
        if vIdx == self.vIdx:
            if self.connL == None: return 'L'
            if self.connR == None: return 'R'
        return None
