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
import copy
from strand import Strand
# import Qt stuff into the module namespace with PySide, PyQt4 independence
util.qtWrapImport('QtCore', globals(), ['pyqtSignal', 'QObject'])
util.qtWrapImport('QtGui', globals(), ['QUndoCommand'])


class Oligo(QObject):
    """
    Oligo is a group of Strands that are connected via 5' and/or 3'
    connections. It corresponds to the physical DNA strand, and is thus
    used tracking and storing properties that are common to a single strand,
    such as its color.

    Commands that affect Strands (e.g. create, remove, merge, split) are also
    responsible for updating the affected Oligos.
    """
    def __init__(self, part, color=None):
        super(Oligo, self).__init__(part)
        self._part = part
        self._strand5p = None
        self._length = 0
        self._isLoop = False
        self._color = color if color else "#0066cc"
    # end def

    def __repr__(self):
        clsName = self.__class__.__name__
        olgId = str(id(self))[-4:]
        strandType = "Stap" if self.isStaple() else "Scaf"
        vhNum = self._strand5p.strandSet().virtualHelix().number()
        idx = self._strand5p.idx5Prime()
        return "<%s %s>(%s %d[%d])" % (clsName, olgId, strandType, vhNum, idx)

    def shallowCopy(self):
        olg = Oligo(self._part)
        olg._strand5p = self._strand5p
        olg._length = self._length
        olg._isLoop = self._isLoop
        olg._color = self._color
        return olg
    # end def

    def deepCopy(self, part):
        olg = Oligo(part)
        olg._strand5p = None
        olg._length = self._length
        olg._isLoop = self._isLoop
        olg._color = self._color
        return olg
    # end def

    ### SIGNALS ###
    oligoIdentityChangedSignal = pyqtSignal(QObject)  # new oligo
    oligoAppearanceChangedSignal = pyqtSignal(QObject)  # self
    oligoSequenceAddedSignal = pyqtSignal(QObject)  # self
    oligoSequenceClearedSignal = pyqtSignal(QObject)  # self

    ### SLOTS ###

    ### ACCESSORS ###

    def undoStack(self):
        return self._part.undoStack()
    # end def

    def part(self):
        return self._part

    def strand5p(self):
        return self._strand5p

    def setStrand5p(self, strand):
        self._strand5p = strand
    # end def

    def color(self):
        return self._color
    # end def

    ### PUBLIC METHODS FOR QUERYING THE MODEL ###
    def isLoop(self):
        return self._isLoop

    def isStaple(self):
        return self._strand5p.isStaple()

    def length(self):
        return self._length
    # end def

    def sequence(self):
        temp = self.strand5p()
        if not temp:
            return None
        if temp.sequence():
            return ''.join([Strand.sequence(strand) \
                        for strand in self.strand5p().generator3pStrand()])
        else:
            return None
    # end def

    def sequenceExport(self):
        vhNum5p = self.strand5p().virtualHelix().number()
        idx5p = self.strand5p().idx5Prime()
        seq = ''
        for strand in self.strand5p().generator3pStrand():
            seq = seq + Strand.sequence(strand, forExport=True)
            if strand.connection3p() == None:  # last strand in the oligo
                vhNum3p = strand.virtualHelix().number()
                idx3p = strand.idx3Prime()
        output = "%d[%d],%d[%d],%s,%s,%s\n" % \
                (vhNum5p, idx5p, vhNum3p, idx3p, seq, len(seq), self._color)
        return output
    # end def

    def shouldHighlight(self):
        if not self._strand5p:
            return False
        if self._strand5p.isScaffold():
            return False
        if self.length() < 18:
            return True
        if self.length() > 50:
            return True
        return False
    # end def

    ### PUBLIC METHODS FOR EDITING THE MODEL ###
    def applyColor(self, color, useUndoStack=True):
        if color == self._color:
            return  # oligo already has color
        c = Oligo.ApplyColorCommand(self, color)
        util.execCommandList(self, [c], desc="Color Oligo", useUndoStack=useUndoStack)
    # end def

    def applySequence(self, sequence, useUndoStack=True):
        c = Oligo.ApplySequenceCommand(self, sequence)
        util.execCommandList(self, [c], desc="Apply Sequence", useUndoStack=useUndoStack)
    # end def

    def applySequenceCMD(self, sequence, useUndoStack=True):
        return Oligo.ApplySequenceCommand(self, sequence)
    # end def

    def setLoop(self, bool):
        self._isLoop = bool

    ### PUBLIC SUPPORT METHODS ###
    def addToPart(self, part):
        self._part = part
        self.setParent(part)
        part.addOligo(self)
    # end def

    def destroy(self):
        # QObject also emits a destroyed() Signal
        self.setParent(None)
        self.deleteLater()
    # end def

    def decrementLength(self, delta):
        self.setLength(self._length-delta)
    # end def

    def incrementLength(self, delta):
        self.setLength(self._length+delta)
    # end def

    def refreshLength(self):
        temp = self.strand5p()
        if not temp:
            return
        length = 0
        for strand in temp.generator3pStrand():
            length += strand.totalLength()
        self.setLength(length)
    # end def

    def removeFromPart(self):
        """
        This method merely disconnects the object from the model.
        It still lives on in the undoStack until clobbered

        Note: don't set self._part = None because we need to continue passing
        the same reference around.
        """
        self._part.removeOligo(self)
        self.setParent(None)
    # end def

    def setColor(self, color):
        self._color = color
    # end def

    def setLength(self, length):
        before = self.shouldHighlight()
        self._length = length
        if before != self.shouldHighlight():
            self.oligoAppearanceChangedSignal.emit(self)
    # end def

    def strandMergeUpdate(self, oldStrandLow, oldStrandHigh, newStrand):
        """
        This method sets the isLoop status of the oligo and the oligo.
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
            if oldStrandLow.connection5p() != None:
                self._strand5p = oldStrandLow.oligo()._strand5p
            else:
                self._strand5p = newStrand
        elif not oldStrandHigh.isDrawn5to3() and self._strand5p == oldStrandLow:
            """
            the oldStrandHigh is more 5p than self._strand5p 
            and the self._strand5p was pointing to the oldLowStrand but the 
            low strand didn't have priority so make
            the new strands oligo
            """ 
            if oldStrandLow.connection5p() != None:
                self._strand5p = oldStrandHigh.oligo()._strand5p
            else:
                self._strand5p = newStrand
        # end if
    # end def

    def strandResized(self, delta):
        """
        Called by a strand after resize. Delta is used to update the length,
        which may case an appearance change.
        """
        pass
    # end def

    def strandSplitUpdate(self, newStrand5p, newStrand3p, oligo3p, oldMergedStrand):
        """
        If the oligo is a loop, splitting the strand does nothing. If the
        oligo isn't a loop, a new oligo must be created and assigned to the
        newStrand and everything connected to it downstream.
        """
        # if you split it can't be a loop
        self._isLoop = False
        if oldMergedStrand.oligo().isLoop():
            self._strand5p = newStrand3p
            return
        else:
            if oldMergedStrand.connection5p() == None:
                self._strand5p = newStrand5p
            else:
                self._strand5p = oldMergedStrand.oligo()._strand5p
            oligo3p._strand5p = newStrand3p
        # end else
    # end def

    ### PRIVATE SUPPORT METHODS ###

    ### COMMANDS ###
    class ApplyColorCommand(QUndoCommand):
        def __init__(self, oligo, color):
            super(Oligo.ApplyColorCommand, self).__init__()
            self._oligo = oligo
            self._newColor = color
            self._oldColor = oligo.color()
        # end def

        def redo(self):
            olg = self._oligo
            olg.setColor(self._newColor)
            olg.oligoAppearanceChangedSignal.emit(olg)
        # end def

        def undo(self):
            olg = self._oligo
            olg.setColor(self._oldColor)
            olg.oligoAppearanceChangedSignal.emit(olg)
        # end def
    # end class

    class ApplySequenceCommand(QUndoCommand):
        def __init__(self, oligo, sequence):
            super(Oligo.ApplySequenceCommand, self).__init__()
            self._oligo = oligo
            self._newSequence = sequence
            self._oldSequence = oligo.sequence()
            self._strandType = oligo._strand5p.strandSet().strandType()
        # end def

        def redo(self):
            olg = self._oligo
            nS = ''.join(self._newSequence) if self._newSequence else None
            oligoList = [olg]
            for strand in olg.strand5p().generator3pStrand():
                usedSeq, nS = strand.setSequence(nS)
                # get the compliment ahead of time
                usedSeq = util.comp(usedSeq) if usedSeq else None
                compSS = strand.strandSet().complementStrandSet()
                for compStrand in compSS._findOverlappingRanges(strand):
                    subUsedSeq = compStrand.setComplementSequence(usedSeq, strand)
                    oligoList.append(compStrand.oligo())
                # end for
                if nS == None:
                    break
            # end for
            for oligo in oligoList:
                oligo.oligoSequenceAddedSignal.emit(oligo)
        # end def

        def undo(self):
            olg = self._oligo
            oS = ''.join(self._oldSequence) if self._oldSequence else None

            oligoList = [olg]

            for strand in olg.strand5p().generator3pStrand():
                usedSeq, oS = strand.setSequence(oS)

                # get the compliment ahead of time
                usedSeq = util.comp(usedSeq) if usedSeq else None
                compSS = strand.strandSet().complementStrandSet()
                for compStrand in compSS._findOverlappingRanges(strand):
                    subUsedSeq = compStrand.setComplementSequence(usedSeq, strand)
                    oligoList.append(compStrand.oligo())
                # end for
            # for

            # olg.oligoSequenceClearedSignal.emit(olg)
            for oligo in oligoList:
                oligo.oligoSequenceAddedSignal.emit(oligo)
        # end def
    # end class
    class ApplyColorCommand(QUndoCommand):
        def __init__(self, oligo, color):
            super(Oligo.ApplyColorCommand, self).__init__()
            self._oligo = oligo
            self._newColor = color
            self._oldColor = oligo.color()
        # end def

        def redo(self):
            olg = self._oligo
            olg.setColor(self._newColor)
            olg.oligoAppearanceChangedSignal.emit(olg)
        # end def

        def undo(self):
            olg = self._oligo
            olg.setColor(self._oldColor)
            olg.oligoAppearanceChangedSignal.emit(olg)
        # end def
    # end class

    class RemoveOligoCommand(QUndoCommand):
        def __init__(self, oligo, sequence):
            super(Oligo.RemoveOligoCommand, self).__init__()
        # end def

        def redo(self):
            pass
        # end def

        def undo(self):
            pass
        # end def
    # end class
# end class
    