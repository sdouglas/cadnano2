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
pathhelix.py
Created by Shawn on 2011-01-27.
"""

from exceptions import AttributeError, ValueError
from PyQt4.QtCore import Qt
from PyQt4.QtCore import QLine, QRectF, QPointF, QPoint
from PyQt4.QtGui import QBrush, QColor
from PyQt4.QtGui import QGraphicsItem
from PyQt4.QtGui import QGraphicsSimpleTextItem
from PyQt4.QtGui import QPainter, QPainterPath
from PyQt4.QtGui import QPen, QDrag, QUndoCommand, QPolygonF
import ui.styles as styles
from model.enum import EndType, LatticeType, StrandType
from model.virtualhelix import VirtualHelix
from handles.breakpointhandle import BreakpointHandle
from mmayacadnano.pathhelix3d import PathHelix3D  # For Campbell
from weakref import ref
from handles.pathhelixhandle import PathHelixHandle
from math import floor

baseWidth = styles.PATH_BASE_WIDTH
ppL5 = QPainterPath()  # Left 5' PainterPath
ppR5 = QPainterPath()  # Right 5' PainterPath
ppL3 = QPainterPath()  # Left 3' PainterPath
ppR3 = QPainterPath()  # Right 3' PainterPath
# set up ppL5 (left 5' blue square)
ppL5.addRect(0.25 * baseWidth, 0.125 * baseWidth,\
             0.75 * baseWidth, 0.75 * baseWidth)
# set up ppR5 (right 5' blue square)
ppR5.addRect(0, 0.125 * baseWidth,\
             0.75 * baseWidth, 0.75 * baseWidth)
# set up ppL3 (left 3' blue triangle)
l3poly = QPolygonF()
l3poly.append(QPointF(baseWidth, 0))
l3poly.append(QPointF(0.25 * baseWidth, 0.5 * baseWidth))
l3poly.append(QPointF(baseWidth, baseWidth))
ppL3.addPolygon(l3poly)
# set up ppR3 (right 3' blue triangle)
r3poly = QPolygonF()
r3poly.append(QPointF(0, 0))
r3poly.append(QPointF(0.75 * baseWidth, 0.5 * baseWidth))
r3poly.append(QPointF(0, baseWidth))
ppR3.addPolygon(r3poly)


class PathHelix(QGraphicsItem):
    """
    PathHelix is the primary "view" of the VirtualHelix data.
    It manages the ui interactions from the user, such as
    dragging breakpoints or crossovers addition/removal,
    and updates the data model accordingly.

    parent should be set to...
    """
    minorGridPen = QPen(styles.minorgridstroke, 1)
    majorGridPen = QPen(styles.majorgridstroke, 2)
    scafPen = QPen(styles.scafstroke, 2)
    nobrush = QBrush(Qt.NoBrush)
    baseWidth = styles.PATH_BASE_WIDTH

    def __init__(self, vhelix, pathHelixGroup):
        super(PathHelix, self).__init__()
        self.setAcceptHoverEvents(True)  # for pathtools
        self._pathHelixGroup = pathHelixGroup
        self._scafBreakpointHandles = []
        self._stapBreakpointHandles = []
        self._scafXoverHandles = []
        self._stapXoverHandles = []
        self._scaffoldLines = None
        self._minorGridPainterPath = None
        self._majorGridPainterPath = None
        self.step = 21  # 32 for Square lattice
        self.setZValue(styles.ZPATHHELIX)
        self.rect = QRectF()
        self._vhelix = None
        self._handle = None
        self._mouseDownBase = None
        self._activeTool = None
        self.setVHelix(vhelix)
    # end def
    
    def activeTool(self):
        return self.controller().activeTool()
    
    def controller(self):
        return self._pathHelixGroup.controller()

    def vhelix(self):
        return self._vhelix
        
    def undoStack(self):
        return self.vhelix().undoStack()
        
    def setVHelix(self, newVH):
        if self._vhelix:
            self._vhelix.basesModified.disconnect(self.vhelixBasesModified)
            self._vhelix.vhelixDimensionsModified.disconnect(self.vhelixDimensionsModified)
        self._vhelix = newVH
        newVH.basesModified.connect(self.vhelixBasesModified)
        newVH.dimensionsModified.connect(self.vhelixDimensionsModified)
        self.vhelixDimensionsModified()
        self.vhelixBasesModified()
    
    def handle(self):
        if self._handle:
            return self._handle
        self._handle = PathHelixHandle(self.vhelix())
        return self._handle

    def number(self):
        return self._vhelix.number()

    def row(self):
        return self._vhelix.row()

    def col(self):
        return self._vhelix.col()

    def evenParity(self):
        return self._vhelix.evenParity()

    def vhelixDimensionsModified(self):
        """Sets rect width to reflect number of bases in vhelix. Sets
        rect height to the width of two bases (one for scaffold and
        one for staple)"""
        canvasSize = self._vhelix.part().numBases()
        self.prepareGeometryChange()
        self.rect.setWidth(self.baseWidth * canvasSize)
        self.rect.setHeight(2 * self.baseWidth)
        self._minorGridPainterPath = None
        self._majorGridPainterPath = None

    def boundingRect(self):
        return self.rect
    
    def hoverEnterEvent(self, event):
        activeTool = self.activeTool()
        if activeTool and hasattr(activeTool, pathHelixHoverEnter):
            self.activeTool().pathHelixHoverEnter(self, event)
        else:
            QGraphicsItem.hoverEnterEvent(self,event)
    
    def hoverLeaveEvent(self, event):
        if self.activeTool():
            self.activeTool().hoverLeave(self, event)
        else:
            QGraphicsItem.hoverLeaveEvent(self,event)
    
    def hoverMoveEvent(self, event):
        if self.activeTool():
            self.activeTool().hoverLeave(self, event)
        else:
            QGraphicsItem.hoverLeaveEvent(self,event)

    def mousePressEvent(self, event):
        """Activate this item as the current helix"""
        self._mouseDownBase = self.baseAtLocation(event.pos().x(), event.pos().y())
        if self.controller().toolUse == True:
            self.controller().toolPress(self,event)
        else:
            if self._mouseDownBase:
                self.vhelix().setSandboxed(True)
                self.painterToolApply(self._mouseDownBase, self._mouseDownBase)
        self.updateAsActiveHelix(self._mouseDownBase[1])
        # QGraphicsItem.mousePressEvent(self,event)
    
    def mouseMoveEvent(self, event):
        if self.controller().toolUse == True:
            return
        newBase = self.baseAtLocation(event.pos().x(), event.pos().y())
        if self._mouseDownBase and newBase:
            self.vhelix().undoStack().undo()
            self.painterToolApply(self._mouseDownBase, newBase)
    
    def mouseReleaseEvent(self, event):
        if self.controller().toolUse == True:
            return
        if self._mouseDownBase:
            self.vhelix().setSandboxed(False)
    
    def painterToolApply(self, fr, to):
        """PainterTool is the default tool that lets one
        create scaffold and staple by dragging starting on
        an empty or endpoint base or destroy scaffold/staple
        by dragging from a connected base. from and to take the
        format of (strandType, base)"""
        vh = self.vhelix()
        fr = vh.validatedBase(*fr, raiseOnErr=False)
        to = vh.validatedBase(*to,   raiseOnErr=False)
        if (None, None) in (fr, to):
            return False
        useClearMode = self.vhelix().hasStrandAt(*fr)
        if useClearMode:
            self.vhelix().clearStrand(fr[0], fr[1], to[1])
        else:
            self.vhelix().connectStrand(fr[0], fr[1], to[1])        

    def hidePreXoverHandles(self):
        pass
    # end def

    def addXoverHandle(self, xh, strandType):
        """addXoverHandle gets called by PathHelixGroup
        when the handles are changed (e.g. by sliceHelixClickedSlot
        or when a crossover is added)."""
        if strandType == StrandType.Scaffold:
            self._scafXoverHandles.append(xh)
        elif strandType == StrandType.StrandType:
            self._stapXoverHandles.append(xh)
        else:
            raise AttributeError("strandType not recognized.")
    # end def

    def removeXoverHandle(self, xh, strandType):
        """addXoverHandle gets called by PathHelixGroup
        when the handles are changed (e.g. by sliceHelixClickedSlot
        or when a crossover is added)."""
        if strandType == StrandType.Scaffold:
            self._scafXoverHandles.remove(xh)
        elif strandType == StrandType.StrandType:
            self._stapXoverHandles.remove(xh)
        else:
            raise AttributeError("strandType not recognized.")
    # end def

    def updateAsActiveHelix(self, index):
        if self._pathHelixGroup.activeHelix != None:  # deactivate old
            self._pathHelixGroup.activeHelix.hidePreXoverHandles()
        # end if
        self._pathHelixGroup.activeHelix = self  # activate new
        self._vhelix.updatePreCrossoverPositions(index)
        self._pathHelixGroup.notifyPreCrossoverGroupAfterUpdate(self._vhelix)
        self.update(self.boundingRect())
    # end def

    ################################ Loading and Updating State From VHelix ##########################
    def vhelixBasesModified(self):
        self._endpoints = None  # Clear endpoint drawing cache
        self._scaffoldLines = None  # Clear drawing cache of lines
        self.update()

    ################################ Drawing ##########################
    def paint(self, painter, option, widget=None):
        # Note that the methods that fetch the paths
        # cache the paths and that those caches are
        # invalidated as the primary mechanism
        # of updating after a change in vhelix's bases
        painter.save()
        painter.setBrush(self.nobrush)
        painter.setPen(self.minorGridPen)
        painter.drawPath(self.minorGridPainterPath())  # Minor grid lines
        painter.setPen(self.majorGridPen)
        painter.drawPath(self.majorGridPainterPath())  # Major grid lines
        painter.setPen(self.scafPen)
        painter.drawLines(self.scaffoldLines())  # Blue scaffold lines
        painter.setBrush(styles.bluestroke)
        painter.setPen(Qt.NoPen)
        painter.drawPath(self.scaffoldEndpoints())  # Blue square, triangle endpoints
        painter.restore()

    def minorGridPainterPath(self):
        """
        Returns a QPainterPath object for the minor grid lines.
        The path also includes a border outline and a midline for
        dividing scaffold and staple bases.
        """
        if self._minorGridPainterPath:
            return self._minorGridPainterPath
        path = QPainterPath()
        canvasSize = self._vhelix.part().numBases()
        # border
        path.addRect(0, 0, self.baseWidth * canvasSize, 2 * self.baseWidth)
        # minor tick marks
        for i in range(canvasSize):
            if (i % 7 != 0):
                x = round(self.baseWidth*i) + .5
                path.moveTo(x, 0)
                path.lineTo(x, 2 * self.baseWidth)
        # staple-scaffold divider
        path.moveTo(0, self.baseWidth)
        path.lineTo(self.baseWidth * canvasSize, self.baseWidth)
        self._minorGridPainterPath = path
        return path

    def majorGridPainterPath(self):
        """
        Returns a QPainterPath object for the major grid lines.
        This is separated from the minor grid lines so different
        pens can be used for each.
        """
        if self._majorGridPainterPath:
            return self._majorGridPainterPath
        path = QPainterPath()
        canvasSize = self._vhelix.part().numBases()
        # major tick marks
        for i in range(0, canvasSize + 1, 7):
            x = round(self.baseWidth*i) + .5
            path.moveTo(x, .5)
            path.lineTo(x, 2 * self.baseWidth - .5)
        self._majorGridPainterPath = path
        return path
    
    def scaffoldLines(self):
        """Returns an array of lines that display the connected segments of the
        scaffold and staple strands @todo factor out staple."""
        if self._scaffoldLines:
            return self._scaffoldLines
        self._scaffoldLines = []
        for strandType in (StrandType.Scaffold, StrandType.Staple):
            for [startIndex, endIndex] in self._vhelix.getSegments(strandType):
                fr = self.baseLocation(strandType, startIndex, center=True)
                to = self.baseLocation(strandType, endIndex, center=True)
                self._scaffoldLines.append(QLine(QPoint(*fr),QPoint(*to)))
        return self._scaffoldLines
    
    def scaffoldEndpoints(self):
        """Return a QPainterPath ready to paint the endpoints of the scaffold"""
        if self._endpoints:
            return self._endpoints
        e = QPainterPath()
        for strandType in (StrandType.Scaffold, StrandType.Staple):
            top = self.strandIsTop(strandType)
            for (startIndex, endIndex) in self._vhelix.getSegments(strandType):
                startLoc = self.baseLocation(strandType, startIndex)
                e.addPath(ppL5.translated(*startLoc) if top else ppL3.translated(*startLoc))
                endLoc = self.baseLocation(strandType, endIndex)
                e.addPath(ppR3.translated(*endLoc) if top else ppR5.translated(*endLoc))
        self._endpoints = e
        return e

    def strandIsTop(self, strandType):
        return self.evenParity() and strandType==StrandType.Scaffold\
           or not self.evenParity() and strandType == StrandType.Staple
    
    def baseAtLocation(self, x, y):
        """Returns the (strandType, index) under the location x,y or None."""
        baseIdx = int(floor(x/self.baseWidth))
        if baseIdx < 0 or baseIdx >= self.vhelix().numBases():
            return None
        strandIdx = floor(y*1./self.baseWidth)
        if strandIdx < 0 or strandIdx > 1: return None
        if self.strandIsTop(StrandType.Scaffold):
            strands = StrandType.Scaffold, StrandType.Staple
        else:
            strands = StrandType.Staple, StrandType.Scaffold
        return (strands[int(strandIdx)], baseIdx)
    
    def baseLocation(self, strandType, baseIdx, center=False):
        """Returns the coordinates of the upper left corner of the base
        referenced by strandType and baseIdx. If center=True, returns the
        center of the base instead of the upper left corner."""
        if self.strandIsTop(strandType):
            y = 0
        else:
            y = self.baseWidth
        x = baseIdx*self.baseWidth
        if center:
            y += self.baseWidth/2
            x += self.baseWidth/2
        return (x,y)
# end class
# but wait, there's more! Now, for an encore of Events
# which can be more easily installed with less code duplication
# in a dynamic way

################################ Events ################################     
forwardedEvents = ('hoverEnter', 'hoverLeave', 'hoverMove', 'mousePress', 'mouseMove', 'mouseRelease')
for evName in forwardedEvents:
    def templateEvent(self, event):
        
    
