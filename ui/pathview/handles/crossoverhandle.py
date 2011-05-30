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
from PyQt4.QtCore import QPointF, QRectF, Qt
from PyQt4.QtGui import QBrush, QFont
from PyQt4.QtGui import QGraphicsItem, QGraphicsSimpleTextItem
from PyQt4.QtGui import QPainterPath
from PyQt4.QtGui import QPolygonF
from PyQt4.QtGui import QPen
from model.enum import HandleOrient, StrandType
import ui.styles as styles


class XoverHandle(object):
    """
    XoverHandlePair responds to mouse input and serves as an interface
    for adding scaffold crossovers.
    """
    _myfont = QFont("Times", 10, QFont.Bold)
    _myRect = QRectF(0, 0, styles.PATH_BASE_WIDTH, styles.PATH_BASE_WIDTH)
    _pen = QPen(styles.bluestroke, 2)  # FIX: use styles
    _pen.setCapStyle(Qt.RoundCap)
    _pen.setJoinStyle(Qt.RoundJoin)
    _baseWidth = styles.PATH_BASE_WIDTH
    xScale = styles.PATH_XOVER_LINE_SCALE_X  # control point x constant
    yScale = styles.PATH_XOVER_LINE_SCALE_Y  # control point y constant

    def __init__(self):
        """Create XoverHandlePair (parented to the PathHelixGroup)."""
        pass
    # end def

    def getXover(self, phg, strandtype, fromHelix,\
                       fromIndex, toHelix, toIndex):
        """
        Draws a line from the center of the fromBase (pA) to the
        top or bottom of that same base, depending on its direction (qA),
        then a quad curve to the top or bottom of the toBase (qB), and
        finally to the center of the toBase (pB).
        """
        # if we need to speed this up, we could keep track if pA changed?
        pA = QPointF(*fromHelix.baseLocation(strandtype,\
                                             fromIndex,\
                                             center=True))
        pA = phg.mapFromItem(fromHelix, pA)
        pB = QPointF(*toHelix.baseLocation(strandtype,\
                                           toIndex,\
                                           center=True))
        pB = phg.mapFromItem(toHelix, pB)
        yA = yB = self._baseWidth / 2
        if fromHelix.vhelix().directionOfStrandIs5to3(strandtype):
            orientA = HandleOrient.LeftUp
            yA = -yA
        else:
            orientA = HandleOrient.RightDown
        if toHelix.vhelix().directionOfStrandIs5to3(strandtype):
            orientB = HandleOrient.RightUp
            yB = -yB
        else:
            orientB = HandleOrient.LeftDown

        # Determine start and end points of quad curve
        qA = QPointF(pA.x(), pA.y() + yA)
        qB = QPointF(pB.x(), pB.y() + yB)

        # Determine control point of quad curve
        c1 = QPointF()
        # case 1: same strand
        if fromHelix.number() == toHelix.number():
            if pA.x() < pB.x():  # draw only from left
                if orientA == HandleOrient.LeftUp or \
                   orientA == HandleOrient.RightUp:
                    dx = abs(pB.x() - pA.x())
                    c1.setX(0.5 * (pA.x() + pB.x()))
                    c1.setY(pA.y() - self.yScale * dx)
                # end if
            # end if
        # case 2: same parity
        elif fromHelix.evenParity() == toHelix.evenParity():
            dy = abs(pB.y() - pA.y())
            c1.setX(pA.x() + self.xScale * dy)
            c1.setY(0.5 * (pA.y() + pB.y()))
        # case 3: default
        else:
            if orientA == HandleOrient.LeftUp:
                c1.setX(pA.x() - self.xScale * abs(pB.y() - pA.y()))
            else:
                c1.setX(pA.x() + self.xScale * abs(pB.y() - pA.y()))
            c1.setY(0.5 * (pA.y() + pB.y()))

        # Construct painter path
        painterpath = QPainterPath()
        painterpath.moveTo(pA)
        painterpath.lineTo(qA)
        painterpath.quadTo(c1, qB)
        painterpath.lineTo(pB)
        return painterpath
    # end def
# end class
