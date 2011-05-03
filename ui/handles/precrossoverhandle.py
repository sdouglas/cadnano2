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
from PyQt4.QtCore import QPointF, QRectF, Qt, SIGNAL, QMimeData
from PyQt4.QtGui import QBrush
from PyQt4.QtGui import QGraphicsItem
from PyQt4.QtGui import QPainterPath
from PyQt4.QtGui import QPolygonF
from PyQt4.QtGui import QPen, QUndoCommand
from model.base import EndType
from model.virtualhelix import StrandType, Parity, BreakType
import ui.styles as styles

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
        self.rect = QRectF(0, 0, 0, 0)
        self.type = None
        self.fiveorthree= None
        self.index = None
        self.parity = None
        self.partner = None
        self.setZValue(styles.ZPRECROSSOVERHANDLE)
        
    def configure(self, strandtype, fiveorthree, index, parity, partner):
        """"""
        self.type = strandtype
        self.fiveorthree = fiveorthree
        self.index = index
        self.parity = parity
        self.partner = partner
        self.rect.setX(self.baseWidth*index)
        
        if strandtype == StrandType.Scaffold:
            if parity == Parity.Odd and fiveorthree == EndType.ThreePrime: 
                self.rect.setY(2*self.baseWidth)
                self.handlePainter = drawRightDown
            if parity == Parity.Odd and fiveorthree == EndType.FivePrime:
                self.rect.setY(2*self.baseWidth) 
                self.handlePainter = drawLeftDown
            if parity == Parity.Even and fiveorthree == EndType.ThreePrime:
                self.rect.setY(-self.baseWidth) 
                self.handlePainter = drawLeftUp
            if parity == Parity.Even and fiveorthree == EndType.FivePrime:
                self.rect.setY(-self.baseWidth) 
                self.handlePainter = drawRightUp
            else:
                print "problem!!! PreCrossoverHandle.configure Scaffold"
        elif strandtype == StrandType.Staple:
            if parity == Parity.Odd and fiveorthree == EndType.ThreePrime:
                self.rect.setY(-self.baseWidth) 
                self.handlePainter = drawLeftUp
            if parity == Parity.Odd and fiveorthree == EndType.FivePrime:
                self.rect.setY(-self.baseWidth)  
                self.handlePainter = drawRightUp
            if parity == Parity.Even and fiveorthree == EndType.ThreePrime:
                self.rect.setY(2*self.baseWidth)  
                self.handlePainter = drawRightDown
            if parity == Parity.Even and fiveorthree == EndType.FivePrime:
                self.rect.setY(2*self.baseWidth)  
                self.handlePainter = drawLeftDown
            else:
                print "problem!!! PreCrossoverHandle.configure Staple"
        else:
            print "Invalid argument, PreCrossoverHandle.configure"            
    # end def
    
    def drawLeftUp(self,painter):
        painter.drawLine(self.rect.bottomLeft(),self.rect.bottomRight())
        painter.drawLine(self.rect.bottomRight(),self.rect.topRight())
    # end def
    
    def drawLeftDown(self,painter):
        painter.drawLine(self.rect.topLeft(),self.rect.topRight())
        painter.drawLine(self.rect.bottomRight(),self.rect.topRight())
    # end def
    
    def drawRightUp(self,painter):
        painter.drawLine(self.rect.bottomLeft(),self.rect.bottomRight())
        painter.drawLine(self.rect.bottomLeft(),self.rect.topLeft())
    # end def
    
    def drawRightDown(self,painter):
        painter.drawLine(self.rect.topLeft(),self.rect.topRight())
        painter.drawLine(self.rect.bottomLeft(),self.rect.topLeft())
    # end def
    
    def boundingRect(self):
        return self.rect

    def paint(self, painter, option, widget=None):
        self.handlePainter(painter)
    # end def

    def setParity(self):
        """docstring for setParity"""
        if self.vhelix.number() % 2 == 0:
            self.parity = Parity.Even
        else:
            self.parity = Parity.Odd

    def getYoffset(self):
        """
        This function returns the appropriate Y offset according to the
        rule that even-parity staples and odd-parity scaffolds run in the
        negative-z direction and are drawn in the lower half of the
        path helix grid.
        """
        if (self.parity == Parity.Even and self.strandType == StrandType.Staple) or \
           (self.parity == Parity.Odd and self.strandType == StrandType.Scaffold):
            return self.baseWidth
        else:
            return 0

    def mousePressEvent(self, event):
        if event.button() != Qt.LeftButton:
            QGraphicsItem.mousePressEvent(self,event)
        else:
            # if self.parentItem() == self.restoreParentItem:
            self.scene().views()[0].addToPressList(self)
            self._dragMode = True
            self.scene().clearSelection()
            self.pressX = event.scenePos().x()
            self.pressXoffset = self.pressX % self.baseWidth
            self.setCursor(Qt.ClosedHandCursor)
    # end def

