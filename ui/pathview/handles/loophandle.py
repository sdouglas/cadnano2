# The MIT License
#
# Copyright (c) 2011 Wyss Institute at Harvard University
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of self software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and self permission notice shall be included in
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
# http:#www.opensource.org/licenses/mit-license.php
"""
loophandle.py
Created by Shawn on 2011-05-03.
"""

import ui.styles as styles
from model.enum import StrandType

# from PyQt4.QtCore import QPointF, QRectF, Qt
# from PyQt4.QtGui import QBrush, QFont
# from PyQt4.QtGui import QGraphicsItem, QGraphicsTextItem, QTextCursor
# from PyQt4.QtGui import QPainterPath
# from PyQt4.QtGui import QPen

import util
# import Qt stuff into the module namespace with PySide, PyQt4 independence
util.qtWrapImport('QtCore', globals(), [ 'QPointF', 'QRectF', 'Qt'] )
util.qtWrapImport('QtGui', globals(), [ 'QBrush', 'QFont', \
                                        'QGraphicsItem', 'QGraphicsTextItem', \
                                        'QTextCursor', 'QPainterPath', 'QPen'] )

class LoopItem(object):
    """
    This is just the shape of the Loop item
    """
    _myRect = QRectF(0, 0, styles.PATH_BASE_WIDTH, styles.PATH_BASE_WIDTH)
    _pen = QPen(styles.bluestroke, 2)
    baseWidth = styles.PATH_BASE_WIDTH
    halfbaseWidth = baseWidth / 2
    _offset = baseWidth / 4

    def _loopGen(path, start, c1, p1, c2):
        path.moveTo(start)
        path.quadTo(c1, p1)
        path.quadTo(c2, start)
    # end def

    _pathStart = QPointF(halfbaseWidth, halfbaseWidth)
    _pathMidUp = QPointF(halfbaseWidth, -baseWidth)
    _pathUpUpCtrlPt = QPointF(-halfbaseWidth, -baseWidth)
    _pathUpDownCtrlPt = QPointF(1.5 * baseWidth, -baseWidth)
    _pathMidDown = QPointF(halfbaseWidth, 2 * baseWidth)
    _pathDownDownCtrlPt = QPointF(-halfbaseWidth, 2 * baseWidth)
    _pathDownUpCtrlPt = QPointF(1.5 * baseWidth, 2 * baseWidth)
    _loopPathUp = QPainterPath()
    _loopGen(_loopPathUp, _pathStart, _pathUpUpCtrlPt,\
             _pathMidUp, _pathUpDownCtrlPt)
    _loopPathUp.translate(_offset, 0)
    _loopPathDown = QPainterPath()
    _loopGen(_loopPathDown, _pathStart, _pathDownDownCtrlPt,\
             _pathMidDown, _pathDownUpCtrlPt)
    _loopPathDown.translate(-_offset, 0)

    def __init__(self):
        super(LoopItem, self).__init__()
    # end def

    def getPen(self):
        return self._pen
    # end def

    def getLoop(self, istop):
        if istop:
            return self._loopPathUp
        else:
            return self._loopPathDown
    # end def
# end class


class SkipItem(object):
    """
    This is just the shape of the Loop item
    """
    _myRect = QRectF(0, 0, styles.PATH_BASE_WIDTH, styles.PATH_BASE_WIDTH)
    _pen = QPen(styles.redstroke, 2)
    baseWidth = styles.PATH_BASE_WIDTH
    halfbaseWidth = baseWidth / 2

    def _xGen(path, p1, p2, p3, p4):
        path.moveTo(p1)
        path.lineTo(p2)
        path.moveTo(p3)
        path.lineTo(p4)
    # end def

    _pathStart = QPointF(halfbaseWidth, halfbaseWidth)
    _skipPath = QPainterPath()
    _xGen(_skipPath, _myRect.bottomLeft(), _myRect.topRight(), \
                        _myRect.topLeft(), _myRect.bottomRight())

    def __init__(self):
        super(SkipItem, self).__init__()
    # end def

    def getPen(self):
        return self._pen
    # end def

    def getSkip(self):
        return self._skipPath
    # end def
# end class


