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
base.py
Created by Shawn Douglas on 2011-02-08.
"""
from .enum import StrandType
from random import Random
from PyQt4.QtGui import QColor
import ui.styles as styles
prng = Random()

class Base(object):
    """
    A POD class that lives in the private API of virtualhelix.
    (Why not put it inside VirtualHelix? Because it's already quite crowded)
    Provides information about which bases are connected to which other bases.
    """
    def __init__(self, vhelix, strandtype, index):
        super(Base, self).__init__()
        self._5pBase = None
        self._3pBase = None
        self._color = None
        self._vhelix = vhelix
        self._strandtype = strandtype
        self._n = index
        self._floatingXoverDestination = False
        self._strandLength = 0
        self._sequence = " "

    def __str__(self):
        fiveTo3 = self._vhelix.directionOfStrandIs5to3(self._strandtype)
        if fiveTo3:
            # If we move to self._3pBase and stay on the same 5 to 3 strand
            # we expect self._3pBase._n = self._n+1
            nOffsetOf3 = 1
        else:
            nOffsetOf3 = -1
        # What can a (3' or 5' end) look like?
        # _     if _{3,5}pBase == None
        # <     this base connects to the preceeding (leftward in the
        # graphical view, can be either 3' or 5' depending on parity) base
        # 0:12  this base connects to vhelx 0, base 12
        # What does a base look like?
        # (3' or 5' end)(3' or 5' end), of course
        # Examples:
        # <,>   a base in the middle of a segment (connected part of a strand)
        # <,_   an endpoint of a segment (triangular or square handle)
        # 0:1,>  a crossover to vhelix 0, base 1 connected to rightward segment
        threeB, fiveB = '_', '_'
        if self._3pBase:
            if self._3pBase._vhelix == self._vhelix and\
               self._3pBase._n == self._n + nOffsetOf3:
                    threeB = '>' if fiveTo3 else '<'
            else:
                    threeB = "%i:%i" % (self._3pBase.vhelixNum(),\
                                        self._3pBase._n)
        if self._5pBase:
            if self._5pBase._vhelix == self._vhelix and\
               self._5pBase._n == self._n - nOffsetOf3:
                    fiveB = '<' if fiveTo3 else '>'
            else:
                    fiveB = "%i:%i" % (self._5pBase.vhelixNum(),\
                                       self._5pBase._n)
        if fiveTo3:
            return fiveB + ',' + threeB
        else:
            return threeB + ',' + fiveB

    def setConnectsFromString(self, string):
        # Resets self._{5,3}pBase according to str, which
        # is a string in the format of those returned by __str__
        fiveTo3 = self._vhelix.directionOfStrandIs5to3(self._strandtype)
        if self._strandtype == StrandType.Staple:
            oppositeST = StrandType.Scaffold
        else:
            oppositeST = StrandType.Staple
        direction3p = 1 if fiveTo3 else -1
        strand = self._vhelix._strand(self._strandtype)
        l, r = string.split(',')
        fiveP, threeP = (l, r) if fiveTo3 else (r, l)
        if threeP == '_':
            self._3pBase = None
        elif threeP == ('>' if fiveTo3 else '<'):
            self._3pBase = strand[self._n + direction3p]
        elif threeP == ('<' if fiveTo3 else '>'):
            err = "Opposite directions on 3p of base '%s' in %s strand?!" %\
                                       (string, "5->3" if fiveTo3 else "3->5")
            raise ValueError(err)
        else:
            helixNum, baseNum = threeP.split(':')
            remoteVH = self._vhelix.part().getVirtualHelix(int(helixNum))
            self._3pBase = remoteVH._strand(oppositeST)[int(baseNum)]
        if fiveP == '_':
            self._5pBase = None
        elif fiveP == ('<' if fiveTo3 else '>'):
            self._5pBase = strand[self._n - direction3p]
        elif fiveP == ('>' if fiveTo3 else '<'):
            err = "Opposite directions on 5p of base '%s' in %s strand?!" %\
                                       (string, "5->3" if fiveTo3 else "3->5")
            raise ValueError(err)
        else:
            helixNum, baseNum = fiveP.split(':')
            remoteVH = self._vhelix.part().getVirtualHelix(int(helixNum))
            self._5pBase = remoteVH._strand(oppositeST)[int(baseNum)]
    
    def sequence(self):
        nonempty = self._hasNeighbor3p() or self._hasNeighbor5p()
        if not nonempty:
            return " "
        else:
            return "A"

    def __repr__(self):
        if self._3pBase:
            b3 = str(self._3pBase._vhelix.number()) + \
                    '.' + str(self._3pBase._n)
        else:
            b3 = ' '
        if self._5pBase:
            b5 = str(self._5pBase._vhelix.number()) + \
                '.' + str(self._5pBase._n)
        else:
            b5 = ' '
        if self._vhelix.directionOfStrandIs5to3(self._strandtype):
            return str((b5, self._n, b3))
        else:
            return str((b3, self._n, b5))

    def _set5Prime(self, toBase):
        """Only VirtualHelix should call this method. Returns l
        such that self._unset5Prime(toBase, *l) undoes this command."""
        fromOld5, toOld3 = self._5pBase, None
        if fromOld5:
            fromOld5._3pBase = None
        if toBase:
            toOld3 = toBase._3pBase
            toBase._3pBase = self
        if toOld3:
            toOld3._5pBase = None
        self._5pBase = toBase
        if toOld3:
            toOld3._vhelix.setHasBeenModified()
        if fromOld5:
            fromOld5._vhelix.setHasBeenModified()
        self._vhelix.setHasBeenModified()
        if toBase:
            toBase._vhelix.setHasBeenModified()
        part = self._vhelix.part()
        if part:
            part.basesModified.add(self)
            part.basesModified.add(toOld3)
            part.basesModified.add(fromOld5)
        return (fromOld5, toOld3)

    def _unset5Prime(self, toBase, fromOld5, toOld3):
        """Only VirtualHelix should call this method."""
        self._set5Prime(fromOld5)
        if toOld3 != None:
            toBase._set3Prime(toOld3)
        if toOld3:
            toOld3._vhelix.setHasBeenModified()
        if fromOld5:
            fromOld5._vhelix.setHasBeenModified()
        if toBase:
            toBase._vhelix.setHasBeenModified()
        part = self._vhelix.part()
        if part:
            part.basesModified.add(self)
            part.basesModified.add(toOld3)
            part.basesModified.add(fromOld5)
        self._vhelix.setHasBeenModified()

    def _set3Prime(self, toBase):
        """Only VirtualHelix should call this method. Returns l
        such that self._unset5Prime(toBase, *l) undoes this command."""
        fromOld3, toOld5 = self._3pBase, None
        if fromOld3:
            fromOld3._5pBase = None
        if toBase:
            toOld5 = toBase._5pBase
            toBase._5pBase = self
        if toOld5:
            toOld5._3pBase = None
        self._3pBase = toBase
        if toOld5:
            toOld5._vhelix.setHasBeenModified()
        if fromOld3:
            fromOld3._vhelix.setHasBeenModified()
        if toBase:
            toBase._vhelix.setHasBeenModified()
        part = self._vhelix.part()
        if part:
            part.basesModified.add(self)
            part.basesModified.add(toOld5)
            part.basesModified.add(fromOld3)
        self._vhelix.setHasBeenModified()
        return (fromOld3, toOld5)

    def _unset3Prime(self, toBase, fromOld3, toOld5):
        """Only VirtualHelix should call this method."""
        self._set3Prime(fromOld3)
        if toOld5 != None:
            toBase._set5Prime(toOld5)
        if toOld5:
            toOld5._vhelix.setHasBeenModified()
        if fromOld3:
            fromOld3._vhelix.setHasBeenModified()
        if toBase:
            toBase._vhelix.setHasBeenModified()
        part = self._vhelix.part()
        if part:
            part.basesModified.add(self)
            part.basesModified.add(toOld5)
            part.basesModified.add(fromOld3)
        self._vhelix.setHasBeenModified()

    def vhelix(self):
        return self._vhelix

    def vhelixNum(self):
        return self._vhelix.number()

    def get5pBase(self):
        return self._5pBase
    
    def has5pBase(self):
        return self._5pBase!=None
    
    def has3pXover(self):
        return self.has3p

    def get3pBase(self):
        return self._3pBase
    
    def has3pBase(self):
        return self._3pBase!=None

    def _setColor(self, newColor):
        if newColor==None:
            newHue = prng.randint(0, 255)
            newColor = QColor()
            newColor.setHsv(newHue, 255, 255)
        oldColor = self.getColor()
        self._color = newColor
        self._vhelix.setHasBeenModified()
        return oldColor  # For undo

    def getColor(self):
        if self._strandtype == StrandType.Scaffold:
            # return QColor(44, 51, 141)
            return styles.bluestroke
        if self._color == None:
            self._color = QColor()
        return self._color

    def isEmpty(self):
        return self._5pBase == None and \
               self._3pBase == None

    def is5primeEnd(self):
        """Return True if no 5pBase, but 3pBase exists."""
        return self._hasNeighbor3p() and not self._hasNeighbor5p()

    def is3primeEnd(self):
        """Return True if no 3pBase, but 5pBase exists."""
        return self._hasNeighbor5p() and not self._hasNeighbor3p()
    
    def _neighbor5p(self):
        n = self._5pBase
        if n and n.floatingXoverDestination():
            return None
        return n
    def _neighbor3p(self):
        if self.floatingXoverDestination():
            return None
        return self._3pBase
    def _neighborR(self):
        if self._vhelix.directionOfStrandIs5to3(self._strandtype):
            return self._neighbor3p()
        else:
            return self._neighbor5p()
    def _neighborL(self):
        if self._vhelix.directionOfStrandIs5to3(self._strandtype):
            return self._neighbor5p()
        else:
            return self._neighbor3p()

    # A neighbor base is one that is connected to the base represented
    # by self through a phosphate linkage
    # When a crossover is being forcibly created (right click pencil tool
    # or left click force tool) the base being dragged from is considered
    # to have a "floating" destination that causes _hasNeighbor3p (and one
    # of _hasNeighbor{L,R}) to return True but will still show up as None
    # if _neighbor3p is called.
    def _hasNeighbor5p(self):
        return self._neighbor5p() != None
    def _hasNeighbor3p(self):
        return self._neighbor3p() != None
    def _hasNeighborR(self):
        if self._vhelix.directionOfStrandIs5to3(self._strandtype):
            return self._neighbor3p()!=None or self.floatingXoverDestination()
        else:
            return self._neighbor5p() != None
    def _hasNeighborL(self):
        if self._vhelix.directionOfStrandIs5to3(self._strandtype):
            return self._neighbor5p()!=None or self.floatingXoverDestination()
        else:
            return self._neighbor3p() != None
    
    # A segment is a connection between a base and its neighbor
    # base on the same strand
    def _connectsToNat5p(self):
        strnd = self._vhelix._strand(self._strandtype)
        if self._vhelix.directionOfStrandIs5to3(self._strandtype):
            guiLeftNeighbor = strnd[self._n-1] if self._n>0 else None
            return self._neighbor5p() == guiLeftNeighbor
        else:
            guiRightNeighbor = strnd[self._n+1] if self._n<len(strnd)-1 else None
            return self._neighbor5p() == guiRightNeighbor
    def _connectsToNat3p(self):
        strnd = self._vhelix._strand(self._strandtype)
        if self._vhelix.directionOfStrandIs5to3(self._strandtype):
            guiRightNeighbor = strnd[self._n+1] if self._n<len(strnd)-1 else None
            return self._neighbor3p() == guiRightNeighbor
        else:
            guiLeftNeighbor = strnd[self._n-1] if self._n>0 else None
            return self._neighbor3p() == guiLeftNeighbor
    def _connectsToNatR(self):
        strnd = self._vhelix._strand(self._strandtype)
        guiRightNeighbor = strnd[self._n+1] if self._n<len(strnd)-1 else None
        if not guiRightNeighbor:
            return False
        if self._vhelix.directionOfStrandIs5to3(self._strandtype):
            return self._neighbor3p() == guiRightNeighbor
        else:
            return self._neighbor5p() == guiRightNeighbor
    def _connectsToNatL(self):
        strnd = self._vhelix._strand(self._strandtype)
        guiLeftNeighbor = strnd[self._n-1] if self._n>0 else None
        if not guiLeftNeighbor:
            return False
        if self._vhelix.directionOfStrandIs5to3(self._strandtype):
            return self._neighbor5p() == guiLeftNeighbor
        else:
            return self._neighbor3p() == guiLeftNeighbor
    
    # A crossover is a connection between a base and a base
    # that isn't its neighbor on the same strand
    def _hasCrossover5p(self):
        strnd = self._vhelix._strand(self._strandtype)
        if self._vhelix.directionOfStrandIs5to3(self._strandtype):
            guiLeftNeighbor = strnd[self._n-1] if self._n>0 else None
            return self._neighbor5p() not in (None, guiLeftNeighbor)
        else:
            guiRightNeighbor = strnd[self._n+1] if self._n<len(strnd)-1 else None
            return self._neighbor5p() not in (None, guiRightNeighbor)
    def _hasCrossover3p(self):
        strnd = self._vhelix._strand(self._strandtype)
        if self._vhelix.directionOfStrandIs5to3(self._strandtype):
            guiRightNeighbor = strnd[self._n+1] if self._n<len(strnd)-1 else None
            return self._neighbor3p() not in (None, guiRightNeighbor)
        else:
            guiLeftNeighbor = strnd[self._n-1] if self._n>0 else None
            return self._neighbor3p() not in (None, guiLeftNeighbor)
    def _hasCrossoverR(self):
        strnd = self._vhelix._strand(self._strandtype)
        guiRightNeighbor = strnd[self._n+1] if self._n<len(strnd)-1 else None
        if self._vhelix.directionOfStrandIs5to3(self._strandtype):
            if self.floatingXoverDestination():
                return True
            return self._neighbor3p() not in (None, guiRightNeighbor)
        else:
            return self._neighbor5p() not in (None, guiRightNeighbor)
    def _hasCrossoverL(self):
        strnd = self._vhelix._strand(self._strandtype)
        guiLeftNeighbor = strnd[self._n-1] if self._n>0 else None
        if self._vhelix.directionOfStrandIs5to3(self._strandtype):
            return self._neighbor5p() not in (None, guiLeftNeighbor)
        else:
            if self.floatingXoverDestination():
                return True
            return self._neighbor3p() not in (None, guiLeftNeighbor)

    def isEnd(self):
        if self._hasNeighbor5p() and\
           not self._hasNeighbor3p():
            return 3
        if self._hasNeighbor3p() and\
           not self._hasNeighbor5p():
            return 5
        return False

    def isStrand(self):
        return self._5pBase != None and\
               self._3pBase != None

    def partId(self):
        """docstring for partNum"""
        return id(self._vhelix.part())

    def isCrossover(self):
        """Return True if the part id or vhelix number of the prev or
        next base does not match the same for this base."""
        return self._hasCrossover3p() or self._hasCrossover5p()
    
    def floatingXoverDestination(self):
        """When a force crossover is being added, a crossover
        is displayed from the 3' end to the location of the mouse.
        That's called a floating crossover and its QPoint destination
        (the location of the mouse) is returned by this method."""
        return self._floatingXoverDestination

    def is3primeXover(self):
        """Return True if no 3pBase, but 5pBase exists."""
        if self._floatingXoverDestination:
            return True
        if self._3pBase != None:
            if self.vhelixNum() != self._3pBase.vhelixNum():
                return True
            elif self.partId() != self._3pBase.partId():
                # print "something"
                return True
            # this case assumes the opposite of the first number case
            elif abs(self._n - self._3pBase._n) != 1:
                return True
        return False
