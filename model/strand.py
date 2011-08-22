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
util.qtWrapImport('QtGui', globals(), ['QUndoCommand', 'QColor'] )
nextStrandDebugIdentifier = 0

class Strand(QObject):
    logger = None  # Tracing will be written by calling logger.write
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
        self._color = QColor()
        self._hasPreviewConnection3 = False
        self._hasPreviewConnection5 = False
        global nextStrandDebugIdentifier
        self.traceID = nextStrandDebugIdentifier
        nextStrandDebugIdentifier += 1
        self.connectivityChanged.connect(self.apparentConnectivityChanged.emit)

    def assertConsistent(self):
        pass
        # No longer true in light of Visual FeedBack
        # if self.vStrand() != None:
        #     assert(self in self.vStrand().ranges)

    def defaultUndoStack(self):
        return self.part().undoStack()

    def part(self):
        return self.vStrand().part()

    def canMergeWithTouchingStrand(self, other):
        """ We already have that the ranges for self and other could merge """
        return False  # ...but we're default behavior, so we don't care.

    def drawn5To3(self):
        return self.vStrand().drawn5To3()

    def conn3(self):
        return self._conn3
    def conn5(self):
        return self._conn5
    def setConn3(self, newConn, useUndoStack=True, undoStack=None):
        assert(newConn == None or isinstance(newConn, Strand))
        com = self.SetConn3Command(self, newConn)
        if useUndoStack == True and undoStack == None:
            undoStack = self.defaultUndoStack()
        if undoStack != None:
            undoStack.push(com)
        else:
            com.redo()
    def setConn5(self, newConn, useUndoStack=True, undoStack=None):
        assert(newConn == None or isinstance(newConn, Strand))
        com = self.SetConn5Command(self, newConn)
        if useUndoStack == True and undoStack == None:
            undoStack = self.defaultUndoStack()
        if undoStack != None:
            undoStack.push(com)
        else:
            com.redo()
    class SetConn3Command(QUndoCommand):
        def __init__(self, strand, strandNew3):
            QUndoCommand.__init__(self)
            self.strand, self.strandNew3 = strand, strandNew3
            self.strandOld3 = strand.conn3()
            if strandNew3 != None:
                self.newConn3oldConn5 = strandNew3.conn5()
        def redo(self):
            strand = self.strand
            strandNew3 = self.strandNew3
            strandOld3 = self.strandOld3
            if strandNew3 == strandOld3:
                # Shortcut if this is a glorified NOP :)
                return
            # We emit connectivityChanged signals at the end so that all strands
            # are in a consistent state when the notifications get emitted
            strandOld3ConnectivityChanged = False
            strandNew3ConnectivityChanged = False
            newConn3oldConn5ConnectivityChanged = False
            # ---------------------------- A ----------------------------------
            # If strand's 3' end was already connected to another strand
            # (strandOld3) we must break that connection
            if strandOld3 != None:
                strandOld3._conn5 = None
                strandOld3ConnectivityChanged = True
            # ---------------------------- B ----------------------------------
            # If we're connecting to a strand, we need to maintain the doubly-
            # linked-list condition and make sure its 5' end points back
            if strandNew3 != None:
                # ------------------------ BA ---------------------------------
                # If the strand we will be connecting to is already
                # connected to a strand, we must break that connection
                # before claiming its 5' back-pointer for ourselves
                newConn3oldConn5 = self.newConn3oldConn5
                if newConn3oldConn5 != None:
                    newConn3oldConn5._conn3 = None
                    newConn3oldConn5ConnectivityChanged = True
                # ------------------------ BB ---------------------------------
                strandNew3._conn5 = strand
                strandNew3ConnectivityChanged = True
            # ---------------------------- C ----------------------------------
            # Finally, we can go ahead and make the connection
            strand._conn3 = strandNew3
            # -----------------------------------------------------------------
            # Now that things are back in a consistent state, advertise what
            # we've done to the world
            if strandOld3ConnectivityChanged:
                strandOld3.connectivityChanged.emit(strandOld3)
            if newConn3oldConn5ConnectivityChanged:
                newConn3oldConn5.connectivityChanged.emit(newConn3oldConn5)
            if strandNew3ConnectivityChanged:
                strandNew3.connectivityChanged.emit(strandNew3)
            strand.connectivityChanged.emit(strand)
        def undo(self):
            strand = self.strand
            strandNew3 = self.strandNew3
            strandOld3 = self.strandOld3
            if strandNew3 == strandOld3:
                # Shortcut if this is a glorified NOP :)
                return
            # We emit connectivityChanged signals at the end so that all strands
            # are in a consistent state when the notifications get emitted
            strandOld3ConnectivityChanged = False
            strandNew3ConnectivityChanged = False
            newConn3oldConn5ConnectivityChanged = False
            # ---------------------------- ~C ---------------------------------
            # First, we reset strand's connection to what it was before
            strand._conn3 = strandOld3
            # ---------------------------- ~B ---------------------------------
            # If we connected to a new strand, that connection needs to be
            # undone
            if strandNew3 != None:
                newConn3oldConn5 = self.newConn3oldConn5
                # ------------------------ ~BB --------------------------------
                strandNew3._conn5 = newConn3oldConn5
                strandNew3ConnectivityChanged = True
                # ------------------------ ~BA --------------------------------
                # If the strand we connected to had a back-connection before
                # strand itself came along, the back-connection needs its
                # forward pointer reset to maintain the doubly-linked-list
                # condition
                if newConn3oldConn5 != None:
                    newConn3oldConn5._conn3 = strandOld3
                    newConn3oldConn5ConnectivityChanged = True
            # ---------------------------- ~A ---------------------------------
            # If strand was connected to another strand before redo(), we
            # reinstate the reverse connection (we've already reset the forward
            # connection in part ~D)
            if strandOld3 != None:
                strandOld3._conn5 = strand
                strandOld3ConnectivityChanged = True
            # -----------------------------------------------------------------
            # Now that things are back in a consistent state, advertise what
            # we've done to the world
            if strandOld3ConnectivityChanged:
                strandOld3.connectivityChanged.emit(strandOld3)
            if newConn3oldConn5ConnectivityChanged:
                newConn3oldConn5.connectivityChanged.emit(newConn3oldConn5)
            if strandNew3ConnectivityChanged:
                strandNew3.connectivityChanged.emit(strandNew3)
            strand.connectivityChanged.emit(strand)
    class SetConn5Command(QUndoCommand):
        def __init__(self, strand, strandNew5):
            QUndoCommand.__init__(self)
            self.strand, self.strandNew5 = strand, strandNew5
            self.strandOld5 = strand.conn5()
            if strandNew5 != None:
                self.newConn5oldConn3 = strandNew5.conn3()
        def redo(self):
            strand = self.strand
            strandNew5 = self.strandNew5
            strandOld5 = self.strandOld5
            if strandNew5 == strandOld5:
                # Shortcut if this is a glorified NOP :)
                return
            # We emit connectivityChanged signals at the end so that all strands
            # are in a consistent state when the notifications get emitted
            strandOld5ConnectivityChanged = False
            strandNew5ConnectivityChanged = False
            newConn5oldConn3ConnectivityChanged = False
            # ---------------------------- A ----------------------------------
            # If strand's 5' end was already connected to another strand
            # (strandOld5) we must break that connection
            if strandOld5 != None:
                strandOld5._conn3 = None
                strandOld5ConnectivityChanged = True
            # ---------------------------- B ----------------------------------
            # If we're connecting to a strand, we need to maintain the doubly-
            # linked-list condition and make sure its 3' end points back
            if strandNew5 != None:
                # ------------------------ BA ---------------------------------
                # If the strand we will be connecting to is already
                # connected to a strand, we must break that connection
                # before claiming its 3' back-pointer for ourselves
                newConn5oldConn3 = self.newConn5oldConn3
                if newConn5oldConn3 != None:
                    newConn5oldConn3._conn5 = None
                    newConn5oldConn3ConnectivityChanged = True
                # ------------------------ BB ---------------------------------
                strandNew5._conn3 = strand
                strandNew5ConnectivityChanged = True
            # ---------------------------- C ----------------------------------
            # Finally, we can go ahead and make the connection
            strand._conn5 = strandNew5
            # -----------------------------------------------------------------
            # Now that things are back in a consistent state, advertise what
            # we've done to the world
            if strandOld5ConnectivityChanged:
                strandOld5.connectivityChanged.emit(strandOld5)
            if newConn5oldConn3ConnectivityChanged:
                newConn5oldConn3.connectivityChanged.emit(newConn5oldConn3)
            if strandNew5ConnectivityChanged:
                strandNew5.connectivityChanged.emit(strandNew5)
            strand.connectivityChanged.emit(strand)
        def undo(self):
            strand = self.strand
            strandNew5 = self.strandNew5
            strandOld5 = self.strandOld5
            if strandNew5 == strandOld5:
                # Shortcut if this is a glorified NOP :)
                return
            # We emit connectivityChanged signals at the end so that all strands
            # are in a consistent state when the notifications get emitted
            strandOld5ConnectivityChanged = False
            strandNew5ConnectivityChanged = False
            newConn5oldConn3ConnectivityChanged = False
            # ---------------------------- ~C ---------------------------------
            # First, we reset strand's connection to what it was before
            strand._conn5 = strandOld5
            # ---------------------------- ~B ---------------------------------
            # If we connected to a new strand, that connection needs to be
            # undone
            if strandNew5 != None:
                newConn5oldConn3 = self.newConn5oldConn3
                # ------------------------ ~BB --------------------------------
                strandNew5._conn3 = newConn5oldConn3
                strandNew5ConnectivityChanged = True
                # ------------------------ ~BA --------------------------------
                # If the strand we connected to had a back-connection before
                # strand itself came along, the back-connection needs its
                # forward pointer reset to maintain the doubly-linked-list
                # condition
                if newConn5oldConn3 != None:
                    newConn5oldConn3._conn5 = strandOld5
                    newConn5oldConn3ConnectivityChanged = True
            # ---------------------------- ~A ---------------------------------
            # If strand was connected to another strand before redo(), we
            # reinstate the reverse connection (we've already reset the forward
            # connection in part ~D)
            if strandOld5 != None:
                strandOld5._conn3 = strand
                strandOld5ConnectivityChanged = True
            # -----------------------------------------------------------------
            # Now that things are back in a consistent state, advertise what
            # we've done to the world
            if strandOld5ConnectivityChanged:
                strandOld5.connectivityChanged.emit(strandOld5)
            if newConn5oldConn3ConnectivityChanged:
                newConn5oldConn3.connectivityChanged.emit(newConn5oldConn3)
            if strandNew5ConnectivityChanged:
                strandNew5.connectivityChanged.emit(strandNew5)
            strand.connectivityChanged.emit(strand)
    def connL(self, strand=None):
        """ Get the strand that is covalently attached to the left end of
        self (left is 5' if drawn5To3) """
        if strand == None: strand = self.vStrand()
        return self.conn5() if strand.drawn5To3() else self.conn3()
    def connR(self, strand=None):
        """ Get the strand that is covalently attached to the right end of
        self (right is 3' if drawn5To3) """
        if strand == None: strand = self.vStrand()
        return self.conn3() if strand.drawn5To3() else self.conn5()
    def setConnL(self, newConn, useUndoStack=True, undoStack=None):
        if self.vStrand().drawn5To3():
            self.setConn5(newConn, useUndoStack, undoStack)
        else:
            self.setConn3(newConn, useUndoStack, undoStack)
    def setConnR(self, newConn, useUndoStack=True, undoStack=None):
        if self.vStrand().drawn5To3():
            self.setConn3(newConn, useUndoStack, undoStack)
        else:
            self.setConn5(newConn, useUndoStack, undoStack)

    def clearVFB(self):
        print "clr %s"%self
    def setVFB(self, clrStart, afterClrEnd, endptsToConnect):
        print "set %s (%i, %i) %s"%(self, clrStart, afterClrEnd, endptsToConnect)

    def hasPreviewConnection3(self):
        return self._hasPreviewConnection3
    def hasPreviewConnection5(self):
        return self._hasPreviewConnection5
    def hasPreviewConnectionL(self):
        if self.vStrand().drawn5To3():
            return self.hasPreviewConnection5() 
        else:
            return self.hasPreviewConnection3()
    def hasPreviewConnectionR(self):
        if self.vStrand().drawn5To3():
            return self.hasPreviewConnection3() 
        else:
            return self.hasPreviewConnection5()
    def setHasPreviewConnectionL(self, newVal):
        if self.vStrand().drawn5To3():
            self.setHasPreviewConnection5(newVal)
        else:
            self.setHasPreviewConnection3(newVal)
    def setHasPreviewConnectionR(self, newVal):
        if self.vStrand().drawn5To3():
            self.setHasPreviewConnection3(newVal)
        else:
            self.setHasPreviewConnection5(newVal)
    def setHasPreviewConnection3(self, newVal):
        if newVal == self._hasPreviewConnection3:
            return
        self._hasPreviewConnection3 = newVal
        self.apparentConnectivityChanged.emit(self)
    def setHasPreviewConnection5(self, newVal):
        if newVal == self._hasPreviewConnection5:
            return
        self._hasPreviewConnection5 = newVal
        self.apparentConnectivityChanged.emit(self)

    def color(self):
        return QColor()

    def shouldHighlight(self):
        return False

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
        