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
pathhelixgroup.py

Created by Shawn on 2011-01-27.
"""

from PyQt4.QtCore import QRectF, QPointF, QEvent, pyqtSlot, QObject
from PyQt4.QtCore import pyqtSignal
from PyQt4.QtGui import QBrush
from PyQt4.QtGui import QGraphicsItem#, QGraphicsObject
from .pathhelix import PathHelix
from handles.activeslicehandle import ActiveSliceHandle
from handles.breakpointhandle import BreakpointHandle, EndType, StrandType
from handles.pathhelixhandle import PathHelixHandle
import styles


class PhgObject(QObject):
    """
    A placeholder class until QGraphicsObject is available to allow signaling
    """
    scaffoldChange = pyqtSignal(int)
    def __init__(self):
        super(PhgObject, self).__init__()
# end class

class PathHelixGroup(QGraphicsItem):
    """
    PathHelixGroup maintains data and state for a set of object that provide
    an interface to the schematic view of a DNA part. These objects include
    the PathHelix, PathHelixHandles, and ActiveSliceHandle.
    """
    handleRadius = styles.SLICE_HELIX_RADIUS
    
    def __init__(self, dnaPartInst, type="honeycomb", controller=None,\
                 scene=None, parent=None):
        super(PathHelixGroup, self).__init__()
        self.dnaPartInst = dnaPartInst
        self.part = dnaPartInst.part()
        self.pathController = controller
        self.scene = scene
        self.parent = parent
        self.numToPathHelix = {}
        
        # Lattice-specific initialization 
        self.crossSectionType = self.dnaPartInst.part().getCrossSectionType()
        if self.crossSectionType == "honeycomb":
            # set honeycomb parameters
            self.rect = QRectF(0, 0, 1000, 1000)
            self.pathCanvasWidth = 42 # FIX: set from config file
            self.startBase = 21
        else:
            # set square parameters
            self.pathCanvasWidth = 32 # FIX: set from config file
            self.startBase = 16
        count = self.part.getVirtualHelixCount()
        self.activeslicehandle = ActiveSliceHandle(count,\
                                                   self.startBase,\
                                                   self.pathCanvasWidth)
        if count > 0: # initalize if loading from file, otherwise delay
            self.activeslicehandle.setParentItem(self)
        # set up signals
        self.qObject = PhgObject()
        self.scaffoldChange = self.qObject.scaffoldChange
    # end def

    def paint(self, painter, option, widget=None):
        pass

    def boundingRect(self):
        return self.rect

    @pyqtSlot('QPointF', int)
    def handleHelixAdded(self, pos, number):
        """
        Retrieve reference to new VirtualHelix vh based on number relayed
        by the signal event. Next, create a new PathHelix associated 
        with vh and draw it on the screen. Finally, create or update
        the ActiveSliceHandle.
        """
        vh = self.part.getVirtualHelix(number)
        count = self.part.getVirtualHelixCount()
        # add PathHelixHandle
        x = -4*self.handleRadius
        y = count * (styles.PATH_BASE_HEIGHT + styles.PATH_HELIX_PADDING)
        phh = PathHelixHandle(vh, QPointF(x, y), self)
        phh.setParentItem(self)
        # add PathHelix
        ph = PathHelix(vh, QPointF(0, y), self)
        ph.setParentItem(self)
        self.numToPathHelix[number] = ph
        # update activeslicehandle
        if count == 1: # first vhelix added by mouse click
            self.activeslicehandle = ActiveSliceHandle(count,\
                                                       self.startBase,\
                                                       self.pathCanvasWidth)
            self.activeslicehandle.setParentItem(self)
        else:
            self.activeslicehandle.resize(count)

    @pyqtSlot('QPointF', int)
    def handleSliceHelixClick(self, number):
        """docstring for handleSliceHelixClick"""
        index = self.activeslicehandle.getPosition()
        vh = self.part.getVirtualHelix(number)
        ph = self.numToPathHelix[number]

        # move activeslice away from edge
        if index == 0:
            index = 1
            self.activeslicehandle.setPosition(1)
        elif index == self.part.getCanvasSize() - 1:
            index -= 1
            self.activeslicehandle.setPosition(index)

        # initialize some scaffold bases
        if number % 2 == 0:  # even parity
            prev = vh.scaffoldBase(index-1)
            curr = vh.scaffoldBase(index)
            next = vh.scaffoldBase(index+1)
            prev.setNext(curr)
            curr.setPrev(prev)
            curr.setNext(next)
            next.setPrev(curr)
        else:  # odd parity
            prev = vh.scaffoldBase(index+1)
            curr = vh.scaffoldBase(index)
            next = vh.scaffoldBase(index-1)
            prev.setNext(curr)
            curr.setPrev(prev)
            curr.setNext(next)
            next.setPrev(curr)

        # install breakpoints
        (list5p, list3p) = vh.getScaffoldBreakpoints()
        print "breaklists:", list5p, list3p
        for index in list5p:
            bh = BreakpointHandle(vh,\
                                  EndType.Left5Prime,\
                                  StrandType.Scaffold,\
                                  index)
            bh.setParentItem(ph)
        for index in list3p:
            bh = BreakpointHandle(vh,\
                                  EndType.Right3Prime,\
                                  StrandType.Scaffold,\
                                  index)
            bh.setParentItem(ph)

        s = "sliceHelix %d clicked at index %d" % (number, index)
        print s

    def bringToFront(self):
        """collidingItems gets a list of all items that overlap. sets
        this items zValue to one higher than the max."""
        zval = 1
        items = self.collidingItems() # the is a QList
        for item in items:
            temp = item.zValue()
            if temp >= zval:
                zval = item.zValue() + 1
            # end if
        # end for
        self.setZValue(zval)
    # end def
