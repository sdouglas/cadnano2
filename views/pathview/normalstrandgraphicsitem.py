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

util.qtWrapImport('QtGui', globals(), [ 'QBrush', 'QGraphicsItem', 'QPen'])
from views import styles

class NormalStrandGraphicsItem(QGraphicsLineItem):
    def __init__(self, normalStrand, pathHelix):
        self.normalStrand = normalStrand
        self.pathHelix = pathHelix
        normalStrand.didMove.connect(self.update)
        normalStrand.apparentConnectivityChanged.connect(self.update)
        normalStrand.willBeRemoved.connect(self.remove)
        self.update()

    def update(self, strand):
        ph = self.pathHelix
        halfBaseWidth = ph.baseWidth / 2.0
        vbL, vbR = strand.vBaseL(), strand.vBaseR()
        lUpperLeftX, lUpperLeftY = ph.upperLeftCornerOfVBase(vbL)
        rUpperLeftX, rUpperLeftY = ph.upperLeftCornerOfVBase(vbR)
        if strand.apparentlyConnectedL():
            lx = lUpperLeftX
        else:
            lx = lUpperLeftX + halfBaseWidth
        ly = lUpperLeftY + halfBaseWidth
        if strand.apparentlyConnectedR():
            rx = rUpperLeftX + ph.baseWidth
        else:
            rx = rUpperLeftX + halfBaseWidth
        ry = ly
        self.setLine(lx, ly, rx, ry)
        if vbL.vStrand.isScaf():
            pen = QPen(styles.scafstroke, styles.PATH_STRAND_STROKE_WIDTH)
        else:
            pen = QPen(QColor(), styles.PATH_STRAND_STROKE_WIDTH)
        self.setPen(pen)

    def remove(self, strand):
        self.scene.removeItem(self)