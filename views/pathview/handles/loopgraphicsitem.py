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

import util
# import Qt stuff into the module namespace with PySide, PyQt4 independence
util.qtWrapImport('QtCore', globals(), [ 'QPointF', 'QRectF', 'Qt'] )
util.qtWrapImport('QtGui', globals(), [ 'QBrush', 'QFont', \
                                        'QGraphicsItem', 'QGraphicsTextItem', \
                                        'QTextCursor', 'QPainterPath', 'QPen', \
                                        'QLabel', 'QMatrix', 'QGraphicsPathItem'] )

class LoopItem(object):
    """
    This is just the shape of the Loop item
    """
    _myRect = QRectF(0, 0, styles.PATH_BASE_WIDTH, styles.PATH_BASE_WIDTH)
    _pen = QPen(styles.bluestroke, styles.LOOPWIDTH)
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
    _loopPathUpRect = _loopPathUp.boundingRect()
    _loopPathDown = QPainterPath()
    _loopGen(_loopPathDown, _pathStart, _pathDownDownCtrlPt,\
             _pathMidDown, _pathDownUpCtrlPt)
    _loopPathDown.translate(_offset, 0)
    _loopPathDownRect = _loopPathDown.boundingRect()

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
    _pen = QPen(styles.redstroke, styles.SKIPWIDTH)
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


class LoopGraphicsItem(QGraphicsPathItem):
    """
    This is just the shape of the Loop item
    """
    _loopItem = LoopItem()
    _skipItem = SkipItem()
    _myRect = QRectF(0, 0, styles.PATH_BASE_WIDTH, styles.PATH_BASE_WIDTH)
    _myRect = _myRect.united(LoopItem._loopPathUpRect)
    _myRect = _myRect.united(LoopItem._loopPathDownRect)
    _pen = QPen(styles.bluestroke, 2)
    _baseWidth = styles.PATH_BASE_WIDTH
    _offset = styles.PATH_BASE_WIDTH*0.75
    _halfbaseWidth = _baseWidth / 2
    _font = QFont(styles.thefont, 10, QFont.Bold)
    _myRect.adjust(-15, -15, 30, 30)
    # Bases are drawn along and above the loop path.
    # These calculations revolve around fixing the characters at a certain
    # percentage of the total arclength.
    # The fraction of the loop that comes before the first character and
    # after the last character is the padding, and the rest is divided evenly.
    _fractionLoopToPad = .10

    def __init__(self, parent=None):
        super(LoopGraphicsItem, self).__init__(parent)
        self._label = None
        self.label()  # Poke the cache so the label actually exists
        self._seq = QGraphicsPathItem(self)
        self.setZValue(styles.ZLOOPHANDLE)
        self._loopsize = 0
        self._index = 0
        self._strandType = None
        self._painterPath = None
        self.refreshPath()
    # end def

    def remove(self):
        self.scene().removeItem(self._label)
        self._label = None
        self.scene().removeItem(self._seq)
        self._seq = None
        self.scene().removeItem(self)

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
        print "focusing out"
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
        test = unicode(self._label.toPlainText())
        try:
            loopsize = int(test)
        except:
            loopsize = None
        if loopsize != None and loopsize != self._loopsize:
            self._loopsize = loopsize
            self.parentObject().vhelix().installLoop(self._strandType,\
                                                     self._index,\
                                                     self._loopsize)
            if self._loopsize:
                self.resetPosition()
                self._label.clearFocus()
        # end if
        self.focusOut()

    def refreshPath(self):
        # if self._painterPath == None:
        # if self.path().isEmpty() == True:
        self._painterPath = self.painterPath()
        
    def painterPath(self):
        ph = self.parentObject()
        vh = ph.vhelix()
        strandType = self._strandType
        istop = ph.strandIsTop(strandType)
        index = self._index
        loopsize = self._loopsize
        textPath = QPainterPath()
        if loopsize > 0:
            painterpath = QPainterPath()
            painterpath.addPath(self._loopItem.getLoop(istop))
            self.setPen(QPen(vh.colorOfBase(strandType, index), styles.LOOPWIDTH))
            # self._seq.setPen(QPen(Qt.black))
            # self._seq.setBrush(QBrush(Qt.NoBrush))
            self._seq.setBrush(QBrush(Qt.black))
            # draw sequence on the loop
            baseText = vh.sequenceForLoopAt(strandType, index)
            if baseText[0] != ' ':  # only draw sequences if they exist
                if istop:
                    angleOffset = 0
                else:
                    angleOffset = 180
                if len(baseText) > 20:
                    baseText = baseText[:17] + '...'
                fractionArclenPerChar = (1.-2*self._fractionLoopToPad)/(len(baseText)+1)
                
                for i in range(len(baseText)):
                    frac = self._fractionLoopToPad + (i+1)*fractionArclenPerChar
                    pt = painterpath.pointAtPercent(frac)
                    tangAng = painterpath.angleAtPercent(frac)
                    
                    tempPath = QPainterPath()
                    tempPath.addText(0, 0, ph.sequenceFont, baseText[i if istop else -i-1])   
                    # perform angular translation and rotation
                    mat = QMatrix()
                    
                    mat.translate(pt.x(),pt.y())
                    
                    mat.rotate(-tangAng + angleOffset)
                    
                    mat.translate(-ph.sequenceFontCharWidth/2.,
                                              -2 if istop else ph.sequenceFontH)
                    if not istop:
                        mat.translate(0, -ph.sequenceFontH - styles.LOOPWIDTH)
                                                
                    tempPath = mat.map(tempPath)                       
                    textPath.addPath(tempPath)
                # end for
            # end if
        # end if
        else:  # loopsize < 0 (a skip)
            painterpath = self._skipItem.getSkip()
            self.setPen(self._skipItem.getPen())
        self.setPath(painterpath)
        self._seq.setPath(textPath)
        return painterpath
    # end def

    def setLabel(self, ph, strandType, index, number):
        self._loopsize = number
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
            self._label.setPos(self._offset-txtOffset, -self._baseWidth)
        else:
            self._label.setPos(self._offset-txtOffset, self._baseWidth)
        if self._loopsize > 0:
            self._label.show()
        else:
            self._label.hide()
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
        self.handles = {}

    def boundingRect(self):
        return QRectF()

    def paint(self, painter, option, widget=None):
        pass

    def updateActiveHelix(self, ph):
        """
        Collects the locations of each type of LoopHandle from the
        recently activated VirtualHelix vhelix. Each self._index corresponds
        to a pair of LoopHandle that must be updated and displayed.
        """
        vhelix = ph.vhelix()
        handles = self.handles.get(vhelix,[])
        if not handles:
            self.handles[vhelix] = handles
        scafLoopDict = vhelix.loop(StrandType.Scaffold)
        stapLoopDict = vhelix.loop(StrandType.Staple)
        numLoopsNeeded = len(scafLoopDict) + len(stapLoopDict)
        while len(handles) < numLoopsNeeded:
            handles.append(LoopGraphicsItem(parent=ph))
        while len(handles) > numLoopsNeeded:
            handle = handles.pop()
            handle.remove()
            handle = None
        i = 0
        for strandtype in (StrandType.Scaffold, StrandType.Staple):
            for index, loopsize in vhelix.loop(strandtype).iteritems():
                handles[i].setLabel(ph, strandtype, index, loopsize)
                handles[i].refreshPath()
                i += 1

