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
    
    def __init__(self):
        super(Base, self).__init__()
        self._prevBase = Base._null
        self._nextBase = Base._null

    def simpleRep(self, encoder):
        """
        Provides a representation of the receiver in terms of simple
        (container, atomic) classes and other objects implementing simpleRep
        """
        ret = {'.class': "Base"}
        ret['prevBase'] = self._prevBase
        ret['nextBase'] = self._nextBase
        return ret

    @classmethod
    def fromSimpleRep(cls, rep):
        b = Base()
        b.prevID = rep['prevBase']
        b.nextID = rep['nextBase']
        return ret

    def resolveSimpleRepIDs(self, idToObj):
        self._part = idToObj[self.partID]
        del self.partID

    def getPrev(self):
        """docstring for getPrev"""
        return _prevBase

    def setPrev(self, base):
        """docstring for setPrev"""
        self._prevBase = base

    def getNext(self):
        """docstring for getNext"""
        return _nextBase

    def setNext(self, base):
        """docstring for setPrev"""
        self._nextBase = base

    def is5primeEnd(self):
        """docstring for is5primeEnd"""
        if self._prevBase == Base._null and self._nextBase != Base._null:
            return True
        else:
            return False

    def is3primeEnd(self):
        """docstring for is3primeEnd"""
        if self._prevBase != Base._null and self._nextBase == Base._null:
            return True
        else:
            return False

