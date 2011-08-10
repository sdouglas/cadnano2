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

class Strand(QObject):
    didMove = pyqtSignal(object)  # Arg is the object emitting the signal
    willBeRemoved = pyqtSignal(object)  # Arg is the object emitting the signal
    connectivityChanged = pyqtSignal(object)  # Arg is the object emitting the s
    apparentConnectivityChanged = pyqtSignal(object)   # Arg is the object emitt
    didLiftoff = pyqtSignal(object)  # Arg is the object emitting the signal
    didSetdown = pyqtSignal(object)  # Arg is the object emitting the signal
    def __init__(self):
        QObject.__init__(self)
        self._conn3 = None  # The Strand connected to the 3' end of self
        self._conn5 = None  # The Strand connected to the 5' end of self
        self._lifted = False
        global nextStrandDebugIdentifier
        self.traceID = nextStrandDebugIdentifier
        nextStrandDebugIdentifier += 1

    def assertConsistent(self):
        if self.vStrand != None:
            assert(self in self.vStrand.ranges)

    def defaultUndoStack(self):
        return self.part().undoStack()

    def part(self):
        return self.vStrand().part()

    def canMergeWithTouchingStrand(self, other):
        """ We already have that the ranges for self and other could merge """
        return False  # ...but we're default behavior, so we don't care.

    def conn3(self):
        return self._conn3
    def setConn3(self, newConn, useUndoStack=True, undoStack=None):
        com = self.SetConn3Command(self, newConn)
        if useUndoStack == True and undoStack == None:
            undoStack = self.defaultUndoStack()
        if undoStack != None:
            undoStack.push(com)
        else:
            com.redo()
    class SetConn3Command(QUndoCommand):
        def __init__(self, strand, newConn3):
            self.strand, self.newConn3 = strand, newConn3
            self.oldConn3 = strand.conn3()
        def redo(self, actuallyUndo=False):
            strand = self.strand
            newValue = self.oldConn3 if actuallyUndo else self.newConn3
            if strand._conn3 == newValue:
                return
            strand._conn3 = newValue
            strand.connectivityChanged.emit(strand)
        def undo(self):
            self.redo(actuallyUndo=True)

    def conn5(self):
        return self._conn5
    def setConn5(self, newConn, useUndoStack=True, undoStack=None):
        com = self.SetConn5Command(self, newConn)
        if useUndoStack == True and undoStack == None:
            undoStack = self.defaultUndoStack()
        if undoStack != None:
            undoStack.push(com)
        else:
            com.redo()
    class SetConn5Command(QUndoCommand):
        def __init__(self, strand, newConn5):
            self.strand, self.newConn5 = strand, newConn5
            self.oldConn5 = strand.conn5()
        def redo(self, actuallyUndo=False):
            strand = self.strand
            newValue = self.oldConn5 if actuallyUndo else self.newConn5
            if strand._conn5 == newValue:
                return
            strand._conn5 = newValue
            strand.connectivityChanged.emit(strand)
        def undo(self):
            self.redo(actuallyUndo=True)

    def connL(self):
        return self.conn5 if self.vStrand.drawn5To3() else self.conn3
    def setConnL(self, newConn, useUndoStack=True, undoStack=None):
        if self.vStrand.drawn5To3():
            self.setConn5(newConn, useUndoStack, undoStack)
        else:
            self.setConn3(newConn, useUndoStack, undoStack)

    def connR(self):
        return self.conn3 if self.vStrand.drawn5To3() else self.conn5
    def setConnR(self, newConn, useUndoStack=True, undoStack=None):
        if self.vStrand.drawn5To3():
            self.setConn3(newConn, useUndoStack, undoStack)
        else:
            self.setConn5(newConn, useUndoStack, undoStack)

    def clearVFB(self):
        print "clr %s"%self
    def setVFB(self, clrStart, afterClrEnd, endptsToConnect):
        print "set %s (%i, %i) %s"%(self, clrStart, afterClrEnd, endptsToConnect)

    def setdown(self, useUndoStack=True, undoStack=None):
        """ Turns a strand used for VisualFeedBack into a strand actually
        embedded in the data model. If we imagine that the VisualFeedBack
        strands hover above the model, which is how they appear in the UI, the
        name of this function makes sense. """
        self.vStrand().addStrand(self, useUndoStack, undoStack)
        self._lifted = False
        self.didSetdown.emit(self)

    def liftoff(self, useUndoStack=True, undoStack=None):
        """ Removes a strand from the model so that it can be used in
        VisualFeedBack mode. If we imagine that the VisualFeedBack
        strands hover above the model, which is how they appear in the UI, the
        name of this function makes sense. """
        self._lifted = True
        self.didLiftoff.emit(self)
        