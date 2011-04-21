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
dnapartinstance.py
Created by Shawn Douglas on 2011-02-01.
"""
from .partinstance import PartInstance

class DNAPartInstance(PartInstance):
    """
    DNAPartInstance stores view-level customization that does not
    change the underlying data structure, such as color schemes and
    VirtualHelix ordering.
    """
    
    def __init__(self, part, *args, **kwargs):
        super(DNAPartInstance, self).__init__(part, *args, **kwargs)
        self._part = part
        self._virtualHelixOrder = []
        self._stapleColor = {}
        self._scaffoldColor = {}

    def simpleRep(self,encoder):
        """Returns a representation in terms of simple JSON-encodable types
        or types that implement simpleRep"""
        ret = {".class":"DNAPartInstance"}
        ret['virtualHelixOrder'] = self._virtualHelixOrder
        ret['stapleColor'] = self._stapleColor
        ret['scaffoldColor'] = self._scaffoldColor
        return ret

    @classmethod
    def fromSimpleRep(cls, rep):
        """Instantiates one of the parent class from the simple
        representation rep"""
        dpi = DNAPartInstance()
        dpi.partID = rep['part']
        dpi._virtualHelixOrder = rep['virtualHelixOrder']
        dpi._stapleColor = rep['stapleColor']
        dpi._scaffoldColor = rep['scaffoldColor']
        return dpi

    def resolveSimpleRepIDs(self, idToObj):
        self._part = idToObj[self.partID]
        del self.partID

    def getVirtualHelixOrder(self):
        """getVirtualHelixOrder returns a list of """
        return self._virtualHelixOrder

        