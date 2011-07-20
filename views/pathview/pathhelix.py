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
from views import styles
from model.enum import EndType, LatticeType, StrandType
from model.virtualhelix import VirtualHelix
from weakref import ref
from handles.pathhelixhandle import PathHelixHandle
from handles.loophandle import LoopItem, SkipItem
from handles.precrossoverhandle import PreCrossoverHandle
from math import floor, pi, ceil
from cadnano import app
from itertools import product
from ui.mainwindow.svgbutton import SVGButton

import util
# import Qt stuff into the module namespace with PySide, PyQt4 independence
util.qtWrapImport('QtCore', globals(), ['Qt', 'QRect', 'QLine', 'QRectF',\
                                        'QPointF', 'QPoint', 'pyqtSlot',\
                                        'QEvent', 'SLOT',  'pyqtSignal'])
util.qtWrapImport('QtGui', globals(), ['QBrush', 'QColor', 'QFont',\
                                       'QGraphicsObject', 'QFontMetricsF',\
                                       'QGraphicsSimpleTextItem',\
                                       'QPainter', 'QPainterPath', 'QPen',\
                                       'QDrag', 'QPolygonF', 'QUndoCommand',
                                       'QInputDialog', 'QGraphicsItem'])

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


class PathHelix(QGraphicsObject):
    """
    PathHelix is the primary "view" of the VirtualHelix data.
    It manages the ui interactions from the user, such as
    dragging breakpoints or crossovers addition/removal,
    and updates the data model accordingly.

    parent should be set to...
    """
    minorGridPen = QPen(styles.minorgridstroke, styles.MINOR_GRID_STROKE_WIDTH)
    minorGridPen.setCosmetic(True)
    majorGridPen = QPen(styles.majorgridstroke, styles.MAJOR_GRID_STROKE_WIDTH)
    majorGridPen.setCosmetic(True)

    scafPen = QPen(styles.scafstroke, 2)
    nobrush = QBrush(Qt.NoBrush)
    baseWidth = styles.PATH_BASE_WIDTH

    # The next block of code does setup necessary for
    # drawing the sequence text onto the PathView
    sequenceFont = QFont("Monaco")
    if hasattr(QFont, 'Monospace'):
        sequenceFont.setStyleHint(QFont.Monospace)
    sequenceFont.setFixedPitch(True)
    sequenceFontH = baseWidth / 3.
    sequenceFont.setPixelSize(sequenceFontH)
    sequenceFontMetrics = QFontMetricsF(sequenceFont)
    sequenceFontCharWidth = sequenceFontMetrics.width('A')
    sequerceFontCharHeight = sequenceFontMetrics.height()
    sequenceFontExtraWidth = baseWidth - sequenceFontCharWidth
    sequenceFont.setLetterSpacing(QFont.AbsoluteSpacing,
                                  sequenceFontExtraWidth)
    sequenceTextXCenteringOffset = sequenceFontExtraWidth / 2.
    sequenceTextYCenteringOffset = baseWidth / 2.

    # Items that calculate paths for loops and skips
    _skipitem = SkipItem()
    _loopitem = LoopItem()
    # Bases are drawn along and above the loop path.
    # These calculations revolve around fixing the
    # characters at a certain percentage of the total
    # arclength.
    # The fraction of the loop that comes before the
    # first character and after the last character is
    # the padding, and the rest is divided evenly.
    fractionLoopToPad = .10    

    def __init__(self, vhelix, pathHelixGroup):
        super(PathHelix, self).__init__()
        self.setAcceptHoverEvents(True)  # for pathtools
        self._pathHelixGroup = pathHelixGroup
        self._scafBreakpointHandles = []
        self._stapBreakpointHandles = []
        self._scafXoverHandles = []
        self._stapXoverHandles = []
        self._preXOverHandles = None
        self._XOverCacheEnvironment = None
        self._segmentPaths = None
        self._endptPaths = None
        self._minorGridPainterPath = None
        self._majorGridPainterPath = None
        self.step = vhelix.part().crossSectionStep()
        self.setZValue(styles.ZPATHHELIX)
        self.rect = QRectF()
        self._vhelix = None
        self._handle = None
        self._mouseDownBase = None
        self.addBasesButton = SVGButton(":/pathtools/add-bases", self)
        self.addBasesButton.clicked.connect(self.addBasesClicked)
        self.removeBasesButton = SVGButton(":/pathtools/remove-bases", self)
        self.removeBasesButton.clicked.connect(self.removeBasesClicked)
        self.setVHelix(vhelix)
        self.setFlag(QGraphicsItem.ItemUsesExtendedStyleOption)
        self.setPreXOverHandlesVisible(False)
        if app().ph != None:  # Convenience for the command line -i mode
            app().ph[vhelix.number()] = self
    # end def

    def activeTool(self):
        return self.controller().activeTool()

    def controller(self):
        return self._pathHelixGroup.controller()

    def pathHelixGroup(self):
        return self._pathHelixGroup

    def vhelix(self):
        return self._vhelix

    def palette(self):
        return self._vhelix.palette()

    def phgroup(self):
        return self._pathHelixGroup
    # end def

    def undoStack(self):
        return self.vhelix().undoStack()

    def setVHelix(self, newVH):
        if self._vhelix:
            self._vhelix.basesModified.disconnect(self.vhelixBasesModified)
            self._vhelix.vhelixDimensionsModified.disconnect(\
                                             self.vhelixDimensionsModified)
        self._vhelix = newVH
        newVH.basesModified.connect(self.vhelixBasesModified)
        newVH.dimensionsModified.connect(self.vhelixDimensionsModified)
        self.vhelixDimensionsModified()
        self.vhelixBasesModified()

    def handle(self):
        if self._handle:
            return self._handle
        self._handle = PathHelixHandle(self.vhelix(),\
                                       parent=self._pathHelixGroup)
        return self._handle

    def number(self):
        return self._vhelix.number()

    def row(self):
        return self._vhelix.row()

    def col(self):
        return self._vhelix.col()

    def evenParity(self):
        return self._vhelix.evenParity()
    
    def addBasesClicked(self):
        part = self.vhelix().part()
        dlg = QInputDialog(self.window())
        dlg.setInputMode(QInputDialog.IntInput)
        dlg.setIntMinimum(0)
        dlg.setIntValue(part.step)
        dlg.setIntMaximum(1000000)
        dlg.setIntStep(part.step)
        dlg.setLabelText(( "Number of bases to add to the existing"\
                         + " %i bases\n(must be a multiple of %i)")\
                         % (part.numBases(),part.step))
        dlg.intValueSelected.connect(self.userChoseToAddNBases)
        dlg.open()
        self.addBasesDialog = dlg  # Prevent GC from eating it
    
    @pyqtSlot(int)
    def userChoseToAddNBases(self, numBases):
        part = self.vhelix().part()
        dim = list(part.dimensions())
        numBases = int(numBases) / 21 * 21
        part.setDimensions((dim[0], dim[1], dim[2]+numBases))
        self.addBasesDialog.intValueSelected.disconnect(self.userChoseToAddNBases)
        del self.addBasesDialog

    def removeBasesClicked(self):
        part = self.vhelix().part()
        # First try to shrink to fit used bases
        newNumBases = part.indexOfRightmostNonemptyBase() + 1
        newNumBases = int(ceil(float(newNumBases)/part.step))*part.step
        newNumBases = util.clamp(newNumBases, part.step, 10000)
        
        dim = list(part.dimensions())
        # If that didn't do anything, reduce the length
        # of the vhelix by one step.
        if dim[2] == newNumBases and dim[2] > part.step:
            newNumBases = newNumBases - part.step
        part.setDimensions((dim[0], dim[1], newNumBases))

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
        addx = self.rect.width()
        addy = -(self.addBasesButton.boundingRect().height()*1.2)
        self.addBasesButton.setPos(addx, addy)
        self.addBasesButton.show()
        remx = self.rect.width()-self.removeBasesButton.boundingRect().width()
        remy = -(self.removeBasesButton.boundingRect().height()*1.2)
        bbr = self.removeBasesButton.boundingRect()
        self.removeBasesButton.setPos(remx, remy)
    
    # signal to update xover graphicsitems when pathelices move
    # this must happen AFTER the pathhelices move such that the positions
    # of Xover endpoints are valid/new before they get recalculated
    xoverUpdate = pyqtSignal()
    def positionInPhgChanged(self):
        if self._pathHelixGroup.topmostPathHelix() == self:
            self.addBasesButton.show()
            self.removeBasesButton.show()
        else:
            self.addBasesButton.hide()
            self.removeBasesButton.hide()
        self.xoverUpdate.emit()

    def boundingRect(self):
        return self.rect

    ################# Crossover Handles #################
    def preXOverHandlesVisible(self):
        return self._preXOverHandles != None

    def setPreXOverHandlesVisible(self, shouldBeVisible):
        areVisible = self._preXOverHandles != None
        if areVisible and not shouldBeVisible:
            for pch in self._preXOverHandles:
                if pch.scene():
                    pch.scene().removeItem(pch)
            self._preXOverHandles = None
            self.vhelix().part().virtualHelixAtCoordsChanged.disconnect(\
                                                   self.updatePreXOverHandles)
        elif not areVisible and shouldBeVisible:
            self._preXOverHandles = []
            for strandType, facingRight in\
              product((StrandType.Scaffold, StrandType.Staple), (True, False)):
                # Get potential crossovers in [neighborVirtualHelix, index] format
                potentialXOvers = self.vhelix().potentialCrossoverList(facingRight, strandType)
                numBases = self.vhelix().numBases()
                assert(all(index < numBases for neighborVH, index in potentialXOvers))
                for (neighborVH, fromIdx) in potentialXOvers:
                    pch = PreCrossoverHandle(self, strandType, fromIdx,\
                                             neighborVH, fromIdx,\
                                             not facingRight)
                    self._preXOverHandles.append(pch)
            self.vhelix().part().virtualHelixAtCoordsChanged.connect(self.updatePreXOverHandles)
        self._XOverCacheEnvironment = (self.vhelix().neighbors(), self.vhelix().numBases())

    def updatePreXOverHandles(self):
        cacheConstructionEnvironment = self._XOverCacheEnvironment
        currentEnvironment = (self.vhelix().neighbors(), self.vhelix().numBases())
        if cacheConstructionEnvironment != currentEnvironment:
            self.setPreXOverHandlesVisible(False)
            self.setPreXOverHandlesVisible(True)

    def makeSelfActiveHelix(self):
        self._pathHelixGroup.setActiveHelix(self)

    ################# Loading and Updating State From VHelix #################
    def vhelixBasesModified(self):
        self._endpoints = None  # Clear endpoint drawing cache
        self._segmentPaths = None  # Clear drawing cache of lines
        # Reset active helix if necessary
        if self.phgroup().getActiveHelix() == self:
            self.makeSelfActiveHelix()
        self.update()

    ############################# Drawing ##########################
    def paint(self, painter, option, widget=None):
        # Note that the methods that fetch the paths
        # cache the paths and that those caches are
        # invalidated as the primary mechanism
        # of updating after a change in vhelix's bases
        if not self.boundingRect().intersects(option.exposedRect):
            return
        painter.save()
        painter.setBrush(self.nobrush)
        painter.setPen(self.minorGridPen)
        painter.drawPath(self.minorGridPainterPath())  # Minor grid lines
        painter.setPen(self.majorGridPen)
        painter.drawPath(self.majorGridPainterPath())  # Major grid lines
        painter.setBrush(Qt.NoBrush)
        segmentPaths, endptPths = self.segmentAndEndptPaths()
        for sp in segmentPaths:
            pen, path = sp
            strandRect = path.controlPointRect().adjusted(0, 0, 5, 5)
            if not strandRect.intersects(option.exposedRect):
                continue
            painter.setPen(pen)
            painter.drawPath(path)
        painter.setPen(Qt.NoPen)
        for ep in endptPths:
            brush, path = ep
            if not path.controlPointRect().intersects(option.exposedRect):
                continue
            painter.setBrush(brush)
            painter.drawPath(path)
        self.paintLoopsAndSkips(painter)
        self.paintHorizontalBaseText(painter)
        painter.restore()

    def paintLoopsAndSkips(self, painter):
        vh = self.vhelix()
        for strandType in (StrandType.Scaffold, StrandType.Staple):
            istop = self.strandIsTop(strandType)
            for index, loopsize in vh.loop(strandType).iteritems():
                ul = self.baseLocation(strandType, index)
                if loopsize > 0:
                    path = self._loopitem.getLoop(istop)
                    path = path.translated(*ul)
                    # painter.setPen(self._loopitem.getPen())
                    painter.setPen(QPen(vh.colorOfBase(strandType, index), styles.LOOPWIDTH))
                    painter.setBrush(Qt.NoBrush)
                    painter.drawPath(path)
                    
                    # draw sequence on the loop
                    baseText = vh.sequenceForLoopAt(strandType, index)
                    if baseText[0] != ' ':  # only draw sequences if they exist
                        if istop:
                            angleOffset = 0
                        else:
                            angleOffset = 180
                        if len(baseText) > 20:
                            baseText = baseText[:17] + '...'
                        fractionArclenPerChar = (1.-2*self.fractionLoopToPad)/(len(baseText)+1)
                        painter.setPen(QPen(Qt.black))
                        painter.setBrush(Qt.NoBrush)
                        painter.setFont(self.sequenceFont)
                        for i in range(len(baseText)):
                            frac = self.fractionLoopToPad + (i+1)*fractionArclenPerChar
                            pt = path.pointAtPercent(frac)
                            tangAng = path.angleAtPercent(frac)
                            painter.save()
                            painter.translate(pt)
                            painter.rotate(-tangAng + angleOffset)
                            painter.translate(QPointF(-self.sequenceFontCharWidth/2.,
                                                      -2 if istop else self.sequenceFontH))
                            if not istop:
                                painter.translate(0, -self.sequenceFontH - styles.LOOPWIDTH)
                            painter.drawText(0, 0, baseText[i if istop else -i-1])
                            painter.restore()
                    # end if
                else:  # loopsize < 0 (a skip)
                    path = self._skipitem.getSkip()
                    path = path.translated(*ul)
                    painter.setPen(self._skipitem.getPen())
                    painter.drawPath(path)

    def paintHorizontalBaseText(self, painter):
        vh = self.vhelix()
        scafTxt = vh.sequenceForVirtualStrand(StrandType.Scaffold)
        scafY = self.baseWidth*0 + self.sequenceTextYCenteringOffset
        stapTxt = vh.sequenceForVirtualStrand(StrandType.Staple)
        stapY = self.baseWidth*1 + self.sequenceTextYCenteringOffset
        if self.strandIsTop(StrandType.Staple):
            # We assumed scaffold was on top. Correct that.
            scafY, stapY = stapY, scafY
        if vh.directionOfStrandIs5to3(StrandType.Scaffold):
            # Text goes from 5 to 3, so staple gets vertically flipped
            shouldVFlipScaf = False
            # We still want the text to be drawn at the same Y coordinate,
            # just upside down, so we undo the transform as it applies
            # to the Y coord
            stapY = -stapY
        else:
            shouldVFlipScaf = True
            scafY = -scafY
        scafX = stapX = self.sequenceTextXCenteringOffset
        painter.setPen(QPen(Qt.black))
        painter.setBrush(Qt.NoBrush)
        painter.setFont(self.sequenceFont)
        if shouldVFlipScaf:
            painter.rotate(180)
            painter.translate(-self.baseWidth*vh.numBases(), 0)
            # draw the text and reverse the string to draw 5 prime to 3 prime
            scafTxt = scafTxt[::-1]
        # end if
        else:
            # draw the text and reverse the string to draw 5 prime to 3 prime
            # pass
            stapTxt = stapTxt[::-1]
        # end else
        # print vh.numBases()
        painter.drawText(scafX, scafY, self.baseWidth*vh.numBases(),\
                         self.baseWidth/2., Qt.AlignVCenter, scafTxt)
        # flip to draw (or flip back)
        painter.rotate(180)
        painter.translate(-self.baseWidth*vh.numBases(), 0)
        # stapTxt = stapTxt.replace(' ', 'K')
        painter.drawText(stapX, stapY, self.baseWidth*vh.numBases(),\
                                self.baseWidth/2., Qt.AlignVCenter, stapTxt)

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
            if (i % self._vhelix.part().majorGrid() != 0):
                x = round(self.baseWidth * i) + .5
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
        # major tick marks  FIX: 7 is honeycomb-specific
        for i in range(0, canvasSize + 1, self._vhelix.part().majorGrid()):
            x = round(self.baseWidth * i) + .5
            path.moveTo(x, .5)
            path.lineTo(x, 2 * self.baseWidth - .5)
        self._majorGridPainterPath = path
        return path

    def segmentAndEndptPaths(self):
        """Returns an array of (pen, penPainterPath, brush, brushPainterPath)
        for drawing segment lines and handles."""
        if self._segmentPaths and self._endptPaths:
            return (self._segmentPaths, self._endptPaths)
        self._segmentPaths = []
        self._endptPaths = []
        vh = self.vhelix()
        for strandType in (StrandType.Scaffold, StrandType.Staple):
            top = self.strandIsTop(strandType)
            segments, ends3, ends5 = self._vhelix.getSegmentsAndEndpoints(strandType)
            # print "[%i:%s] "%(vh.number(), "scaf" if strandType==StrandType.Scaffold else "stap") + " ".join(str(b) for b in segments)
            for (startIndex, endIndex) in segments:
                numBasesInOligo = vh.numberOfBasesConnectedTo(strandType,\
                                                              int(startIndex))
                highlight = (numBasesInOligo > styles.oligoLenAboveWhichHighlight or\
                             numBasesInOligo < styles.oligoLenBelowWhichHighlight) and\
                             strandType == StrandType.Staple

                startPt = self.baseLocation(strandType, startIndex, centerY=True)
                endPt = self.baseLocation(strandType, endIndex, centerY=True)

                # Only draw to the edge of breakpoints.
                if self._vhelix.hasEndAt(strandType, startIndex):
                    startPt = (startPt[0]+styles.PATH_BASE_WIDTH/2, startPt[1])
                elif highlight and self._vhelix.hasCrossoverAt(strandType, startIndex):
                    # compensate for width of stroke in crossover path
                    startPt = (startPt[0]+styles.PATH_STRAND_HIGHLIGHT_STROKE_WIDTH/2, startPt[1])
                if self._vhelix.hasEndAt(strandType, endIndex):
                    endPt = (endPt[0]-styles.PATH_BASE_WIDTH/2, endPt[1])
                elif highlight and self._vhelix.hasCrossoverAt(strandType, endIndex):
                    endPt = (endPt[0]-styles.PATH_STRAND_HIGHLIGHT_STROKE_WIDTH/2, endPt[1])

                pp = QPainterPath()
                pp.moveTo(*startPt)
                pp.lineTo(*endPt)
                color = vh.colorOfBase(strandType, int(startIndex))
                width = styles.PATH_STRAND_STROKE_WIDTH
                if numBasesInOligo > styles.oligoLenAboveWhichHighlight or\
                   numBasesInOligo < styles.oligoLenBelowWhichHighlight:
                    if strandType == StrandType.Staple:
                        color.setAlpha(128)
                        width = styles.PATH_STRAND_HIGHLIGHT_STROKE_WIDTH
                else:
                    color.setAlpha(255)
                pen = QPen(color, width)
                pen.setCapStyle(Qt.FlatCap)
                self._segmentPaths.append((pen, pp))
            for e3 in ends3:
                upperLeft = self.baseLocation(strandType, e3)
                bp = QPainterPath()
                color = QColor(vh.colorOfBase(strandType, e3))
                color.setAlpha(255)
                brush = QBrush(color)
                bp.addPath(ppR3.translated(*upperLeft) if top else\
                                                    ppL3.translated(*upperLeft))
                self._endptPaths.append((brush, bp))
            for e5 in ends5:
                upperLeft = self.baseLocation(strandType, e5)
                bp = QPainterPath()
                color = QColor(vh.colorOfBase(strandType, e5))
                color.setAlpha(255)
                brush = QBrush(color)
                bp.addPath(ppL5.translated(*upperLeft) if top else\
                                                    ppR5.translated(*upperLeft))
                self._endptPaths.append((brush, bp))
        return (self._segmentPaths, self._endptPaths)

    def strandIsTop(self, strandType):
        return self.evenParity() and strandType == StrandType.Scaffold\
           or not self.evenParity() and strandType == StrandType.Staple

    def baseAtLocation(self, x, y, clampX=False, clampY=False):
        """Returns the (strandType, index) under the location x,y or None.
        
        It shouldn't be possible to click outside a pathhelix and still call
        this function. However, this sometimes happens if you click exactly
        on the top or bottom edge, resulting in a negative y value.
        """
        baseIdx = int(floor(x / self.baseWidth))
        minBase, maxBase = 0, self.vhelix().numBases()
        if baseIdx < minBase or baseIdx >= maxBase:
            if clampX:
                baseIdx = util.clamp(baseIdx, minBase, maxBase-1)
            else:
                return None
        if y < 0:
            y = 0  # HACK: zero out y due to erroneous click
        strandIdx = floor(y * 1. / self.baseWidth)
        if strandIdx < 0 or strandIdx > 1:
            if clampY:
                strandIdx = int(util.clamp(strandIdx, 0, 1))
            else:
                return None
        if self.strandIsTop(StrandType.Scaffold):
            strands = StrandType.Scaffold, StrandType.Staple
        else:
            strands = StrandType.Staple, StrandType.Scaffold
        return (strands[int(strandIdx)], baseIdx)

    def baseLocation(self, strandType, baseIdx, center=False, centerY=False):
        """Returns the coordinates of the upper left corner of the base
        referenced by strandType and baseIdx. If center=True, returns the
        center of the base instead of the upper left corner."""
        if self.strandIsTop(strandType):
            y = 0
        else:
            y = self.baseWidth
        x = baseIdx * self.baseWidth
        if center:
            x += self.baseWidth / 2
            y += self.baseWidth / 2
        if centerY:
            y += self.baseWidth / 2
        return (x, y)

    def sceneEvent(self, event):
        """Included for unit testing in order to grab events that are sent
        via QGraphicsScene.sendEvent()."""
        if self.controller().testRecorder:
            self.controller().testRecorder.pathSceneEvent(event, self.number())
        if event.type() == QEvent.MouseButtonPress:
            self.mousePressEvent(event)
            return True
        elif event.type() == QEvent.MouseButtonRelease:
            self.mouseReleaseEvent(event)
            return True
        elif event.type() == QEvent.MouseMove:
            self.mouseMoveEvent(event)
            return True
        QGraphicsObject.sceneEvent(self, event)
        return False


# end class
# but wait, there's more! Now, for Events
# which can be more easily installed with less code duplication
# in a dynamic way

################################ Events ################################
forwardedEvents = ('hoverEnter', 'hoverLeave', 'hoverMove', 'mousePress',\
                   'mouseMove', 'mouseRelease')
util.defineEventForwardingMethodsForClass(PathHelix, 'PathHelix', forwardedEvents)
# end class
