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

import util
# import Qt stuff into the module namespace with PySide, PyQt4 independence
util.qtWrapImport('QtCore', globals(), ['QPointF', 'QRectF', 'Qt'])
util.qtWrapImport('QtGui', globals(), ['QBrush', 'QFont', 'QGraphicsItem',\
                                       'QGraphicsSimpleTextItem', 'QPen',\
                                       'QPolygonF', 'QPainterPath', \
                                       'QColor', 'QFontMetrics'])


class XoverHandle(QGraphicsItem):
    """
    This class lets us draw crossovers as a child below pathhelixgroup
    """
    _baseWidth = styles.PATH_BASE_WIDTH
    _rect = QRectF(0, 0, _baseWidth, _baseWidth)
    _toHelixNumFont = styles.XOVER_LABEL_FONT
    fm = QFontMetrics(_toHelixNumFont)
    _labelBrush = QBrush(Qt.SolidPattern)
    
    def _hashMarkGen(path, p1, p2):
        path.moveTo(p1)
        path.lineTo(p2)
    # end

    _pathCenter = QPointF(_baseWidth / 2,\
                          _baseWidth / 2)
    _pathUp = QPointF(_baseWidth / 2, 0)
    _pathDown = QPointF(_baseWidth / 2, _baseWidth)
    _ppathUp = QPainterPath()
    _hashMarkGen(_ppathUp, _pathCenter, _pathUp)
    _ppathDown = QPainterPath()
    _hashMarkGen(_ppathDown, _pathCenter, _pathDown)
    
    def __init__(self, xoverpair, idx, fromVH, toVH, parentPH):
        "this sets the parent object to the phg"
        super(XoverHandle, self).__init__(parent=parentPH)
        self._phg = parentPH.pathHelixGroup()
        self.setZValue(styles.ZXOVERHANDLEPAIR)
        self._xoverpair = xoverpair
        # self.phg.geometryChanged.connect(self.prepareGeometryChange)
        self._index = idx  
        self._toVH = toVH
        self._fromVH = fromVH
        fromVH.basesModified.connect(self.update)
        toVH.basesModified.connect(self.update)
        self.hide()
        x = self._baseWidth * self._index
        y = (0 if self.onTopStrand() else 1) * self._baseWidth
        self.setPos(x, y)
        
        halfLabelH = self.fm.tightBoundingRect(str(toVH.number())).height()/2
        #halfLabelW = self.fm.boundingRect(str(toVH.number())).width()/2
        labelX = 0

        if self.onTopStrand():
            labelY = -1.05*halfLabelH - .5
            self._endPoint = self._pathUp
            self._painterpath = self._ppathUp
        else:
            labelY = 1.05*halfLabelH + .5
            self._endPoint = self._pathDown
            self._painterpath = self._ppathDown
        self._labelRect = QRectF()
        self.show()
    # end def

    def setLabelRect(self, rect):
        self._labelRect = rect
    #end def
       
    def endPoint(self):
        return self._endPoint
   
    def onTopStrand(self):
        return self._fromVH.evenParity() and \
            self._xoverpair._strandtype == StrandType.Scaffold or \
                not self._fromVH.evenParity() and \
                self._xoverpair._strandtype == StrandType.Staple

    def paint(self, painter, option, widget=None):
        painter.setBrush(Qt.NoBrush)
        self._xoverpair.refreshPen()
        pen = self._xoverpair.getPen()
        painter.setPen(pen)
        bw = self._baseWidth
        pw = pen.widthF()
        center = QPointF(bw/2, bw/2)
        if self.onTopStrand():
            edge = QPointF(bw/2, pw/2.0)
        else:
            edge = QPointF(bw/2, bw-pw/2.0)
        painter.drawLine(center, edge)
        self.drawLabel(painter)
   
    def drawLabel(self, painter):
        painter.setBrush(self._labelBrush)
        painter.setFont(self._toHelixNumFont)
        painter.drawText(self._labelRect, Qt.AlignCenter, str(self._toVH.number() ) )
    # end def

    def boundingRect(self):
       return self._rect
   
    def mousePressEvent(self, event):
        xop = self._xoverpair
        xop._fromVH.removeXoverTo(xop._strandtype, xop._fromIdx, xop._toVH, xop._toIdx)

