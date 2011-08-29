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
    def __init__(self, ph, xover3strand):
        QGraphicsPathItem.__init__(self, ph)
        self.xover3strand = xover3strand
        self.setPen(QPen(Qt.NoPen))
    def updatePos(self):
        strand = self.xover3strand
        vb = strand.vBase()
        self.setPos(self.ph.pointForVBase(vb))
        # We can only expose a 5' end. But on which side?
        self.setPath(ppL5 if vb.drawn5To3() else ppR5)
        self.setBrush(QBrush(strand.color()))
        self.updateConnectivity()
    def updateConnectivity(self):
        self.setVisible(self.xover3strand.conn5() != None)
    def strandWillBeRemoved(self, strand):
        self.scene().removeItem(self)

class XoverItem5(QGraphicsPathItem):
    def __init__(self, ph, xover5strand):
        QGraphicsPathItem.__init__(self, ph)
        self.xover5strand = xover5strand
        self.setPen(QPen(Qt.NoPen))
    def updatePos(self):
        strand = self.xover5strand
        vb = strand.vBase()
        self.setPos(self.ph.pointForVBase(vb))
        # We can only expose a 3' end. But on which side?
        self.setPath(ppR35 if vb.drawn5To3() else ppL3)
        self.setBrush(QBrush(strand.color()))
        self.updateConnectivity()
    def updateConnectivity(self):
        self.setVisible(self.xover5strand.conn3() != None)
    def strandWillBeRemoved(self, strand):
        self.scene().removeItem(self)

class XoverItem(QGraphicsPathItem):
    """
    This class lets us draw crossovers as a child below pathhelixgroup
    """
    _baseWidth = styles.PATH_BASE_WIDTH

    _xScale = styles.PATH_XOVER_LINE_SCALE_X  # control point x constant
    _yScale = styles.PATH_XOVER_LINE_SCALE_Y  # control point y constant
    
    _rect = QRectF(0, 0, _baseWidth, _baseWidth)
    _toHelixNumFont = styles.XOVER_LABEL_FONT
    fm = QFontMetrics(_toHelixNumFont)
    _labelBrush = QBrush(Qt.SolidPattern)

    def __init__(self, phg, strandItem):
        """
        strandItem is a the model representation of the xover strand
        """
        QGraphicsPathItem.__init__(self, phg)
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
        strand5 = strand3.conn3()
        oldStrand3 = self._strand
        if oldStrand3 != None:
            oldStrand5 = oldStrand3.conn3()
            oldStrand3.didMove.disconnect(self.strandDidMove)
            oldStrand5.didMove.disconnect(self.strandDidMove)
            oldStrand3.connectivityChanged.disconnect(self.conn3Changed)
            oldStrand5.connectivityChanged.disconnect(self.conn5Changed)
            oldStrand3.willBeRemoved.disconnect(self.strandWillBeRemoved)
        self._strand = strand3
        strand3.didMove.connect(self.strandDidMove)
        strand5.didMove.connect(self.strandDidMove)
        strand3.connectivityChanged.connect(self.conn3Changed)
        strand5.connectivityChanged.connect(self.conn5Changed)
        strand3.willBeRemoved.connect(self.strandWillBeRemoved)
        self.strandDidMove()

    def conn3Changed(self):
        pass

    def conn5Changed(self):
        pass

    def strandWillBeRemoved(self):
        self.scene().removeItem(self)

    def strandDidMove(self):
        self.updatePath()
        self.updatePen()

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
        ms = self.strand()
        bw = self._baseWidth
        phg = self._pathhelixgroup
        vBase3 = self._strand.vBase()
        vBase5 = self._strand.conn3().vBase()
        pt3 = phg.pointForVBase(self._strand.vBase())
        if vBase5 == None:
            pt5 = self._strand.pt5()
            isFloating = True
        else:
            pt5 = phg.pointForVBase(vBase5)
            isFloating = False
        
        # Null source / dest => don't paint ourselves => no painterpath
        if pt3 == None\
           or pt5 == None:
            return None

        # print "regenerating path"
        # begin calculations of how to draw labels and crossover orientations

        from5To3 = ms.vStrand().drawn5To3()
        if from5To3:
            orient3 = HandleOrient.LeftUp
            labelPos3 = QPointF(pt3.x() - 0.75*bw,\
                                    pt3.y() - 1.5*bw)
            threeExitPt = pt3 + QPointF(0, 0.5) # the point leaving the pathhelix
        else:
            orient3 = HandleOrient.RightDown
            labelPos3 = QPointF(pt3.x() - 0.25*bw,\
                                pt3.y() + 0.5*bw)
            threeExitPt = pt3 + QPointF(0, -0.5) # the point leaving the pathhelix
        toIs5To3 = vBase5.drawn5To3() if vBase5 != None else from5To3
        if toIs5To3:
            orient5 = HandleOrient.RightUp
            labelPos5 = QPointF(pt5.x() - 0.25*bw, \
                                pt5.y() - 1.5*bw)
            fiveEnterPt = pt5 + QPointF(bw/2.0, 0) # the point entering the pathhelix
        else:
            orient5 = HandleOrient.LeftDown
            labelPos5 = QPointF(pt5.x() - 0.75*bw, \
                                pt5.y() + 0.5*bw)
            fiveEnterPt = pt5 + QPointF(bw/2.0, bw) # the point entering the pathhelix

        threeInsetPt = pt3 # the centerpoint

        if isFloating == True:
            fiveEnterPt = pt5
            fiveInsetPt = fiveEnterPt
        else: #self._toPt == None
            fiveInsetPt = pt5 # this is the center point
            
        # Determine control point of quad curve
        c1 = QPointF()
        if isFloating == True:
            sameStrand = False
            sameParity = False
        else:
            sameStrand = pt3.y() == pt5.y()
            sameParity = vBase5.evenParity() == vBase3.evenParity()
        # case 1: same strand
        if sameStrand:
            dx = abs(fiveEnterPt.x() - threeExitPt.x())
            c1.setX(0.5 * (threeExitPt.x() + fiveEnterPt.x()))
            if orient3 in [HandleOrient.LeftUp, HandleOrient.RightUp]:
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
            if orient3 == HandleOrient.LeftUp:
                c1.setX(threeExitPt.x() - self._xScale *\
                        abs(fiveEnterPt.y() - threeExitPt.y()))
            else:
                c1.setX(threeExitPt.x() + self._xScale *\
                        abs(fiveEnterPt.y() - threeExitPt.y()))
            c1.setY(0.5 * (threeExitPt.y() + fiveEnterPt.y()))

        # Construct painter path
        painterpath = QPainterPath()
        painterpath.moveTo(threeInsetPt)
        painterpath.lineTo(threeExitPt)
        painterpath.quadTo(c1, fiveEnterPt)
        painterpath.lineTo(fiveInsetPt)
        
        # draw labels
        if not isFloating:
            painterpath.addText(labelPos3, self._toHelixNumFont, ("%d" % (vBase5.vHelix().number())))
            painterpath.addText(labelPos5, self._toHelixNumFont, ("%d" % (vBase3.vHelix().number())))
        self.setPath(painterpath)

    def updatePen(self):
        ms = self.strand()
        color = ms.color()
        pen = QPen(color)
        #pen.setWidth(styles.PATH_STRAND_STROKE_WIDTH)
        pen.setCapStyle(Qt.SquareCap)
        if ms.vStrand().isStap():
            if ms.shouldHighlight():
                pen.setWidth(styles.PATH_STRAND_HIGHLIGHT_STROKE_WIDTH)
                color.setAlpha(128)
        self.setPen(pen)
# end class XOverItem