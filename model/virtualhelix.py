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

"""
virtualhelix.py
Created by Jonathan deWerd on 2011-01-26.
"""
import sys
from exceptions import AttributeError, IndexError
from itertools import product
from .enum import LatticeType, Parity, StrandType, BreakType
from .enum import Crossovers, EndType
from PyQt4.QtCore import pyqtSignal, QObject
from PyQt4.QtGui import QUndoCommand, QUndoStack, QColor
from .base import Base
from util import *
from cadnano import app
import ui.styles as styles
import re


class VirtualHelix(QObject):
    """Stores staple and scaffold routing information."""
    basesModified = pyqtSignal()
    dimensionsModified = pyqtSignal()

    def __init__(self, numBases=21, idnum=0, incompleteArchivedDict=None):
        super(VirtualHelix, self).__init__()
        # Row, col are always owned by the parent part;
        # they cannot be specified in a meaningful way
        # for a detached helix (part==None). Only dnaparts
        # get to modify these.
        self._row = None
        self._col = None
        # If self._part exists, it owns self._number
        # in that only it may modify it through the
        # private interface. The public interface for
        # setNumber just routes the call to the parent
        # dnapart if one is present. If self._part == None
        # the vhelix owns self._number and may modify it.
        self._number = idnum
        # Attaching to a part via setPart gives the part ownership of
        # the above three properties (it asks part to set them,
        # self should no longer modify _row, _col, or _number)
        self._part = None
        # The base arrays are owned entirely by virtualhelix
        self._stapleBases = []
        self._scaffoldBases = []
        
        """
        This is for loops and skips.
        a dictionary for loops and skips is added
        for loops and skips
        of the form { index: count }
        + count indicates loop 
        - count indicates skip
        """
        self._stapleLoops = {}
        self._scaffoldLoops = {}
        
        # setSandboxed(True) gives self a private undo stack
        # in order to insulate undo/redo on the receiver
        # from global undo/redo (so that if a haywire tool
        # using undo() and redo() to give a live preview of
        # tho tool's effect calls undo() a million times it
        # doesn't make the document disappear). setSandboxed(False)
        # then clears _privateUndoStack at which point self
        # goes back to using the part / document undo stack.
        self._privateUndoStack = None
        self._sandboxed = False
        # numBases is a simulated property that corresponds to the
        # length of _stapleBases and _scaffoldBases
        if incompleteArchivedDict:
            numBases = len(re.split('\s+',\
                                    incompleteArchivedDict['staple'])) - 1
        self.setNumBases(numBases, notUndoable=True)
        # Command line convenience for -i mode
        if app().v != None:
            app().v[self.number()] = self

    def __repr__(self):
        return 'vh%i' % self.number()

    def __str__(self):
        scaf = '%-2iScaffold: ' % self.number() + \
                            ' '.join((str(b) for b in self._scaffoldBases))
        stap = '%-2iStaple:   ' % self.number() + \
                                ' '.join((str(b) for b in self._stapleBases))
        return scaf + '\n' + stap

    def part(self):
        return self._part

    def _setPart(self, newPart, row, col, num):
        """Should only be called by dnapart. Use dnapart's
        setVirtualHelixAt to add a virtualhelix to a dnapart."""
        if self._part:
            self._part.setVirtualHelixAt((row, col), None)
        self._row = row
        self._col = col
        self._number = num
        self._part = newPart
        self.setNumBases(newPart.numBases(), notUndoable=True)

    def numBases(self):
        return len(self._stapleBases)

    def setNumBases(self, newNumBases, notUndoable=False):
        newNumBases = int(newNumBases)
        assert(newNumBases >= 0)
        oldNB = self.numBases()
        if self.part():
            assert(self.part().numBases() == newNumBases)
        if newNumBases == oldNB:
            return
        if newNumBases > oldNB:
            c = self.SetNumBasesCommand(self, newNumBases)
            if notUndoable:
                c.redo()
            else:
                self.undoStack().push(c)
        if newNumBases < oldNB:
            c0 = self.ClearStrandCommand(self, StrandType.Scaffold,\
                                         newNumBases, oldNB)
            c1 = self.ClearStrandCommand(self, StrandType.Staple,\
                                         newNumBases, oldNB)
            c2 = self.SetNumBasesCommand(self, newNumBases)
            if notUndoable:
                c0.redo()
                c1.redo()
                c2.redo()
            else:
                u = self.undoStack()
                u.beginMacro("Changing the number of bases")
                u.push(c0)
                u.push(c1)
                u.push(c2)
                u.endMacro()

    def number(self):
        """return VirtualHelix number"""
        return self._number

    def setNumber(self, newNumber):
        if self.part():
            self.part().renumberVirtualHelix(self, newNumber)
        else:  # If we aren't attached to a part
            self._number = newNumber

    def selected(self):
        return self in self.part().selection()

    # dnapart owns its selection, so look there for related
    # event emission
    def setSelected(self, willBeSelected):
        currentSelection = self.part().selection()
        selected = self in currentSelection
        needsSelecting = willBeSelected and not selected
        needsDeselectig = not willBeSelected and selected
        if needsSelecting:
            # We're modifying part()'s selection
            # object beneath it. I won't tell it
            # if you don't. Safety would demand
            # selection() returns a copy.
            currentSelection.append(self)
        elif needsDeselectig:
            currentSelection.remove(self)
        self.part().setSelection(currentSelection)

    def _setNumber(self, newNumber):
        """_part is responsible for assigning ids, so only it gets to
        use this method."""
        self._number = newNumber
        self.changed.emit()

    def coord(self):
        return (self._row, self._col)

    def evenParity(self):
        """
        returns True or False
        """
        if self._part:
            return self._part.virtualHelixParityEven(self)
        else:
            return self._number % 2 == 0

    def directionOfStrandIs5to3(self, strandtype):
        """
        method to determine 5' to 3' or 3' to 5'
        """
        if self.evenParity() and strandtype == StrandType.Scaffold:
            return True
        elif not self.evenParity() and strandtype == StrandType.Staple:
            return True
        else:
            return False
    # end def

    def row(self):
        """return VirtualHelix helical-axis row"""
        return self._row

    def col(self):
        """return VirtualHelix helical-axis column"""
        return self._col

    def _strand(self, strandType):
        """The returned strand should be considered privately
        mutable"""
        if strandType == StrandType.Scaffold:
            return self._scaffoldBases
        elif strandType == StrandType.Staple:
            return self._stapleBases
        else:
            raise IndexError("%s is not Scaffold=%s or Staple=%s"%(strandType, StrandType.Scaffold, StrandType.Staple))
            
    def _loop(self, strandType):
        """The returned loop list should be considered privately
        mutable"""
        if strandType == StrandType.Scaffold:
            return self._scaffoldLoops
        elif strandType == StrandType.Staple:
            return self._stapleLoops
        else:
            raise IndexError("%s is not Scaffold=%s or Staple=%s"%(strandType, StrandType.Scaffold, StrandType.Staple))

    ########################### Access to Bases ###################
    def hasBaseAt(self, strandType, index):
        """Returns true if a base is present at index on strand strandtype."""
        base = self._baseAt(strandType, index)
        if not base:
            return False
        else:
            return not base.isEmpty()

    def validatedBase(self, strandType, index, raiseOnErr=False):
        """Makes sure the basespec (strandType,index) is valid
        and raises or returns (None, None) according to raiseOnErr if
        it isn't valid"""
        if strandType != StrandType.Scaffold and \
                                            strandType != StrandType.Staple:
            if raiseOnErr:
                raise IndexError("Base (strand:%s index:%i) Not Valid" % \
                                                        (strandType, index))
            return (None, None)
        index = int(index)
        if index < 0 or index > self.numBases() - 1:
            if raiseOnErr:
                raise IndexError("Base (strand:%s index:%i) Not Valid" % \
                                                        (strandType, index))
            return (None, None)
        return (strandType, index)

    def _baseAt(self, strandType, index, raiseOnErr=False):
        strandType, index = \
                self.validatedBase(strandType, index, raiseOnErr=raiseOnErr)
        if strandType == None:
            return None
        return self._strand(strandType)[index]

    def hasCrossoverAt(self, strandType, index):
        """docstring for hasScafCrossoverAt"""
        base = self._baseAt(strandType, index)
        if not base:
            return False
        else:
            return base.isCrossover()

    def hasStrandAt(self, strandType, index):
        """A strand base is a base that is connected to
        other bases on both sides (possibly over a staple)"""
        base = self._baseAt(strandType, index)
        if not base:
            return False
        else:
            return base.isStrand()

    def hasEndAt(self, strandType, index):
        base = self._baseAt(strandType, index)
        if not base:
            return False
        else:
            return base.isEnd()
    
    def getSegments(self, strandType):
        """Returns a list of segments of connected bases in the form
        [(startIdx, startIsXO, endIdx, endIsXO), ...]"""
        ret = []
        strand = self._strand(strandType)
        i, s = 0, None
        # s is the start index of the segment
        for i in range(len(strand)):
            b = strand[i]
            isXO = b.isCrossover()
            isEnd = b.isEnd()
            if not isXO and not isEnd:
                continue
            if s == None:
                s = (i, isXO)
            else:
                ret.append(s + (i, isXO))
                s = None
        return ret

    def get3PrimeXovers(self, strandType):
        """
        Returns a tuple of tuples of the FROM base (3p end) the TO base
        (5p end)
        """
        ret = []
        strand = self._strand(strandType)
        i, s = 0, None
        for base in strand:
            if base.is3primeXover():
                ret.append(((self, base._n),\
                    (base._3pBase.vhelix(), base._3pBase._n)))
        # end for
        return ret
    # end def

    def getXover(self, strandType, idx):
        """
        Takes an index and returns a tuple of the FROM (3p) end helix and
        the vhelix and index it points to on the TO (5p) end.
        """
        strand = self._strand(strandType)
        if strand[idx].is3primeXover():
            return ((self, idx),\
                    (strand[idx]._3pBase.vhelix(), strand[idx]._3pBase._n))
        else:  # it's a 5-prime Xover end, reverse it
            return ((strand[idx]._5pBase.vhelix(), strand[idx]._5pBase._n),\
                    (self, idx))
    # end def

    def colorOfBase(self, strandType, idx):
        if strandType == StrandType.Scaffold:
            return styles.bluestroke
            # return QColor(44, 51, 141)
        # hue = 47 * idx + 31 * self.number()
        # return QColor.fromHsl(hue % 256, 255, 128)
        c = QColor(self._stapleBases[idx].getColor())
        # print "colorOfBase", idx, c.name(), self._stapleBases[idx].getColor()
        return c

    def sandboxed(self):
        return self._sandboxed

    def setSandboxed(self, sb):
        """Set True to give the receiver a temporary undo stack
        that will be deleted upon set False. Since tools can be
        made live by repeatedly pushing and popping undo commands,
        it occasionally happens that a bug pops many things off the
        undo stack. The temporary undo stack prevents excessive popping
        from reverting the document to a blank state."""
        if sb and not self._privateUndoStack:
            self._sandboxed = True
            if not self._privateUndoStack:
                self._privateUndoStack = QUndoStack()
        elif not sb:
            if self._sandboxed:
                self._sandboxed = False
                self._privateUndoStack = None

    def undoStack(self):
        if self._privateUndoStack != None:
            return self._privateUndoStack
        if self.part() != None:
            return self.part().undoStack()
        if self._privateUndoStack == None:
            print "Creating detached undo stack for %s" % self
            self._privateUndoStack = QUndoStack()
        return self._privateUndoStack

    ################## Public Base Modification API #########
    """
    Overview: the bases in a virtualhelix can be modified
    with the public methods, which under the hood just validate
    their arguments and push
    undo commands (of a similar name to the public methods)
    that call private methods (often of exactly the same name
    as the public methods except for a prefixed underscore).
    Outside World -> doSomething() -> DoSomethingUndoCommand ->
        _doSomething() -> Private API
    or Outside World -> doSomething() -> DoSomethingUndoCommand -> Private API
    """
    def emitModificationSignal(self):
        self.basesModified.emit()

    def connectStrand(self, strandType, startIndex, endIndex):
        """
        Connects sequential bases on a single strand, starting with
        startIndex and ending with etdIndex (inclusive)
        Sets {s.n, (s+1).np, ..., (e-2).np, (e-1).np, e.p}
        """
        strand = self._strand(strandType)
        endIndex, startIndex = int(max(startIndex, endIndex)),\
                                        int(min(startIndex, endIndex))
        startIndex = clamp(startIndex, 0, len(strand) - 1)
        endIndex = clamp(endIndex, 0, len(strand) - 1)
        c = self.ConnectStrandCommand(self, strandType, startIndex, endIndex)
        self.undoStack().push(c)

    def clearStrand(self, strandType, startIndex, endIndex):
        endIndex, startIndex = int(max(startIndex, endIndex)),\
                                        int(min(startIndex, endIndex))
        strand = strandType == StrandType.Scaffold and \
            self._scaffoldBases or self._stapleBases
        startIndex = clamp(startIndex, 1, len(strand))
        endIndex = clamp(endIndex, 1, len(strand))
        c = self.ClearStrandCommand(self, strandType, startIndex, endIndex)
        self.undoStack().push(c)

    def installXoverFrom3To5(self, strandType, fromIndex, toVhelix, toIndex):
        """
        The from base must provide the 3' pointer, and to must provide 5'.
        """
        if strandType == StrandType.Scaffold:
            assert(self.possibleNewCrossoverAt(StrandType.Scaffold, \
                                            fromIndex, toVhelix, toIndex))
        elif strandType == StrandType.Staple:
            assert(self.possibleNewCrossoverAt(StrandType.Staple, \
                                            fromIndex, toVhelix, toIndex))
        else:
            raise IndexError("%s doesn't look like a StrandType" % strandType)
        c = self.Connect3To5Command(strandType, self, fromIndex, toVhelix,\
                                    toIndex)
        self.undoStack().push(c)

    def removeXoverTo(self, strandType, fromIndex, toVhelix, toIndex):
        """
        The from base must provide the 3' pointer, and to must provide 5'.
        """
        strand = self._strand(strandType)
        fromBase = strand[fromIndex]
        toBase = toVhelix._strand(strandType)[toIndex]
        if fromBase._3pBase != toBase or fromBase != toBase._5pBase:
            raise IndexError("Crossover does not exist to be removed.")
        c = self.Break3To5Command(strandType, self, fromIndex)
        self.undoStack().push(c)
        
    def hasLoopAt(self, strandType, index):
        """
        check for key "index" in the loop dictionary based on strandtype
        returns 0 if no loop or skip and returns the length of the skip
        otherwise
        """
        if index in self._loop(strandType):
            return self._loop(strandType)[index]
        else:
            return 0
    # end def
        
    def installLoop(self, strandType, index, loopsize):
        """
        Main function for installing loops and skips
        -1 is a skip, +N is a loop
        """
        c = self.LoopCommand(self, strandType, index, loopsize)
        self.undoStack().push(c)
    # end def
    
    def emitModificationSignal(self):
        self.basesModified.emit()
        #self.part().virtualHelixAtCoordsChanged.emit(*self.coord())

    ################ Private Base Modification API ###########################
    class LoopCommand(QUndoCommand):
        def __init__(self, virtualHelix, strandType, index, loopsize):
            super(VirtualHelix.LoopCommand, self).__init__()
            self._vh = virtualHelix
            self._strandType = strandType
            self._index = index
            self._loopsize = loopsize
            self._oldLoopsize = None
            
        def redo(self):
            if self._vh.hasStrandAt(self._strandType, self._index):
                loop = self._vh._loop(self._strandType)
                self._oldLoopsize = 0
                if self._loopsize != 0: # if we are not removing the loop
                    if self._index in loop:
                        self._oldLoopsize = loop[self._index]
                    # end if
                    loop[self._index] = self._loopsize # set the model
                else: # trying to set the loop to zero so get rid of it! 
                    if self._index in loop:
                        self._oldLoopsize = loop[self._index]
                        del loop[self._index]
                    # end if
                # end else
                self._vh.emitModificationSignal()
            
        def undo(self):
            if self._vh.hasStrandAt(self._strandType, self._index):
                loop = self._vh._loop(self._strandType)
                assert(self._oldLoopsize != None)  # Must redo/apply before undo
                if self._oldLoopsize != 0: # if we are not removing the loop
                    loop[self._index] = self._oldLoopsize
                else: 
                    if self._index in loop:
                        del loop[self._index]
                    # end if
                # end else
                self._vh.emitModificationSignal()

    def applyColorAt(self, colorName, strandType, index):
        """docstring for applyColorAt"""
        strand = self._strand(strandType)
        startBase = strand[index]
        # traverse to 5' end
        base = startBase
        while not base.is5primeEnd():
            base.setColor(colorName)
            base = base.get5pBase()  # advance to next
            if base == startBase:  # check for circular path
                return
        base.setColor(colorName)  # last 5' base
        # traverse to 3' end
        if not startBase.is3primeEnd():
            base = startBase.get3pBase()  # already processed startBase
            while not base.is3primeEnd():
                base.setColor(colorName)
                base = base.get3pBase()  # advance to next
            base.setColor(colorName)  # last 3' base
        self.emitModificationSignal()

    class ConnectStrandCommand(QUndoCommand):
        def __init__(self, virtualHelix, strandType, startIndex, endIndex):
            super(VirtualHelix.ConnectStrandCommand, self).__init__()
            self._vh = virtualHelix
            self._strandType = strandType
            self._startIndex = startIndex
            self._endIndex = endIndex
            self._oldLinkage = None

        def redo(self):
            # Sets {s.n, (s+1).np, ..., (e-2).np, (e-1).np, e.p}
            # st s, s+1, ..., e-1, e are connected
            strand = self._vh._strand(self._strandType)
            ol = self._oldLinkage = []
            if self._vh.directionOfStrandIs5to3(self._strandType):
                for i in range(self._startIndex, self._endIndex):
                    ol.append(strand[i]._set3Prime(strand[i + 1]))
            # end if
            else:
                for i in range(self._startIndex, self._endIndex):
                    ol.append(strand[i]._set5Prime(strand[i + 1]))
            # end else
            self._vh.emitModificationSignal()

        def undo(self):
            strand = self._vh._strand(self._strandType)
            ol = self._oldLinkage
            assert(ol != None)  # Must redo/apply before undo
            if self._vh.directionOfStrandIs5to3(self._strandType):
                for i in range(self._endIndex - 1, self._startIndex - 1, -1):
                    strand[i]._unset3Prime(strand[i + 1],\
                                           *ol[i - self._startIndex])
                # end for
            # end if
            else:
                for i in range(self._endIndex - 1, self._startIndex - 1, -1):
                    strand[i]._unset5Prime(strand[i + 1],\
                                           *ol[i - self._startIndex])
                # end for
            # end else
            self._vh.emitModificationSignal()

    class ClearStrandCommand(QUndoCommand):
        def __init__(self, virtualHelix, strandType, startIndex, endIndex):
            super(VirtualHelix.ClearStrandCommand, self).__init__()
            self._vh = virtualHelix
            self._strandType = strandType
            self._startIndex = startIndex
            self._endIndex = endIndex
            self._oldLinkage = None

        def redo(self):
            # Clears {s.n, (s+1).np, ..., (e-1).np, e.p}
            # Be warned, start index and end index become endpoints
            # if this is called in the middle of a connected strand
            strand = self._vh._strand(self._strandType)
            ol = self._oldLinkage = []

            if self._vh.directionOfStrandIs5to3(self._strandType):
                for i in range(self._startIndex - 1, self._endIndex):
                    ol.append(strand[i]._set3Prime(None))
                # end for
            # end if
            else:
                for i in range(self._startIndex - 1, self._endIndex):
                    ol.append(strand[i]._set5Prime(None))
                # end for
            # end else
            self._vh.emitModificationSignal()
        # end def

        def undo(self):
            strand = self._vh._strand(self._strandType)
            ol = self._oldLinkage
            assert(ol != None)  # Must redo/apply before undo
            if self._vh.directionOfStrandIs5to3(self._strandType):
                for i in range(self._endIndex - 1, self._startIndex - 2, -1):
                    strand[i]._unset3Prime(None, *ol[i - self._startIndex + 1])
                # end for
            # end if
            else:
                for i in range(self._endIndex - 1, self._startIndex - 2, -1):
                    strand[i]._unset5Prime(None, *ol[i - self._startIndex + 1])
                # end for
            # end else
            self._vh.emitModificationSignal()
        # end def

    class Connect3To5Command(QUndoCommand):
        def __init__(self, strandType, fromHelix, fromIndex, toHelix, toIndex):
            super(VirtualHelix.Connect3To5Command, self).__init__()
            self._strandType = strandType
            self._fromHelix = fromHelix
            self._fromIndex = fromIndex
            self._toHelix = toHelix
            self._toIndex = toIndex

        def redo(self):
            fromB = self._fromHelix._strand(self._strandType)[self._fromIndex]
            toB = self._toHelix._strand(self._strandType)[self._toIndex]
            self._undoDat = fromB._set3Prime(toB)
            self._fromHelix.emitModificationSignal()
            self._toHelix.emitModificationSignal()

        def undo(self):
            fromB = self._fromHelix._strand(self._strandType)[self._fromIndex]
            toB = self._toHelix._strand(self._strandType)[self._toIndex]
            assert(self._undoDat)  # Must redo/apply before undo
            fromB._unset3Prime(toB, *self._undoDat)
            self._fromHelix.emitModificationSignal()
            self._toHelix.emitModificationSignal()

    class Break3To5Command(QUndoCommand):
        def __init__(self, strandType, vhelix, index):
            super(VirtualHelix.Break3To5Command, self).__init__()
            self._strandType = strandType
            self._base = vhelix._strand(strandType)[index]

        def redo(self):
            base = self._base
            self._old3pBase = base._3pBase
            base._set3Prime(None)
            base._vhelix.emitModificationSignal()
            otherVH = self._old3pBase._vhelix
            if otherVH != base._vhelix:
                otherVH.emitModificationSignal()

        def undo(self):
            assert(self._old3pBase)
            base = self._base
            base._set3Prime(self._old3pBase)
            base._vhelix.emitModificationSignal()
            otherVH = self._old3pBase._vhelix
            if otherVH != base._vhelix:
                otherVH.emitModificationSignal()

    class SetNumBasesCommand(QUndoCommand):
        def __init__(self, vhelix, newNumBases):
            super(VirtualHelix.SetNumBasesCommand, self).__init__()
            self.vhelix = vhelix
            self.newNumBases = newNumBases

        def redo(self, actuallyUndo=False):
            vh = self.vhelix
            if actuallyUndo:
                newNumBases, oldNB = self.oldNumBases, self.newNumBases
            else:
                self.oldNumBases = vh.numBases()
                newNumBases, oldNB = self.newNumBases, self.oldNumBases
            if vh.part():
                # If we are attached to a dnapart we must obey its dimensions
                assert(vh.part().numBases() == newNumBases)
            if newNumBases > oldNB:
                for n in range(oldNB, newNumBases):
                    vh._stapleBases.append(Base(vh, StrandType.Staple, n))
                    vh._scaffoldBases.append(Base(vh, StrandType.Scaffold, n))
            else:
                del vh._stapleBases[oldNB:-1]
                del vh._scaffoldBases[oldNB:-1]
            vh.dimensionsModified.emit()

        def undo(self):
            self.redo(actuallyUndo=True)

    ################################ Crossovers ##############################
    def potentialCrossoverList(self, facingRight, strandType):
        """Returns a list of [neighborVirtualHelix, index] potential
        crossovers"""
        ret = []  # LUT = Look Up Table
        part = self._part
        luts = (part.scafL, part.scafR, part.stapL, part.stapR)

        # these are the list of crossover points simplified
        lut = luts[int(facingRight) +\
                   2 * int(strandType == StrandType.Staple)]

        neighbors = self.neighbors()
        for p in range(len(neighbors)):
            neighbor = neighbors[p]
            if not neighbor:
                continue
            for i, j in product(range(0, self.numBases(), part.step), lut[p]):
                index = i + j
                ret.append([neighbor, index])
        return ret

    def crossoverAt(self, strandType, fromIndex, neighbor, toIndex):
        return

    def scaffoldBase(self, index):
        """docstring for scaffoldBase"""
        return self._scaffoldBases[index]

    def stapleBase(self, index):
        """docstring for stapleBase"""
        return self._stapleBases[index]
    
    def possibleNewCrossoverAt(self, strandType, fromIndex, neighbor, toIndex):
        """
        Return true if scaffold could crossover to neighbor at index.
        Useful for seeing if potential crossovers from potentialCrossoverList
        should be presented as points at which new a new crossover can be
        formed.
        """
        fromB = self._strand(strandType)[fromIndex]
        toB = neighbor._strand(strandType)[toIndex]
        if fromB.isCrossover() or toB.isCrossover():
            return False
        else:
            if strandType == StrandType.Scaffold:
                return  not self.scaffoldBase(fromIndex).isEmpty() and \
                    not neighbor.scaffoldBase(toIndex).isEmpty()
            else:
                return  not self.stapleBase(fromIndex).isEmpty() and \
                    not neighbor.stapleBase(toIndex).isEmpty()

    def getLeftScafPreCrossoverIndexList(self):
        return self.potentialCrossoverList(False, StrandType.Scaffold)

    def getRightScafPreCrossoverIndexList(self):
        return self.potentialCrossoverList(True, StrandType.Scaffold)

    def getLeftStapPreCrossoverIndexList(self):
        return self.potentialCrossoverList(False, StrandType.Staple)

    def getRightStapPreCrossoverIndexList(self):
        return self.potentialCrossoverList(True, StrandType.Staple)

    def neighbors(self):
        """The part (which controls helix layout) decides who
        the virtualhelix's neighbors are. A list is returned,
        possibly containing None in some slots, so that
        neighbors()[i] corresponds to the neighbor in direction
        i (where the map between directions and indices is defined
        by the part)"""
        return self._part.getVirtualHelixNeighbors(self)

    #################### Archiving / Unarchiving #############################
    # A helper method; not part of the archive protocol
    def encodeStrand(self, strandType):
        strand = self._strand(strandType)
        numBases = self.numBases()
        strdir = "5->3" if self.directionOfStrandIs5to3(strandType) else "3->5"
        return "(%s) " % (strdir) + " ".join(str(b) for b in strand)

    def fillSimpleRep(self, sr):
        """Fills sr with a representation of self in terms
        of simple types (strings, numbers, objects, and arrays/dicts
        of objects that also implement fillSimpleRep)"""
        sr['.class'] = "VirtualHelix"
        sr['tentativeHelixID'] = self.number()  # Not used... for readability
        sr['staple'] = self.encodeStrand(StrandType.Staple)
        sr['scafld'] = self.encodeStrand(StrandType.Scaffold)

    # First objects that are being unarchived are sent
    # ClassNameFrom.classAttribute(incompleteArchivedDict)
    # which has only strings and numbers in its dict and then,
    # sometime later (with ascending finishInitPriority) they get
    # finishInitWithArchivedDict, this time with all entries
    finishInitPriority = 1.0  # AFTER DNAParts finish init

    def finishInitWithArchivedDict(self, completeArchivedDict):
        scaf = re.split('\s+', completeArchivedDict['scafld'])[1:]
        stap = re.split('\s+', completeArchivedDict['staple'])[1:]
        # Did the init method set the number of bases correctly?
        assert(len(scaf) == len(stap) and len(stap) == self.numBases())
        for i in range(len(scaf)):
            self._scaffoldBases[i].setConnectsFromString(scaf[i])
            self._stapleBases[i].setConnectsFromString(stap[i])