class XoverHandlePair(QGraphicsItem):
    """
    XoverHandlePair responds to mouse input and serves as an interface
    for adding scaffold crossovers.
    """
    _baseWidth = styles.PATH_BASE_WIDTH
    _xScale = styles.PATH_XOVER_LINE_SCALE_X  # control point x constant
    _yScale = styles.PATH_XOVER_LINE_SCALE_Y  # control point y constant

    def __init__(self, phg, fromVH, fromIdx, toVH, toIdx, strandtype):
        """Create XoverHandlePair (parented to the PathHelixGroup)."""
        super(XoverHandlePair, self).__init__(phg)
        # print "created XOVER"
        self._phg = phg
        self._fromVH = fromVH
        self._strandtype = strandtype   # strandtype
        self._fromIdx = fromIdx
        self._toVH = toVH
        self._toIdx = toIdx
        self.hide()
        if self._strandtype == StrandType.Scaffold:
            self._pen = self._phg._scafPen
        else:
            self._pen = QPen(self._phg._stapPen)
        
        self._rect = QRectF()

        self._xover3prime = XoverHandle(self, self._fromIdx, \
                                        self._fromVH, self._toVH, \
                                        self._phg.getPathHelix(self._fromVH))
        self._xover5prime = XoverHandle(self, self._toIdx, \
                                        self._toVH, self._fromVH, 
                                        self._phg.getPathHelix(self._toVH))
        
        self._fromVH.basesModified.connect(self.refresh)
        self._toVH.basesModified.connect(self.refresh)
        self._phg.displayedVHsChanged.connect(self.refresh)
        self.refresh()
        self.show()
    # end def
    
    # def _5PrimeVH(self):
    #     return self._fromVH
    #     
    # def _3PrimeVH(self):
    #     return self._toVH
    
    def getPen(self):
        return self._pen
    # end def
    
    def keyMe(self):
        return ( (self._fromVH, self._fromIdx), (self._toVH, self._toIdx) )
    
    def destroy(self):
        """docstring for destroy"""
        self._xover3prime.hide()
        self._xover5prime.hide()
        self._xover3prime = None
        self._xover5prime = None
        self._phg.displayedVHsChanged.disconnect(self.refresh)
        self._fromVH.basesModified.disconnect(self.refresh)
        self._toVH.basesModified.disconnect(self.refresh)
        self.hide()
        key = self.keyMe()
        del self._phg.xovers[self.keyMe()]
        self.scene().removeItem(self)
    # end def
    
    def refresh(self):
        if self._fromVH.isaXover(self._fromIdx, self._toVH, self._toIdx, self._strandtype):
        #if True:
            self.refreshPath()
            self.refreshPen()
            self.update(self.boundingRect())
            self._xover3prime.update(self._xover3prime.boundingRect())
            self._xover5prime.update(self._xover5prime.boundingRect())
        else:
            self.destroy()
    # end def
    
    def refreshPen(self):
        if self._strandtype == StrandType.Staple:
            self._pen = QPen()
            color = QColor(self._fromVH.colorOfBase(self._strandtype, self._fromIdx))
            oligoLength = self._fromVH.numberOfBasesConnectedTo(self._strandtype, self._fromIdx)
            #print oligoLength, "resized"
            if oligoLength > styles.oligoLenAboveWhichHighlight or \
               oligoLength < styles.oligoLenBelowWhichHighlight:
                self._pen.setWidth(styles.PATH_STRAND_HIGHLIGHT_STROKE_WIDTH)
                color.setAlpha(128)
            else:
                self._pen.setWidth(styles.PATH_STRAND_STROKE_WIDTH)
                color.setAlpha(255)
            self._pen.setColor(color)
        # end if
        else:
            self._pen = self._phg._scafPen
        self.refreshRect()
    # end def

    def paint(self, painter, option, widget=None):
        painter.setBrush(Qt.NoBrush)
        self.refreshPen()
        pen = QPen(self._pen)
        pen.setCapStyle(Qt.FlatCap)
        painter.setPen(pen)
        # painter.drawRect(self._rect)
        painter.drawPath(self._painterpath)

    def boundingRect(self):
        return self._rect

    def refreshPath(self, floatPos=None):
        """
        Draws a line from the center of the fromBase (fromBaseCenter) to the
        top or bottom of that same base, depending on its direction (q3),
        then a quad curve to the top or bottom of the toBase (q5), and
        finally to the center of the toBase (toBaseCenter).

        If floatPos!=None, this is a floatingXover and floatPos is the
        destination point (where the mouse is) while toHelix, toIndex
        are potentially None and represent the base at floatPos.

        returns a tuple of the (QPainter, QRectF, QRectF) representing the
        (quad curve, the FROM label rectangle, and the TO label rectangle)
        
        Why have toStrandtype? A PathHelix should display inconsistencies
        in the model, and a crossover from one strand type to another is
        an inconsistency that would be very nice to have a visual indication
        of (rather than having strange errors popping up down the line; the
        particular instance prompting this addition cost 4 hours of time)
        """
        fromBaseCenter = self._xover3prime.endPoint()
        fromBaseCenter = self._phg.mapFromItem(self._xover3prime, fromBaseCenter)
        if floatPos:
            toBaseCenter = floatPos
        else:
            toBaseCenter = self._xover5prime.endPoint()
            toBaseCenter = self._phg.mapFromItem(self._xover5prime, toBaseCenter)

        # begin calculations of how to draw labels and crossover orientations
        y3 = y5 = self._baseWidth / 2
        from5To3 = self._fromVH.directionOfStrandIs5to3(self._strandtype)
        if from5To3:
            orient3 = HandleOrient.LeftUp
            y3 = -y3
            labelPosRect3 = QRectF(self._xover3prime.endPoint().x() - 0.75*self._baseWidth,\
                                    self._xover3prime.endPoint().y() - 1.5*self._baseWidth,\
                                    self._baseWidth, self._baseWidth)
            self._xover3prime.setLabelRect(labelPosRect3)
        else:
            orient3 = HandleOrient.RightDown
            labelPosRect3 = QRectF(self._xover3prime.endPoint().x() - 0.25*self._baseWidth,\
                                    self._xover3prime.endPoint().y() + 0.5*self._baseWidth,\
                                    self._baseWidth, self._baseWidth)
            self._xover3prime.setLabelRect(labelPosRect3)
        if floatPos and not self._toVH:
            toIs5To3 = not from5To3
        else:
            toIs5To3 = self._toVH.directionOfStrandIs5to3(self._strandtype)
        if toIs5To3:
            orient5 = HandleOrient.RightUp
            y5 = -y5
            labelPosRect5 = QRectF(self._xover5prime.endPoint().x() - 0.25*self._baseWidth, \
                                    self._xover5prime.endPoint().y() - 1.5*self._baseWidth, \
                                    self._baseWidth, self._baseWidth)
            self._xover5prime.setLabelRect(labelPosRect5)
        else:
            orient5 = HandleOrient.LeftDown
            labelPosRect5 = QRectF(self._xover5prime.endPoint().x() - 0.75*self._baseWidth, \
                                    self._xover5prime.endPoint().y() + 0.5*self._baseWidth, \
                                    self._baseWidth, self._baseWidth)
            self._xover5prime.setLabelRect(labelPosRect5)
        # Determine start and end points of quad curve
        yOffsetFromCenterToEdge = self._baseWidth*1.0/3 * (-1 if from5To3 else 1)
        q3 = QPointF(fromBaseCenter.x(),\
                     fromBaseCenter.y() + yOffsetFromCenterToEdge)
        yOffsetFromCenterToEdge = self._baseWidth*1.0/3 * (-1 if toIs5To3 else 1)
        q5 = QPointF(toBaseCenter.x(),\
                     toBaseCenter.y() + yOffsetFromCenterToEdge)

        # Determine control point of quad curve
        c1 = QPointF()
        if floatPos and not self._toVH:
            sameStrand = False
            sameParity = False
        else:
            sameStrand = self._fromVH == self._toVH
            sameParity = self._fromVH.evenParity() == self._toVH.evenParity()
        # case 1: same strand
        if sameStrand:
            dx = abs(toBaseCenter.x() - fromBaseCenter.x())
            c1.setX(0.5 * (fromBaseCenter.x() + toBaseCenter.x()))
            if orient3 in [HandleOrient.LeftUp, HandleOrient.RightUp]:
                c1.setY(q3.y() - self._yScale * dx)
            else:
                c1.setY(q3.y() + self._yScale * dx)
        # case 2: same parity
        elif sameParity:
            dy = abs(toBaseCenter.y() - fromBaseCenter.y())
            c1.setX(fromBaseCenter.x() + self._xScale * dy)
            c1.setY(0.5 * (fromBaseCenter.y() + toBaseCenter.y()))
        # case 3: different parity
        else:
            if orient3 == HandleOrient.LeftUp:
                c1.setX(fromBaseCenter.x() - self._xScale *\
                        abs(toBaseCenter.y() - fromBaseCenter.y()))
            else:
                c1.setX(fromBaseCenter.x() + self._xScale *\
                        abs(toBaseCenter.y() - fromBaseCenter.y()))
            c1.setY(0.5 * (fromBaseCenter.y() + toBaseCenter.y()))

        # Construct painter path
        painterpath = QPainterPath()
        painterpath.moveTo(fromBaseCenter)
        painterpath.lineTo(q3)
        painterpath.quadTo(c1, q5)
        painterpath.lineTo(toBaseCenter)
        self._painterpath = painterpath
        self.refreshRect()
    # end def

    def refreshRect(self):
        self._rect = self._painterpath.boundingRect()
        penW = self.getPen().widthF()
        self._rect.adjust(-penW, -penW, 2*penW, 2*penW)        
# end class
