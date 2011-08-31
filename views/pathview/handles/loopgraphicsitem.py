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
loopgraphicsitem.py
Created by Nick on 2011-08-18.
"""

from views import styles
from model.enum import StrandType
from views.pathview.normalstrandgraphicsitem import ppL5, ppR5, ppL3, ppR3

import util
# import Qt stuff into the module namespace with PySide, PyQt4 independence
util.qtWrapImport('QtCore', globals(), [ 'QPointF', 'QRectF', 'Qt'] )
util.qtWrapImport('QtGui', globals(), [ 'QBrush', 'QFont', \
                                        'QGraphicsItem', 'QGraphicsTextItem', \
                                        'QTextCursor', 'QPainterPath', 'QPen',\
                                        'QBrush', 'QColor',\
                                        'QLabel', 'QMatrix', 'QGraphicsPathItem'] )

baseWidth = styles.PATH_BASE_WIDTH
halfBaseWidth = baseWidth / 2
loopOffset = 0

loopPathUp = QPainterPath()
loopPathUp.moveTo(halfBaseWidth, halfBaseWidth)
loopPathUp.quadTo(-halfBaseWidth, -baseWidth,    halfBaseWidth, -baseWidth)
loopPathUp.quadTo(1.5 * baseWidth, -baseWidth,    halfBaseWidth, halfBaseWidth)
loopPathUp.translate(loopOffset, 0)
padding = max(styles.PATH_STRAND_STROKE_WIDTH,\
              styles.PATH_STRAND_HIGHLIGHT_STROKE_WIDTH)
paddingvec = (-padding, -padding, 2 * padding, 2 * padding)
loopPathUpBR = loopPathUp.boundingRect().adjusted(*paddingvec)

loopPathDown = QPainterPath()
loopPathDown.moveTo(halfBaseWidth, halfBaseWidth)
loopPathDown.quadTo(-halfBaseWidth, 2 * baseWidth,\
                    halfBaseWidth, 2 * baseWidth)
loopPathDown.quadTo(1.5 * baseWidth, 2 * baseWidth,\
                    halfBaseWidth, halfBaseWidth)
loopPathDown.translate(loopOffset, 0)
loopPathDownBR = loopPathDown.boundingRect().adjusted(*paddingvec)


def makeLoopPathWithConnectivity(leftConnected, loopPath, rightConnected):
    p = QPainterPath()
    if leftConnected:
        p.moveTo(0, halfBaseWidth)
        p.lineTo(halfBaseWidth + loopOffset, halfBaseWidth)
    else:
        p.moveTo(baseWidth / 4, halfBaseWidth)
        p.lineTo(halfBaseWidth + loopOffset, halfBaseWidth)
    p.addPath(loopPath)
    if rightConnected:
        p.moveTo(halfBaseWidth + loopOffset, halfBaseWidth)
        p.lineTo(baseWidth, halfBaseWidth)
    else:
        p.moveTo(halfBaseWidth + loopOffset, halfBaseWidth)
        p.lineTo(3 * baseWidth / 4, halfBaseWidth)
    return p

loopPaths = [makeLoopPathWithConnectivity(bool(i&1),\
                                          loopPathUp if i&2 else loopPathDown,\
                                          bool(i&4))\
             for i in range(8)]
def loopPathWithConnectivity(leftConnected, onTopStrand, rightConnected):
    return loopPaths[int(leftConnected) + 2*int(onTopStrand) + 4*int(rightConnected)]

class SkipItem(object):
    """
    This is just the shape of the Loop item
    """
    _myRect = QRectF(0, 0, styles.PATH_BASE_WIDTH, styles.PATH_BASE_WIDTH)
    _pen = QPen(styles.redstroke, styles.SKIPWIDTH)
    baseWidth = styles.PATH_BASE_WIDTH
    halfBaseWidth = baseWidth / 2

    def _xGen(path, p1, p2, p3, p4):
        path.moveTo(p1)
        path.lineTo(p2)
        path.moveTo(p3)
        path.lineTo(p4)
    # end def

    _pathStart = QPointF(halfBaseWidth, halfBaseWidth)
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


class LoopGraphicsItem(QGraphicsPathItem):
    _font = QFont(styles.thefont, 10, QFont.Bold)
    # _pen = QPen(styles.bluestroke, 2)
    # _halfBaseWidth = _baseWidth / 2
    # _myRect.adjust(-15, -15, 30, 30)
    # Bases are drawn along and above the loop path.
    # These calculations revolve around fixing the characters at a certain
    # percentage of the total arclength.
    # The fraction of the loop that comes before the first character and
    # after the last character is the padding, and the rest is divided evenly.
    _fractionLoopToPad = .10

    def __init__(self, strand, pathHelix):
        super(LoopGraphicsItem, self).__init__(pathHelix)
        self._label = None
        self._leftCap = None
        self._rightCap = None
        self.setZValue(styles.ZINSERTHANDLE)
        self._pathHelix = pathHelix
        self._strand = None
        self.setStrand(strand)

    def setStrand(self, newStrand):
        if self._strand != None:
            self._strand.didMove.disconnect(self.refreshPosAndLabel)
            self._strand.numBasesChanged.disconnect(self.refreshLabel)
            self._strand.willBeRemoved.disconnect(self.remove)
            self._strand.connectivityChanged.disconnect(self.refreshPath)
        self._strand = newStrand
        if newStrand != None:
            newStrand.didMove.connect(self.refreshPosAndLabel)
            newStrand.numBasesChanged.connect(self.refreshLabel)
            newStrand.willBeRemoved.connect(self.remove)
            newStrand.connectivityChanged.connect(self.refreshPath)
            self.refreshPosAndLabel()

    def remove(self):
        scene = self.scene()
        if scene == None:
            return
        if self._leftCap != None:
            scene.removeItem(self._leftCap)
        if self._rightCap != None:
            scene.removeItem(self._rightCap)
        scene.removeItem(self._label)
        scene.removeItem(self)

    def label(self):
        if self._label:
            return self._label
        label = QGraphicsTextItem("", parent=self)
        label.setFont(self._font)
        label.setParentItem(self)
        label.setTextInteractionFlags(Qt.TextEditorInteraction)
        label.inputMethodEvent = self.inputProcess
        label.keyPressEvent = self.textkeyPressEvent
        label.mousePressEvent = self.labelMousePressEvent
        label.setTextWidth(-1)
        self._label = label
        return label

    def focusOut(self):
        cursor = self._label.textCursor()
        cursor.clearSelection()
        self._label.setTextCursor(cursor)
        self._label.clearFocus()

    def labelMousePressEvent(self, event):
        """
        Pre-selects the text for editing when you click
        the label.
        """
        self._label.setTextInteractionFlags(Qt.TextEditorInteraction)
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
        try:
            loopsize = int(unicode(self._label.toPlainText()))
        except ValueError:
            loopsize = None
        if loopsize != None and loopsize != self._strand.numBases():
            self._strand.setNumBases(loopsize)
        self._label.clearFocus()
        self.focusOut()

    def refreshPosAndLabel(self):
        self.setPos(self._pathHelix.pointForVBase(self._strand.vBase()))
        self.refreshPath()
        self.refreshLabel()

    def refreshLabel(self):
        self.label().setPlainText("%d" % (self._strand.numBases()))
        txtOffset = self._label.boundingRect().width()/2 
        if self._pathHelix.vBaseIsTop(self._strand.vBase()):
            self._label.setPos(halfBaseWidth+loopOffset-txtOffset, -baseWidth)
        else:
            self._label.setPos(halfBaseWidth+loopOffset-txtOffset, baseWidth)

    def refreshPath(self):
        strand = self._strand
        vbase = strand.vBase()
        pos = self._pathHelix.pointForVBase(vbase)
        isOnTop = self._pathHelix.vBaseIsTop(vbase)
        drawn5To3 = vbase.drawn5To3()
        hasLConnection = strand.connL() != None
        hasRConnection = strand.connR() != None
        self.setPath(loopPathWithConnectivity(hasLConnection,\
                                              isOnTop,\
                                              hasRConnection))
        pen = QPen(strand.color(), styles.PATH_STRAND_STROKE_WIDTH )
        pen.setCapStyle(Qt.FlatCap)
        self.setPen(pen)
        if hasLConnection:
            if self._leftCap != None:
                self._leftCap.hide()
        else:
            if self._leftCap == None:
                self._leftCap = QGraphicsPathItem(ppL5 if drawn5To3 else ppL3, self._pathHelix)
                self._leftCap.setPen(QPen(Qt.NoPen))
                self._leftCap.setBrush(strand.color())
            self._leftCap.setPos(pos)
            self._leftCap.show()
        if hasRConnection:
            if self._rightCap != None:
                self._rightCap.hide()
        else:
            if self._rightCap == None:
                self._rightCap = QGraphicsPathItem(ppL5 if drawn5To3 else ppL3, self._pathHelix)
                self._rightCap.setPen(QPen(Qt.NoPen))
                self._rightCap.setBrush(strand.color())
            self._rightCap.setPos(pos)
            self._rightCap.show()
            
                                              