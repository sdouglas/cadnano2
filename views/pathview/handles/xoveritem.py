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
crossoverhandle.py
Created by Nick on 2011-05-25.
"""
from exceptions import AttributeError, NotImplementedError
from model.enum import HandleOrient, StrandType
from views import styles
from views.pathview.normalstrandgraphicsitem import ppL5, ppR5, ppL3, ppR3
import util, time
# import Qt stuff into the module namespace with PySide, PyQt4 independence
util.qtWrapImport('QtCore', globals(), ['QPointF', 'QRectF', 'Qt', 'QEvent'])
util.qtWrapImport('QtGui', globals(), ['QBrush', 'QFont', 'QGraphicsItem',\
                                'QGraphicsSimpleTextItem', 'QPen',\
                                'QPolygonF', 'QPainterPath', \
                                'QColor', 'QFontMetrics', 'QGraphicsPathItem'])

FromSide = "FromSide"
ToSide = "ToSide"

class XoverItem3(QGraphicsPathItem):
    """
    XoverItem3 handles:
    1. Drawing of the 3' end of an xover, and its text label. Drawing style
    is determined by the location of the xover with in a vhelix (is it a top
    or bottom vstrand?).
    2. Notifying XoverStrands in the model when connectivity changes.
    """
    baseWidth = styles.PATH_BASE_WIDTH
    toHelixNumFont = styles.XOVER_LABEL_FONT
    # precalculate the height of a number font.  Assumes a fixed font
    # and that only numbers will be used for labels
    fm = QFontMetrics(toHelixNumFont)
    enabbrush = QBrush(Qt.SolidPattern)  # Also for the helix number label
    nobrush = QBrush(Qt.NoBrush)
    # _rect = QRectF(0, 0, baseWidth, baseWidth)

    def __init__(self, ph, xover3strand):
        super(XoverItem3, self).__init__(ph)
        self.ph = ph
        self.strand = xover3strand
        self.setPen(QPen(Qt.NoPen))
        self._label = None
        self.updatePositionAndAppearance()
        xover3strand.willBeRemoved.connect(self.strandWillBeRemoved)
        xover3strand.connectivityChanged.connect(self.updateConnectivity)
        self.setPen(QPen(Qt.NoPen))
        self.setBrush(self.nobrush)
    # end def

    def undoStack(self):
        return self.ph.vhelix().undoStack()
    # end def

    def updatePositionAndAppearance(self):
        """
        Sets position by asking the PathHelix.
        Sets appearance by choosing among pre-defined painterpaths (from
        normalstrandgraphicsitem) depending on drawing direction.
        """
        strand = self.strand
        vb = strand.vBase()
        self.setPos(self.ph.pointForVBase(vb))
        # We can only expose a 5' end. But on which side?
        isLeft = True if vb.drawn5To3() else False
        self.setPath(ppL5 if isLeft else ppR5)
        self.updateLabel(strand.conn3(), isLeft)

    def updateConnectivity(self):
        strand = self.strand
        if strand.conn5() == None:
            self.setBrush(QBrush(strand.color()))
        else:
            self.setBrush(self.nobrush)
        isLeft = True if  strand.vBase().drawn5To3() else False
        self.updateLabel(strand.conn3(), isLeft)

    def strandWillBeRemoved(self, strand):
        """
        Handles crossover destruction:
        1. disconnect signals
        2. clean strands that were connected to the xover item
        Triggered by a vstrand clearStrand command, which was
        probably triggered by a select/pencil tool mouseReleasePathHelix
        event.
        """
        self.strand.willBeRemoved.disconnect(self.strandWillBeRemoved)
        self.strand.connectivityChanged.disconnect(self.updateConnectivity)
        scene = self.scene()
        scene.removeItem(self._label)
        self._label = None
        scene.removeItem(self)

    def updateLabel(self, partnerStrand, isLeft):
        """
        Called by updatePositionAndAppearance during init, or later by
        updateConnectivity. Updates drawing and position of the label.
        """
        xos = self.strand
        lbl = self._label
        if not xos.isFloating():
            if self._label == None:
                bw = self.baseWidth
                num = partnerStrand.vBase().vHelix().number()
                tBR = self.fm.tightBoundingRect(str(num))
                halfLabelH = tBR.height()/2.0
                halfLabelW = tBR.width()/2.0
                # determine x and y positions
                labelX = bw/2.0 - halfLabelW
                if self.onTopStrand():
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
                lbl.setBrush(self.enabbrush)
                lbl.setFont(self.toHelixNumFont)
                self._label = lbl
            # end if
            lbl.setText( str(partnerStrand.vBase().vHelix().number()))
        # end if
    # end def

    def onTopStrand(self):
        """Helper method for updateLabel"""
        vb = self.strand.vBase()
        vs = self.strand.vStrand()
        return vb.evenParity() and vs.isScaf() or \
                not vb.evenParity() and vs.isStap() 
    # end def
# end class


class XoverItem5(XoverItem3):
    """
    XoverItem5 is the partner of XoverItem3. It dif
    XoverItem3 handles:
    1. Drawing of the 5' end of an xover, and its text label. Drawing style
    is determined by the location of the xover with in a vhelix (is it a top
    or bottom vstrand?).
    2. Notifying XoverStrands in the model when connectivity changes.

    """
    def __init__(self, ph, xover5strand):
        super(XoverItem5, self).__init__(ph, xover5strand)
    # end def

    def updatePositionAndAppearance(self):
        """Same as XoverItem3, but exposes 3' end"""
        strand = self.strand
        vb = strand.vBase()
        self.setPos(self.ph.pointForVBase(vb))
        # We can only expose a 3' end. But on which side?
        isLeft = False if vb.drawn5To3() else True
        self.setPath(ppL3 if isLeft else ppR3)
        self.updateLabel(strand.conn5(), isLeft)

    def updateConnectivity(self):
        self.setVisible(not self.strand.isFloating())
        if self.strand.conn3() == None:
            self.setBrush(QBrush(self.strand.color()))
        else:
            self.setBrush(self.nobrush)
