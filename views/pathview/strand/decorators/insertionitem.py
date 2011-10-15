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
                                        'QTextCursor', 'QPainterPath', 'QPen', 'QColor',\
                                        'QLabel', 'QGraphicsPathItem', 'QMatrix', 'QFontMetricsF'] )

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
        return _bpen
    # end def

    def getInsert(self, istop):
        if istop:
            return _insertPathUp
        else:
            return _insertPathDown
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
        return _rpen
    # end def

    def getSkip(self):
        return self._skipPath
    # end def
# end class

_insertPath = InsertionPath()
_skipPath = SkipPath()

class InsertionItem(QGraphicsPathItem):
    """
    This is just the shape of the Insert item
    """

    def __init__(self, virtualHelixItem, strand, insertion):
        super(InsertionItem, self).__init__(virtualHelixItem)
        self._strand = strand
        self._insertion = insertion
        isOnTop = self._isOnTop = virtualHelixItem.isStrandOnTop(strand)
        if isOnTop:
            self.setPos(_bw*insertion.idx(), 0)
        else:
            self.setPos(_bw*insertion.idx(), _bw)
        self.hide()
        self.setZValue(styles.ZINSERTHANDLE)
        # do label stuff to depict the length of the insertion
        label = QGraphicsTextItem("", parent=self)
        label.setFont(_font)
        label.setTextInteractionFlags(Qt.TextEditorInteraction)
        label.inputMethodEvent = self.inputProcess
        label.keyPressEvent = self.textkeyPressEvent
        label.mousePressEvent = self.labelMousePressEvent
        label.setTextWidth(-1)
        self._label = label
        self._seqItem = QGraphicsPathItem(parent=self)
        self.updateItem()
        self.show()
    # end def

    def focusOut(self):
        lbl = self._label
        cursor = lbl.textCursor()
        cursor.clearSelection()
        lbl.setTextCursor(cursor)
        lbl.clearFocus()
    # end def

    def remove(self):
        scene = self.scene()
        scene.removeItem(self._label)
        self._label = None
        scene.removeItem(self._seqItem)
        self._seqItem = None
        scene.removeItem(self)
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
            insertionSize = int(test)
        except:
            insertionSize = None
        insertion = self._insertion
        length = insertion.length()
        if insertionSize != None and insertionSize != length:
            self._strand.changeInsertion(insertion.idx(), insertionSize)
            if insertion.length():
                self.resetPosition()
        # end if
        self.focusOut()

    def updateItem(self):
        self.updatePath()
        self.updateLabel()
        self.resetPosition()
    # end def

    def updatePath(self):
        strand = self._strand
        if strand == None:
            self.hide()
            return
        else:
            self.show()

        isOnTop = self._isOnTop

        if self._insertion.length() > 0:
            self.setPath(_insertPath.getInsert(isOnTop))
            self.setPen(QPen(QColor(strand.oligo().color()), styles.INSERTWIDTH))
            self.setBrush(QBrush(Qt.NoBrush))
        else:  # insertionSize < 0 (a skip)
            self.setPath(_skipPath.getSkip())
            self.setPen(_skipPath.getPen())
    # end def

    def _updateSequenceText(self):
        seqItem = self._seqItem
        strand = self._strand
        isOnTop = self._isOnTop
        index = self._insertion.idx()

        # draw sequence on the insert
        baseText = strand.sequenceForInsertAt(index)
        if baseText:  # only draw sequences if they exist i.e. not None!
            lenBT = len(baseText)
            if isOnTop:
                angleOffset = 0
            else:
                angleOffset = 180
            if lenBT > 20:
                baseText = baseText[:17] + '...'
            fractionArclenPerChar = (1.-2*_fractionInsertToPad)/(lenBT+1)
            seqItem.setPen(QPen(Qt.black))
            seqItem.setBrush(QBrush(Qt.NoBrush))

            seqPath = QPainterPath()
            for i in range(lenBT):
                frac = _fractionInsertToPad + (i+1)*fractionArclenPerChar
                pt = seqPath.pointAtPercent(frac)
                tangAng = seqPath.angleAtPercent(frac)
                # painter.save()

                normalPath = QPainterPath()
                normalPath.setFont(styles.SEQUENCEFONT)
                normalPath.translate(pt)
                normalPath.addText(0, 0, baseText[i if isOnTop else -i-1])
                mat = QMatrix()
                mat.rotate(-tangAng + angleOffset)
                rotatedPath = mat.map(tempPath)

                rotatedPath.translate(QPointF(-styles.SEQUENCEFONTCHARWIDTH/2.,
                                          -2 if isOnTop else styles.SEQUENCEFONTH))
                if not isOnTop:
                    rotatedPath.translate(0, -syles.SEQUENCEFONTH - styles.INSERTWIDTH)
                seqPath.addPath(rotatedPath)
        # end if
    # end def

    def updateLabel(self):
        self._label.setPlainText("%d" % (self._insertion.length()))
    # end def

    def resetPosition(self):
        lbl = self._label
        txtOffset = lbl.boundingRect().width()/2
        insertion = self._insertion
        if self._isOnTop:
            lbl.setPos(_offset2-txtOffset, -_bw)
        else:
            lbl.setPos(_offset2-txtOffset, _bw)
        if insertion.length() > 0:
            lbl.show()
        else:
            lbl.hide()
    # end def
# end class
