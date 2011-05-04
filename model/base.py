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
    """docstring for Base"""
    _null = -1
    
    def __init__(self, vhelix=None, index=None):
        super(Base, self).__init__()
        self._prevBase = Base._null
        self._nextBase = Base._null
        self._vhelix = vhelix
        self._index = index

    def simpleRep(self, encoder):
        """
        Provides a representation of the receiver in terms of simple
        (container, atomic) classes and other objects implementing simpleRep
        """
        ret = {'.class': "Base"}
        ret['prevBase'] = self._prevBase
        ret['nextBase'] = self._nextBase
        ret['vhelix'] = self._vhelix
        ret['index'] = self._index
        return ret

    @classmethod
    def fromSimpleRep(cls, rep):
        """prevBase and nextBase are weak references.
        Everything else handled as normal."""
        b = Base()
        b._index = rep['index']
        b.prevID = rep['prevBase']
        b.nextID = rep['nextBase']
        b.vhelixID = rep['vhelixnum']
        return b

    def resolveSimpleRepIDs(self, idToObj):
        self._prevBase = idToObj[self.prevID]
        del self.prevID
        self._nextBase = idToObj[self.nextID]
        del self.nextID
        self._vhelix = idToObj[self.vhelixID]
        del vhelixID

    def getPrev(self):
        """Return reference to previous base, or _null."""
        return _prevBase

    def setPrev(self, base):
        """Set base as prevBase"""
        self._prevBase = base

    def getNext(self):
        """Return reference to next base, or _null."""
        return _nextBase

    def setNext(self, base):
        """Set base as nextBase"""
        self._nextBase = base

    def clearPrev(self):
        """Set previous base reference to _null"""
        self._prevBase = Base._null

    def clearNext(self):
        """Set previous base reference to _null"""
        self._nextBase = Base._null

    def partId(self):
        """docstring for partNum"""
        return self._vhelix.part().id()

    def vhelixNum(self):
        """docstring for vhelixNum"""
        return self._vhelix.number()

    def isNull(self):
        if self._prevBase == Base._null and\
           self._nextBase == Base._null:
            return True
        else:
            return False

    def is5primeEnd(self):
        """Return True if no prevBase, but nextBase exists."""
        if self._prevBase == Base._null and\
           self._nextBase != Base._null:
            return True
        else:
            return False

    def is3primeEnd(self):
        """Return True if no nextBase, but prevBase exists."""
        if self._prevBase != Base._null and\
           self._nextBase == Base._null:
            return True
        else:
            return False

    def isCrossover(self):
        """Return True if the part id or vhelix number of the prev or
        next base does not match the same for this base."""
        if self.isNull():
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
