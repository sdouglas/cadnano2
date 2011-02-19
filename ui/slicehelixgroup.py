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
slicehelixgroup.py

Created by Shawn Douglas on 2010-06-15.
"""

from heapq import *
from PyQt4.QtCore import QRectF, QPointF, QEvent, pyqtSignal, QObject
from PyQt4.QtGui import QBrush
from PyQt4.QtGui import QGraphicsItem#, QGraphicsObject
from .slicehelix import SliceHelix
import styles


root3 = 1.732051

class ShgObject(QObject):
    helixAdded = pyqtSignal('QPointF', int)
    sliceHelixClicked = pyqtSignal(int)
    def __init__(self):
        super(ShgObject, self).__init__()
# end class

class SliceHelixGroup(QGraphicsItem):  # was a QGraphicsObject change for Qt 4.6
    """
    SliceHelixGroup maintains data and state for a set of SliceHelix objects
    (the circles in the slice view) and serves as the root of their
    drawing tree.
    
    -reserveLabelForHelix and -recycleLabelForHelix maintain a pool
    of labels (these are the nonnegative integers that appear on them)
    for slices.
    """
    def __init__(self, dnaPartInst, nrows=3, ncolumns=6,\
                controller=None, scene=None, parent=None):
        super(SliceHelixGroup, self).__init__(parent)
        # data related
        self.dnaPartInst = dnaPartInst
        self.crossSectionType = self.dnaPartInst.part().getCrossSectionType()
        self.sliceController = controller
        self.scene = scene
        self.parent = parent
        self.oddRecycleBin = []
        self.evenRecycleBin = []
        self.reserveBin = set()
        self.highestUsedOdd = -1  # Used iff the recycle bin is empty and highestUsedOdd+2 is not in the reserve bin
        self.highestUsedEven = -2  # same
        self.qObject = ShgObject()
        self.helixAdded = self.qObject.helixAdded
        self.sliceHelixClicked = self.qObject.sliceHelixClicked
        # drawing related
        self.radius = styles.SLICE_HELIX_RADIUS
        self.nrows = nrows 
        self.ncolumns = ncolumns
        self.handleSize = 15 # FIX: read from config file
        self.setFlags(QGraphicsItem.ItemIsSelectable)
        self.helixhash = {}

        if self.crossSectionType == 'honeycomb':
            self.rect = QRectF(0, 0,\
                               (ncolumns)*self.radius*root3,\
                               (nrows)*self.radius*3)
            # create a SliceHelix at each position in the grid
            for column in range(ncolumns):
               for row in range(nrows):
                   x = column*self.radius*root3
                   if ((row % 2) ^ (column % 2)): # odd parity
                       y = row*self.radius*3 + self.radius
                   else:                          # even parity
                       y = row*self.radius*3
                   helix = SliceHelix(row, column, QPointF(x, y), self)
                   self.helixhash[(row, column)] = helix
                   helix.setParentItem(self)
            # populate neighbor linkages
            for column in range(ncolumns):
                for row in range(nrows):
                    index = (row, column)
                    helix = self.helixhash[index]
                    if helix.parity: # odd parity
                        if column > 0: # if col-1 exists, set P0
                            helix.p0neighbor = self.helixhash[(row,column-1)]
                        # end if
                        if row < nrows-1: # if row+1 exists, set P1
                            helix.p1neighbor = self.helixhash[(row+1,column)]
                        # end if
                        if column < ncolumns-1: # if col+1 exists, set P2
                            helix.p2neighbor = self.helixhash[(row,column+1)]
                        # end if
                    # end if
                    else: # even parity
                        if column < ncolumns-1: # if col+1 exists, set P0
                            helix.p0neighbor = self.helixhash[(row,column+1)]
                        # end if
                        if row > 0: # if row-1 exists, set P1
                            helix.p1neighbor = self.helixhash[(row-1,column)]
                        # end if
                        if column > 0: # if col-1 exists, set P2
                            helix.p2neighbor = self.helixhash[(row,column-1)]
                        # end if
                    # end else
                # end for
            # end for
        # end if
        else: # type = square
            print "self.type == honeycomb is false"
            pass
        # end else
    # end def

    def paint(self, painter, option, widget=None):
        pass

    def boundingRect(self):
        return self.rect

    def reserveLabelForHelix(self, helix, num=None):
        """
        Reserves and returns a unique numerical label appropriate for helix.
        If a specific index is preferable (say, for undo/redo) it can be
        requested in num.
        """
        if num != None: # A special request
            assert num >= 0, long(num) == num
            if num in self.oddRecycleBin:
                self.oddRecycleBin.remove(num)
                return num
            if num in self.evenRecycleBin:
                self.evenRecycleBin.remove(num)
                return num
            self.reserveBin.add(num)
            return num
        # Find an arbitrary index (subject to parity constraints)
        if helix.parity == 1:
            if len(self.oddRecycleBin):
                return heappop(self.oddRecycleBin)
            else:
                while self.highestUsedOdd + 2 in self.reserveBin:
                    self.highestUsedOdd += 2
                self.highestUsedOdd += 2
                return self.highestUsedOdd
        else:
            if len(self.evenRecycleBin):
                return heappop(self.evenRecycleBin)
            else:
                while self.highestUsedEven + 2 in self.reserveBin:
                    self.highestUsedEven += 2
                self.highestUsedEven += 2
                return self.highestUsedEven

    def recycleLabelForHelix(self, n, helix):
        """
        The caller's contract is to ensure that n is not used in *any* helix
        at the time of the calling of this function (or afterwards, unless
        reserveLabelForHelix returns the label again)"""
        if n % 2 == 0:
            heappush(self.evenRecycleBin,n)
        else:
            heappush(self.oddRecycleBin,n)

    def addHelixToPathGroup(self, pos, number):
        """Notify PathHelixGroup that a new VirtualHelix has been
        added to the part.
        pos: a QPointF identifying a slice views XY position for a helix
        number: slicehelix number
        """
        # install VirtualHelix neighbor relationships
        self.helixAdded.emit(pos, number)

    def addBasesToDnaPart(self, number):
        """Notify PathHelixGroup"""
        self.sliceHelixClicked.emit(number)

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

                    
