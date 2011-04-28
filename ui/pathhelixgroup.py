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
pathhelixgroup.py

Created by Shawn on 2011-01-27.
"""

from PyQt4.QtCore import QRectF, QPointF, QEvent, pyqtSlot, QObject, Qt
from PyQt4.QtCore import pyqtSignal
from PyQt4.QtGui import QBrush, QPen, qApp, QGraphicsSimpleTextItem, QFont
from PyQt4.QtGui import QGraphicsItem, QGraphicsItemGroup
from .pathhelix import PathHelix
from handles.activeslicehandle import ActiveSliceHandle
from handles.breakpointhandle import BreakpointHandle
from handles.pathhelixhandle import PathHelixHandle
from model.base import EndType
from model.virtualhelix import StrandType
from model.dnapart import LatticeType
import styles


class PhgObject(QObject):
    """
    A placeholder class until QGraphicsObject is available to allow signaling
    """
    scaffoldChange = pyqtSignal(int)
    def __init__(self):
        super(PhgObject, self).__init__()
# end class

class RoundMoveBox(QGraphicsItem):
    radius = styles.PATHHELIXHANDLE_RADIUS
    def __init__(self, rect, parent=None):
        super(RoundMoveBox, self).__init__(parent)
        self.parent = parent
        self.setParentItem(parent) 
        self.rect = rect
        self.drawMe = False
        # self.setFlag(QGraphicsItem.ItemIsMovable)
        self.pen = QPen(styles.bluestroke, styles.SLICE_HELIX_HILIGHT_WIDTH)
    # end def

    def paint(self, painter, option, widget=None):
        if self.drawMe == True:
            painter.setPen(self.pen)
            painter.drawRoundedRect(self.boundingRect(), self.radius, self.radius)
    # end def

    def boundingRect(self):
        return self.rect
    # end def

    def setRect(self, rect):
        self.rect = rect
# end class

class SquareMoveBox(QGraphicsItem):
    # radius = styles.PATHHELIXHANDLE_RADIUS
    def __init__(self, rect, parent=None):
        super(SquareMoveBox, self).__init__(parent)
        self.parent = parent
        self.setParentItem(parent) 
        self.rect = rect
        self.drawMe = False
        # self.setFlag(QGraphicsItem.ItemIsMovable)
        self.pen = QPen(styles.bluestroke, styles.SLICE_HELIX_HILIGHT_WIDTH)
    # end def

    def paint(self, painter, option, widget=None):
        if self.drawMe == True:
            painter.setPen(self.pen)
            painter.drawRect(self.boundingRect())
    # end def

    def boundingRect(self):
        return self.rect
    # end def

    def setRect(self, rect):
        self.rect = rect
# end class

class PathHelixGroupSelection(QGraphicsItemGroup):
    def __init__(self, boxtype=RoundMoveBox, constraint='y',parent=None):
        super(PathHelixGroupSelection, self).__init__(parent)
        self.parent = parent
        self.setParentItem(parent) 
        self.setFiltersChildEvents(True)
        # self.setFlag(QGraphicsItem.ItemIsMovable)
        self.setFlag(QGraphicsItem.ItemIsSelectable)
        self.pen = QPen(styles.bluestroke, styles.SLICE_HELIX_HILIGHT_WIDTH)
        self.drawMe = False
        self.drawn = False
        
        self.font = QFont("Times", 30, QFont.Bold)
        self.label = QGraphicsSimpleTextItem("Part 1")
        self.label.setFont(self.font)
        self.label.setParentItem(self)
        self.label.setPos(0,0)
        
        # make its parent not itself so we can translate it independently
        self.movebox = boxtype(self.boundingRect(), parent)
        self.dragEnable = False
        self._r0 = 0
        if constraint == 'y':    
            self.getR = self.getY
            self.translateR = self.translateY
        else:
            self.getR = self.getX
            self.translateR = self.translateX
    # end def
    
    def getY(self, event):
        return event.pos().y()
    # end def
    
    def getX(self, event):
        return event.pos().x()
    # end def
    
    def translateY(self,yf):
        self.movebox.translate( 0,(yf - self._r0))
    # end def
    
    def translateX(self,xf):
        self.movebox.translate( (xf - self._r0),0)
    # end def
    
    def paint(self, painter, option, widget=None):
        pass
        # self.movebox.paint(painter, option, widget=None)
        # if self.drawMe == True:
        #     painter.setPen(self.pen)
        #     painter.drawRect(self.boundingRect())
        #     self.drawn = True
        #     print "drawn", self.isSelected()
        #     # self.bringToFront()
    # end def
            
    def bringToFront(self):
        """collidingItems gets a list of all items that overlap. sets
        this items zValue to one higher than the max."""
        zval = 1
        items = self.scene().items(self.boundingRect()) # the is a QList
        for item in items:
            temp = item.zValue()
            if temp >= zval:
                zval = item.zValue() + 1
            # end if
        # end for
        self.setZValue(zval)
    # end def
    
    def mousePressEvent(self, event):
        if event.button() != Qt.LeftButton:
            # print "this might work press plus"
            QGraphicsItemGroup.mousePressEvent(self,event)
        else:
            # print "whoops"
            if self.isSelected():
                # print "this might work press"
                self.dragEnable = True
                self.movebox.resetTransform()
                self.movebox.drawMe = True
                self.movebox.setRect(self.boundingRect())
                self._r0 = self.getR(event) 
                self.scene().views()[0].addToPressList(self)
    # end def
    
    def mouseMoveEvent(self, event):
        if self.isSelected() and self.dragEnable == True:
            # print "nachos!!!"
            # add in translation here
            rf = self.getR(event) 
            self.translateR(rf)
            self._r0 = rf
        else:
            print "this might work move plus", event.button()
            QGraphicsItemGroup.mouseMoveEvent(self,event)

    # end def
    
    def customMouseRelease(self, event):
        """docstring for customMouseRelease"""
        # print "this might work release"
        if self.isSelected():
            # print "selected!!!"
            # self.drawMe = True
            # self.drawn = False
            # self.update(self.boundingRect())
            
            self.movebox.drawMe = False
            self.movebox.resetTransform()
            # self.movebox.setRect(self.boundingRect())
            # self.movebox.update(self.boundingRect())
        # end if
        else:
            # self.drawMe = False
            self.movebox.drawMe = False
            self.movebox.resetTransform()
        # end else
        self.dragEnable = False
    # end def
    
    def itemChange(self, change, value):
        """"""
        if change == QGraphicsItem.ItemSelectedHasChanged:
            print "looking for a selection change..."
            
            if value == False:# and qApp.mouseButtons() != Qt.LeftButton:# self.drawn == True:
                # self.drawMe = False
                self.movebox.drawMe = False
                self.movebox.resetTransform()
                
                for item in self.childItems():
                    if not item.isSelected():
                        # print "before", item.parentItem()
                        self.removeFromGroup(item)
                        # print "after", item.parentItem()
                        try:
                            item.restoreParent()
                        except ValueError:
                            pass
                        #print "removed ", item.number
                        item.setSelected(False) 
                    # end if
                # end for
            # end if
            else:
                print "group selected!"
                # self.drawn = False
        return QGraphicsItemGroup.itemChange(self, change, value)
    # end def
# end class

class PathHelixGroup(QGraphicsItem):
    """
    PathHelixGroup maintains data and state for a set of object that provide
    an interface to the schematic view of a DNA part. These objects include
    the PathHelix, PathHelixHandles, and ActiveSliceHandle.
    """
    handleRadius = styles.SLICE_HELIX_RADIUS
    
    def __init__(self, dnaPartInst, activeslicehandle,\
                       controller=None,\
                       parent=None):
        super(PathHelixGroup, self).__init__(parent)
        self.dnaPartInst = dnaPartInst
        self.part = dnaPartInst.part()
        self.pathController = controller
        self.activeslicehandle = activeslicehandle
        self.parent = parent
        self.setParentItem(parent) 
        self.numToPathHelix = {}
        self.numToPathHelixHandle = {}
        count = self.part.getVirtualHelixCount()
        if count > 0: # initalize if loading from file, otherwise delay
            self.activeslicehandle.setParentItem(self)
        # set up signals
        self.qObject = PhgObject()
        self.scaffoldChange = self.qObject.scaffoldChange
        self.rect = QRectF(0, 0, 200, 200) # NC: w,h don't seem to matter
        self.zoomToFit()
        
        self.QGIGroupPathHelix = PathHelixGroupSelection(constraint='y', \
                                                        parent=self)
        self.QGIGroupBreakPoint = PathHelixGroupSelection(boxtype=SquareMoveBox, \
                                                            constraint='x', \
                                                            parent=self)
    # end def

    def paint(self, painter, option, widget=None):
        pass

    def boundingRect(self):
        return self.rect

    @pyqtSlot(int)
    def helixAddedSlot(self, number):
        """
        Retrieve reference to new VirtualHelix vh based on number relayed
        by the signal event. Next, create a new PathHelix associated 
        with vh and draw it on the screen. Finally, create or update
        the ActiveSliceHandle.
        """
        vh = self.part.getVirtualHelix(number)
        count = self.part.getVirtualHelixCount()
        # add PathHelixHandle
        x = 0#5*self.handleRadius
        xoff = -6*self.handleRadius
        y = count * (styles.PATH_BASE_HEIGHT + styles.PATH_HELIX_PADDING)
        phhY = ((styles.PATH_BASE_HEIGHT-(styles.PATHHELIXHANDLE_RADIUS*2))/2)
        phh = PathHelixHandle(vh, QPointF(xoff, y+phhY), self)
        self.numToPathHelixHandle[number] = phh
        phh.setParentItem(self)
        # add PathHelix
        ph = PathHelix(vh, QPointF(0, y), self)
        self.numToPathHelix[number] = ph
        ph.setParentItem(self)
        # update activeslicehandle
        if count == 1: # first vhelix added by mouse click
            self.activeslicehandle.setParentItem(self)
        # end if
        self.activeslicehandle.resize(count)
        self.zoomToFit()  # Auto zoom to center the scene
    # end def

    def zoomToFit(self):
        # Auto zoom to center the scene
        thescene = self.scene()
        theview = thescene.views()[0]
        theview.zoomToFit()
    # end def

    @pyqtSlot(int)
    def helixRemovedSlot(self, number):
        scene = self.scene()
        count = self.part.getVirtualHelixCount()
        # remove PathHelix
        ph = self.numToPathHelix[number]
        scene.removeItem(ph)
        del self.numToPathHelix[number]
        # remove PathHelixHandle
        phh = self.numToPathHelixHandle[number]
        scene.removeItem(phh)
        del self.numToPathHelixHandle[number]
        # update or hide activeslicehandle
        if count == 0:
            scene.removeItem(self.activeslicehandle)
        else:
            rect = self.activeslicehandle.boundingRect()
            self.activeslicehandle.resize(count)
            self.parent.update(rect)
    # end def

    @pyqtSlot(int, int)
    def sliceHelixClickedSlot(self, number, index):
        """docstring for sliceHelixClickedSlot"""
        vh = self.part.getVirtualHelix(number)
        ph = self.numToPathHelix[number]

        # move activeslice away from edge
        if index == 0:
            index = 1
            self.activeslicehandle.setPosition(1)
        elif index == self.part.getCanvasSize() - 1:
            index -= 1
            self.activeslicehandle.setPosition(index)

        # initialize some scaffold bases
        if number % 2 == 0:  # even parity
            prev = vh.scaffoldBase(index-1)
            curr = vh.scaffoldBase(index)
            next = vh.scaffoldBase(index+1)
            prev.setNext(curr)
            curr.setPrev(prev)
            curr.setNext(next)
            next.setPrev(curr)
        else:  # odd parity
            prev = vh.scaffoldBase(index+1)
            curr = vh.scaffoldBase(index)
            next = vh.scaffoldBase(index-1)
            prev.setNext(curr)
            curr.setPrev(prev)
            curr.setNext(next)
            next.setPrev(curr)

        # install breakpointhandles
        for index in vh.getScaffold5PrimeEnds():
            bh = BreakpointHandle(vh,\
                                  EndType.FivePrime,\
                                  StrandType.Scaffold,\
                                  index,\
                                  parent=ph)
            ph.addScaffoldBreakHandle(bh)
        for index in vh.getScaffold3PrimeEnds():
            bh = BreakpointHandle(vh,\
                                  EndType.ThreePrime,\
                                  StrandType.Scaffold,\
                                  index,\
                                  parent=ph)
            ph.addScaffoldBreakHandle(bh)
        ph.updateBreakBounds(StrandType.Scaffold)
        ph.redrawLines(StrandType.Scaffold)
    # end def


    def bringToFront(self):
        """collidingItems gets a list of all items that overlap. sets
        this items zValue to one higher than the max."""
        zval = 1
        items = self.collidingItems() # the is a QList
        for item in items:
            temp = item.zValue()
            if temp >= zval:
                zval = item.zValue() + 1
            # end if
        # end for
        self.setZValue(zval)
    # end def