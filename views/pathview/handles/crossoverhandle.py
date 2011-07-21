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

import util, time
# import Qt stuff into the module namespace with PySide, PyQt4 independence
util.qtWrapImport('QtCore', globals(), ['QPointF', 'QRectF', 'Qt', 'QEvent'])
util.qtWrapImport('QtGui', globals(), ['QBrush', 'QFont', 'QGraphicsItem',\
                                       'QGraphicsSimpleTextItem', 'QPen',\
                                       'QPolygonF', 'QPainterPath', \
                                       'QColor', 'QFontMetrics'])

FromSide = "FromSide"
ToSide = "ToSide"

class XoverHandle(QGraphicsItem):
    """
    This class lets us draw crossovers as a child below pathhelixgroup
    """
    _baseWidth = styles.PATH_BASE_WIDTH
    _rect = QRectF(0, 0, _baseWidth, _baseWidth)
    _toHelixNumFont = styles.XOVER_LABEL_FONT
    fm = QFontMetrics(_toHelixNumFont)
    _labelBrush = QBrush(Qt.SolidPattern)

    def __init__(self, xoverPair, base=None):
        QGraphicsItem.__init__(self, parent=xoverPair._phg)
        self.setZValue(styles.ZXOVERHANDLEPAIR)
        self._xoverPair = xoverPair
        self._ph, self._vh = None, None
        self._strand, self._idx = None, None
        self.labelRect = QRectF()
        self.setBase(base)

    def setBase(self, newBase):
        if newBase == None or None in newBase:
            newBase = None
        if self._vh:
            self._vh.basesModified.disconnect(self.update)
        if newBase == None:
            self._ph, self._vh = None, None
            self._strand, self._idx = None, None
            if self.isVisible():
                self.hide()
        else:
            phg = self._xoverPair._phg
            self._vh, self._strand, self._idx = newBase
            self._ph = phg.pathHelixForVHelix(self._vh)
            self._vh.basesModified.connect(self.update)
            self.setParentItem(self._ph)
            self.setPos(*self._ph.baseLocation(self._strand, self._idx))
            self.setLabelRect(QRectF())
            if not self.isVisible():
                self.show()

    def setLabelRect(self, rect):
        self._labelRect = rect

    def onTopStrand(self):
        if self._vh == None:
            return True
        return self._vh.evenParity() and \
               self._strand == StrandType.Scaffold or \
               not self._vh.evenParity() and \
               self._strand == StrandType.Staple

    def paint(self, painter, option, widget=None):
        # Draw label only; elbow gets drawn by the crossover pair
        painter.setBrush(self._labelBrush)
        painter.setFont(self._toHelixNumFont)
        painter.drawText(self._labelRect, Qt.AlignCenter, str(self._vh.number() ) )

    def boundingRect(self):
       return self._rect

    def mousePressEvent(self, event):
        phg = self._xoverPair._phg
        if phg.dragging:
            return QGraphicsItem.mousePressEvent(self, event)
        self._vh.removeXoversAt(self._strand, self._idx)

    def strandExitPoint(self, penWidthsYShiftedTowardsCenter=0):
        """
        Returns the point at which the segment at
        the represented base leaves the PathHelix.
        1*biasDirection is half the parent XoverHandlePair's
        pen's width
        """
        bw = self._baseWidth
        pw = self._xoverPair.getPen().widthF()
        if self.onTopStrand():
            return QPointF(bw/2.0, penWidthsYShiftedTowardsCenter*pw)
        else:
            return QPointF(bw/2.0, bw - penWidthsYShiftedTowardsCenter*pw)

    def centerPoint(self):
        bw = self._baseWidth
        return QPointF(bw/2.0, bw/2.0)

