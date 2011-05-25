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
    """A POD class that lives in the private API of
    virtualhelix (Why not put it inside VirtualHelix?
    Because it's already quite crowded in VirtualHelix)
    and provides information about which bases
    are connected to which other bases"""    
    def __init__(self, vhelix=None, index=None):
        super(Base, self).__init__()
        self._prevBase = None
        self._nextBase = None
        self._vhelix = vhelix
        self._n = index
    
    def __str__(self, vhelix=None, index=None):
        p, n = '_', '_'
        if self._nextBase:
            if self._nextBase.vhelixNum()==self.vhelixNum():
                n = '>'
            else:
                n = str(self._nextBase.vhelixNum())
        if self._prevBase:
            if self._prevBase.vhelixNum()==self.vhelixNum():
                p = '<'
            else:
                p = str(self._prevBase.vhelixNum())
        return p+n
            
    
    def _setPrev(self, newPrevBase, oldPrevNext=None):
        """Only VirtualHelix should call this method. Returns
        a list l such that _setPrev(*l) undoes the command."""
        if newPrevBase:
            undoDat = (self._prevBase, newPrevBase._nextBase)
        else:
            undoDat = (self._prevBase, None)
        if self._prevBase:
            self._prevBase._nextBase = oldPrevNext
        if newPrevBase:
            newPrevBase._nextBase = self
        self._prevBase = newPrevBase
        return undoDat
    
    def _setNext(self, newNextBase, oldNextPrev=None):
        """Only VirtualHelix should call this method. Returns
        a list l such that _setNext(*l) undoes the command"""
        if newNextBase:
            undoDat = (self._nextBase, newNextBase._prevBase)
        else:
            undoDat = (self._nextBase, None)
        if self._nextBase:
            self._nextBase._prevBase = oldNextPrev
        if newNextBase:
            newNextBase._prevBase = self
        self._nextBase = newNextBase
        return undoDat
    
    def vhelixNum(self):
        return self._vhelix.number()

    def isEmpty(self):
        return self._prevBase == None and\
               self._nextBase == None

    def is5primeEnd(self):
        """Return True if no prevBase, but nextBase exists."""
        return self._prevBase == None and\
               self._nextBase != None

    def is3primeEnd(self):
        """Return True if no nextBase, but prevBase exists."""
        return self._prevBase != None and\
               self._nextBase == None
    
    def isEnd(self):
        return (self._prevBase==None) ^ (self._nextBase==None)

    def isCrossover(self):
        """Return True if the part id or vhelix number of the prev or
        next base does not match the same for this base."""
        if self.isEmpty():
            return False

        if self._prevBase != Base._null:
            if self.vhelixNum() != self._prevBase.vhelixNum():
                return True
            elif self.partId() != self._prevBase.partId():
                return True
        if self._nextBase != Base._null:
            if self.vhelixNum() != self._nextBase.vhelixNum():
                return True
            elif self.partId() != self._nextBase.partId():
                return True
        return False
