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
from PyQt4.QtCore import pyqtSignal, QObject


class DNAPart(Part):
    changed = pyqtSignal()
    tweaked = pyqtSignal()

    def __init__(self, *args, **kwargs):
        super(DNAPart, self).__init__(self, *args, **kwargs)
        self._numberToVirtualHelix = {}  # number -> VirutalHelix
        self._coordToVirtualHelix = {}  # (row,col) -> VirtualHelix
        self._staples = []
        self._scaffolds = []
        self._name = kwargs.get('name', 'untitled')
        self._crossSectionType = kwargs.get('crossSectionType', LatticeType.Honeycomb)
        if (self._crossSectionType == LatticeType.Honeycomb):
            self._canvasSize = 42
        elif (self._crossSectionType == LatticeType.Square):
            self._crossSectionType = 32
        else:
            raise NotImplementedError
        # Signals

    def getCanvasSize(self):
        """Returns the current canvas size (# of bases) for the DNA part."""
        return self._canvasSize
        
    ############################# Archiving/Unarchiving #############################
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
    
    ############################# VirtualHelix CRUD #############################
    # Take note: vhrefs are the shiny new way to talk to dnapart about its constituent
    # virtualhelices. Wherever you see f(vhref) you can
    # f(27)         use the virtualhelix's id number
    # f(vh)         use an actual virtualhelix
    # f((1,42))     use the coordinate representation of its position
    def getVirtualHelix(self, vhref, returnNoneIfAbsent=True):
        """A vhref is the number of a virtual helix, the (row, col) of a virtual helix,
        or the virtual helix itself. For conveniece, CRUD should now work with any of them."""
        vh = None
        if type(vhref) in ('int', 'long'):
            vh = self._numberToVirtualHelix.get(number, None)
        elif type(vhref) == 'tuple':
            vh = self._coordToVirtualHelix(vh, None)
        if not isinstance(vh, VirtualHelix):
            if returnNoneIfAbsent:
                return None
            else:
                raise IndexError("Couldn't find the virtual helix in part %s referenced by index %s"%(self, vhref))
        return vh

    def addVirtualHelix(self, slicehelix):
        """Adds a new VirtualHelix to the part in response to user input and
        adds slicehelix as an observer."""
        row, col = slicehelix.row(), slicehelix.col()
        vhelix = VirtualHelix(part=self,\
                              number=slicehelix.number(),\
                              row=row,\
                              col=col,\
                              size=self._canvasSize)
        self._numberToVirtualHelix[slicehelix.number()] = vhelix
        self._coordToVirtualHelix[(row, col)] = vhelix
        self.changed.emit()
        return vhelix

    def removeVirtualHelix(self, vhref, failIfAbsent=True):
        """Called by SliceHelix.removeVirtualHelix() to update data."""
        vh = getVirtualHelix(vhref, returnNoneIfAbsent = True)
        if not vh:
            if failIfAbsent:
                raise IndexError('Couldn\'t find virtual helix %s for removal'%str(vhref))
            else:
                return
        del self._coordToVirtualHelix[vh.coord()]
        del self._numberToVirtualHelix[vh.number()]
        self.changed.emit()

    def getVirtualHelixCount(self):
        """docstring for getVirtualHelixList"""
        return len(self._numberToVirtualHelix)

    ############################# VirtualHelix Arrangement (@todo: move into DNAHoneycombPart subclass) #############################
    def virtualHelixParityEven(self, vhref):
        """A property of the part, because the part is responsible for laying out
        the virtualhelices and parity is a property of the layout more than it is a
        property of a helix (maybe a non-honeycomb layout could support a different
        notion of parity?)"""
        vh = self.getVirtualHelix(vhref, returnNoneIfAbsent=False)
        return vh.number() % 2 == 0;
        
    def getVirtualHelixNeighbors(self, vhref):
        neighbors = []
        vh = self.getVirtualHelix(vhref, returnNoneIfAbsent=False)
        (r,c) = vh.coord()
        if self.virtualHelixParityEven(vh):
            neighbors.append(self.getVirtualHelix((r,c+1)))  # p0 neighbor (p0 is a direction)
            neighbors.append(self.getVirtualHelix((r-1,c)))  # p1 neighbor
            neighbors.append(self.getVirtualHelix((r,c-1)))  # p2 neighbor
        else:
            neighbors.append(self.getVirtualHelix((r,c-1)))  # p0 neighbor (p0 is a direction)
            neighbors.append(self.getVirtualHelix((r+1,c)))  # p1 neighbor
            neighbors.append(self.getVirtualHelix((r,c+1)))  # p2 neighbor
        return neighbors  # Note: the order and presence of Nones is important
        # If you need the indices of potential neighbors use range(0,len(neighbors))

    #  @todo eliminate via subclassing
    def crossSectionType(self):
        """Returns the cross-section type of the DNA part."""
        return self._crossSectionType
