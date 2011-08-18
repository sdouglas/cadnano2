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

class XOverStrand(Strand):
    """
    Owns exactly two bases, each of which is on a different vStrand.
    Since the concepts of a "Left" and "Right" base becomes less useful
    for a strand that crosses between vHelix, XOverStrands adopt the convention
    that self.vBaseL==self.vBase3 and self.vBaseR==self.vBase5.
    """
    logger = None
    kind = 'xovr'
    def __init__(self, vBase3, vBase5):
        self._vBase3 = vBase3
        self._vBase5 = vBase5
        self._pt5 = None

    def __repr__(self):
        return "XOverStrand(%s, %s, %s, %s)"%(vStrand3, vBase3, vStrand5, vBase5)

    def numBases(self):
        return 2

    def assertConsistent(self):
        assert( self.vBase3.vStrand != self.vBase5.vStrand )
        assert( self.vBase3.vStrand.isScaf() == self.vBase5.vStrand.isScaf() )

    def idxsOnStrand(self, vstrand):
        if   vstrand == self._vBase3.vStrand:
            idx = self.vBase3
        elif vstrand == self._vBase5.vStrand:
            idx = self.vBase5
        else:
            assert(False)  # Knows not about the strand of which you speak
        return (idx, idx + 1)

    def vBase3(self):
        return self._vBase3
    def setVBase3(self, newBase, undoStack=None):
        com = self.SetVBase3Command(self, newBase)
        if undoStack != None: undoStack.push(com)
        else:                 com.redo()
    class SetVBase3Command(QUndoCommand):
        def __init__(self, strand, newVBase3):
            QUndoCommand.__init__(self)
            self.strand = strand
            self.newVBase3 = newVBase3
            self.oldVBase3 = strand.vBase3
        def redo(self):
            self.strand.vBase3 = self.newVBase3
        def undo(self):
            self.strand.vBase3 = self.oldVBase3

    def pt5(self):
        """ A floating crossover's destination. A floating crossover is a
        crossover which has a defined vBase3 but has xo.vBase5()==None, created
        during force-crossover creation where the 5' end tracks the mouse until
        it is placed over a valid vBase). This is the point under the mouse in
        PathHelixGroup. """
        return self._pt5
    def setPt5(self, newPt5):
        self._pt5 = newPt5
        self.didMove.emit()
    def vBase5(self):
        return self._vBase5
    def setVBase5(self, newBase, undoStack=None):
        com = self.SetVBase5Command(self, newBase)
        if undoStack != None: undoStack.push(com)
        else:                 com.redo()
    class SetVBase5Command(QUndoCommand):
        def __init__(self, strand, newVBase3):
            QUndoCommand.__init__(self)
            self.strand = strand
            self.newVBase5 = newVBase5
            self.oldVBase5 = strand.vBase5
        def redo(self):
            self.strand.vBase5 = self.newVBase5
        def undo(self):
            self.strand.vBase5 = self.oldVBase5

    def exposedEndsAt(self, vBase):
        """
        Returns 'L' or 'R' if a segment exists at vStrand, idx and it exposes
        an unbound endpoint on its 3' or 5' end. Otherwise returns None.
        """
        if vBase == self.vBase3:
            return 
        ret = ''
        if vBase == self.vBase3:
            drawn5To3 = self.vBase3.drawn5To3()
            if self.conn3() == None:
                ret += '3R' if drawn5To3 else '3L'
        if vBase == self.vBase5:
            drawn5To3 = self.vBase5.drawn5To3()
            if self.conn5() == None:
                ret += '5L' if drawn5To3 else '5R'
        return ret
