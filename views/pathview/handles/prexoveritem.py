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
prexoveritem.py
Created by Nick on 2011-08-25.
"""

from exceptions import AttributeError, NotImplementedError
from model.enum import StrandType, Parity, BreakType, HandleOrient
from views import styles
from itertools import product
from controllers.forcetooloperation import ForceToolOperation

import util
# import Qt stuff into the module namespace with PySide, PyQt4 independence
util.qtWrapImport('QtCore', globals(), ['QPointF', 'QRectF', 'Qt'])
util.qtWrapImport('QtGui', globals(), [ 'QBrush', 'QFont', 'QGraphicsPathItem', \
                                        'QGraphicsSimpleTextItem', \
                                        'QFontMetrics', 'QPainterPath', \
                                        'QPolygonF', 'QGraphicsRectItem',\
                                        'QPen', 'QUndoCommand'])

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

class PreXoverItem(QGraphicsPathItem):
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
    rect = QRectF(0, 0, styles.PATH_BASE_WIDTH, 1.2*styles.PATH_BASE_WIDTH)
    toHelixNumFont = styles.XOVER_LABEL_FONT

    # precalculate the height of a number font.  Assumes a fixed font
    # and that only numbers will be used for labels
    fm = QFontMetrics(toHelixNumFont)

    def __init__(self, parentPH, fromVBase, toVBase, orientedLeft):
        super(PreXoverItem, self).__init__(parentPH)
        self.pathhelix = parentPH
        self.fromVBase = fromVBase
        self.toVBase = toVBase
        self.orientedLeft = orientedLeft

        bw = self.baseWidth
        callback = self.updateVisibilityAndEnabledness
        fromVBase.vStrand().indicesModifiedSignal.connect(callback)
        toVBase.vStrand().indicesModifiedSignal.connect(callback)

        x = bw * self.fromVBase.vIndex()
        y = (-1.25 if self.onTopStrand() else 2.25) * bw
        self.setPos(x, y)

        num = self.toVBase.vHelix().number()
        tBR = self.fm.tightBoundingRect(str(num))
        halfLabelH = tBR.height()/2.0
        halfLabelW = tBR.width()/2.0

        labelX = bw/2.0 - halfLabelW #
        if num == 1:  # adjust for the number one
            labelX -= halfLabelW/2.0

        if self.onTopStrand():
            labelY = -0.25*halfLabelH - .5
        else:
            labelY = 2*halfLabelH + .5
        self._isLabelVisible = False
        self._label = QGraphicsSimpleTextItem(self)
        self._label.setPos(labelX, labelY)
        self.updateVisibilityAndEnabledness()
        # create a bounding rect item to process click events
        # over a wide area
        br = self.boundRect = QGraphicsRectItem(self.rect, self)
        br.mousePressEvent = self.mousePress
        yoffset = 0.2*bw if self.onTopStrand() else -0.4*bw
        br.setPos(0, yoffset)
        br.setPen(QPen(Qt.NoPen))
    # end def

    def undoStack(self):
        return self.pathhelix.vhelix().undoStack()
    # end def

    def remove(self):
        scene = self.scene()
        callback = self.updateVisibilityAndEnabledness
        self.fromVBase.vStrand().indicesModifiedSignal.disconnect(callback)
        self.toVBase.vStrand().indicesModifiedSignal.disconnect(callback)
        scene.removeItem(self._label)
        self._label = None
        scene.removeItem(self)
    # end def

    def phg(self):
        return self.pathhelix.pathHelixGroup()

    def onTopStrand(self):
        vstrand = self.fromVBase.vStrand()
        evenPar = self.fromVBase.evenParity()
        return  evenPar and vstrand.isScaf() or \
               not evenPar and vstrand.isStap()

    def couldFormNewCrossover(self):
        fb = self.fromVBase
        return fb.vStrand().possibleNewCrossoverAt(fb, self.toVBase)

    def crossoverExists(self):
        fb = self.fromVBase
        return fb.vStrand().hasCrossoverAt(fb.vIndex())

    def is3pEndOfCrossover(self):
        underlyingStrand5To3 = self.fromVBase.vStrand().drawn5To3()
        return self.orientedLeft == underlyingStrand5To3

    def updateVisibilityAndEnabledness(self):
        shouldBeVisible = not self.crossoverExists()
        self.setVisible(shouldBeVisible)
        self._isLabelVisible = True
        if self.couldFormNewCrossover():
            self.labelBrush = self.enabbrush
        else:
            self.labelBrush = self.disabbrush
        self.painterPath()
        self.update()
    # end def

    def updateLabel(self):
        lbl = self._label
        lbl.setBrush(self.labelBrush)
        lbl.setFont(self.toHelixNumFont)
        lbl.setText( str(self.toVBase.vHelix().number() ) )
    # end def

    def painterPath(self):
        #Look Up Table
        pathLUT = (_ppathRD, _ppathRU, _ppathLD, _ppathLU)
        path = pathLUT[2*int(self.orientedLeft) + int(self.onTopStrand())]
        pen = self.disabpen
        if self.couldFormNewCrossover():
            if self.fromVBase.vStrand().isScaf():
                pen = self.scafpen
            else:
                pen = self.stappen
        self.setPen(pen)
        self.setPath(path)
        if self._isLabelVisible == True:
            self.updateLabel()

    def mousePress(self, event):
        if event.button() != Qt.LeftButton:
            return QGraphicsPathItem.mousePressEvent(self, event)
        if not self.couldFormNewCrossover():
            return
        # Determine upstream base
        fromVB, toVB = self.fromVBase, self.toVBase
        endToTakeColorFrom = 3
        if not self.is3pEndOfCrossover():
            fromVB, toVB = toVB, fromVB
            endToTakeColorFrom = 5
        # Create XoverHandlePair and store references
        fto = ForceToolOperation(fromVB, self.undoStack())
        fto.updateDestination(toVB)
        fto.end()
    # end def
