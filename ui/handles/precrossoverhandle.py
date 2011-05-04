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
pathhelixhandle.py
Created by Shawn on 2011-02-06.
"""

from exceptions import AttributeError, NotImplementedError
from PyQt4.QtCore import QPointF, QRectF, Qt
from PyQt4.QtGui import QBrush
from PyQt4.QtGui import QGraphicsItem, QGraphicsSimpleTextItem
from PyQt4.QtGui import QPainterPath
from PyQt4.QtGui import QPolygonF
from PyQt4.QtGui import QPen, QUndoCommand
from model.base import EndType
from model.virtualhelix import StrandType, Parity, BreakType
import ui.styles as styles

class PreCrossoverHandleGroup(QGraphicsItem):
    def __init__(self, parent=None):
        super(PreCrossoverHandleGroup, self).__init__(parent)
        for i in range(256):
            self.handles[i] = PreCrossoverHandle(parent=self)
        # end for
        self.count = 0
        self.helix = None
    # end def
    
    def updateActiveHelix(self, helix_new, index):
        """ 
        Takes a new helix and an index around which to populate
        precrossovers
        """
        new_count = 0 # the number of precrossovershandles to display
        
        # get the index and other data for a precrossover
        # FILL IN CODE
        for i in range(new_count):
            self.handles[i].configure(  strandtype, \
                                        fiveorthree, index, parity, partner)
        # end for
        
        # hide extra precrossoverhandles as necessary
        if self.count > new_count:
            for i in range(new_count, self.count):
                self.handles[i].hide()
            # end for
        # end if
        
        # update state
        self.helix = helix_new
        self.count = new_count
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
        """Determine parity from vhelix. Make sure the breakpoint is
        drawn in the correct orientation depending on parity and whether
        it's a 5' end or a 3' end."""
        super(PreCrossoverHandle, self).__init__(parent)
        self.undoStack = parent.parentItem().pathController.mainWindow.undoStack
        self.rect = QRectF(0, 0, styles.PATH_BASE_WIDTH , styles.PATH_BASE_WIDTH )
        self.type = None
        self.fiveorthree= None
        self.index = None
        self.parity = None
        self.partner = None
        self.setZValue(styles.ZPRECROSSOVERHANDLE)
        
        self.font = QFont("Times", 30, QFont.Bold)
        self.label = QGraphicsSimpleTextItem("", parent=self)
        self.label.setPos(0, 0)
        self.label.setFont(self.font)
        self.label.hide()
        self.textOffset = 30
        self.hide()
        
    def configure(self, strandtype, fiveorthree, index, parity, partner):
        """"""
        self.type = strandtype
        self.fiveorthree = fiveorthree
        self.index = index
        self.parity = parity
        self.partner = partner
        self.label.setText("%d" % self.partner.number())
        self.setX(self.baseWidth*index)
        
        if strandtype == StrandType.Scaffold:
            if parity == Parity.Odd and fiveorthree == EndType.ThreePrime: 
                self.handlePainter = drawRightDown
            elif parity == Parity.Odd and fiveorthree == EndType.FivePrime:
                self.handlePainter = drawLeftDown
            elif parity == Parity.Even and fiveorthree == EndType.ThreePrime: 
                self.handlePainter = drawLeftUp
            elif parity == Parity.Even and fiveorthree == EndType.FivePrime:
                self.handlePainter = drawRightUp
            else:
                print "problem!!! PreCrossoverHandle.configure Scaffold"
        elif strandtype == StrandType.Staple:
            if parity == Parity.Odd and fiveorthree == EndType.ThreePrime: 
                self.handlePainter = drawLeftUp
            elif parity == Parity.Odd and fiveorthree == EndType.FivePrime: 
                self.handlePainter = drawRightUp
            elif parity == Parity.Even and fiveorthree == EndType.ThreePrime: 
                self.handlePainter = drawRightDown
            elif parity == Parity.Even and fiveorthree == EndType.FivePrime:
                self.handlePainter = drawLeftDown
            else:
                print "problem!!! PreCrossoverHandle.configure Staple"
        else:
            print "Invalid argument, PreCrossoverHandle.configure"
        self.show()
        self.label.show()            
    # end def
    
    def drawLeftUp(self,painter):
        self.label.setY(-self.baseWidth-self.textOffset)
        self.setY(-self.baseWidth)
        painter.drawLine(self.rect.bottomLeft(),self.rect.bottomRight())
        painter.drawLine(self.rect.bottomRight(),self.rect.topRight())
    # end def
    
    def drawLeftDown(self,painter):
        self.label.setY(2*self.baseWidth+self.textOffset)
        self.setY(2*self.baseWidth) 
        painter.drawLine(self.rect.topLeft(),self.rect.topRight())
        painter.drawLine(self.rect.bottomRight(),self.rect.topRight())
    # end def
    
    def drawRightUp(self,painter):
        self.label.setY(-self.baseWidth-self.textOffset)
        self.setY(-self.baseWidth)
        painter.drawLine(self.rect.bottomLeft(),self.rect.bottomRight())
        painter.drawLine(self.rect.bottomLeft(),self.rect.topLeft())
    # end def
    
    def drawRightDown(self,painter):
        self.label.setY(2*self.baseWidth+self.textOffset)
        self.setY(2*self.baseWidth) 
        painter.drawLine(self.rect.topLeft(),self.rect.topRight())
        painter.drawLine(self.rect.bottomLeft(),self.rect.topLeft())
    # end def
    
    def boundingRect(self):
        return self.rect

    def paint(self, painter, option, widget=None):
        self.handlePainter(painter)
    # end def

    def mousePressEvent(self, event):
        if event.button() != Qt.LeftButton:
            QGraphicsItem.mousePressEvent(self,event)
        # end else
        else:
            # install crossover
            # FILL IN
        # end else
    # end def