class XoverHandlePair(QGraphicsItem):
    """
    XoverHandlePair responds to mouse input and serves as an interface
    for adding scaffold crossovers.
    """
    _baseWidth = styles.PATH_BASE_WIDTH
    _xScale = styles.PATH_XOVER_LINE_SCALE_X  # control point x constant
    _yScale = styles.PATH_XOVER_LINE_SCALE_Y  # control point y constant

    def __init__(self, phg, fromBase, toBase):
        """Create XoverHandlePair (parented to the PathHelixGroup)."""
        super(XoverHandlePair, self).__init__(phg)
        self._phg = phg
        self._fromVH, self._toVH = None, None
        self._fromIdx, self._toIdx = None, None
        self._fromStrand, self._toStrand = None, None
        self._toPt = None
        self._rect = QRectF()
        self._pen = None
        self._painterpath = None
        
        self._xover3prime = XoverHandle(self, fromBase)
        self._xover5prime = XoverHandle(self, toBase)
        self.setFromBase(fromBase)
        self.setToBase(toBase)
        
        # print "++++++crossoverhandle (%s->%s)"%(self._fromIdx, self._toIdx)
        self.refresh()

    def fromBase(self):
        return (self._fromVH, self._fromStrand, self._fromIdx)
    
    def setFromBase(self, newBase):
        if (self._fromVH, self._fromStrand, self._fromIdx) == newBase:
            return
        self._painterpath = None
        if self._fromVH != None:
            self._fromVH.basesModified.disconnect(self.refresh)
            
            # this handles changes in pathhelix screen position
            self._xover3prime._ph.xoverUpdate.disconnect(self.refresh)
            
        if newBase == None:
            self._fromVH, self._fromStrand, self._fromIdx = None, None, None
            if self.isVisible():
                self.hide()
        else:
            self._fromVH, self._fromStrand, self._fromIdx = newBase
            self._fromVH.basesModified.connect(self.refresh)
            
            # this handles changes in pathhelix screen position
            self._xover3prime._ph.xoverUpdate.connect(self.refresh)
            
            self._xover3prime.setBase(newBase)
            if not self.isVisible():
                self.show()
        self.refreshRect()
        self.update()

    def setToBase(self, newBase):
        if (self._fromVH, self._fromStrand, self._fromIdx) == newBase\
           or self._toPt == newBase and self._toPt != None:
            return
        self._painterpath = None
        if self._toVH != None:
            self._toVH.basesModified.disconnect(self.refresh)
            
            # this handles changes in pathhelix screen position
            self._xover5prime._ph.xoverUpdate.disconnect(self.refresh)
            
        if newBase == None:
            self._toVH, self._toIdx = None, None
            self._toPt = None
        else:
            if type(newBase) in (tuple, list):
                self._toVH, self._toStrand, self._toIdx = newBase
                self._toVH.basesModified.connect(self.refresh)
                
                # this handles changes in pathhelix screen position
                self._xover5prime._ph.xoverUpdate.connect(self.refresh)
                
                self._toPt = None
            else:
                self._toVH, self._toStrand, self._toIdx = None, None, None
                self._toPt = newBase
        self.refreshRect()
        self.update()

    def setToPoint(self, newToPt):
        # It's smarter than the caller of this method thought
        self.setToBase(newToPt)
    
    def keyMe(self):
        return ((self._fromVH, self._fromStrand, self._fromIdx),\
                (self._toVH, self._toStrand, self._toIdx))
    
    def destroy(self):
        """docstring for destroy"""
        # print "------crossoverhandle (%s->%s)"%(self._fromIdx, self._toIdx)
        if self._toVH == None:
            # Don't destroy the floating crossover
            return
        self.scene().removeItem(self._xover5prime)
        self.scene().removeItem(self._xover3prime)
        key = self.keyMe()
        self.scene().removeItem(self)
        if key in self._phg.xovers:
            del self._phg.xovers[self.keyMe()]
        self._fromVH = self._toVH = None

    def representedXoverExistsInModel(self):
        if self._toVH != None:
            retv = self._fromVH.isaXover(self._fromIdx,\
                                         self._toVH,\
                                         self._toIdx,\
                                         self._fromStrand)
            return retv
        if self._toPt != None:
            floatingXover = self._fromVH.floatingXover()
            # floatingXover[0] is the (vh, st, idx)
            if floatingXover == None:
                return False
            retv = floatingXover[0] == (self._fromVH,\
                                        self._fromStrand,\
                                        self._fromIdx)
            return retv
        return True

    def refresh(self):
        self._painterpath = None
        self._pen = None
        self.refreshRect()
        self.update(self.boundingRect())
        # not sure why this is necessary here HACKish
        # apparently, color isn't done updating when bounding rect is calculated
        self._pen = None 
        if self._fromVH == None or (self._toVH == None and self._toPt == None):
            # No need to destroy ourselves if we've been intentionally set
            # to have a null source / destination (that's intentional)
            return
        if not self.representedXoverExistsInModel():
            # If we represent a valid xover (nonnull source/dest)
            # that does not exist anymore, we need to auto-destroy
            # ourselves.
            self.destroy()
    # end def
    
    def getPen(self):
        if self._pen != None:
            return self._pen
        if self._fromVH == None:
            return QPen()
        color = QColor(self._fromVH.colorOfBase(self._fromStrand, self._fromIdx))
        self._pen = QPen(color)
        self._pen.setWidth(styles.PATH_STRAND_STROKE_WIDTH)
        self._pen.setCapStyle(Qt.SquareCap)
        if self._fromStrand == StrandType.Staple:
            oligoLength = self._fromVH.numberOfBasesConnectedTo(self._fromStrand, self._fromIdx)
            if oligoLength > styles.oligoLenAboveWhichHighlight or \
               oligoLength < styles.oligoLenBelowWhichHighlight:
                self._pen.setWidth(styles.PATH_STRAND_HIGHLIGHT_STROKE_WIDTH)
                color.setAlpha(128)
                self._pen.setColor(color)
        return self._pen

    def paint(self, painter, option, widget=None):
        painter.setBrush(Qt.NoBrush)
        pen = QPen(self.getPen())
        painter.setPen(pen)
        # painter.drawRect(self._rect)
        painter.drawPath(self.getPainterPath())

    def boundingRect(self):
        return self._rect
    # end def
    
    def refreshRect(self):
        if self.painterPath() == None:
            self._rect = QRectF()
            return
        newRect = self.painterPath().controlPointRect()
        penW = self.getPen().widthF()
        newRect.adjust(-penW, -penW, 2*penW, 2*penW)
        if self._rect != newRect:
            self._rect = newRect
            self.prepareGeometryChange()
    # end def

    def getPainterPath(self):
        if self._painterpath == None:
            self.painterPath()
            # print "regenerated"
        return self._painterpath

    def painterPath(self):
        """
        Draws a quad curve from the edge of the fromBase
        to the top or bottom of the toBase (q5), and
        finally to the center of the toBase (toBaseEndpoint).

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
        # Null source / dest => don't paint ourselves => no painterpath
        if self._fromVH == None\
           or self._toVH == None and self._toPt == None:
            return None
        
        if self._painterpath:
            return self._painterpath
        
        # print "regenerating path"
        # begin calculations of how to draw labels and crossover orientations
        y3 = y5 = self._baseWidth / 2
        from5To3 = self._fromVH.directionOfStrandIs5to3(self._fromStrand)
        if from5To3:
            orient3 = HandleOrient.LeftUp
            y3 = -y3
            labelPosRect3 = QRectF(self._xover3prime.strandExitPoint().x() - 0.75*self._baseWidth,\
                                    self._xover3prime.strandExitPoint().y() - 1.5*self._baseWidth,\
                                    self._baseWidth, self._baseWidth)
            self._xover3prime.setLabelRect(labelPosRect3)
        else:
            orient3 = HandleOrient.RightDown
            labelPosRect3 = QRectF(self._xover3prime.strandExitPoint().x() - 0.25*self._baseWidth,\
                                    self._xover3prime.strandExitPoint().y() + 0.5*self._baseWidth,\
                                    self._baseWidth, self._baseWidth)
            self._xover3prime.setLabelRect(labelPosRect3)
        if self._toVH == None:
            toIs5To3 = True
        else:
            toIs5To3 = self._toVH.directionOfStrandIs5to3(self._toStrand)
        if toIs5To3:
            orient5 = HandleOrient.RightUp
            y5 = -y5
            labelPosRect5 = QRectF(self._xover5prime.strandExitPoint().x() - 0.25*self._baseWidth, \
                                    self._xover5prime.strandExitPoint().y() - 1.5*self._baseWidth, \
                                    self._baseWidth, self._baseWidth)
            self._xover5prime.setLabelRect(labelPosRect5)
        else:
            orient5 = HandleOrient.LeftDown
            labelPosRect5 = QRectF(self._xover5prime.strandExitPoint().x() - 0.75*self._baseWidth, \
                                    self._xover5prime.strandExitPoint().y() + 0.5*self._baseWidth, \
                                    self._baseWidth, self._baseWidth)
            self._xover5prime.setLabelRect(labelPosRect5)
        
        threeInsetPt = self._xover3prime.centerPoint()
        threeInsetPt = self.mapFromItem(self._xover3prime, threeInsetPt)
        threeExitPt = self._xover3prime.strandExitPoint()
        threeExitPt = self.mapFromItem(self._xover3prime, threeExitPt)
        
        if self._toPt != None:
            fiveEnterPt = floatPos = self._phg.mapFromScene(self._toPt)
            fiveInsetPt = fiveEnterPt
        else: #self._toPt == None
            floatPos = None
            fiveEnterPt = self._xover5prime.strandExitPoint()
            fiveEnterPt = self.mapFromItem(self._xover5prime, fiveEnterPt)
            fiveInsetPt = self._xover5prime.centerPoint()
            fiveInsetPt = self.mapFromItem(self._xover5prime, fiveInsetPt)
            
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
        self._painterpath = painterpath
        return painterpath
    # end def


# end class