class LoopHandle(QGraphicsItem):
    """
    This is just the shape of the Loop item
    """
    _myRect = QRectF(0, 0, styles.PATH_BASE_WIDTH, styles.PATH_BASE_WIDTH)
    _pen = QPen(styles.bluestroke, 2)
    _baseWidth = styles.PATH_BASE_WIDTH
    _offset = styles.PATH_BASE_WIDTH / 4
    _halfbaseWidth = _baseWidth / 2
    _font = QFont("Times", 10, QFont.Bold)

    def __init__(self, parent=None):
        super(LoopHandle, self).__init__(parent)
        self._label = None
        self.label()  # Poke the cache so the label actually exists
        self.setZValue(styles.ZLOOPHANDLE)
        self._loopsize = 0
        self._index = 0
        self._strandtype = None
        self.hide()
    # end def

    def label(self):
        if self._label:
            return self._label
        label = QGraphicsTextItem("")
        label.setFlags(QGraphicsTextItem.ItemIsSelectable)
        label.setFont(self._font)
        label.setParentItem(self)
        label.setTextInteractionFlags(Qt.TextEditorInteraction)
        label.inputMethodEvent = self.inputProcess
        label.keyPressEvent = self.textkeyPressEvent
        label.mousePressEvent = self.labelMousePressEvent
        label.setTextWidth(-1)
        self._label = label
        return label

    def labelMousePressEvent(self, event):
        """
        This is supposed to pre-select the text for editing when you click
        the label. Doesn't work.
        """
        cursor = self._label.textCursor()
        cursor.setPosition(0)
        cursor.movePosition(QTextCursor.End, QTextCursor.KeepAnchor)
        self._label.setTextCursor(cursor)

    def textkeyPressEvent(self, event):
        """
        Must intercept invalid input events.  Make changes here
        """
        a = event.key()
        text = event.text()
        if a in [Qt.Key_Space, Qt.Key_Tab]:
            return
        elif a in [Qt.Key_Return, Qt.Key_Enter]:
            self._label.setTextInteractionFlags(Qt.NoTextInteraction)
            self.inputProcess(event)
            self._label.setTextInteractionFlags(Qt.TextEditorInteraction)
            return
        elif unicode(text).isalpha():
            return
        else:
            return QGraphicsTextItem.keyPressEvent(self._label, event)

    def inputProcess(self, event):
        """
        This is run on the label being changed
        """
        test = unicode(self._label.toPlainText())
        try:
            self._loopsize = int(test)
            self.parentItem().vhelix().installLoop(self._strandtype,\
                                                    self._index,\
                                                    self._loopsize)
            self.resetPosition()
        except:
            print "not an integer"
            self._label.setPlainText("%d" % (self._loopsize))
    # end def

    def boundingRect(self):
        return self._myRect

    def paint(self, painter, option, widget=None):
        pass
    # end def

    def setLabel(self, ph, strandType, index, number):
        self._loopsize = number
        self._index = index
        self._strandtype = strandType
        self._label.setPlainText("%d" % (number))
        self.setParentItem(ph)
        self.resetPosition()
    # end def

    def resetPosition(self):
        txtOffset = self._label.boundingRect().width() / 2
        ph = self.parentItem()
        posItem = ph.baseLocation(self._strandtype, self._index, center=True)
        if ph.strandIsTop(self._strandtype):
            self.setPos(posItem[0] - txtOffset + self._offset,\
                        posItem[1] - 1.5 * self._baseWidth)
        else:
            self.setPos(posItem[0] - txtOffset - self._offset,\
                        posItem[1] + 0.5 * self._baseWidth)
        if self._loopsize > 0:
            self.show()
        else:
            self.hide()
    # end def


class LoopHandleGroup(QGraphicsItem):
    """
    Loop handle consists of the LoopItem and the QLabel and manages loop
    manipulation.
    """
    def __init__(self, parent=None):
        super(LoopHandleGroup, self).__init__(parent)
        self.setZValue(styles.ZLOOPHANDLE)
        self.parent = parent
        self.rect = QRectF(0, 0, 0, 0)
        self.handles = []

    def boundingRect(self):
        return self.rect
    # end def

    def paint(self, painter, option, widget=None):
        pass
    # end def

    def updateActiveHelix(self, ph):
        """
        Collects the locations of each type of LoopHandle from the
        recently activated VirtualHelix vhelix. Each self._index corresponds
        to a pair of LoopHandle that must be updated and displayed.
        """
        vhelix = ph.vhelix()
        for oldHandle in self.handles:
            oldHandle.scene().removeItem(oldHandle)
        scafLoopDict = vhelix._loop(StrandType.Scaffold)
        stapLoopDict = vhelix._loop(StrandType.Staple)
        numLoopsNeeded = len(scafLoopDict) + len(stapLoopDict)
        while len(self.handles) < numLoopsNeeded:
            self.handles.append(LoopHandle(parent=ph))
        while len(self.handles) > numLoopsNeeded:
            handle = self.handles.pop()
            handle.scene().removeItem(handle)
        i = 0
        for strandtype in (StrandType.Scaffold, StrandType.Staple):
            for index, loopsize in vhelix._loop(strandtype).iteritems():
                self.handles[i].setLabel(ph, strandtype, index, loopsize)
                i += 1

