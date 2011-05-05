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
        count = sum([len(scafL), len(scafR), len(stapL), len(stapR)])

        # Procees Scaffold PreCrossoverHandles
        strandtype = StrandType.Scaffold
        ph1 = self.parentItem().getPathHelix(vhelix)
        i = 0
        for [neighbor, index] in scafL:
            if vhelix.parity() == Parity.Even:
                orient = HandleOrient.LeftUp
            else:
                orient = HandleOrient.LeftDown
            ph2 = self.parentItem().getPathHelix(neighbor)
            self.handles[i].configure(strandtype, orient, index, ph2, ph1)
            self.handles[i+1].configure(strandtype, orient, index, ph1, ph2)
            i += 2
        for [neighbor, index] in scafR:
            if vhelix.parity() == Parity.Even:
                orient = HandleOrient.RightUp
            else:
                orient = HandleOrient.RightDown
            ph2 = self.parentItem().getPathHelix(neighbor)
            self.handles[i].configure(strandtype, orient, index, ph2, ph1)
            self.handles[i+1].configure(strandtype, orient, index, ph1, ph2)
            i += 2
        # Process Staple PreCrossoverHandles
        strandtype = StrandType.Staple
        for [neighbor, index] in stapL:
            if vhelix.parity() == Parity.Even:
                orient = HandleOrient.LeftUp
            else:
                orient = HandleOrient.LeftDown
            ph2 = self.parentItem().getPathHelix(neighbor)
            self.handles[i].configure(strandtype, orient, index, ph2, ph1)
            self.handles[i+1].configure(strandtype, orient, index, ph1, ph2)
            i += 2
        for [neighbor, index] in stapR:
            if vhelix.parity() == Parity.Even:
                orient = HandleOrient.RightUp
            else:
                orient = HandleOrient.RightDown
            ph2 = self.parentItem().getPathHelix(neighbor)
            self.handles[i].configure(strandtype, orient, index, ph2, ph1)
            self.handles[i+1].configure(strandtype, orient, index, ph1, ph2)
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
    pen = QPen(styles.minorgridstroke, styles.PATH_GRID_STROKE_WIDTH)
    nopen = QPen(Qt.NoPen)
    brush = QBrush(styles.bluestroke)
    selectbrush = QBrush(styles.bluishstroke)
    nobrush = QBrush(Qt.NoBrush)
    baseWidth = styles.PATH_BASE_WIDTH

    def __init__(self, parent=None):
        """
        Merely initialize a PreCrossoverHandle and some basic details
        like it's label and rectangle
        
        initially these are all hidden as well
        """
        super(PreCrossoverHandle, self).__init__(parent)
        self.undoStack = parent.parentItem().pathController.mainWindow.undoStack
        self.rect = QRectF(0, 0, styles.PATH_BASE_WIDTH, styles.PATH_BASE_WIDTH)
        self.type = None
        self.index = None
        self.orientation = None
        self.partner = None
        self.handlePainter = self.drawLeftUp
        self.setZValue(styles.ZPRECROSSOVERHANDLE)
        self.font = QFont("Times", 30, QFont.Bold)
        self.label = QGraphicsSimpleTextItem("", parent=self)
        self.label.setPos(0, 0)
        self.label.setFont(self.font)
        self.label.hide()
        self.textOffset = 30
        self.hide()

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
        self.label.setText("%d" % self.partner.number())
        self.setX(self.baseWidth*index) # the position on the helix to draw

        if orientation == HandleOrient.RightDown:
            self.downDrawConfig()
            self.handlePainter = self.drawRightDown
        elif orientation == HandleOrient.LeftDown:
            self.downDrawConfig()
            self.handlePainter = self.drawLeftDown
        elif orientation == HandleOrient.LeftUp:
            self.upDrawConfig()
            self.handlePainter = self.drawLeftUp
        elif orientation == HandleOrient.RightUp:
            self.upDrawConfig()
            self.handlePainter = self.drawRightUp
        else:
            print "problem!!! PreCrossoverHandle.configure Scaffold"
        self.show()
        self.label.show()
    # end def

    def upDrawConfig(self):
        self.label.setY(-self.baseWidth-self.textOffset)
        self.setY(-self.baseWidth)     
    #end def
    
    def downDrawConfig(self):
        self.label.setY(2*self.baseWidth+self.textOffset)
        self.setY(2*self.baseWidth) 
    #end def

    def drawLeftUp(self, painter):
        painter.drawLine(self.rect.bottomLeft(), self.rect.bottomRight())
        painter.drawLine(self.rect.bottomRight(), self.rect.topRight())
    # end def

    def drawLeftDown(self, painter):
        painter.drawLine(self.rect.topLeft(), self.rect.topRight())
        painter.drawLine(self.rect.bottomRight(), self.rect.topRight())
    # end def

    def drawRightUp(self, painter):
        painter.drawLine(self.rect.bottomLeft(), self.rect.bottomRight())
        painter.drawLine(self.rect.bottomLeft(), self.rect.topLeft())
    # end def

    def drawRightDown(self, painter):
        painter.drawLine(self.rect.topLeft(), self.rect.topRight())
        painter.drawLine(self.rect.bottomLeft(), self.rect.topLeft())
    # end def

    def boundingRect(self):
        return self.rect

    def paint(self, painter, option, widget=None):
        painter.setPen(self.pen)
        self.handlePainter(painter)
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
