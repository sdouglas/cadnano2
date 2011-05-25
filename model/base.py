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

class Base(object):
    """
    A POD class that lives in the private API of
    virtualhelix (Why not put it inside VirtualHelix?
    Because it's already quite crowded in VirtualHelix)
    and provides information about which bases
    are connected to which other bases
    """    
    def __init__(self, vhelix=None, strandtype=None, index=None):
        super(Base, self).__init__()
        self._5pBase = None
        self._3pBase = None
        self._vhelix = vhelix
        self._strandtype = strandtype
        self._n = index
    
    def __str__(self, vhelix=None, index=None):
        threeB, fiveB = '_', '_'
        fiveTo3 = self._vhelix.directionOfStrandIs5to3(self._strandtype)
        if self._3pBase:
            if self._3pBase.vhelixNum()==self.vhelixNum():
                threeB = fiveTo3 and '>' or '<'
            else:
                threeB = str(self._3pBase.vhelixNum())
        if self._5pBase:
            if self._5pBase.vhelixNum()==self.vhelixNum():
                fiveB = fiveTo3 and '<' or '>'
            else:
                fiveB = str(self._5pBase.vhelixNum())
        if self._vhelix.directionOfStrandIs5to3(self._strandtype):
            return fiveB+threeB
        else:
            return threeB+fiveB
            
    
    def _set5Prime(self, new5pBase, old5p3p=None):
        """Only VirtualHelix should call this method. Returns
        a list l such that _setPrev(*l) undoes the command."""
        if new5pBase:
            undoDat = (self._5pBase, new5pBase._3pBase)
        else:
            undoDat = (self._5pBase, None)
        if self._5pBase:
            self._5pBase._3pBase = old5p3p
        if new5pBase:
            new5pBase._3pBase = self
        self._5pBase = new5pBase
        return undoDat
    
    def _set3Prime(self, new3pBase, old3p5p=None):
        """Only VirtualHelix should call this method. Returns
        a list l such that _set3p(*l) undoes the command"""
        if new3pBase:
            undoDat = (self._3pBase, new3pBase._5pBase)
        else:
            undoDat = (self._3pBase, None)
        if self._3pBase:
            self._3pBase._5pBase = old3p5p
        if new3pBase:
            new3pBase._5pBase = self
        self._3pBase = new3pBase
        return undoDat
    
    def vhelixNum(self):
        return self._vhelix.number()

    def isEmpty(self):
        return self._prevBase == None and\
               self._nextBase == None

    def is5primeEnd(self):
        """Return True if no 5pBase, but 3pBase exists."""
        return self._5pBase == None and\
               self._3pBase != None

    def is3primeEnd(self):
        """Return True if no 3pBase, but 5pBase exists."""
        return self._5pBase != None and\
               self._3pBase == None
    
    def isEnd(self):
        return (self._5pBase==None) ^ (self._3pBase==None)

    def isCrossover(self):
        """Return True if the part id or vhelix number of the prev or
        next base does not match the same for this base."""
        if self.isEmpty():
            return False

        if self._5pBase != Base._null:
            if self.vhelixNum() != self._5pBase.vhelixNum():
                return True
            elif self.partId() != self._5pBase.partId():
                return True
        if self._3pBase != Base._null:
            if self.vhelixNum() != self._3pBase.vhelixNum():
                return True
            elif self.partId() != self._3pBase.partId():
                return True
        return False
