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
        self._colorName = None
        self._vhelix = vhelix
        self._strandtype = strandtype
        self._n = index

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
        return (fromOld5, toOld3)

    def _unset5Prime(self, toBase, fromOld5, toOld3):
        """Only VirtualHelix should call this method."""
        self._set5Prime(fromOld5)
        if toOld3 != None:
            toBase._set3Prime(toOld3)

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
        return (fromOld3, toOld5)

    def _unset3Prime(self, toBase, fromOld3, toOld5):
        """Only VirtualHelix should call this method."""
        self._set3Prime(fromOld3)
        if toOld5 != None:
            toBase._set5Prime(toOld5)

    def vhelix(self):
        return self._vhelix

    def vhelixNum(self):
        return self._vhelix.number()

    def get5pBase(self):
        return self._5pBase

    def get3pBase(self):
        return self._3pBase

    def setColor(self, colorName):
        self._colorName = colorName

    def getColor(self):
        return self._colorName

    def isEmpty(self):
        return self._5pBase == None and \
               self._3pBase == None

    def is5primeEnd(self):
        """Return True if no 5pBase, but 3pBase exists."""
        return self._5pBase == None and \
               self._3pBase != None

    def is3primeEnd(self):
        """Return True if no 3pBase, but 5pBase exists."""
        return self._5pBase != None and \
               self._3pBase == None

    def isEnd(self):
        if self.is5primeEnd():
            return 5
        if self.is3primeEnd():
            return 3
        return False

    def isStrand(self):
        return self._5pBase != None and\
               self._3pBase != None

    def partId(self):
        """docstring for partNum"""
        return self._vhelix.part().id()

    def isCrossover(self):
        """Return True if the part id or vhelix number of the prev or
        next base does not match the same for this base."""
        if self.isEmpty():
            return False
        if self._5pBase != None:
            if self.vhelixNum() != self._5pBase.vhelixNum():
                return True
            elif self.partId() != self._5pBase.partId():
                return True
        if self._3pBase != None:
            if self.vhelixNum() != self._3pBase.vhelixNum():
                return True
            elif self.partId() != self._3pBase.partId():
                return True
        return False

    def is3primeXover(self):
        """Return True if no 3pBase, but 5pBase exists."""
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
