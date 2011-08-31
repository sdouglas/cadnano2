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

import util
util.qtWrapImport('QtGui', globals(), [ 'QBrush', 'QGraphicsLineItem', 'QPen',\
                                        'QColor', 'QPainterPath', 'QPolygonF',\
                                        'QGraphicsPathItem'])
util.qtWrapImport('QtCore', globals(), [ 'QPointF', 'Qt' ])
from views import styles

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
NoPen = QPen(Qt.NoPen)

class NormalStrandGraphicsItem(QGraphicsLineItem):
    def __init__(self, normalStrand, pathHelix):
        QGraphicsLineItem.__init__(self, pathHelix)
        self.normalStrand = normalStrand
        self.pathHelix = pathHelix
        normalStrand.didMove.connect(self.update)
        normalStrand.apparentConnectivityChanged.connect(self.update)
        normalStrand.willBeRemoved.connect(self.remove)
        drawn5To3 = normalStrand.drawn5To3()
        self.leftCap = QGraphicsPathItem(ppL5 if drawn5To3 else ppL3, self)
        self.leftCap.setPen(NoPen)
        self.rightCap = QGraphicsPathItem(ppR3 if drawn5To3 else ppR5, self)
        self.rightCap.setPen(NoPen)
        self.update(normalStrand)

    def update(self, strand):
        ph = self.pathHelix
        halfBaseWidth = ph.baseWidth / 2.0
        vbL, vbR = strand.vBaseL, strand.vBaseR
        lUpperLeftX, lUpperLeftY = ph.upperLeftCornerOfVBase(vbL)
        rUpperLeftX, rUpperLeftY = ph.upperLeftCornerOfVBase(vbR)
        if strand.apparentlyConnectedL():
            lx = lUpperLeftX
            self.leftCap.hide()
        else:
            lx = lUpperLeftX + halfBaseWidth
            self.leftCap.setPos(lUpperLeftX, lUpperLeftY)
            self.leftCap.show()
        ly = lUpperLeftY + halfBaseWidth
        if strand.apparentlyConnectedR():
            rx = rUpperLeftX + ph.baseWidth
            self.rightCap.hide()
        else:
            rx = rUpperLeftX + halfBaseWidth
            self.rightCap.setPos(rUpperLeftX, rUpperLeftY)
            self.rightCap.show()
        ry = ly
        self.setLine(lx, ly, rx, ry)
        if vbL.vStrand().isScaf():
            pen = QPen(styles.scafstroke, styles.PATH_STRAND_STROKE_WIDTH)
            brush = QBrush(styles.handlefill)
        else:
            pen = QPen(QColor(), styles.PATH_STRAND_STROKE_WIDTH)
            brush = QBrush(self.normalStrand.color())
        pen.setCapStyle(Qt.FlatCap)
        self.setPen(pen)
        self.leftCap.setBrush(brush)
        self.rightCap.setBrush(brush)

    def remove(self, strand):
        ns = self.normalStrand
        ns.didMove.disconnect(self.update)
        ns.apparentConnectivityChanged.disconnect(self.update)
        ns.willBeRemoved.disconnect(self.remove)
        scene = self.scene()
        scene.removeItem(self.rightCap)
        self.scene().removeItem(self.leftCap)
        self.rightCap = None
        self.leftCap = None
        scene.removeItem(self)