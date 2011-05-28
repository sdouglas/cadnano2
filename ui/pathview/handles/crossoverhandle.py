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
    _pen = QPen(styles.bluestroke, 2)
    
    def _hashMarkGen(path, p1, p2, p3):
        path.moveTo(p1)
        path.lineTo(p2)
        path.lineTo(p3)
    # end

    # hash mark parameters
    _pathCenter = QPointF(0,0)
    _pathLeft = QPointF(-styles.PATH_BASE_WIDTH / 2, 0)
    _pathUp = QPointF(0, -styles.PATH_BASE_WIDTH / 2)
    _pathRight = QPointF(styles.PATH_BASE_WIDTH / 2, 0)
    _pathDown = QPointF(0, styles.PATH_BASE_WIDTH / 2)
    _ppathLU = QPainterPath()
    _hashMarkGen(_ppathLU, _pathLeft, _pathCenter, _pathUp)
    _ppathRU = QPainterPath()
    _hashMarkGen(_ppathRU, _pathRight, _pathCenter, _pathUp)
    _ppathRD = QPainterPath()
    _hashMarkGen(_ppathRD, _pathRight, _pathCenter, _pathDown)
    _ppathLD = QPainterPath()
    _hashMarkGen(_ppathLD, _pathLeft, _pathCenter, _pathDown)
    
    # Xover parameters
    _pen = QPen(styles.bluestroke, 2)
    _pen.setCapStyle(Qt.RoundCap)
    _pen.setJoinStyle(Qt.RoundJoin)
    baseWidth = styles.PATH_BASE_WIDTH
    xScale = styles.PATH_XOVER_LINE_SCALE_X  # control point x constant
    yScale = styles.PATH_XOVER_LINE_SCALE_Y  # control point y constant
    
    def __init__(self):
        """
        Create XoverHandlePair (parented to the PathHelixGroup)
        """
        pass
    # end def
    
    def getXover(self, phg, strandtype, fromHelix, fromIndex, toHelix, toIndex):
        # if we need to speed this up, we could keep track if pA changed?
 
        pA = QPointF(*fromHelix.baseLocation(strandtype, fromIndex, center=True))
        pA = phg.mapFromItem(fromHelix, pA)
        pB = QPointF(*toHelix.baseLocation(strandtype, toIndex, center=True))
        pB = phg.mapFromItem(toHelix, pB)
        c1 = QPointF()
        
        if fromHelix.vhelix().directionOfStrandIs5to3(strandtype):
            orientA = HandleOrient.LeftUp
            pathA = self._ppathLU
        else: 
            orientA = HandleOrient.RightDown
            pathA = self._ppathRD
        if toHelix.vhelix().directionOfStrandIs5to3(strandtype):
            orientB = HandleOrient.RightUp
            pathB = self._ppathRU
        else:
            orientB = HandleOrient.LeftDown
            pathB = self._ppathLD
            
        painterpath = pathA.translated(pA)
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
            if orientA == HandleOrient.LeftUp:# or \
                #orientA == HandleOrient.LeftDown:
                c1.setX(pA.x() - self.xScale * abs(pB.y() - pA.y()))
            else:
                c1.setX(pA.x() + self.xScale * abs(pB.y() - pA.y()))
            c1.setY(0.5 * (pA.y() + pB.y()))
        painterpath.moveTo(pA)
        painterpath.quadTo(c1, pB)
        painterpath.connectPath(pathB.translated(pB))
        
        return painterpath
    # end def
# end def