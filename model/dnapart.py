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
DNAPart.py
"""
from exceptions import NotImplementedError
import json
from .part import Part
from .virtualhelix import VirtualHelix
from .enum import LatticeType

class DNAPart(Part):
    def __init__(self, *args, **kwargs):
        super(DNAPart, self).__init__(self, *args, **kwargs)
        self._virtualHelices = {}
        self._staples = []
        self._scaffolds = []
        self._name = kwargs.get('name', 'untitled')
        self._crossSectionType = kwargs.get('crossSectionType', LatticeType.Honeycomb)
        # FIX: defaults should be read from a config file
        if (self._crossSectionType == LatticeType.Honeycomb):
            self._canvasSize = 42
        elif (self._crossSectionType == LatticeType.Square):
            self._crossSectionType = 32
        else:
            raise NotImplementedError

    def simpleRep(self, encoder):
        """
        Provides a representation of the receiver in terms of simple
        (container,atomic) classes and other objects implementing simpleRep
        """
        ret = {'.class': "DNAPart"}
        ret['virtualHelices'] = self._virtualHelices
        ret['name'] = self._name
        ret['staples'] = self._staples
        ret['scaffolds'] = self._scaffolds
        return ret

    @classmethod
    def fromSimpleRep(cls, rep):
        ret = DNAPart()
        ret._virtualHelices = rep['virtualHelices']
        ret._name = rep['name']
        ret._staples = rep['staples']
        ret._scaffolds = rep['scaffolds']
        return ret

    def resolveSimpleRepIDs(self,idToObj):
        pass  # DNAPart owns its virtual helices, staples, and scaffods
              # so we don't need to make weak refs to them

    def crossSectionType(self):
        """Returns the cross-section type of the DNA part."""
        return self._crossSectionType

    def getCanvasSize(self):
        """Returns the current canvas size (# of bases) for the DNA part."""
        return self._canvasSize

    def addVirtualHelix(self, slicehelix):
        """Adds a new VirtualHelix to the part in response to user input and
        adds slicehelix as an observer."""
        vhelix = VirtualHelix(part=self,\
                              number=slicehelix.number(),\
                              row=slicehelix.row(),\
                              col=slicehelix.col(),\
                              size=self._canvasSize)
        self._virtualHelices[slicehelix.number()] = vhelix
        [p0, p1, p2, p3] = slicehelix.getNeighboringVirtualHelixList()
        vhelix.connectNeighbors(p0, p1, p2, p3)
        vhelix.addObserver(slicehelix)
        return vhelix

    def removeVirtualHelix(self, number):
        """Called by SliceHelix.removeVirtualHelix() to update data."""
        del self._virtualHelices[number]

    def getVirtualHelix(self, number, returnNoneIfAbsent=True):
        """Look up and return reference to a VirtualHelix"""
        return self._virtualHelices.get(number, None)

    def hasVirtualHelix(self, number):
        if number in self._virtualHelices:
            return True
        else:
            return False

    def getVirtualHelixCount(self):
        """docstring for getVirtualHelixList"""
        return len(self._virtualHelices)
