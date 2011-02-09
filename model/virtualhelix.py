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
from .base import Base

class VirtualHelix(object):
    """Stores staple and scaffold routing information."""
    def __init__(self, *args, **kwargs):
        super(VirtualHelix, self).__init__()
        self._part = kwargs.get('part', None)
        self._number = kwargs.get('number', None)
        self._size = kwargs.get('size', 0)
        self._stapleBases = [Base() for n in range(self._size)]
        self._scaffoldBases = [Base() for n in range(self._size)]

    def simpleRep(self, encoder):
        """Returns a representation in terms of simple JSON-encodable types
        or types that implement simpleRep"""
        ret = {'.class': "DNAPart"}
        ret['part'] = self._part
        ret['number'] = self._number
        ret['size'] = self._size
        ret['stapleBases'] = self._stapleBases
        ret['scaffoldBases'] = self._scaffoldBases
        return ret

    @classmethod
    def fromSimpleRep(cls, rep):
        """Instantiates one of the parent class from the simple
        representation rep"""
        ret = VirtualHelix()
        ret._part = rep['part']
        ret._number = rep['number']
        ret._stapleBases = rep['stapleBases']
        ret._scaffoldBases = rep['scaffoldBases']
        return ret

    def resolveSimpleRepIDs(self,idToObj):
        raise NotImplementedError

    def number(self):
        """return VirtualHelix number"""
        return self._number

    def part(self):
        """docstring for part"""
        return self._part

    def stapleBase(self, index):
        """docstring for stapleBase"""
        return self._stapleBases[index]

    def scaffoldBase(self, index):
        """docstring for scaffoldBase"""
        return self._scaffoldBases[index]

    def getScaffoldBreakpoints(self):
        """
        Returns a tuple of lists. The first list contains the indices
        of bases that are 5' breakpoints. The second list contains the
        indices of bases that are 3' breakpoints.
        """
        list5p = []
        list3p = []
        for i in range(len(self._scaffoldBases)):
            if self._scaffoldBases[i].is5primeEnd():
                list5p.append(i)
            if self._scaffoldBases[i].is3primeEnd():
                list3p.append(i)
        return (list5p, list3p)



