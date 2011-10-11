#!/usr/bin/env python
# encoding: utf-8

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

from exceptions import NotImplementedError
import util

from views import styles
from model.enum import StrandType

import util
# import Qt stuff into the module namespace with PySide, PyQt4 independence
util.qtWrapImport('QtCore', globals(), [ 'QPointF', 'QRectF', 'Qt'] )
util.qtWrapImport('QtGui', globals(), [ 'QBrush', 'QFont', \
                                        'QGraphicsItem', 'QGraphicsTextItem', \
                                        'QTextCursor', 'QPainterPath', 'QPen', \
                                        'QLabel'] )

_baseWidth = _bw = styles.PATH_BASE_WIDTH
_halfbaseWidth = _hbw = _baseWidth / 2
_offset1 = _baseWidth / 4

_myRect = QRectF(0, 0, _bw, _bw)
_bpen = QPen(styles.bluestroke, styles.INSERTWIDTH)
_rpen = QPen(styles.redstroke, styles.SKIPWIDTH)

def _insertGen(path, start, c1, p1, c2):
    path.moveTo(start)
    path.quadTo(c1, p1)
    path.quadTo(c2, start)
# end def


_pathStart = QPointF(_hbw, _hbw)
_pathMidUp = QPointF(_hbw, -_bw)
_pathUpUpCtrlPt = QPointF(-_hbw, -_bw)
_pathUpDownCtrlPt = QPointF(1.5 * _bw, -_bw)
_pathMidDown = QPointF(_hbw, 2 * _bw)
_pathDownDownCtrlPt = QPointF(-_hbw, 2 * _bw)
_pathDownUpCtrlPt = QPointF(1.5 * _bw, 2 * _bw)
_insertPathUp = QPainterPath()
_insertGen(_insertPathUp, _pathStart, _pathUpUpCtrlPt,\
         _pathMidUp, _pathUpDownCtrlPt)
_insertPathUp.translate(_offset1, 0)
_insertPathUpRect = _insertPathUp.boundingRect()
_insertPathDown = QPainterPath()
_insertGen(_insertPathDown, _pathStart, _pathDownDownCtrlPt,\
         _pathMidDown, _pathDownUpCtrlPt)
_insertPathDown.translate(_offset1, 0)
_insertPathDownRect = _insertPathDown.boundingRect()


_bigRect = _myRect.united(_insertPathUpRect)
_bigRect = _bigRect.united(_insertPathDownRect)
_bpen2 = QPen(styles.bluestroke, 2)
_offset2 = _bw*0.75
_font = QFont(styles.thefont, 10, QFont.Bold)
_bigRect.adjust(-15, -15, 30, 30)
# Bases are drawn along and above the insert path.
# These calculations revolve around fixing the characters at a certain
# percentage of the total arclength.
# The fraction of the insert that comes before the first character and
# after the last character is the padding, and the rest is divided evenly.
_fractionInsertToPad = .10


class InsertionPath(object):
    """
    This is just the shape of the Insert item
    """

    def __init__(self):
        super(InsertionPath, self).__init__()
    # end def

    def getPen(self):
        return self._pen
    # end def

    def getInsert(self, istop):
        if istop:
            return self._insertPathUp
        else:
            return self._insertPathDown
    # end def
# end class

def _xGen(path, p1, p2, p3, p4):
    path.moveTo(p1)
    path.lineTo(p2)
    path.moveTo(p3)
    path.lineTo(p4)
# end def

_pathStart = QPointF(_hbw, _hbw)

class SkipPath(object):
    """
    This is just the shape of the Insert item
    """
    
    
    _skipPath = QPainterPath()
    _xGen(_skipPath, _myRect.bottomLeft(), _myRect.topRight(), \
                        _myRect.topLeft(), _myRect.bottomRight())

    def __init__(self):
        super(SkipPath, self).__init__()
    # end def

    def getPen(self):
        return self._pen
    # end def

    def getSkip(self):
        return self._skipPath
    # end def
# end class

