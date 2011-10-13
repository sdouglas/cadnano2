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
xoveritem.py
Created by Nick on 2011-05-25.
"""
from exceptions import AttributeError, NotImplementedError
from model.enum import HandleOrient, StrandType
from views import styles

from controllers.itemcontrollers.strand.xoveritemcontroller import XoverItemController

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

class XoverNode3(QGraphicsRectItem):
    """
    This is a QGraphicsRectItem to allow actions and also a 
    QGraphicsSimpleTextItem to allow a label to be drawn
    """
    def __init__(self, virtualHelixItem, strand3p, idx):
        super(XoverNode3, self).__init__(virtualHelixItem)
        self._vhi = virtualHelixItem
        self._strand = strand3p
        self._idx = idx
        self._isOnTop = virtualHelixItem.isStrandOnTop(strand3p)
        self._isDrawn5to3 = strand3p.strandSet().isDrawn5to3()

        self.setPen(QPen(Qt.NoPen))
        self._label = None
        self.updatePositionAndAppearance()
        self.setPen(QPen(Qt.NoPen))
        self.setBrush(_nobrush)
        self.setRect(_rect)
    # end def

    def strand(self):
        return self._strand
    # end def
    
    def strandType(self):
        return self._strand.strandSet().strandType()
    # end def
    
    def idx(self):
        return self._idx
    # end def
    
    def virtualHelixItem(self):
        return self._vhi
    # end def
    
    def point(self):
        return self._vhi.upperLeftCornerOfBase(self._idx, self._strand)
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
        strand = self._strand
        self.setPos(*self.point())
        # We can only expose a 5' end. But on which side?
        isLeft = True if self._isDrawn5to3 else False
        # self.setPath(ppL5 if isLeft else ppR5)
        self.updateLabel(strand.connection3p(), isLeft)
    # end def

    def updateConnectivity(self):
        strand = self._strand
        if strand.connection5p() == None:
            self.setBrush(QBrush(strand.oligo().color()))
        else:
            self.setBrush(_nobrush)
        isLeft = True if self._isDrawn5to3 else False
        self.updateLabel(strand.connection3p(), isLeft)
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

    def updateLabel(self, partnerStrand, isLeft):
        """
        Called by updatePositionAndAppearance during init, or later by
        updateConnectivity. Updates drawing and position of the label.
        """
        xos = self._strand
        lbl = self._label
        if self._idx != None:
            if lbl == None:
                bw = _baseWidth
                num = partnerStrand.virtualHelix().number()
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
            lbl.setText( str(partnerStrand.virtualHelix().number()) )
        # end if
    # end def

# end class


class XoverNode5(XoverNode3):
    """
    XoverNode5 is the partner of XoverNode3. It dif
    XoverNode3 handles:
    1. Drawing of the 5' end of an xover, and its text label. Drawing style
    is determined by the location of the xover with in a vhelix (is it a top
    or bottom vstrand?).
    2. Notifying XoverStrands in the model when connectivity changes.

    """
    def __init__(self, virtualHelixItem, strand5p, idx):
        super(XoverNode5, self).__init__(virtualHelixItem, strand5p, idx)
    # end def

    def updatePositionAndAppearance(self):
        """Same as XoverItem3, but exposes 3' end"""
        strand = self._strand
        self.setPos(*self.point())
        # We can only expose a 3' end. But on which side?
        isLeft = False if self._isDrawn5to3 else True
        # self.setPath(ppL3 if isLeft else ppR3)
        self.updateLabel(strand.connection5p(), isLeft)
    # end def

    def updateConnectivity(self):
        strand = self._strand
        self.setVisible(not strand.isFloating())
        if strand.connection3p() == None:
            self.setBrush(QBrush(strand.oligo().color()))
        else:
            self.setBrush(_nobrush)
    # end def
# end class

