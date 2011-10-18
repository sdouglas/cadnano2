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
import sys
from abstractpathtool import AbstractPathTool


import util
util.qtWrapImport('QtCore', globals(), [])
util.qtWrapImport('QtGui', globals(), [])


class PencilTool(AbstractPathTool):
    """
    docstring for PencilTool
    """
    def __init__(self, controller):
        super(PencilTool, self).__init__(controller)
        self._tempXover = ForcedXoverItem(None, None)
        self._isFloatingXoverBegin = True

    def __repr__(self):
        return "pencilTool"  # first letter should be lowercase
        
    def floatingXover(self):
        return self._tempXover
    # end def 

    def isFloatingXoverBegin(self):
        return self._isFloatingXoverBegin
    # end def

    def setFloatingXoverBegin(self, boolval):
        self._isFloatingXoverBegin = boolval
        if boolval:
            self._tempXover.hideIt()
        else:
            self._tempXover.showIt()
    # end def
# end class

from exceptions import AttributeError, NotImplementedError
import time
from views import styles

import util, time

# import Qt stuff into the module namespace with PySide, PyQt4 independence
util.qtWrapImport('QtCore', globals(), ['QPointF', 'QRectF', 'Qt', 'QEvent'])
util.qtWrapImport('QtGui', globals(), ['QBrush', 'QFont', 'QGraphicsItem',\
                                'QGraphicsSimpleTextItem', 'QPen',\
                                'QPolygonF', 'QPainterPath', 'QGraphicsRectItem', \
                                'QColor', 'QFontMetrics', 'QGraphicsPathItem'])

_baseWidth = styles.PATH_BASE_WIDTH
_toHelixNumFont = styles.XOVER_LABEL_FONT
# precalculate the height of a number font.  Assumes a fixed font
# and that only numbers will be used for labels
_fm = QFontMetrics(_toHelixNumFont)
_enabbrush = QBrush(Qt.SolidPattern)  # Also for the helix number label
_nobrush = QBrush(Qt.NoBrush)
# _rect = QRectF(0, 0, baseWidth, baseWidth)
_xScale = styles.PATH_XOVER_LINE_SCALE_X  # control point x constant
_yScale = styles.PATH_XOVER_LINE_SCALE_Y  # control point y constant
_rect = QRectF(0, 0, _baseWidth, _baseWidth)

class ForcedXoverNode3(QGraphicsRectItem):
    """
    This is a QGraphicsRectItem to allow actions and also a 
    QGraphicsSimpleTextItem to allow a label to be drawn
    """
    def __init__(self, virtualHelixItem, xoverItem, strand3p, idx):
        super(ForcedXoverNode3, self).__init__(virtualHelixItem)
        self._vhi = virtualHelixItem
        self._xoverItem = xoverItem
        self._idx = idx
        self._isOnTop = virtualHelixItem.isStrandOnTop(strand3p)
        self._isDrawn5to3 = strand3p.strandSet().isDrawn5to3()
        self._strandType = strand3p.strandSet().strandType()

        self._partnerVirtualHelix = virtualHelixItem

        self.setPen(QPen(Qt.NoPen))
        self._label = None
        self.setPen(QPen(Qt.NoPen))
        self.setBrush(_nobrush)
        self.setRect(_rect)
    # end def

    def updateForFloatFromVHI(self, virtualHelixItem, strandType, idxX, idxY):
        """

        """
        self._vhi = virtualHelixItem
        self.setParentItem(virtualHelixItem)
        self._strandType = strandType
        self._idx = idxX
        self._isOnTop = self._isDrawn5to3 = True if idxY == 0 else False
        self.updatePositionAndAppearance()
    # end def

    def updateForFloatFromStrand(self, virtualHelixItem, strand3p, idx):
        """

        """
        self._vhi = virtualHelixItem
        self.setParentItem(virtualHelixItem)
        self._idx = idx
        self._isOnTop = virtualHelixItem.isStrandOnTop(strand3p)
        self._isDrawn5to3 = strand3p.strandSet().isDrawn5to3()
        self._strandType = strand3p.strandSet().strandType()
        self.updatePositionAndAppearance()
    # end def

    def strandType(self):
        return self._strandType
    # end def

    def refreshXover(self):
        self._xoverItem.refreshXover()
    # end def

    def setPartnerVirtualHelix(self, virtualHelixItem):
        self._partnerVirtualHelix = virtualHelixItem
    # end def

    def idx(self):
        return self._idx
    # end def

    def virtualHelixItem(self):
        return self._vhi
    # end def

    def point(self):
        return self._vhi.upperLeftCornerOfBaseType(self._idx, self._strandType)
    # end def

    def floatPoint(self):
        pt = self.pos()
        return pt.x(), pt.y()
    # end def

    def isOnTop(self):
        return self._isOnTop
    # end def

    def isDrawn5to3(self):
        return self._isDrawn5to3
    # end def

    def updatePositionAndAppearance(self):
        """
        Sets position by asking the VirtualHelixItem
        Sets appearance by choosing among pre-defined painterpaths (from
        normalstrandgraphicsitem) depending on drawing direction.
        """
        self.setPos(*self.point())
        # We can only expose a 5' end. But on which side?
        isLeft = True if self._isDrawn5to3 else False
        self.updateLabel(isLeft)
    # end def

    def updateConnectivity(self):
        isLeft = True if self._isDrawn5to3 else False
        self.updateLabel(isLeft)
    # end def

    def remove(self):
        """
        Clean up this joint
        """
        scene = self.scene()
        scene.removeItem(self._label)
        self._label = None
        scene.removeItem(self)
    # end def

    def updateLabel(self, isLeft):
        """
        Called by updatePositionAndAppearance during init, or later by
        updateConnectivity. Updates drawing and position of the label.
        """
        lbl = self._label
        if self._idx != None:
            if lbl == None:
                bw = _baseWidth
                num = self._partnerVirtualHelix.number()
                tBR = _fm.tightBoundingRect(str(num))
                halfLabelH = tBR.height()/2.0
                halfLabelW = tBR.width()/2.0
                # determine x and y positions
                labelX = bw/2.0 - halfLabelW
                if self._isOnTop:
                    labelY = -0.25*halfLabelH - 0.5 - 0.5*bw
                else:
                    labelY = 2*halfLabelH + 0.5 + 0.5*bw
                # adjust x for left vs right
                labelXoffset = 0.25*bw if isLeft else -0.25*bw
                labelX += labelXoffset
                # adjust x for numeral 1
                if num == 1: labelX -= halfLabelW/2.0
                # create text item
                lbl = QGraphicsSimpleTextItem(str(num), self)
                lbl.setPos(labelX, labelY)
                lbl.setBrush(_enabbrush)
                lbl.setFont(_toHelixNumFont)
                self._label = lbl
            # end if
            # print "setting label"
            lbl.setText( str(self._partnerVirtualHelix.number()) )
            lbl.show()
        # end if
    # end def

    def hideLabel(self):
        if self._label:
            self._label.hide()
    # end def

