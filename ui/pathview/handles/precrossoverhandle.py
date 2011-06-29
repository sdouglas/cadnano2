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
precrossoverhandle.py
Created by Nick on 2011-05-03.
"""

from exceptions import AttributeError, NotImplementedError
from model.enum import StrandType, Parity, BreakType, HandleOrient
import ui.styles as styles
from itertools import product

import util
# import Qt stuff into the module namespace with PySide, PyQt4 independence
util.qtWrapImport('QtCore', globals(), ['QPointF', 'QRectF', 'Qt'] )
util.qtWrapImport('QtGui', globals(), [ 'QBrush', 'QFont', 'QGraphicsItem', \
                                        'QGraphicsSimpleTextItem', \
                                        'QFontMetrics', 'QPainterPath', \
                                        'QPolygonF', \
                                        'QPen', 'QUndoCommand'] )

# construct paths for breakpoint handles
def hashMarkGen(path, p1, p2, p3):
    path.moveTo(p1)
    path.lineTo(p2)
    path.lineTo(p3)
# end

# create hash marks QPainterPaths only once
_ppRect = QRectF(0, 0, styles.PATH_BASE_WIDTH, styles.PATH_BASE_WIDTH)
_pathCenter = QPointF(styles.PATH_BASE_WIDTH / 2,\
                          styles.PATH_BASE_WIDTH / 2)
_pathUCenter = QPointF(styles.PATH_BASE_WIDTH / 2, 0)
_pathDCenter = QPointF(styles.PATH_BASE_WIDTH / 2, styles.PATH_BASE_WIDTH)
_ppathLU = QPainterPath()
hashMarkGen(_ppathLU, _ppRect.bottomLeft(), _pathDCenter, _pathCenter)
_ppathRU = QPainterPath()
hashMarkGen(_ppathRU, _ppRect.bottomRight(), _pathDCenter, _pathCenter)
_ppathRD = QPainterPath()
hashMarkGen(_ppathRD, _ppRect.topRight(), _pathUCenter, _pathCenter)
_ppathLD = QPainterPath()
hashMarkGen(_ppathLD, _ppRect.topLeft(), _pathUCenter, _pathCenter)

class PreCrossoverHandle(QGraphicsItem):
    scafpen = QPen(styles.pch_scaf_stroke, styles.PATH_STRAND_STROKE_WIDTH)
    scafpen.setCapStyle(Qt.FlatCap)  # or Qt.RoundCap
    scafpen.setJoinStyle(Qt.RoundJoin)
    stappen = QPen(styles.pch_stap_stroke, styles.PATH_STRAND_STROKE_WIDTH)
    stappen.setCapStyle(Qt.FlatCap)  # or Qt.RoundCap
    stappen.setJoinStyle(Qt.RoundJoin)
    disabpen = QPen(styles.pch_disab_stroke, styles.PATH_STRAND_STROKE_WIDTH)
    disabpen.setCapStyle(Qt.FlatCap)
    disabpen.setJoinStyle(Qt.RoundJoin)
    disabbrush = QBrush(styles.pch_disab_stroke)  # For the helix number label
    enabbrush = QBrush(Qt.SolidPattern)  # Also for the helix number label
    baseWidth = styles.PATH_BASE_WIDTH
    rect = QRectF(0, 0, styles.PATH_BASE_WIDTH, styles.PATH_BASE_WIDTH)
    toHelixNumFont = styles.XOVER_LABEL_FONT

    # precalculate the height of a number font.  Assumes a fixed font
    # and that only numbers will be used for labels
    fm = QFontMetrics(toHelixNumFont)
    
    def __init__(self, parentPH, fromStrand, fromIdx, toVH, toIdx, orientedLeft):
        super(PreCrossoverHandle, self).__init__(parentPH)
        self.fromVH = parentPH.vhelix()
        self.fromStrand = fromStrand
        self.fromIdx = fromIdx
        self.toVH = toVH
        self.toIdx = toIdx
        self.orientedLeft = orientedLeft

        self.fromVH.basesModified.connect(self.updateVisibilityAndEnabledness)
        self.toVH.basesModified.connect(self.updateVisibilityAndEnabledness)

        x = self.baseWidth * self.fromIdx
        y = (-1.25 if self.onTopStrand() else 2.25) * self.baseWidth
        self.setPos(x, y)
        halfLabelH = self.fm.tightBoundingRect(str(toVH.number())).height()/2
        #halfLabelW = self.fm.boundingRect(str(toVH.number())).width()/2
        labelX = 0
        
        if self.onTopStrand():
            labelY = -1.05*halfLabelH-.5
        else:
            labelY = 1.05*halfLabelH+.5
        self.labelRect = QRectF(labelX,\
                                labelY,\
                                self.baseWidth, self.baseWidth)
        self._isLabelVisible = False
        self.updateVisibilityAndEnabledness()
    # end def
        
    def drawLabel(self, painter):
        painter.setBrush(self.labelBrush)
        painter.setFont(self.toHelixNumFont)
        painter.drawText(self.labelRect, Qt.AlignCenter, str(self.toVH.number() ) )
    # end def
        
    def onTopStrand(self):
        return self.fromVH.evenParity() and self.fromStrand==StrandType.Scaffold or\
               not self.fromVH.evenParity() and self.fromStrand==StrandType.Staple

    def couldFormNewCrossover(self):
        return self.fromVH.possibleNewCrossoverAt(self.fromStrand, self.fromIdx, self.toVH, self.toIdx)

    def crossoverExists(self):
        return self.fromVH.hasCrossoverAt(self.fromStrand, self.fromIdx)

    def is3pEndOfCrossover(self):
        underlyingStrand5To3 = self.fromVH.directionOfStrandIs5to3(self.fromStrand)
        return self.orientedLeft == underlyingStrand5To3

    def updateVisibilityAndEnabledness(self):
        shouldBeVisible = not self.crossoverExists()
        self.setVisible(shouldBeVisible)
        self._isLabelVisible = True
        if self.couldFormNewCrossover():
            self.labelBrush = self.enabbrush
        else:
            self.labelBrush = self.disabbrush
        self.update()

    def paint(self, painter, option, widget=None):
        #Look Up Table
        pathLUT = (_ppathRD, _ppathRU, _ppathLD, _ppathLU)
        path = pathLUT[2*int(self.orientedLeft) + int(self.onTopStrand())]
        pen = self.disabpen
        if self.couldFormNewCrossover():
            if self.fromStrand == StrandType.Scaffold:
                pen = self.scafpen
            else:
                pen = self.stappen
        painter.setPen(pen)
        painter.drawPath(path)
        if self._isLabelVisible == True:
            self.drawLabel(painter)
        
    def boundingRect(self):
        return self.rect

    def mousePressEvent(self, event):
        if event.button() != Qt.LeftButton:
            return QGraphicsItem.mousePressEvent(self, event)
        if not self.couldFormNewCrossover():
            return
        # Determine upstream base
        fromHelix, toHelix = self.fromVH, self.toVH
        fromIdx, toIdx = self.fromIdx, self.toIdx
        endToTakeColorFrom = 3
        if not self.is3pEndOfCrossover():
            fromHelix, toHelix = toHelix, fromHelix
            fromIdx, toIdx = toIdx, fromIdx
            endToTakeColorFrom = 5
        # Create XoverHandlePair and store references
        fromHelix.installXoverFrom3To5(self.fromStrand, \
                fromIdx, toHelix, toIdx, endToTakeColorFrom=endToTakeColorFrom)
        fromHelix.palette().shuffle()