class XoverItem(QGraphicsPathItem):
    """
    This class handles:
    1. Drawing the spline between the XoverNode3 and XoverNode5 graphics
    items in the path view.

    XoverItem should be a child of a PartItem.
    """

    def __init__(self, partItem, strand3p, strand5p):
        """
        strandItem is a the model representation of the xover strand
        """
        super(XoverItem, self).__init__(partItem)
        self._partItem = partItem
        # wire it up to the 3 prime strand, wire it to the 5 prime strand
        vhi3p = partItem.itemForVirtualHelix(strand3p.virtualHelix())
        vhi5p = partItem.itemForVirtualHelix(strand5p.virtualHelix())
        self._node3 = XoverNode3(vhi3p, strand3p, strand3p.idx3Prime())
        self._node5 = XoverNode5(vhi5p, strand5p, strand5p.idx5Prime())
        # to allow killing an xoveritem on deletion of a strand
        self._controller = XoverItemController(self, strand3p)
        self._updatePath()
    # end def

    ### SLOTS ###
    def oligoAppearanceChangedSlot(self, oligo):
        self._updatePen()
    # end def

    def strandHasNewOligoSlot(self, strand):
        self._controller.reconnectOligoSignals()
    # end def

    def strandRemovedSlot(self, strand):
        pass
    # end def
    def strandDestroyedSlot(self, strand):
        pass
    # end def
    def strandDecoratorAddedSlot(self, strand):
        pass
    # end def

    def xover5pRemovedSlot(self):
        self._controller.disconnectSignals()
        self._controller = None
        scene = self.scene()
        scene.removeItem(self._node3)
        scene.removeItem(self._node5)
        self._partItem.removeXoverItem(self)
        scene.removeItem(self)
    # end def

    ### METHODS ###

    def part(self):
        return self._partItem.part()
        
    def oligo(self):
        return self._node3.strand().oligo()

    def virtualHelixItems(self):
        """
        return a tuple of the associated virtualHelixItems
        """
        return self._node3.virtualHelixItem(), self._node5.virtualHelixItem()
    # end def
    
    def indicesAndStrandTypes(self):
        """
        return a tuple of the associated virtualHelixItems
        indices and StrandTypes
        """
        node3 = self._node3
        node5 = self._node5
        iAST3p = node3.idx(), node3.strandType()
        iAST5p = node5.idx(), node5.strandType()
        return iAST3p, iAST5p
    # end def

    def _updatePath(self):
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
        
        strand3p = node3.strand()
        bw = _baseWidth
        part = self.part()
        partItem = self._partItem
        
        vhi3 = node3.virtualHelixItem()
        pt3 = vhi3.mapToItem(partItem, *node3.point())
                            
        threeIsTop = node3.isOnTop()
        threeIs5to3 = node3.isDrawn5to3()
        
        if node5.idx() == None: # is it a floating Xover?
            pt5 = strand.pt5()  # NEED TO UPDATE THIS FLOATING POINT
            vhi5 = None
            fiveIsTop = True
            fiveIs5to3 = True
            isFloating = True
            sameStrand = False
            sameParity = False
        else:
            strand5p = node5.strand()
            vhi5 = node5.virtualHelixItem()
            pt5 = vhi5.mapToItem(partItem, *node5.point())

            fiveIsTop = node5.isOnTop()
            fiveIs5to3 = node5.isDrawn5to3()
            isFloating = False
            sameStrand = node3.strand() == node5.strand()
            sameParity = fiveIs5to3 == threeIs5to3

        # Null source / dest => don't paint ourselves => no painterpath
        if pt3 == None or pt5 == None:
            self.hide()
            return None
        else:
            self.show()

        # Enter/exit are relative to the direction that the path travels
        # overall.
        threeEnterPt = pt3 + QPointF(0 if threeIs5to3 else 1, .5)*bw
        threeCenterPt = pt3 + QPointF(.5, .5)*bw
        threeExitPt = pt3 + QPointF(.5, 0 if threeIsTop else 1)*bw
        if isFloating:
            fiveEnterPt = fiveCenterPt = fiveEnterPt = pt5
        else:
            fiveEnterPt = pt5 + QPointF(.5, 0 if fiveIsTop else 1)*bw
            fiveCenterPt = pt5 + QPointF(.5, .5)*bw
            fiveExitPt = pt5 + QPointF(1 if fiveIs5to3 else 0, .5)*bw

        c1 = QPointF()
        # case 1: same strand
        if sameStrand:
            dx = abs(fiveEnterPt.x() - threeExitPt.x())
            c1.setX(0.5 * (threeExitPt.x() + fiveEnterPt.x()))
            if threeIsTop:
                c1.setY(threeExitPt.y() - _yScale * dx)
            else:
                c1.setY(threeExitPt.y() + _yScale * dx)
        # case 2: same parity
        elif sameParity:
            dy = abs(fiveEnterPt.y() - threeExitPt.y())
            c1.setX(threeExitPt.x() + _xScale * dy)
            c1.setY(0.5 * (threeExitPt.y() + fiveEnterPt.y()))
        # case 3: different parity
        else:
            if threeIsTop and threeIs5to3:
                c1.setX(threeExitPt.x() - _xScale *\
                        abs(fiveEnterPt.y() - threeExitPt.y()))
            else:
                c1.setX(threeExitPt.x() + _xScale *\
                        abs(fiveEnterPt.y() - threeExitPt.y()))
            c1.setY(0.5 * (threeExitPt.y() + fiveEnterPt.y()))

        # Construct painter path
        painterpath = QPainterPath()
        if strand3p.connection5p() != None:
            # The xover3's non-crossing-over end (5') has a connection
            painterpath.moveTo(threeEnterPt)
            painterpath.lineTo(threeCenterPt)
            painterpath.lineTo(threeExitPt)
        else:
            painterpath.moveTo(threeCenterPt)
            painterpath.lineTo(threeExitPt)
        if strand3p.connection3p().connection3p() != None:
            # The xover5's non-crossing-over end (3') has a connection
            painterpath.quadTo(c1, fiveEnterPt)
            painterpath.lineTo(fiveCenterPt)
            painterpath.lineTo(fiveExitPt)
        else:
            painterpath.quadTo(c1, fiveEnterPt)
            painterpath.lineTo(fiveCenterPt)
        self.setPath(painterpath)
        self._updatePen()
    # end def

    def _updatePen(self):
        oligo = self._node3.strand().oligo()
        color = QColor(oligo.color())
        penWidth = styles.PATH_STRAND_STROKE_WIDTH
        if oligo.shouldHighlight():
            penWidth = styles.PATH_STRAND_HIGHLIGHT_STROKE_WIDTH
            color.setAlpha(128)
        pen = QPen(color, penWidth)
        pen.setCapStyle(Qt.FlatCap)
        self.setPen(pen)
    # end def
# end class XoverItem