# end class


class ForcedXoverNode5(ForcedXoverNode3):
    """
    XoverNode5 is the partner of XoverNode3. It dif
    XoverNode3 handles:
    1. Drawing of the 5' end of an xover, and its text label. Drawing style
    is determined by the location of the xover with in a vhelix (is it a top
    or bottom vstrand?).
    2. Notifying XoverStrands in the model when connectivity changes.

    """
    def __init__(self, virtualHelixItem, xoverItem, strand5p, idx):
        super(ForcedXoverNode5, self).__init__(virtualHelixItem, xoverItem, strand5p, idx)
    # end def

    def updatePositionAndAppearance(self):
        """Same as XoverItem3, but exposes 3' end"""
        self.setPos(*self.point())
        # # We can only expose a 3' end. But on which side?
        isLeft = False if self._isDrawn5to3 else True
        self.updateLabel(isLeft)
    # end def
# end class

class ForcedXoverItem(QGraphicsPathItem):
    """
    This class handles:
    1. Drawing the spline between the XoverNode3 and XoverNode5 graphics
    items in the path view.

    XoverItem should be a child of a PartItem.
    """

    def __init__(self, partItem, virtualHelixItem):
        """
        strandItem is a the model representation of the 5prime most strand
        of a Xover
        """
        super(ForcedXoverItem, self).__init__(partItem)
        self._virtualHelixItem = virtualHelixItem
        self._strand5p = None
        self._node5 = None
        self._node3 = None
        self.hide()
    # end def

    ### SLOTS ###

    ### METHODS ###
    def remove(self):
        scene = self.scene()
        if self._node3:
            scene.removeItem(self._node3)
            scene.removeItem(self._node5)
        scene.removeItem(self)
    # end def

    def hideIt(self):
        self.hide()
        if self._node3:
            self._node3.hide()
            self._node5.hide()
    # end def

    def showIt(self):
        self.show()
        if self._node3:
            self._node3.show()
            self._node5.show()
    # end def

    def refreshXover(self):
        if self._strand5p:
            self.update(self._strand5p)
    # end def

    def updateBase(self, virtualHelixItem, strand5p, idx):
        # floating Xover!
        self._virtualHelixItem = virtualHelixItem
        if self._node5 == None:
            self._node5 = ForcedXoverNode5(virtualHelixItem, self, strand5p, idx)
            self._node3 = ForcedXoverNode3(virtualHelixItem, self, strand5p, idx)
        self._node5.updateForFloatFromStrand(virtualHelixItem, strand5p, idx)
    # end def

    def updateFloatingFromVHI(self, virtualHelixItem, strandType, idxX, idxY):
        # floating Xover!
        self._node5.setPartnerVirtualHelix(virtualHelixItem)
        self._node5.updatePositionAndAppearance()
        self._node3.setPartnerVirtualHelix(self._virtualHelixItem)
        self._node3.updateForFloatFromVHI(virtualHelixItem, strandType, idxX, idxY)
        self.updateFloatPath()
    # end def

    def updateFloatingFromStrandItem(self, virtualHelixItem, strand3p, idx):
        # floating Xover!
        self._node3.updateForFloatFromStrand(virtualHelixItem, strand3p, idx)
        self.updateFloatPath()
    # end def

    def updateFloatingFromPartItem(self, partItem, pt):
        self._node3.hideLabel()
        self.updateFloatPath(pt)
    # end def

    def updateFloatPath(self, point=None):
        """
        Draws a quad curve from the edge of the fromBase
        to the top or bottom of the toBase (q5), and
        finally to the center of the toBase (toBaseEndpoint).

        If floatPos!=None, this is a floatingXover and floatPos is the
        destination point (where the mouse is) while toHelix, toIndex
        are potentially None and represent the base at floatPos.

        """
        # print "updating xover curve", self.parentObject()
        node3 = self._node3
        node5 = self._node5

        bw = _baseWidth

        vhi5 = self._virtualHelixItem
        partItem = vhi5.partItem()
        pt5 = vhi5.mapToItem(partItem, *node5.floatPoint())

        fiveIsTop = node5.isOnTop()
        fiveIs5to3 = node5.isDrawn5to3()

        vhi3 = node3.virtualHelixItem()

        if point:
            pt3 = point
        else: 
            pt3 = vhi3.mapToItem(partItem, *node3.point())

        threeIsTop = True
        threeIs5to3 = True
        sameStrand = False
        sameParity = False

        # Enter/exit are relative to the direction that the path travels
        # overall.
        fiveEnterPt = pt5 + QPointF(0 if fiveIs5to3 else 1, .5)*bw
        fiveCenterPt = pt5 + QPointF(.5, .5)*bw
        fiveExitPt = pt5 + QPointF(.5, 0 if fiveIsTop else 1)*bw

        threeEnterPt = threeCenterPt = threeEnterPt = pt3

        c1 = QPointF()
        # case 1: same strand
        if sameStrand:
            dx = abs(threeEnterPt.x() - fiveExitPt.x())
            c1.setX(0.5 * (fiveExitPt.x() + threeEnterPt.x()))
            if fiveIsTop:
                c1.setY(fiveExitPt.y() - _yScale * dx)
            else:
                c1.setY(fiveExitPt.y() + _yScale * dx)
            # case 2: same parity
        elif sameParity:
             dy = abs(threeEnterPt.y() - fiveExitPt.y())
             c1.setX(fiveExitPt.x() + _xScale * dy)
             c1.setY(0.5 * (fiveExitPt.y() + threeEnterPt.y()))
        # case 3: different parity
        else:
            if fiveIsTop and fiveIs5to3:
                c1.setX(fiveExitPt.x() - _xScale *\
                        abs(threeEnterPt.y() - fiveExitPt.y()))
            else:
                c1.setX(fiveExitPt.x() + _xScale *\
                        abs(threeEnterPt.y() - fiveExitPt.y()))
            c1.setY(0.5 * (fiveExitPt.y() + threeEnterPt.y()))

        # Construct painter path
        painterpath = QPainterPath()
        painterpath.moveTo(fiveCenterPt)
        painterpath.lineTo(fiveExitPt)
        painterpath.quadTo(c1, threeEnterPt)
        painterpath.lineTo(threeCenterPt)

        self.setPath(painterpath)
        self._updateFloatPen()
    # end def

    def _updatePen(self, strand5p):
        oligo = strand5p.oligo()
        color = QColor(oligo.color())
        penWidth = styles.PATH_STRAND_STROKE_WIDTH
        if oligo.shouldHighlight():
            penWidth = styles.PATH_STRAND_HIGHLIGHT_STROKE_WIDTH
            color.setAlpha(128)
        pen = QPen(color, penWidth)
        pen.setCapStyle(Qt.FlatCap)
        self.setPen(pen)
    # end def

    def _updateFloatPen(self):
        color = styles.redstroke
        penWidth = styles.PATH_STRAND_STROKE_WIDTH
        pen = QPen(color, penWidth)
        pen.setCapStyle(Qt.FlatCap)
        self.setPen(pen)
    # end def
# end class XoverItem