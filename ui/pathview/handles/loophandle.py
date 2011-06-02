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

from PyQt4.QtCore import QPointF, QRectF, Qt
from PyQt4.QtGui import QBrush, QFont
from PyQt4.QtGui import QGraphicsItem, QGraphicsTextItem
from PyQt4.QtGui import QPainterPath
from PyQt4.QtGui import QPen
import ui.styles as styles
from model.enum import StrandType

class LoopItem(object):
    """
    This is just the shape of the Loop item
    """
    _myRect = QRectF(0, 0, styles.PATH_BASE_WIDTH, styles.PATH_BASE_WIDTH)
    _pen = QPen(styles.bluestroke, 2)
    baseWidth = styles.PATH_BASE_WIDTH
    halfbaseWidth = baseWidth / 2

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
    _loopPathDown = QPainterPath()
    _loopGen(_loopPathDown, _pathStart, _pathDownDownCtrlPt,\
             _pathMidDown, _pathDownUpCtrlPt)

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
    halfbaseWidth = baseWidth/2
    
    def _xGen(path, p1, p2, p3, p4):
        path.moveTo(p1)
        path.lineTo(p2)
        path.moveTo(p3)
        path.lineTo(p4)
    # end def

    _pathStart = QPointF(halfbaseWidth,halfbaseWidth)
    
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
        label.setVisible(False)
        label.setFont(self._font)
        label.setParentItem(self)
        label.setTextInteractionFlags(Qt.TextEditorInteraction)
        label.inputMethodEvent = self.inputProcess
        label.keyPressEvent = self.textkeyPressEvent
        label.setTextWidth(-1)
        self._label = label
        self._label.hide()
        return label

    def textkeyPressEvent(self, event):
        """
        Must intercept invalid input events.  Make changes here
        """
        a = event.key()
        text = event.text()
        if a == Qt.Key_Space or a == Qt.Key_Tab:
            return
        elif a == Qt.Key_Return:
            self._label.setTextInteractionFlags(Qt.NoTextInteraction)
            self.inputProcess(event)
            self._label.setTextInteractionFlags(Qt.TextEditorInteraction)
            return 
        elif unicode(text).isalpha():
            return
        else:    
            return QGraphicsTextItem.keyPressEvent(self._label,event)


    def inputProcess(self, event):
        """
        This is run on the label being changed
        """
        test = unicode(self._label.toPlainText())
        try:
            self._loopsize = int(test)
            self.parentItem().vhelix().installLoop(self._strandtype, \
                                                    self._index, \
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
        self._label.show()
        self.show()
    # end def
    
    def resetPosition(self):
        txtOffset = self._label.boundingRect().width()/2
        ph = self.parentItem()
        posItem = ph.baseLocation(self._strandtype, self._index, center=True)
        if ph.strandIsTop(self._strandtype):
            self.setPos(posItem[0]-txtOffset, posItem[1]-1.5*self._baseWidth)
        else:
            self.setPos(posItem[0]-txtOffset, posItem[1]+0.5*self._baseWidth)
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
        
        for i in range(128):
            self.handles.append(LoopHandle(parent=self))
        # end for
        self.activeCount = 0
    # end def
    
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
        count = 0
        # Process Scaffold PreXoverHandles
        strandtype = StrandType.Scaffold
        i = 0
        # this is summing keys in a dictionary
        countScaf = len(vhelix._loop(strandtype))
        if countScaf > 0:
            for index, loopsize in vhelix._loop(strandtype).iteritems():
                self.handles[i].setLabel(ph, strandtype, index, loopsize)
                i += 1
        strandtype = StrandType.Staple
        countStap = len(vhelix._loop(strandtype))
        if countStap > 0:
            for index, loopsize in vhelix._loop(strandtype).iteritems():
                self.handles[i].setLabel(ph, strandtype, index, loopsize)
                i += 1
        # hide extra precrossoverhandles as necessary
        count = countStap + countScaf
        if self.activeCount > count:
            for i in range(count, self.activeCount):
                self.handles[i].hide()
            # end for
        # end if
        self.activeCount = count
    # end def
# end class
