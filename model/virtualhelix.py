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
from PyQt4.QtCore import pyqtSignal, QObject, QTimer
from PyQt4.QtGui import QUndoCommand, QUndoStack, QColor
from .base import Base
from util import *
from cadnano import app
from random import Random
import re

class VirtualHelix(QObject):
    """Stores staple and scaffold routing information."""
    prohibitSingleBaseCrossovers = True
    
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
        # As is the floatingXoverBase if there is one
        self.floatingXoverBase = None
        
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
        
        # During a single UndoCommand, many basesModified signals can be generated.
        # basesModifiedVHs stores a set of VH that will setHasBeenModified
        # upon a call to emitBasesModifiedIfNeeded.
        self.basesModifiedVHs = set()
        
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

    def _setPart(self, newPart, coords, num):
        """Should only be called by dnapart. Use dnapart's
        addVirtualHelixAt to add a virtualhelix to a dnapart."""
        (self._row, self._col) = coords
        if self._part and self._part.getVirtualHelix(coords):
            self._part.addVirtualHelixAt(coords, None)
        self._number = num
        self._part = newPart
        self.setNumBases(newPart.numBases(), notUndoable=True)
        # Command line convenience for -i mode
        if app().v != None:
            app().v[self.number()] = self
    
    def palette(self):
        return self.part().palette()

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
        else:
            self._number = newNumber
    
    # Why two setNumber commands? Because we're faced with
    # a bit of a connundrum. We want
    # 1) part() to control numbering when there is a part().
    #    Not all numbers are valid for all row, col coords (parity),
    #    numbers must be unique in a part, etc, etc. This code
    #    depends on the specifics of the dnapart, and so it
    #    ought to reside in the part.
    # 2) a VirtualHelix without a part to be able to keep track
    #    of a number. 
    # 3) asking a part for its number to be fast. We do it a
    #    lot, so doing a reverse lookup is unseemly.
    # How do we accomplish these goals?
    # 1) We declare that dnapart has the final say on numbers.
    #    it's the master copy. If a VH's self._number disagrees
    #    with the dnapart, the VH is wrong (there is always EXACTLY
    #    one "gold" copy of any data). Parts assign new numbers
    #    to VHs when the VHs are added to them, and they recycle
    #    numbers for deleted VHs.
    # 2) We add a self._number variable to the VH to keep track of
    #    a number when a VH has no part, with the proviso that this
    #    ivar is meaningless when there is a self.part().
    # 3) In times when we have a part, we save self._number from
    #    uselessness by making it a cache for reverse lookups of
    #    the number for a specific VH.
    # So, why two setNumber commands? What is the main question 
    # facing any user of an API? "How do I do x." This is answered
    # by searching for a relevant method name. Once such a method
    # name is found, the next question is "will calling this method
    # suffice?" Wary of caches (implicit or explicit) that need updating,
    # buffers that need flushing, and invariants that must be maintained,
    # this question often has a very complicated answer. A very simple
    # way to make an API user friendly is to ensure that the answer
    # is "Yes" for *ALL* public methods.
    #   No underscore => A caller is only responsible for is calling the method.
    #   underscore    => The caller has to do other voodoo to get the
    #                    suggested result (invalidate caches, flush buffers,
    #                    maintain invariants, pet watchdogs, etc)
    # So, in particular:
    #   setNumber will ask the part to validate the new number,
    #     maintain the numbering system responsible for quickly
    #     assigning numbers to now helices, emit notifications,
    #     and assure that the newNumber isn't already in use by
    #     another VH. If the receiver has no part(), self._number
    #     is a gold copy of the numbering data and can be simply
    #     updated. The user doesn't need to worry about any of this.
    #     In a command line script with no part(), the VH will
    #     use its new number without question, and inside the GUI
    #     changes will automagically appear in the interface.
    #   _setNumber JUST updates the cached value of self._number if
    #     self has a part. It could be skipped, but then DNAPart
    #     would have to touch the ivar self._number directly, which
    #     is mildly bad karma.
    def _setNumber(self, newNumber):
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

    ############################## Access to Bases ###########################
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

    def getSegmentsAndEndpoints(self, strandType):
        """Returns a list of segments, endpoints of self in the format
        ([(startIdx, endIdx), ...],
         [3pEndIdx1, 3pEndIdx2, ...], 
         [5pEndIdx1, ...])
        where startIdx and endIdx can be 1.5, 2.5 etc (multiply by base
        width to see where to draw the lines)"""
        segments, ends3, ends5 = [], [], []
        strand = self._strand(strandType)
        i, s = 0, None
        curColor = None
        # s is the start index of the segment
        # segColor is the color of the current segment
        for i in range(len(strand)):
            b = strand[i]
            
            #Segments
            if b._connectsToNatL():
                if curColor != b.getColor():
                    segments.append((s,i))
                    s = i
                if s==None:
                    s = i
                    curColor = b.getColor()
                else:
                    pass
            else: # not connected to base on left
                if s==None:
                    pass
                else:
                    segments.append((s,i))
                    s = None
            if b._connectsToNatR():
                if s==None:
                    s = i+.5
                    curColor = b.getColor()
                else:
                    pass
            else: # not connected to base on right
                if s==None:
                    pass
                else:
                    segments.append((s,i+.5))
                    s = None
            
            #Endpoints
            if b.is5primeEnd():
                ends5.append(i)
            if b.is3primeEnd():
                ends3.append(i)

        return (segments, ends3, ends5)

    def get3PrimeXovers(self, strandType):
        """
        Returns a tuple of tuples of the form 
        ((fromVH, fromIdx), (toVH, toIdx))
        or, in the case of a floating crossover,
        ((fromVH, fromIdx), toQPoint)
        """
        ret = []
        strand = self._strand(strandType)
        i, s = 0, None
        for base in strand:
            if base.is3primeXover():
                floatDest = base.floatingXoverDestination()
                if floatDest:
                    ret.append(((self, base._n), floatDest))
                else:
                    ret.append(((self, base._n),\
                        (base._3pBase.vhelix(), base._3pBase._n)))
        return ret

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
        # hue = 47 * idx + 31 * self.number()
        # return QColor.fromHsl(hue % 256, 255, 128)
        # print "colorOfBase", idx, c.name(), self._stapleBases[idx].getColor()
        return self._strand(strandType)[idx].getColor()
    
    def _basesConnectedTo(self, strandType, idx):
        strand = self._strand(strandType)
        bases = set()
        treeTips = [strand[idx]]
        while len(treeTips):
            b = treeTips.pop()
            if b in bases:
                continue
            else:
                if b==None:
                    continue
                bases.add(b)
                treeTips.append(b._3pBase)
                treeTips.append(b._5pBase)
        return bases
            
    def sandboxed(self):
        return self._sandboxed

    def setSandboxed(self, sb, mustNotShareStack=False):
        """Set True to give the receiver a temporary undo stack
        that will be deleted upon set False. Since tools can be
        made live by repeatedly pushing and popping undo commands,
        it occasionally happens that a bug pops many things off the
        undo stack. The temporary undo stack prevents excessive popping
        from reverting the document to a blank state."""
        if sb and self._privateUndoStack:
            if mustNotShareStack:
                assert(False)  # Caller needed a private undo stack; we couldn't provide one
            else:
                print "WARNING: attempting to sandbox a vh that already has an undo stack!"
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
    
    ################# New-Style Accessors ###################
    # A neighbor base is one that is connected to the base represented
    # by self through a phosphate linkage. These accessors let you get them
    def neighbor5p(self, strandType, idx):
        b = self._strand(strandType)[idx]._neighbor5p()
        return (b._vhelix, b._strandtype, b._n)
    def neighbor3p(self, strandType, idx):
        b = self._strand(strandType)[idx]._neighbor3p()
        return (b._vhelix, b._strandtype, b._n)
    # Although different strands are oriented different ways inside the gui,
    # R and L always represent the bases to the right and left of the receiver
    # in the GUI
    def neighborR(self, strandType, idx):
        b = self._strand(strandType)[idx]._neighborR()
        return (b._vhelix, b._strandtype, b._n)
    def neighborL(self, strandType, idx):
        b = self._strand(strandType)[idx]._neighborL()
        return (b._vhelix, b._strandtype, b._n)
    
    # Test for the presence of neghbors
    def hasNeighbor5p(self, strandType, idx):
        return self._strand(strandType)[idx]._hasNeighbor5p()
    def hasNeighbor3p(self, strandType, idx):
        return self._strand(strandType)[idx]._hasNeighbor3p()
    def hasNeighborR(self, strandType, idx):
        return self._strand(strandType)[idx]._hasNeighborR()
    def hasNeighborL(self, strandType, idx):
        return self._strand(strandType)[idx]._hasNeighborL()
    
    # A segment is a connection between a base and its neighbor
    # base on the same strand
    def connectsToNat5p(self, strandType, idx):
        return self._strand(strandType)[idx]._connectsToNat5p()
    def connectsToNat3p(self, strandType, idx):
        return self._strand(strandType)[idx]._connectsToNat3p()
    def connectsToNatR(self, strandType, idx):
        return self._strand(strandType)[idx]._connectsToNatR()
    def connectsToNatL(self, strandType, idx):
        return self._strand(strandType)[idx]._connectsToNatL()
    
    # A crossover is a connection between a base and a base
    # that isn't its neighbor on the same strand
    def hasCrossover5p(self, strandType, idx):
        return self._strand(strandType)[idx]._hasCrossover5p()
    def hasCrossover3p(self, strandType, idx):
        return self._strand(strandType)[idx]._hasCrossover3p()
    def hasCrossoverR(self, strandType, idx):
        return self._strand(strandType)[idx]._hasCrossoverR()
    def hasCrossoverL(self, strandType, idx):
        return self._strand(strandType)[idx]._hasCrossoverL()
    

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
    def setHasBeenModified(self):
        if self.part():
            self.part().basesModifiedVHs.add(self)
        else:
            self.basesModified.emit()
    
    def emitBasesModifiedIfNeeded(self):
        if self.part():
            for vh in self.part().basesModifiedVHs:
                vh.basesModified.emit()
            self.part().basesModifiedVHs.clear()
        else:
            self.basesModified.emit()
        #self.part().virtualHelixAtCoordsChanged.emit(*self.coord())
        
    def connectStrand(self, strandType, startIndex, endIndex, undoStack=None, police=True, color=None):
        """
        Connects sequential bases on a single strand, starting with
        startIndex and ending with etdIndex (inclusive)
        Sets {s.n, (s+1).np, ..., (e-2).np, (e-1).np, e.p}
        """
        strand = self._strand(strandType)
        startIndex, endIndex = int(startIndex), int(endIndex)
        startIndex = clamp(startIndex, 0, len(strand) - 1)
        endIndex = clamp(endIndex, 0, len(strand) - 1)
        if undoStack==None:
            undoStack = self.undoStack()
        undoStack.beginMacro("Connect Strand")
        c = self.ConnectStrandCommand(self, strandType, startIndex, endIndex, color=color)
        undoStack.push(c)
        if police:
            self.thoughtPolice(undoStack)  # Check for inconsistencies, fix one-base Xovers, etc
        undoStack.endMacro()

    def clearStrand(self, strandType, startIndex, endIndex, undoStack=None, colorL=None, colorR=None):
        endIndex, startIndex = int(endIndex), int(startIndex)
        strand = strandType == StrandType.Scaffold and \
            self._scaffoldBases or self._stapleBases
        startIndex = clamp(startIndex, 1, len(strand)-1)
        endIndex = clamp(endIndex, 1, len(strand)-1)
        if undoStack==None:
            undoStack = self.undoStack()
        undoStack.beginMacro("Clear Strand")
        c = self.ClearStrandCommand(self, strandType, startIndex, endIndex, colorL=colorL, colorR=colorR)
        undoStack.push(c)
        self.thoughtPolice(undoStack)  # Check for inconsistencies, fix one-base Xovers, etc
        undoStack.endMacro()

    def installXoverFrom3To5(self, strandType, fromIndex, toVhelix, toIndex, undoStack=None, endToTakeColorFrom=3):
        """
        The from base must provide the 3' pointer, and to must provide 5'.
        """
        if undoStack==None:
            undoStack = self.undoStack()
        undoStack.beginMacro("Install 3-5 Xover")
        c = self.Connect3To5Command(strandType, self, fromIndex, toVhelix,\
                                    toIndex, endToTakeColorFrom)
        undoStack.push(c)
        self.thoughtPolice(undoStack)  # Check for inconsistencies, fix one-base Xovers, etc
        toVhelix.thoughtPolice(undoStack=undoStack)
        undoStack.endMacro()
    
    def removeConnectedStrandAt(self, strandType, idx, undoStack=None):
        if not undoStack:
            undoStack = self.undoStack()
        undoStack.beginMacro("Remove Strand")
        bases = self._basesConnectedTo(strandType, idx)
        c = self.RemoveBasesCommand(bases)
        undoStack.push(c)
        affectedVH = set()
        for b in bases:
            affectedVH.add(b._vhelix)
        for vh in affectedVH:
            vh.thoughtPolice(undoStack)
        undoStack.endMacro()
    
    def removeXoversAt(self, strandType, idx, newColor=None):
        base = self._strand(strandType)[idx]
        
        if base._hasCrossover3p():
            fromBase, toBase = base, base._3pBase
            fromBase._vhelix.removeXoverTo(base._strandtype, base._n\
                    , toBase._vhelix, toBase._n, endToKeepColor=3, newColor=newColor)
        if base._hasCrossover5p():
            fromBase, toBase = base._5pBase, base
            fromBase._vhelix.removeXoverTo(base._strandtype, base._n\
                    , toBase._vhelix, toBase._n, endToKeepColor=5, newColor=newColor)

    def removeXoverTo(self, strandType, fromIndex, toVhelix, toIndex, undoStack=None, endToKeepColor=3, newColor=None):
        strand = self._strand(strandType)
        fromBase = strand[fromIndex]
        toBase = toVhelix._strand(strandType)[toIndex]
        if fromBase._3pBase != toBase or fromBase != toBase._5pBase:
            raise IndexError("Crossover does not exist to be removed.")
        if undoStack==None:
            undoStack = self.undoStack()
        undoStack.beginMacro("Remove Xover")
        c = self.Break3To5Command(strandType, self, fromIndex, endToKeepColor=endToKeepColor, newColor=newColor)
        undoStack.push(c)
        self.thoughtPolice(undoStack)  # Check for inconsistencies, fix one-base Xovers, etc
        toVhelix.thoughtPolice(undoStack=undoStack)
        undoStack.endMacro()
        
    def installLoop(self, strandType, index, loopsize):
        """
        Main function for installing loops and skips
        -1 is a skip, +N is a loop
        """
        c = self.LoopCommand(self, strandType, index, loopsize)
        self.undoStack().push(c)
    # end def

    def applyColorAt(self, color, strandType, index, undoStack=None):
        """Determine the connected strand that passes through
        (self, strandType, index) and apply color to every base
        in that strand. If color is none, pick a (bright) random
        color and apply it to every base in that strand"""
        if undoStack==None:
            undoStack = self.undoStack()
        if color==None:
            color = self.palette()[0]
        undoStack.beginMacro("Apply Color")
        bases = self._basesConnectedTo(strandType, index)
        c = self.ApplyColorCommand(bases, color)
        undoStack.push(c)
        undoStack.endMacro()
        self.emitBasesModifiedIfNeeded()

    def setFloatingXover(self, strandType=None, fromIdx=None, toPoint=None):
        """The floating crossover is a GUI hack that is the
        temporary crossover shown while the user is using the
        force tool (pencil tool right click) that has a 3' end
        wherever the user clicked / is dragging from and ends
        beneath the mouse."""
        if self.floatingXoverBase:
            self.floatingXoverBase._floatingXoverDestination = None
            self.floatingXoverBase = None
        if strandType==None or fromIdx==None or toPoint==None:
            self.setHasBeenModified()
            self.emitBasesModifiedIfNeeded()
            return
        newXoverBase = self._strand(strandType)[fromIdx]
        newXoverBase._floatingXoverDestination = toPoint
        self.floatingXoverBase = newXoverBase
        self.setHasBeenModified()
        self.emitBasesModifiedIfNeeded()

    ################ Private Base Modification API ###########################
    # The Notification Responsibilities of a Command
    #   1) Call vh.setHasBeenModified() on every VirtualHelix that is modified.
    #      Judiciously use this method, since all it really does is add the VH
    #      it is called on to a list of dirty VH in the dnapart.
    #   2) Call vh.emitBasesModifiedIfNeeded() when you are done with a command.
    #      This actually emits the signals (this way, Base can automatically
    #      decide which VH were dirtied yet a command that affects 20 bases doesn't
    #      result in 20 duplicate basesModified signals being emitted)
    
    def thoughtPolice(self, undoStack):
        """Make sure that self obeys certain limitations, force it to if it doesn't"""
        if self.prohibitSingleBaseCrossovers:
            for strandType in (StrandType.Scaffold, StrandType.Staple):
                strand = self._strand(strandType)
                for i in range(len(strand)):
                    b = strand[i]
                    hasNeighborL = b._hasNeighborL()
                    hasNeighborR = b._hasNeighborR() 
                    hasXoverL = b._hasCrossoverL()
                    hasXoverR = b._hasCrossoverR()
                    if hasXoverL and not hasNeighborR:
                        self.connectStrand(strandType, i, i+1, undoStack=undoStack)
                    if hasXoverR and not hasNeighborL:
                        self.connectStrand(strandType, i-1, i, undoStack=undoStack, police=False)
    
    class ApplyColorCommand(QUndoCommand):
        def __init__(self, bases, color):
            super(VirtualHelix.ApplyColorCommand, self).__init__()
            self._bases = list(bases)
            if color==None and len(self._bases):
                b = self._bases[0]
                newHue = 199*b._vhelix.number() +\
                         131*int(b._strandtype) +\
                         151*b._n
                color = QColor()
                color.setHsv(newHue%256, 255, 255)
            self._newColor = color
        def redo(self):
            oc = self._oldColors = []
            nc = self._newColor
            vh = None
            for b in self._bases:
                vh = b._vhelix
                oc.append(b._setColor(nc))
            if vh:
                vh.emitBasesModifiedIfNeeded()
        def undo(self):
            oc = self._oldColors
            vh = None
            for b in reversed(self._bases):
                vh = b._vhelix
                b._setColor(oc.pop())
            if vh:
                vh.emitBasesModifiedIfNeeded()
                
    
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
                self._vh.setHasBeenModified()
                self._vh.emitBasesModifiedIfNeeded()

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
                self._vh.setHasBeenModified()
                self._vh.emitBasesModifiedIfNeeded()
    
    class RemoveBasesCommand(QUndoCommand):
        def __init__(self, bases):
            super(VirtualHelix.RemoveBasesCommand, self).__init__()
            self.bases = list(bases)
        def redo(self):
            ol = self._oldLinkage = []
            vh = None
            for b in self.bases:
                ol.append(b._set3Prime(None))
                ol.append(b._set5Prime(None))
                vh = b._vhelix
            if vh:
                vh.emitBasesModifiedIfNeeded()
        def undo(self):
            ol = self._oldLinkage
            vh = None
            for b in reversed(self.bases):
                b._unset5Prime(None, ol.pop())
                b._unset3Prime(None, ol.pop())
                vh = b._vhelix
            if vh:
                vh.emitBasesModifiedIfNeeded()

    class ConnectStrandCommand(QUndoCommand):
        def __init__(self, virtualHelix, strandType, startIndex, endIndex, color=None):
            super(VirtualHelix.ConnectStrandCommand, self).__init__()
            self._vh = virtualHelix
            self._strandType = strandType
            self._startIndex = startIndex
            self._endIndex = endIndex
            self._oldLinkage = None
            self._colorSubCommand = None
            self._explicitColor = color

        def redo(self):
            # Sets {s.n, (s+1).np, ..., (e-2).np, (e-1).np, e.p}
            # st s, s+1, ..., e-1, e are connected
            strand = self._vh._strand(self._strandType)
            ol = self._oldLinkage = []
            firstIdx = min(self._startIndex, self._endIndex)
            stopIdx = max(self._startIndex, self._endIndex)
            if self._vh.directionOfStrandIs5to3(self._strandType):
                for i in range(firstIdx, stopIdx):
                    ol.append(strand[i]._set3Prime(strand[i + 1]))
            else:
                for i in range(firstIdx, stopIdx):
                    ol.append(strand[i]._set5Prime(strand[i + 1]))
            # Now ensure all connected bases have the same color
            # which gets taken from the startIndex base
            if self._explicitColor == None:
                color = strand[self._startIndex].getColor()
            else:
                color = self._explicitColor
            bases = self._vh._basesConnectedTo(self._strandType, self._startIndex)
            self._colorSubCommand = VirtualHelix.ApplyColorCommand(bases, color)
            self._colorSubCommand.redo()
            self._vh.emitBasesModifiedIfNeeded()

        def undo(self):
            strand = self._vh._strand(self._strandType)
            ol = self._oldLinkage
            firstIdx = min(self._startIndex, self._endIndex)
            stopIdx = max(self._startIndex, self._endIndex)
            assert(ol != None)  # Must redo/apply before undo
            if self._vh.directionOfStrandIs5to3(self._strandType):
                for i in range(stopIdx - 1, firstIdx - 1, -1):
                    strand[i]._unset3Prime(strand[i + 1],\
                                           *ol[i - firstIdx])
            else:
                for i in range(stopIdx - 1, firstIdx - 1, -1):
                    strand[i]._unset5Prime(strand[i + 1],\
                                           *ol[i - firstIdx])
            self._colorSubCommand.undo()
            self._vh.emitBasesModifiedIfNeeded()

    class ClearStrandCommand(QUndoCommand):
        def __init__(self, virtualHelix, strandType, startIndex, endIndex, colorL=None, colorR=None):
            super(VirtualHelix.ClearStrandCommand, self).__init__()
            self._vh = virtualHelix
            self._strandType = strandType
            self._startIndex = min(startIndex, endIndex)
            self._endIndex = max(startIndex, endIndex)
            self._oldLinkage = None
            self._colorL = colorL
            self._colorR = colorR

        def redo(self):
            # Clears {s.n, (s+1).np, ..., (e-1).np, e.p}
            # Be warned, start index and end index become endpoints
            # if this is called in the middle of a connected strand
            strand = self._vh._strand(self._strandType)
            ol = self._oldLinkage = []
            startIdx = min(self._startIndex, self._endIndex)
            endIdx = max(self._startIndex, self._endIndex)
            potentialNewEndpoints = []
            if self._vh.directionOfStrandIs5to3(self._strandType):
                for i in range(startIdx-1, endIdx):
                    leftBase, rightBase = strand[i], strand[i+1]
                    # Clear i.next
                    potentialNewEndpoints.extend((leftBase, leftBase._3pBase))
                    ol.append(leftBase._set3Prime(None))
                    # Clear (i+1)prev
                    potentialNewEndpoints.extend((rightBase._5pBase, rightBase))
                    potentialNewEndpoints.append(rightBase._5pBase)
                    ol.append(rightBase._set5Prime(None))
            else:
                for i in range(startIdx-1, endIdx):
                    leftBase, rightBase = strand[i], strand[i+1]
                    # Clear i.next
                    potentialNewEndpoints.extend((leftBase, leftBase._5pBase))
                    ol.append(leftBase._set5Prime(None))
                    # Clear (i+1).prev
                    potentialNewEndpoints.extend((rightBase._3pBase, rightBase))
                    ol.append(rightBase._set3Prime(None))
            isEndpt = lambda x: x!=None and x.isEnd()
            potentialNewEndpoints = list(filter(isEndpt, potentialNewEndpoints))
            newEndpts = []
            if len(potentialNewEndpoints):
                newEndpts = [potentialNewEndpoints[0]]
                for pe in potentialNewEndpoints[1:]:
                    if pe != newEndpts[-1]:
                        newEndpts.append(pe)
                
            # Could filter out endpoints leading to the same strand if
            # that becomes a performance issue for some reason
            colorSubCommands = []
            for i in range(len(newEndpts)):
                e = newEndpts[i]
                bases = e._vhelix._basesConnectedTo(e._strandtype, e._n)
                # None corresponds to a pseudorandom color
                color = None
                if i==0 and self._colorL!=None:
                    color = self._colorL
                elif i==len(newEndpts)-1 and self._colorR!=None:
                    color = self._colorR
                c = VirtualHelix.ApplyColorCommand(bases, color)
                c.redo()
                colorSubCommands.append(c)
            self.colorSubCommands = colorSubCommands
            self._vh.emitBasesModifiedIfNeeded()

        def undo(self):
            strand = self._vh._strand(self._strandType)
            ol = self._oldLinkage
            assert(ol != None)  # Must redo/apply before undo
            startIdx = min(self._startIndex, self._endIndex)
            endIdx = max(self._startIndex, self._endIndex)
            for c in reversed(self.colorSubCommands):
                c.undo()
            if self._vh.directionOfStrandIs5to3(self._strandType):
                for i in range(endIdx - 1, startIdx - 2, -1):
                    strand[i+1]._unset5Prime(None, *ol.pop())
                    strand[i]._unset3Prime(None, *ol.pop())
            else:
                for i in range(endIdx - 1, startIdx - 2, -1):
                    strand[i+1]._unset3Prime(None, *ol.pop())
                    strand[i]._unset5Prime(None, *ol.pop())
            self._vh.emitBasesModifiedIfNeeded()

    class Connect3To5Command(QUndoCommand):
        def __init__(self, strandType, fromHelix, fromIndex, toHelix, toIndex, endToTakeColorFrom=3):
            super(VirtualHelix.Connect3To5Command, self).__init__()
            self._strandType = strandType
            self._fromHelix = fromHelix
            self._fromIndex = fromIndex
            self._toHelix = toHelix
            self._toIndex = toIndex
            self._colorEnd = endToTakeColorFrom

        def redo(self):
            vh, strandType = self._fromHelix, self._strandType
            fromIdx, toIdx = self._fromIndex, self._toIndex
            fromB = vh._strand(strandType)[fromIdx]
            toB = self._toHelix._strand(strandType)[toIdx]
            old3p = fromB._3pBase
            old5p = toB._5pBase
            self._undoDat = fromB._set3Prime(toB)
            if self._colorEnd == 3:
                color = vh.colorOfBase(strandType, fromIdx)
            elif self._colorEnd == 5:
                color = self._toHelix.colorOfBase(strandType, toIdx)
            else:
                assert(False)
            # Ensure that the newly joined strand is all one color
            bases = vh._basesConnectedTo(strandType, fromIdx)
            c = VirtualHelix.ApplyColorCommand(bases, color)
            c.redo()
            self._colorCommand = c
            
            # If we had to split a strand to make the crossover, give
            # the resulting segment a random color
            self._colorCommand1 = None
            if old3p!=None:
                bases1 = old3p._vhelix._basesConnectedTo(old3p._strandtype, old3p._n)
                color1 = vh.palette()[0]
                c1 = VirtualHelix.ApplyColorCommand(bases1, color1)
                c1.redo()
                self._colorCommand1 = c1
            self._colorCommand2 = None
            if old5p != None:
                bases2 = old5p._vhelix._basesConnectedTo(old5p._strandtype, old5p._n)
                color2 = vh.palette()[1]
                c2 = VirtualHelix.ApplyColorCommand(bases2, color2)
                c2.redo()
                self._colorCommand2 = c2
            vh.emitBasesModifiedIfNeeded()

        def undo(self):
            fromB = self._fromHelix._strand(self._strandType)[self._fromIndex]
            toB = self._toHelix._strand(self._strandType)[self._toIndex]
            assert(self._undoDat)  # Must redo/apply before undo
            fromB._unset3Prime(toB, *self._undoDat)
            self._colorCommand.undo()
            if self._colorCommand1:
                self._colorCommand1.undo()
            if self._colorCommand2:
                self._colorCommand2.undo()
            self._fromHelix.emitBasesModifiedIfNeeded()

    class Break3To5Command(QUndoCommand):
        def __init__(self, strandType, vhelix, index, endToKeepColor=3, newColor=None):
            super(VirtualHelix.Break3To5Command, self).__init__()
            self._strandType = strandType
            self._base = vhelix._strand(strandType)[index]
            self._endToKeepColor = endToKeepColor
            self._colorCommand = None
            if newColor==None:
                newColor = vhelix.palette()[0]
            self._newColor = newColor

        def redo(self):
            threeB = self._base
            self._old3pBase = fiveB = threeB._3pBase
            threeB._set3Prime(None)
            if threeB and self._endToKeepColor==5:
                color = self._newColor
                bases = threeB._vhelix._basesConnectedTo(threeB._strandtype, threeB._n)
                c = VirtualHelix.ApplyColorCommand(bases, color)
                c.redo()
                self._colorCommand = c
            elif fiveB and self._endToKeepColor==3:
                color = self._newColor
                bases = fiveB._vhelix._basesConnectedTo(fiveB._strandtype, fiveB._n)
                c = VirtualHelix.ApplyColorCommand(bases, color)
                c.redo()                
                self._colorCommand = c
            threeB._vhelix.emitBasesModifiedIfNeeded()

        def undo(self):
            assert(self._old3pBase)
            base = self._base
            base._set3Prime(self._old3pBase)
            base._vhelix.emitBasesModifiedIfNeeded()
            if self._colorCommand:
                self._colorCommand.undo()

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
        numBases = self.numBases()
        strdir = "5->3" if self.directionOfStrandIs5to3(strandType) else "3->5"
        strand = self._strand(strandType)
        return "(%s) " % (strdir) + " ".join(str(b) for b in strand)

    def fillSimpleRep(self, sr):
        """Fills sr with a representation of self in terms
        of simple types (strings, numbers, objects, and arrays/dicts
        of objects that also implement fillSimpleRep)"""
        sr['.class'] = "VirtualHelix"
        sr['tentativeHelixID'] = self.number()  # Not used (just for readability)
        stapleStrand = self._strand(StrandType.Staple)
        sr['staple'] = self.encodeStrand(StrandType.Staple)
        sr['stapleColors'] = " ".join(str(b.getColor().name()) for b in stapleStrand)
        scaffoldStrand = self._strand(StrandType.Scaffold)
        sr['scafld'] = self.encodeStrand(StrandType.Scaffold)
        sr['scafldColors'] = " ".join(str(b.getColor().name()) for b in scaffoldStrand)

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
        # Give bases the proper colors
        scafColors = re.split('\s+', completeArchivedDict['scafldColors'])
        for i in range(len(scaf)):
            self._scaffoldBases[i]._setColor(QColor(scafColors[i]))
        stapColors = re.split('\s+', completeArchivedDict['stapleColors'])
        for i in range(len(stap)):
            self._stapleBases[i]._setColor(QColor(stapColors[i]))
        