class InsertionItem(QGraphicsItem):
    """
    This is just the shape of the Insert item
    """
    _insertPath = InsertionPath()
    _skipPath = SkipPath()

    def __init__(self, virtualHelixItem, strand, insertion):
        super(InsertionItem, self).__init__(virtualHelixItem)
        self._label = None
        self._vHI = virtualHelixItem
        self._strand = strand
        self._insertion = insertion
        
        self.label()  # Poke the cache so the label actually exists
        self.setZValue(styles.ZINSERTHANDLE)
        
    # end def

    def label(self):
        if self._label:
            return self._label
        label = QGraphicsTextItem("", parent=self)
        label.setFont(_font)
        label.setTextInteractionFlags(Qt.TextEditorInteraction)
        label.inputMethodEvent = self.inputProcess
        label.keyPressEvent = self.textkeyPressEvent
        label.mousePressEvent = self.labelMousePressEvent
        label.setTextWidth(-1)
        self._label = label
        return label

    def focusOut(self):
        # print "focusing out"
        cursor = self._label.textCursor()
        cursor.clearSelection()
        self._label.setTextCursor(cursor)
        self._label.clearFocus()
    # end def

    def labelMousePressEvent(self, event):
        """
        Pre-selects the text for editing when you click
        the label.
        """
        lbl = self._label
        lbl.setTextInteractionFlags(Qt.TextEditorInteraction)
        cursor = lbl.textCursor()
        cursor.setPosition(0)
        cursor.movePosition(QTextCursor.End, QTextCursor.KeepAnchor)
        lbl.setTextCursor(cursor)

    def textkeyPressEvent(self, event):
        """
        Must intercept invalid input events.  Make changes here
        """
        a = event.key()
        text = event.text()
        if a in [Qt.Key_Space, Qt.Key_Tab]:
            return
        elif a in [Qt.Key_Return, Qt.Key_Enter]:
            self.inputProcess(event)
            return
        elif unicode(text).isalpha():
            return
        else:
            return QGraphicsTextItem.keyPressEvent(self._label, event)

    def inputProcess(self, event):
        """
        This is run on the label being changed
        or losing focus
        """
        lbl = self._label
        test = unicode(lbl.toPlainText())
        try:
            insertsize = int(test)
        except:
            insertsize = None
        if insertsize != None and insertsize != self._insertsize:
            self._insertsize = insertsize
            self.parentObject().vhelix().installInsert(self._strandType,\
                                                     self._index,\
                                                     self._insertsize)
            if self._insertsize:
                self.resetPosition()
                lbl.setFocus(False)
        # end if
        self.focusOut()

    def boundingRect(self):
        return self._bigRect

    def paint(self, painter, option, widget=None):
        ph = self.parentObject()
        vh = ph.vhelix()
        strandType = self._strandType
        istop = ph.strandIsTop(strandType)
        index = self._index
        insertsize = self._insertsize
        
        if insertsize > 0:
            path = self._insertItem.getInsert(istop)
            painter.setPen(QPen(vh.colorOfBase(strandType, index), styles.INSERTWIDTH))
            painter.setBrush(Qt.NoBrush)
            painter.drawPath(path)
            # draw sequence on the insert
            baseText = vh.sequenceForInsertAt(strandType, index)
            if baseText[0] != ' ':  # only draw sequences if they exist
                if istop:
                    angleOffset = 0
                else:
                    angleOffset = 180
                if len(baseText) > 20:
                    baseText = baseText[:17] + '...'
                fractionArclenPerChar = (1.-2*self._fractionInsertToPad)/(len(baseText)+1)
                painter.setPen(QPen(Qt.black))
                painter.setBrush(Qt.NoBrush)
                painter.setFont(ph.sequenceFont)
                for i in range(len(baseText)):
                    frac = self._fractionInsertToPad + (i+1)*fractionArclenPerChar
                    pt = path.pointAtPercent(frac)
                    tangAng = path.angleAtPercent(frac)
                    painter.save()
                    painter.translate(pt)
                    painter.rotate(-tangAng + angleOffset)
                    painter.translate(QPointF(-ph.sequenceFontCharWidth/2.,
                                              -2 if istop else ph.sequenceFontH))
                    if not istop:
                        painter.translate(0, -ph.sequenceFontH - styles.INSERTWIDTH)
                    painter.drawText(0, 0, baseText[i if istop else -i-1])
                    painter.restore()
            # end if
        else:  # insertsize < 0 (a skip)
            path = self._skipItem.getSkip()
            painter.setPen(self._skipItem.getPen())
            painter.drawPath(path)
    # end def

    def setLabel(self, ph, strandType, index, number):
        self._insertsize = number
        self._index = index
        self._strandType = strandType
        self._label.setPlainText("%d" % (number))
        self.setParentItem(ph)
        self.resetPosition()
    # end def

    def resetPosition(self):
        txtOffset = self._label.boundingRect().width()/2 
        ph = self.parentObject()
        posItem = ph.baseLocation(self._strandType, self._index, center=False)
        self.setPos(posItem[0], posItem[1])
        if ph.strandIsTop(self._strandType):
            self._label.setPos(self._offset2-txtOffset, -self._baseWidth)
        else:
            self._label.setPos(self._offset2-txtOffset, self._baseWidth)
        if self._insertsize > 0:
            self._label.show()
        else:
            self._label.hide()
    # end def
