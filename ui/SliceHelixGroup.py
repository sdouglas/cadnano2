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
SliceHelixGroup.py

Created by Shawn Douglas on 2010-06-15.
"""

from PyQt4.QtCore import QPointF, QObject, QEvent
from PyQt4.QtCore import QRectF
from PyQt4.QtGui import QBrush
from PyQt4.QtGui import QGraphicsItem, QGraphicsObject

import SliceHelix
import Styles

root3 = 1.732051

#class SliceHelixGroup(QGraphicsItem):
class SliceHelixGroup(QGraphicsObject):
    """docstring for SliceHelixGroup"""
    def __init__(self, nrows=3, ncolumns=6, type="honeycomb", parent=None):
        super(SliceHelixGroup, self).__init__(parent)
        # data related
        self.evens = -2
        self.odds = -1

        # drawing related
        self.radius = Styles.SLICE_HELIX_RADIUS
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
                   helix = SliceHelix.SliceHelix(row, column, QPointF(x, y), self)
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

    def parseHelixClick(self, helix):
        """
        parseHelixClick handles the outcome of a mouseReleaseEvent passed from a child SliceHelix.
        A previously unmarked helix is assigned a number, redrawn, and spawns its corresponding Path VirtualHelix.
        """
        if not helix.marked: # newly marked
            helix.marked = True  # toggle
            if helix.number == -1: # previously un-numbered
                if helix.parity == 1: 
                    self.odds = self.odds + 2 
                    helix.number = self.odds
                # end if 
                else:
                    self.evens = self.evens + 2
                    helix.number = self.evens
                # end else

                helix.useHelix()

                ## PORT: add this back in once Path.py is ready
                # path.addHelix(helix) 
                # 
                # # install vhelix neighbor relationships
                # if helix.p0neighbor != None && helix.p0neighbor.number != -1:
                #     path.pairHelices(helix.vhelix, helix.p0neighbor.vhelix, 0) 
                # if helix.p1neighbor != None && helix.p1neighbor.number != -1:
                #     path.pairHelices(helix.vhelix, helix.p1neighbor.vhelix, 1) 
                # if helix.p2neighbor != None && helix.p2neighbor.number != -1:
                #     path.pairHelices(helix.vhelix, helix.p2neighbor.vhelix, 2) 
            # end if
            else: # update existing helix with new path
                ## PORT: add this back in once Path.py is ready
                # if event.shiftKey:
                #     path.addStapleBases(self.drawPath.currentSlice,helix.vhelix) 
                # # end if 
                # else:
                #     path.addBases(self.drawPath.currentSlice,helix.vhelix) 
                # # end else
                # 
                # helix.vhelix.drawvhelix.update() 
                pass
            # end else
        # end if
        else: # scaffold already present
            pass
            # PORT: add this back when Path.py is ready
            # if helix.number != -1: # previously un-numbered 
            #     if event.shiftKey:
            #         path.addStapleBases(self.drawPath.currentSlice,helix.vhelix) 
            #         helix.vhelix.drawvhelix.update() 
                # end if
            # end if
        # end else
        helix.update()
    # end def

    def resetCounters(even, odd):
        self.evens = even 
        self.odds = odd 
    # end


