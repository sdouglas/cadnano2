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

from math import floor
from exceptions import NotImplementedError
from views import styles
import util
# import Qt stuff into the module namespace with PySide, PyQt4 independence
util.qtWrapImport('QtCore', globals(), ['pyqtSignal', 'QObject', 'QPointF', 'Qt'])
util.qtWrapImport('QtGui', globals(), ['QGraphicsPathItem', 'QPen', 'QPainterPath', 'QPolygonF'])

_baseWidth = styles.PATH_BASE_WIDTH

ppL5 = QPainterPath()  # Left 5' PainterPath
ppR5 = QPainterPath()  # Right 5' PainterPath
ppL3 = QPainterPath()  # Left 3' PainterPath
ppR3 = QPainterPath()  # Right 3' PainterPath
pp53 = QPainterPath()  # Left 5', Right 3' PainterPath
pp35 = QPainterPath()  # Left 5', Right 3' PainterPath
# set up ppL5 (left 5' blue square)
ppL5.addRect(0.25*_baseWidth, 0.125*_baseWidth,0.75*_baseWidth, 0.75*_baseWidth)
# set up ppR5 (right 5' blue square)
ppR5.addRect(0, 0.125*_baseWidth, 0.75*_baseWidth, 0.75*_baseWidth)
# set up ppL3 (left 3' blue triangle)
l3poly = QPolygonF()
l3poly.append(QPointF(_baseWidth, 0))
l3poly.append(QPointF(0.25*_baseWidth, 0.5*_baseWidth))
l3poly.append(QPointF(_baseWidth, _baseWidth))
ppL3.addPolygon(l3poly)
# set up ppR3 (right 3' blue triangle)
r3poly = QPolygonF()
r3poly.append(QPointF(0, 0))
r3poly.append(QPointF(0.75*_baseWidth, 0.5*_baseWidth))
r3poly.append(QPointF(0, _baseWidth))
ppR3.addPolygon(r3poly)


# single base left 5'->3'
pp53.addRect(0, 0.125*_baseWidth, 0.5*_baseWidth, 0.75*_baseWidth)
poly53 = QPolygonF()
poly53.append(QPointF(0.5*_baseWidth, 0))
poly53.append(QPointF(_baseWidth, 0.5*_baseWidth))
poly53.append(QPointF(0.5*_baseWidth, _baseWidth))
pp53.addPolygon(poly53)
# single base left 3'<-5'
pp35.addRect(0.50*_baseWidth, 0.125*_baseWidth, 0.5*_baseWidth, 0.75*_baseWidth)
poly35 = QPolygonF()
poly35.append(QPointF(0.5*_baseWidth, 0))
poly35.append(QPointF(0, 0.5*_baseWidth))
poly35.append(QPointF(0.5*_baseWidth, _baseWidth))
pp35.addPolygon(poly35)

class EndpointItem(QGraphicsPathItem):
    def __init__(self, strandItem, captype, isDrawn5to3):
        """The parent should be a StrandItem."""
        super(EndpointItem, self).__init__(strandItem)
        self._strandItem = strandItem
        self._activeTool = strandItem.activeTool()
        self._captype = captype
        self._isDrawn5to3 = isDrawn5to3
        self._selectToolMousePressIdx = None
        if captype == 'low':
            path = ppL5 if isDrawn5to3 else ppL3
        elif captype == 'high':
            path = ppR3 if isDrawn5to3 else ppR5
        else:
            path = pp53 if isDrawn5to3 else pp35
        self.setPath(path)
    # end def

    def __repr__(self):
        return "%s" % self.__class__.__name__

    ### SIGNALS ###

    ### SLOTS ###

    ### ACCESSORS ###
    def idx(self):
        """Look up baseIdx, as determined by srandItem idxs and cap type."""
        if self._captype == 'low':
            return self._strandItem.idxs()[0]
        else:  # high or dual, doesn't matter
            return self._strandItem.idxs()[1]

    ### EVENT HANDLERS ###
    def mousePressEvent(self, event):
        """
        Parses a mousePressEvent, calling the approproate tool method as
        necessary.
        """
        toolMethodName = str(self._activeTool()) + "MousePress"
        if hasattr(self, toolMethodName):  # if the tool method exists
            getattr(self, toolMethodName)(event.pos().x())  # call it

    def mouseMoveEvent(self, event):
        """
        Parses a mouseMoveEvent, calling the approproate tool method as
        necessary.
        """
        toolMethodName = str(self._activeTool()) + "MouseMove"
        if hasattr(self, toolMethodName):  # if the tool method exists
            getattr(self, toolMethodName)(event.pos().x())  # call it

    def mouseReleaseEvent(self, event):
        """
        Parses a mouseReleaseEvent, calling the approproate tool method as
        necessary.
        """
        toolMethodName = str(self._activeTool()) + "MouseRelease"
        if hasattr(self, toolMethodName):  # if the tool method exists
            getattr(self, toolMethodName)(event.pos().x())  # call it

    ### TOOL METHODS ###
    def selectToolMousePress(self, x):
        """docstring for selectToolMousePress"""
        print "%s.%s [%d]" % (self, util.methodName(), self.idx())
        self._selectToolMousePressIdx = self.idx()
    # end def

    def selectToolMouseMove(self, x):
        """docstring for selectToolMouseMove"""
        # snap to grid location
        newX = int(floor((self.x() + x)/_baseWidth)*_baseWidth)
        self.setPos(newX, self.y())
        # notify stranditem to redraw horiz line
        self._strandItem.updateLine(self)
    # end def

    def selectToolMouseRelease(self, x):
        """docstring for selectToolMouseRelease"""
        baseIdx = int(floor(self.x() / _baseWidth))
        print "%s.%s [%d]" % (self, util.methodName(), baseIdx)
        if self._selectToolMousePressIdx != None:
            if baseIdx != self._selectToolMousePressIdx:
                # do the resize here
                pass
            self._selectToolMousePressIdx = None
        else:
            raise  # mouse release after phantom press
    # end def

    def mergeToolMouseRelease(self, idx):
        """Attempts to merge strand with its neighbor."""
        # if strandset.strandsCanBeMerged(priorityStrand, otherStrand):
        #     strandset.mergeStrands(priorityStrand, otherStrand)
        print "%s.%s [%d]" % (self, util.methodName(), idx)
        pass
    # end def