# end class

class XoverSpline(QGraphicsPathItem):
    """
    This class handles:
    1. Drawing the spline between the XoverItem3 and XoverItem5 graphics
    items in the path view.
    2. Connecting and disconnecting signals the XoverStrands in this xover.

    XoverSpline should be a child of PathHelixGroup.
    """
    _baseWidth = styles.PATH_BASE_WIDTH
    _xScale = styles.PATH_XOVER_LINE_SCALE_X  # control point x constant
    _yScale = styles.PATH_XOVER_LINE_SCALE_Y  # control point y constant
    _rect = QRectF(0, 0, _baseWidth, _baseWidth)

    def __init__(self, phg, strandItem):
        """
        strandItem is a the model representation of the xover strand
        """
        super(XoverSpline, self).__init__(phg)
        # self._clearState()
        self._pathhelixgroup = phg
        self._strand = None
        self.setStrand(strandItem)

    def phg(self):
        return self._pathhelixgroup

    def strand(self):
        return self._strand

    def setStrand(self, strand3):
        if self._strand == strand3:
            return
        self.disconnectSignals()
        self.connectSignals(strand3)
        self.strandDidMove()

    def connectSignals(self, strand3):
        self._strand = strand3
        strand5 = strand3.conn3()
        strand3.didMove.connect(self.strandDidMove)
        strand5.didMove.connect(self.strandDidMove)
        strand3.connectivityChanged.connect(self.conn3Changed)
        strand5.connectivityChanged.connect(self.conn5Changed)
        strand3.oligoChanged.connect(self.updatePen)
        strand3.willBeRemoved.connect(self.strandWillBeRemoved)
        phg = self._pathhelixgroup
        callback = self.updatePath
        ph3 = phg.pathHelixForVHelix(strand3.vBase().vHelix())
        self.ph3 = ph3
        if ph3 != None:
            ph3.xoverUpdate.connect(self.updatePath)
        # need to test for None for a Floating Xover
        vb = strand5.vBase()
        if vb != None:
            ph5 = phg.pathHelixForVHelix(vb.vHelix())
            self.ph5 = ph5
            if ph5 != None:
                ph5.xoverUpdate.connect(self.updatePath)
        else:
            self.ph5 = None
    # end def

    def disconnectSignals(self):
        strand3 = self._strand
        if strand3 != None:
            strand5 = strand3.conn3()
            strand3.didMove.disconnect(self.strandDidMove)
            strand5.didMove.disconnect(self.strandDidMove)
            strand3.connectivityChanged.disconnect(self.conn3Changed)
            strand5.connectivityChanged.disconnect(self.conn5Changed)
            strand3.willBeRemoved.disconnect(self.strandWillBeRemoved)
            phg = self._pathhelixgroup
            ph3 = phg.pathHelixForVHelix(strand3.vBase().vHelix())
            if self.ph3 != None:
                self.ph3.xoverUpdate.disconnect(self.updatePath)
                self.ph3 = None
            if self.ph5 != None:
                self.ph5.xoverUpdate.disconnect(self.updatePath)
                self.ph5 = None
    # end def

    def conn3Changed(self):
        self.updatePath()

    def conn5Changed(self):
        self.updatePath()

    def strandWillBeRemoved(self):
        self.disconnectSignals()
        self.scene().removeItem(self)

    def strandDidMove(self):
        self.updatePath()

    def updatePath(self):
        """
        Draws a quad curve from the edge of the fromBase
        to the top or bottom of the toBase (q5), and
        finally to the center of the toBase (toBaseEndpoint).

        If floatPos!=None, this is a floatingXover and floatPos is the
        destination point (where the mouse is) while toHelix, toIndex
        are potentially None and represent the base at floatPos.

        Why have toStrandtype? A PathHelix should display inconsistencies
        in the model, and a crossover from one strand type to another is
        an inconsistency that would be very nice to have a visual indication
        of (rather than having strange errors popping up down the line; the
        particular instance prompting this addition cost 4 hours of time)
        """
        # print "updating xover curve", self.parentObject()
        ms = self.strand()
        bw = self._baseWidth
        phg = self._pathhelixgroup
        vBase3 = self._strand.vBase()
        vBase5 = self._strand.conn3().vBase()
        ph3 = phg.pathHelixForVHelix(vBase3.vHelix())
        pt3 = ph3.mapToItem(phg, ph3.pointForVBase(vBase3))
        threeIsTop = ph3.vBaseIsTop(vBase3)
        threeIs5To3 = vBase3.drawn5To3()
        if vBase5 == None:
            pt5 = self._strand.pt5()
            ph5 = None
            fiveIsTop = True
            fiveIs5To3 = True
            isFloating = True
            sameStrand = False
            sameParity = False
        else:
            ph5 = phg.pathHelixForVHelix(vBase5.vHelix())
            pt5 = ph5.mapToItem(phg, ph5.pointForVBase(vBase5))
            fiveIsTop = ph5.vBaseIsTop(vBase5)
            fiveIs5To3 = vBase5.drawn5To3()
            isFloating = False
            sameStrand = vBase3.vStrand() == vBase5.vStrand()
            sameParity = fiveIs5To3 == threeIs5To3

        # Null source / dest => don't paint ourselves => no painterpath
        if pt3 == None or pt5 == None:
            self.hide()
            return None
        else:
            self.show()

        # Enter/exit are relative to the direction that the path travels
        # overall.
        threeEnterPt = pt3 + QPointF(0 if threeIs5To3 else 1, .5)*bw
        threeCenterPt = pt3 + QPointF(.5, .5)*bw
        threeExitPt = pt3 + QPointF(.5, 0 if threeIsTop else 1)*bw
        if isFloating:
            fiveEnterPt = fiveCenterPt = fiveEnterPt = pt5
        else:
            fiveEnterPt = pt5 + QPointF(.5, 0 if fiveIsTop else 1)*bw
            fiveCenterPt = pt5 + QPointF(.5, .5)*bw
            fiveExitPt = pt5 + QPointF(1 if fiveIs5To3 else 0, .5)*bw

        c1 = QPointF()
        # case 1: same strand
        if sameStrand:
            dx = abs(fiveEnterPt.x() - threeExitPt.x())
            c1.setX(0.5 * (threeExitPt.x() + fiveEnterPt.x()))
            if threeIsTop:
                c1.setY(threeExitPt.y() - self._yScale * dx)
            else:
                c1.setY(threeExitPt.y() + self._yScale * dx)
        # case 2: same parity
        elif sameParity:
            dy = abs(fiveEnterPt.y() - threeExitPt.y())
            c1.setX(threeExitPt.x() + self._xScale * dy)
            c1.setY(0.5 * (threeExitPt.y() + fiveEnterPt.y()))
        # case 3: different parity
        else:
            if threeIsTop and threeIs5To3:
                c1.setX(threeExitPt.x() - self._xScale *\
                        abs(fiveEnterPt.y() - threeExitPt.y()))
            else:
                c1.setX(threeExitPt.x() + self._xScale *\
                        abs(fiveEnterPt.y() - threeExitPt.y()))
            c1.setY(0.5 * (threeExitPt.y() + fiveEnterPt.y()))

        # Construct painter path
        painterpath = QPainterPath()
        if self._strand.conn5() != None:
            # The xover3's non-crossing-over end (5') has a connection
            painterpath.moveTo(threeEnterPt)
            painterpath.lineTo(threeCenterPt)
            painterpath.lineTo(threeExitPt)
        else:
            painterpath.moveTo(threeCenterPt)
            painterpath.lineTo(threeExitPt)
        if self._strand.conn3().conn3() != None:
            # The xover5's non-crossing-over end (3') has a connection
            painterpath.quadTo(c1, fiveEnterPt)
            painterpath.lineTo(fiveCenterPt)
            painterpath.lineTo(fiveExitPt)
        else:
            painterpath.quadTo(c1, fiveEnterPt)
            painterpath.lineTo(fiveCenterPt)
        self.setPath(painterpath)
        self.updatePen()

    def updatePen(self):
        strand = self.strand()
        color = QColor(strand.color())
        penWidth = styles.PATH_STRAND_STROKE_WIDTH
        if strand.shouldHighlight():
            penWidth = styles.PATH_STRAND_HIGHLIGHT_STROKE_WIDTH
            color.setAlpha(128)
        pen = QPen(color, penWidth)
        pen.setCapStyle(Qt.FlatCap)
        self.setPen(pen)
# end class XOverItem
