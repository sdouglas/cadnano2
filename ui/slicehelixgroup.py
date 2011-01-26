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

from PyQt4.QtCore import QPointF, QObject, QEvent
from PyQt4.QtCore import QRectF
from PyQt4.QtGui import QBrush
from PyQt4.QtGui import QGraphicsItem, QGraphicsObject

import slicehelix
import styles

root3 = 1.732051

class SliceHelixGroup(QGraphicsObject):
    """docstring for SliceHelixGroup"""
    def __init__(self, nrows=3, ncolumns=6, type="honeycomb", parent=None):
        super(SliceHelixGroup, self).__init__(parent)
        # data related
        self.oddRecycleBin = set()
        self.evenRecycleBin = set()
        self.highestUsedOdd = -1  #Used iff the recycle bin is empty
        self.highestUsedEven = -2  #same

        # drawing related
        self.radius = styles.SLICE_HELIX_RADIUS
        self.nrows = nrows 
        self.ncolumns = ncolumns
        self.type = type
        self.handleSize = 15
        self.setFlags(QGraphicsItem.ItemIsSelectable)
        self.helixhash = {}

        if type == "honeycomb":
            self.rect = QRectF(0, \
                               0, \
                               (ncolumns)*self.radius*root3, \
                               (nrows)*self.radius*3)

            # create a SliceHelix at each position in the grid
            for column in range(ncolumns):
               for row in range(nrows):
                   x = column*self.radius*root3
                   if ((row % 2) ^ (column % 2)): # odd parity
                       y = row*self.radius*3 + self.radius
                   else:                          # even parity
                       y = row*self.radius*3
                   helix = slicehelix.SliceHelix(row, column, QPointF(x, y), self)
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
            pass
        # end else
    # end def

    def paint(self, painter, option, widget=None):
        pass

    def boundingRect(self):
        return self.rect

    def newNumberForHelix(self, helix):
        """Reserves and returns a unique numerical label appropriate for helix"""
        if helix.parity == 1:
            if len(self.oddRecycleBin):
                return self.oddRecycleBin.pop()
            else:
                self.highestUsedOdd+=2
                return self.highestUsedOdd
        else:
            if len(self.evenRecycleBin):
                return self.evenRecycleBin.pop()
            else:
                self.highestUsedEven+=2
                return self.highestUsedEven

    def recycleNumberForHelix(self,n,helix):
        """The caller's contract is to ensure that n is not used in *any* helix at the time of the calling of this function"""
        if n%2==0:
            self.evenRecycleBin.add(n)
        else:
            self.oddRecycleBin.add(n)


