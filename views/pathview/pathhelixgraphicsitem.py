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
pathhelixgraphicsitem.py
Created by Nick on 2011-08-19.
"""

from exceptions import AttributeError, ValueError
from views import styles
from model.enum import EndType, LatticeType, StrandType
from model.virtualhelix import VirtualHelix
from weakref import ref
from handles.pathhelixhandle import PathHelixHandle
from handles.loopgraphicsitem import LoopGraphicsItem
# from handles.precrossoverhandle import PreCrossoverHandle
from handles.prexoveritem import PreXoverItem

from math import floor, pi, ceil
from cadnano import app
from itertools import product
from ui.mainwindow.svgbutton import SVGButton
from model.strands.vbase import VBase
from views.pathview.normalstrandgraphicsitem import NormalStrandGraphicsItem
from model.strands.xoverstrand import XOverStrand3, XOverStrand5
from views.pathview.handles.xoveritem import XoverItem, XoverItem3, XoverItem5
from model.strands.normalstrand import NormalStrand
from model.strands.loopstrand import LoopStrand

import util
# import Qt stuff into the module namespace with PySide, PyQt4 independence
util.qtWrapImport('QtCore', globals(), ['Qt', 'QRect', 'QLine', 'QRectF',\
                                        'QPointF', 'QPoint', 'pyqtSlot',\
                                        'QEvent', 'SLOT',  'pyqtSignal', 'QObject'])
util.qtWrapImport('QtGui', globals(), ['QBrush', 'QColor', 'QFont',\
                                       'QGraphicsObject', 'QFontMetricsF',\
                                       'QGraphicsSimpleTextItem',\
                                       'QPainter', 'QPainterPath', 'QPen',\
                                       'QDrag', 'QPolygonF', 'QUndoCommand',
                                       'QInputDialog', 'QGraphicsItem', 'QGraphicsPathItem'])

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

class PHObject(QObject):
    """
    A placeholder class to get the benefits of QObject 
    without needing multiple inheritance and also to still use 
    QGraphicsPathItem instead of QGraphicsObject so we don't need to define
    a slow paint() method in python.
    """
    xoverUpdate = pyqtSignal()
    def __init__(self):
        super(PHObject, self).__init__()
# end class

class PathHelix(QGraphicsPathItem):
    """
    PathHelix is the primary "view" of the VirtualHelix data.
    It manages the ui interactions from the user, such as
    dragging breakpoints or crossovers addition/removal,
    and updates the data model accordingly.

    parent should be set to...
    
    This class draws the minor grid.  The major grid is drawn by a subobject.
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


    def __init__(self, vhelix, pathHelixGroup):
        QGraphicsPathItem.__init__(self)
        self.setAcceptHoverEvents(True)  # for pathtools
        self._pathHelixGroup = pathHelixGroup
        
        # self.minorGrid = QGraphicsPathItem()
        self.signalObject = PHObject()
        self.xoverUpdate = self.signalObject.xoverUpdate
        self.majorGrid = QGraphicsPathItem(self)
        
        # reset cached paths
        self._minorGridPainterPath = None
        self._majorGridPainterPath = None
        
        self._scafXoverHandles = []
        self._stapXoverHandles = []

        self.step = vhelix.part().crossSectionStep()
        self.setZValue(styles.ZPATHHELIX)
        self._vhelix = None
        self._handle = None
        self._mouseDownBase = None
        self.addBasesButton = SVGButton(":/pathtools/add-bases", self)
        self.addBasesButton.clicked.connect(self.addBasesClicked)
        self.removeBasesButton = SVGButton(":/pathtools/remove-bases", self)
        self.removeBasesButton.clicked.connect(self.removeBasesClicked)
        self.setVHelix(vhelix)
        self.setFlag(QGraphicsItem.ItemUsesExtendedStyleOption)

        self.setCacheMode(QGraphicsItem.DeviceCoordinateCache)
        if app().ph != None:  # Convenience for the command line -i mode
            app().ph[vhelix.number()] = self
        self.refreshPath()
    # end def

    def remove(self):
        self.signalObject = None
        self.xoverUpdate = None
        self.scene().removeItem(self.majorGrid)
        self.majorGrid = None
        self.scene().removeItem(self)

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
        vh = self._vhelix
        if vh != None:
            vh.basesModifiedSignal.disconnect(self.vhelixBasesModified)
            vh.vhelixDimensionsModified.disconnect(\
                                             self.vhelixDimensionsModified)
            vh.scaf().didAddStrand.disconnect(self.strandAddedToVStrand)
            vh.stap().didAddStrand.disconnect(self.strandAddedToVStrand)
            scene = self.scene()
            for c in self.childItems:
                scene.removeItem(c)
        self._vhelix = newVH
        if newVH != None:
            newVH.basesModifiedSignal.connect(self.vhelixBasesModified)
            newVH.dimensionsModifiedSignal.connect(self.vhelixDimensionsModified)
            newVH.scaf().didAddStrand.connect(self.strandAddedToVStrand)
            newVH.stap().didAddStrand.connect(self.strandAddedToVStrand)
            for vstrand in (newVH.scaf(), newVH.stap()):
                for strand in vstrand:
                    self.strandAddedToVStrand(strand)
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

    def strandAddedToVStrand(self, strand):
        if isinstance(strand, NormalStrand):
            NormalStrandGraphicsItem(strand, self)
        elif isinstance(strand, XOverStrand3):
            XoverItem(self.pathHelixGroup(), strand)
            XoverItem3(self, strand)
        elif isinstance(strand, XOverStrand5):
            XoverItem5(self, strand)
        elif isinstance(strand, LoopStrand):
            LoopGraphicsItem(strand, self)
        else:
            raise NotImplementedError

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
        rect = self.boundingRect()
        addButton = self.addBasesButton
        rectAdd = addButton.boundingRect()
        remButton = self.removeBasesButton
        rectRemove = remButton.boundingRect()
        rect.setWidth(self.baseWidth * canvasSize)
        rect.setHeight(2 * self.baseWidth)
        
        # reset cached paths
        # self._minorGridPainterPath = None
        # self._majorGridPainterPath = None
        
        addx = rect.width()
        addy = -(rectAdd.height()*1.2)
        addButton.setPos(addx, addy)
        addButton.show()
        remx = addx-rectRemove.width()
        remy = -(rectRemove.height()*1.2)
        # bbr = self.removeBasesButton.boundingRect()
        remButton.setPos(remx, remy)
        self.refreshPath()
    
    # signal to update xover graphicsitems when pathelices move
    # this must happen AFTER the pathhelices move such that the positions
    # of Xover endpoints are valid/new before they get recalculated
    
    def positionInPhgChanged(self):
        if self._pathHelixGroup.topmostPathHelix() == self:
            self.addBasesButton.show()
            self.removeBasesButton.show()
        else:
            self.addBasesButton.hide()
            self.removeBasesButton.hide()
        # emit this signal to be picked up by XoverHandle at least
        self.xoverUpdate.emit()

    def vBaseAtPoint(self, pt, clampY=True):
        x, y = pt.x(), pt.y()
        if clampY:
            if y < 0:                   y = 0
            if y >= 2 * self.baseWidth: y = 2*self.baseWidth
        else:
            if y < 0:                   return None
            if y >= 2 * self.baseWidth: return None
        idx = int(x // self.baseWidth)
        isTop = y < self.baseWidth
        if self.evenParity():
            if isTop: return VBase(self.vhelix().scaf(), idx)
            else:     return VBase(self.vhelix().stap(), idx)
        else:
            if isTop: return VBase(self.vhelix().stap(), idx)
            else:     return VBase(self.vhelix().scaf(), idx)

    def pointForVBase(self, vBase):
        x = self.baseWidth * vBase.vIndex()
        y = self.baseWidth * int(not self.vBaseIsTop(vBase))
        return QPointF(x, y)

    def vBaseIsTop(self, vBase):
        vh = self.vhelix()
        scaf, stap = vh.scaf(), vh.stap()
        if vBase.vStrand() == scaf:
            return True if self.evenParity() else False
        elif vBase.vStrand() == stap:
            return False if self.evenParity() else True
        else:
            assert(False)  # vBase is not on this strand's vhelix!

    ################# Crossover Handles #################

    def isActiveHelix(self, ph):
        return self._pathHelixGroup.getActiveHelix() == ph

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
    # end def
        
    def refreshPath(self):
        # if self._painterPath == None:
        # if self.path().isEmpty() == True:
        self.painterPath()
    # end def
    
    def painterPath(self):
        majG = self.majorGrid
        minG = self #self.minorGrid
        minG.setBrush(self.nobrush)
        minG.setPen(self.minorGridPen)
        minG.setPath(self.minorGridPainterPath())  # Minor grid lines
        majG.setBrush(self.nobrush)
        majG.setPen(self.majorGridPen)
        majG.setPath(self.majorGridPainterPath())  # Major grid lines
    # end def

    def minorGridPainterPath(self):
        """
        Returns a QPainterPath object for the minor grid lines.
        The path also includes a border outline and a midline for
        dividing scaffold and staple bases.
        """
        # if self._minorGridPainterPath:
        #     return self._minorGridPainterPath
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
        # self._minorGridPainterPath = path
        return path

    def majorGridPainterPath(self):
        """
        Returns a QPainterPath object for the major grid lines.
        This is separated from the minor grid lines so different
        pens can be used for each.
        """
        # if self._majorGridPainterPath != None:
        #     return self._majorGridPainterPath
        path = QPainterPath()
        canvasSize = self._vhelix.part().numBases()
        # major tick marks  FIX: 7 is honeycomb-specific
        for i in range(0, canvasSize + 1, self._vhelix.part().majorGrid()):
            x = round(self.baseWidth * i) + .5
            path.moveTo(x, .5)
            path.lineTo(x, 2 * self.baseWidth - .5)
        # self._majorGridPainterPath = path
        return path

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

    def vBaseOnTop(self, vBase):
        strand = vBase.vStrand()
        return self.evenParity() and strand.isScaf() or\
               not self.evenParity() and strand.isStap()

    def upperLeftCornerOfVBase(self, vBase):
        x = vBase.vIndex() * self.baseWidth
        y = 0 if self.vBaseOnTop(vBase) else self.baseWidth
        return x, y

    def keyPanDeltaX(self):
        """How far a single press of the left or right arrow key should move
        the scene (in scene space)"""
        dx = self.vhelix().part().step * self.baseWidth
        return self.mapToScene(QRectF(0, 0, dx, 1)).boundingRect().width()

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
        QGraphicsPathItem.sceneEvent(self, event)
        return False


# end class
# but wait, there's more! Now, for Events
# which can be more easily installed with less code duplication
# in a dynamic way

################################ Events ################################
forwardedEvents = ('hoverEnter', 'hoverLeave', 'hoverMove', 'mousePress',\
                   'mouseMove', 'mouseRelease', 'keyPress')
util.defineEventForwardingMethodsForClass(PathHelix, 'PathHelix', forwardedEvents)
# end class
