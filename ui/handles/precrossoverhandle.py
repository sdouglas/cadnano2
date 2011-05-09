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
precrossoverhandle.py
Created by Nick on 2011-05-03.
"""

from exceptions import AttributeError, NotImplementedError
from PyQt4.QtCore import QPointF, QRectF, Qt
from PyQt4.QtGui import QBrush, QFont
from PyQt4.QtGui import QGraphicsItem, QGraphicsSimpleTextItem
from PyQt4.QtGui import QPainterPath
from PyQt4.QtGui import QPolygonF
from PyQt4.QtGui import QPen, QUndoCommand
from model.enum import StrandType, Parity, BreakType, HandleOrient
import ui.styles as styles

# construct paths for breakpoint handles
def hashMarkGen(path, p1, p2, p3):
    path.moveTo(p1)
    path.lineTo(p2)
    path.lineTo(p3)
# end

ppRect = QRectF(0, 0, styles.PATH_BASE_WIDTH/2, styles.PATH_BASE_WIDTH/2)
ppathLU = QPainterPath()
hashMarkGen(ppathLU,ppRect.bottomLeft(),ppRect.bottomRight(),ppRect.topRight())
ppathRU = QPainterPath()
hashMarkGen(ppathRU,ppRect.bottomRight(),ppRect.bottomLeft(),ppRect.topLeft())
ppathRD = QPainterPath()
hashMarkGen(ppathRD,ppRect.topRight(),ppRect.topLeft(),ppRect.bottomLeft())
ppathLD = QPainterPath()
hashMarkGen(ppathLD,ppRect.topLeft(),ppRect.topRight(),ppRect.bottomRight())


class PreCrossoverHandleGroup(QGraphicsItem):
    def __init__(self, parent=None):
        """
        Merely initialize a PreCrossoverHandle buffer
        sets the group's parent to preferably a PathHelixGroup sets each
        PreCrossoverHandle's parent in the buffer initially to the group
        """
        super(PreCrossoverHandleGroup, self).__init__(parent)
        self.rect = QRectF(0, 0, 0, 0)
        self.handles = []
        for i in range(256):
            self.handles.append(PreCrossoverHandle(parent=self))
        # end for
        self.activeCount = 0
    # end def

    def boundingRect(self):
        return self.rect
    # end def

    def paint(self, painter, option, widget=None):
        pass
    # end def

    def updateActiveHelix(self, vhelix):
        """
        Collects the locations of each type of PreCrossover from the
        recently activated VirtualHelix vhelix. Each index corresponds
        to a pair of PreCrossoverHandle that must be updated and displayed.
        """
        scafL = vhelix.getLeftScafPreCrossoverIndexList()
        scafR = vhelix.getRightScafPreCrossoverIndexList()
        stapL = vhelix.getLeftStapPreCrossoverIndexList()
        stapR = vhelix.getRightStapPreCrossoverIndexList()
        count = 2*sum([len(scafL), len(scafR), len(stapL), len(stapR)])

        # Procees Scaffold PreCrossoverHandles
        strandtype = StrandType.Scaffold
        ph1 = self.parentItem().getPathHelix(vhelix)
        i = 0
        for [neighbor, index] in scafL:
            if vhelix.parity() == Parity.Even:
                orient1 = HandleOrient.LeftUp
                orient2 = HandleOrient.LeftDown
            else:
                orient1 = HandleOrient.LeftDown
                orient2 = HandleOrient.LeftUp
            ph2 = self.parentItem().getPathHelix(neighbor)
            self.handles[i].configure(strandtype, orient1, index, ph2, ph1)
            self.handles[i+1].configure(strandtype, orient2, index, ph1, ph2)
            i += 2
        for [neighbor, index] in scafR:
            if vhelix.parity() == Parity.Even:
                orient1 = HandleOrient.RightUp
                orient2 = HandleOrient.RightDown
            else:
                orient1 = HandleOrient.RightDown
                orient2 = HandleOrient.RightUp
            ph2 = self.parentItem().getPathHelix(neighbor)
            self.handles[i].configure(strandtype, orient1, index, ph2, ph1)
            self.handles[i+1].configure(strandtype, orient2, index, ph1, ph2)
            i += 2
        # Process Staple PreCrossoverHandles
        strandtype = StrandType.Staple
        for [neighbor, index] in stapL:
            if vhelix.parity() == Parity.Even:
                orient1 = HandleOrient.LeftUp
                orient2 = HandleOrient.LeftDown
            else:
                orient1 = HandleOrient.LeftDown
                orient2 = HandleOrient.LeftUp
            ph2 = self.parentItem().getPathHelix(neighbor)
            self.handles[i].configure(strandtype, orient1, index, ph2, ph1)
            self.handles[i+1].configure(strandtype, orient2, index, ph1, ph2)
            i += 2
        for [neighbor, index] in stapR:
            if vhelix.parity() == Parity.Even:
                orient1 = HandleOrient.RightUp
                orient2 = HandleOrient.RightDown
            else:
                orient1 = HandleOrient.RightDown
                orient2 = HandleOrient.RightUp
            ph2 = self.parentItem().getPathHelix(neighbor)
            self.handles[i].configure(strandtype, orient1, index, ph2, ph1)
            self.handles[i+1].configure(strandtype, orient2, index, ph1, ph2)
            i += 2

        # hide extra precrossoverhandles as necessary
        if self.activeCount > count:
            for i in range(count, self.activeCount):
                self.handles[i].hide()
            # end for
        # end if
        self.activeCount = count
    # end def
# end class


class PreCrossoverHandle(QGraphicsItem):
    """
    PreCrossoverHandle responds to mouse input and serves as an interface
    for adding scaffold crossovers

    Each handle is created by the PathController. Its parent is a PathHelix
    """
    pen = QPen(styles.pchstroke, styles.PATH_STRAND_STROKE_WIDTH)
    pen.setCapStyle(Qt.FlatCap)  # or Qt.RoundCap
    pen.setJoinStyle(Qt.RoundJoin)
    baseWidth = styles.PATH_BASE_WIDTH
    _myfont = QFont("Times", 10, QFont.Bold)

    def __init__(self, parent=None):
        """
        Merely initialize a PreCrossoverHandle and some basic details
        like it's label and rectangle
        
        initially these are all hidden as well
        """
        super(PreCrossoverHandle, self).__init__(parent)
        self.undoStack = parent.parentItem().pathController.mainWindow.undoStack
        self.rect = QRectF(0, 0, styles.PATH_BASE_WIDTH/2, styles.PATH_BASE_WIDTH/2)
        self.type = None
        self.index = None
        self.orientation = None
        self.partner = None
        self.setZValue(styles.ZPRECROSSOVERHANDLE)
        self.label = QGraphicsSimpleTextItem("", parent=self)
        self.label.setParentItem(self)
        self.label.setPos(0, 0)
        self.label.setFont(self._myfont)
        self.label.hide()
        self.hide()
        self.painterpath = ppathLD

    def configure(self, strandtype, orientation, index, partner, parent):
        """
        sets up the PCH to be tied to a helix as its parent such that
            when a helix is repostioned, it will redraw correctly
        gives it a partner to know who it needs to be connected to
        figures out the orientation to draw the PCH on the helix
        
        """
        self.setParentItem(parent)
        self.type = strandtype
        self.orientation = orientation
        self.index = index
        self.partner = partner
        self.label.setText("%d" % (self.partner.number()))

        if orientation == HandleOrient.RightDown:
            self.rightDrawConfig()
            self.downDrawConfig()
            self.painterpath = ppathRD
        elif orientation == HandleOrient.LeftDown:
            self.leftDrawConfig()
            self.downDrawConfig()
            self.painterpath = ppathLD
        elif orientation == HandleOrient.LeftUp:
            self.leftDrawConfig()
            self.upDrawConfig()
            self.painterpath = ppathLU
        elif orientation == HandleOrient.RightUp:
            self.rightDrawConfig()
            self.setX(self.baseWidth*index+styles.PATH_BASE_WIDTH/2)
            self.upDrawConfig()
            self.painterpath = ppathRU
        else:
            raise AttributeError("PCH orientation not recognized")
        self.show()
        self.label.show()
    # end def

    def rightDrawConfig(self):
        self.setX(self.baseWidth*self.index + styles.PATH_BASE_WIDTH/2)
        offset = self.label.boundingRect().width()/2
        self.label.setX(-offset)
    # end def

    def leftDrawConfig(self):
        self.setX(self.baseWidth*self.index)
        offset = self.label.boundingRect().width()/2
        self.label.setX(self.baseWidth/2 - offset)
    # end def

    def upDrawConfig(self):
        self.label.setY(-0.57*self.baseWidth)
        self.setY(-0.75*self.baseWidth)
    #end def
    
    def downDrawConfig(self):
        self.label.setY(0.48*self.baseWidth)
        self.setY(2.25*self.baseWidth)
    #end def 

    def boundingRect(self):
        return self.rect

    def paint(self, painter, option, widget=None):
        painter.setPen(self.pen)
        painter.drawPath(self.painterpath)
        # self.handlePainter(painter)
    # end def

    def mousePressEvent(self, event):
        """
        This handles installing crossovers
        """
        if event.button() != Qt.LeftButton:
            QGraphicsItem.mousePressEvent(self,event)
        # end else
        else:
            pass
            # install crossover
            # FILL IN
        # end else
    # end def
# end class
