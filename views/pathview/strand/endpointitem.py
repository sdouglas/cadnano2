#!/usr/bin/env python
# encoding: utf-8

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

from exceptions import NotImplementedError
from views import styles
import util
# import Qt stuff into the module namespace with PySide, PyQt4 independence
util.qtWrapImport('QtCore', globals(), ['pyqtSignal', 'QObject', 'QPointF', 'Qt'])
util.qtWrapImport('QtGui', globals(), ['QGraphicsPathItem', 'QPen', 'QPainterPath', 'QPolygonF'])

baseWidth = styles.PATH_BASE_WIDTH

ppL5 = QPainterPath()  # Left 5' PainterPath
ppR5 = QPainterPath()  # Right 5' PainterPath
ppL3 = QPainterPath()  # Left 3' PainterPath
ppR3 = QPainterPath()  # Right 3' PainterPath
pp53 = QPainterPath()  # Left 5', Right 3' PainterPath
pp35 = QPainterPath()  # Left 5', Right 3' PainterPath
# set up ppL5 (left 5' blue square)
ppL5.addRect(0.25*baseWidth, 0.125*baseWidth,0.75*baseWidth, 0.75*baseWidth)
# set up ppR5 (right 5' blue square)
ppR5.addRect(0, 0.125*baseWidth, 0.75*baseWidth, 0.75*baseWidth)
# set up ppL3 (left 3' blue triangle)
l3poly = QPolygonF()
l3poly.append(QPointF(baseWidth, 0))
l3poly.append(QPointF(0.25*baseWidth, 0.5*baseWidth))
l3poly.append(QPointF(baseWidth, baseWidth))
ppL3.addPolygon(l3poly)
# set up ppR3 (right 3' blue triangle)
r3poly = QPolygonF()
r3poly.append(QPointF(0, 0))
r3poly.append(QPointF(0.75*baseWidth, 0.5*baseWidth))
r3poly.append(QPointF(0, baseWidth))
ppR3.addPolygon(r3poly)


# single base left 5'->3'
pp53.addRect(0, 0.125*baseWidth, 0.5*baseWidth, 0.75*baseWidth)
poly53 = QPolygonF()
poly53.append(QPointF(0.5*baseWidth, 0))
poly53.append(QPointF(baseWidth, 0.5*baseWidth))
poly53.append(QPointF(0.5*baseWidth, baseWidth))
pp53.addPolygon(poly53)
# single base left 3'<-5'
pp35.addRect(0.50*baseWidth, 0.125*baseWidth, 0.5*baseWidth, 0.75*baseWidth)
poly35 = QPolygonF()
poly35.append(QPointF(0.5*baseWidth, 0))
poly35.append(QPointF(0, 0.5*baseWidth))
poly35.append(QPointF(0.5*baseWidth, baseWidth))
pp35.addPolygon(poly35)

class EndpointItem(QGraphicsPathItem):
    def __init__(self, strandItem, isDrawn5to3, captype):
        """The parent should be a StrandItem."""
        super(EndpointItem, self).__init__(strandItem)
        self._strandItem = strandItem
        self._captype = captype
        self._isDrawn5to3 = isDrawn5to3
        if captype == 'low':
            path = ppL5 if isDrawn5to3 else ppL3
        elif captype == 'high':
            path = ppR3 if isDrawn5to3 else ppR5
        else:
            path = pp53 if isDrawn5to3 else pp35
        self.setPath(path)
    # end def
        
    ### SIGNALS ###

    ### SLOTS ###

    ### TOOL METHODS ###
    def selectToolMousePress(self, event):
        """docstring for selectToolMousePress"""
        # self._dragBounds = strand.getDragBounds()
        # self._startIdx = 
        pass
    # end def

    def selectToolMouseMove(self, event):
        """docstring for selectToolMouseMove"""
        # snap to grid location
        # notify stranditem to redraw horiz line
        pass
    # end def

    def selectToolMouseRelease(self, event):
        """docstring for selectToolMouseRelease"""
        pass
    # end def

    def mergeToolMouseRelease(self, event):
        """Attempts to merge strand with its neighbor."""
        # if strandset.strandsCanBeMerged(priorityStrand, otherStrand):
        #     strandset.mergeStrands(priorityStrand, otherStrand)
        pass
    # end def
