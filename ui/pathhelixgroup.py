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
from PyQt4.QtGui import QBrush, QPen, qApp, QGraphicsTextItem, QFont
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
        self.pen = QPen(styles.bluestroke, styles.SLICE_HELIX_HILIGHT_WIDTH)
    # end def

    def paint(self, painter, option, widget=None):
        if self.drawMe == True:
            painter.setPen(self.pen)
            painter.drawRoundedRect(self.rect, self.radius, self.radius)
            painter.drawLine(self.rect.right(),\
                             self.rect.center().y(),\
                             self.rect.right()+self.radius/2,\
                             self.rect.center().y())
    # end def

    def boundingRect(self):
        return self.rect
    # end def

    def setRect(self, rect):
        self.rect = rect
# end class

class SquareMoveBox(QGraphicsItem):
    def __init__(self, rect, parent=None):
        super(SquareMoveBox, self).__init__(parent)
        self.parent = parent
        self.setParentItem(parent) 
        self.rect = rect
        self.drawMe = False
        self.pen = QPen(styles.bluestroke, styles.PATH_SELECTBOX_STROKE_WIDTH)
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
        self.prepareGeometryChange()
        self.rect = rect
# end class

class PathHelixGroupSelection(QGraphicsItemGroup):
    helixHeight = styles.PATH_BASE_HEIGHT + styles.PATH_HELIX_PADDING
    
    def __init__(self, boxtype=RoundMoveBox, constraint='y', parent=None):
        super(PathHelixGroupSelection, self).__init__(parent)
        self.parent = parent
        self.setParentItem(parent) 
        self.setFiltersChildEvents(True)
        self.setFlag(QGraphicsItem.ItemIsSelectable)
        self.pen = QPen(styles.bluestroke, styles.PATH_SELECTBOX_STROKE_WIDTH)
        self.drawMe = False
        self.drawn = False
        # make the movebox parent not itself so we can translate it independently
        self.movebox = boxtype(self.boundingRect(), parent)
        self.dragEnable = False
        self._r0 = 0  # save original mousedown
        self._r = 0  # latest position for moving
        self.clickItem = None
        
        if constraint == 'y':
            self.getR = self.getY
            self.translateR = self.translateY
        else:
            self.getR = self.getX
            self.translateR = self.translateX
    # end def
    
    def getY(self, pos):
        return pos.y()
    # end def
    
    def getX(self, pos):
        return pos.x()
    # end def
    
    def translateY(self, yf):
        self.movebox.translate(0, (yf - self._r))
    # end def
    
    def translateX(self, xf):
        self.movebox.translate((xf - self._r), 0)
    # end def
    
    def paint(self, painter, option, widget=None):
        pass
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
            QGraphicsItemGroup.mousePressEvent(self, event)
        else:
            self.dragEnable = True
            self.movebox.resetTransform()
            
            # this code block is a HACK to update the boundingbox of the group
            if self.childItems()[0] != None:
                item = self.childItems()[0] 
                self.removeFromGroup(item)
                item.restoreParent()
                self.addToGroup(item)
                
            self.movebox.setRect(self.boundingRect())
            self.movebox.drawMe = True
            self._r0 = self.getR(event.scenePos()) 
            self._r = self._r0
            self.scene().views()[0].addToPressList(self)
            self.clickItem = None
    # end def
    
    def mouseMoveEvent(self, event):
        if self.dragEnable == True: #and self.isSelected()
            rf = self.getR(event.scenePos())
            self.translateR(rf)
            self._r = rf
        else:
            # print "this might work move plus", event.button()
            QGraphicsItemGroup.mouseMoveEvent(self,event)

    # end def
    
    def customMouseRelease(self, event):
        """docstring for customMouseRelease"""
        if self.isSelected():
            rd = (self._r - self._r0) # r delta
            # tick mark in middle of the movebox determines where
            # a group gets reinserted into the list
            midHeight = self.movebox.boundingRect().height()/2
            if rd >= 0:  # moved down, delta is postiive
                delta = int((rd - midHeight)/self.helixHeight)
            else:  # moved up, delta is negative
                delta = int((rd + midHeight)/self.helixHeight)
            self.movebox.drawMe = False
            self.movebox.resetTransform()
            self.dragEnable = False
            if delta == 0:  # no change
                return
            # sort on y() to determine selection group boundaries
            items = sorted(self.childItems(), key=lambda phh: phh.y())
            self.parent.reorderHelices(items[0].number(), items[-1].number(), delta)
            print "delta is: ", delta, rd, midHeight, rd - midHeight, (rd - midHeight)/self.helixHeight, int((rd - midHeight)/self.helixHeight)
        # end if
        else:
            self.movebox.drawMe = False
            self.movebox.resetTransform()
            self.dragEnable = False
        # end else
    # end def
    
    def itemChange(self, change, value):
        """"""
        if change == QGraphicsItem.ItemSelectedHasChanged:
            # print "looking for a selection change..."
            
            if value == False:# and qApp.mouseButtons() != Qt.LeftButton:# self.drawn == True:
                # self.drawMe = False
                self.movebox.drawMe = False
                self.movebox.resetTransform()
                self.removeSelectedItems()
                self.parentItem().selectionLock = None
            # end if
            else:
                pass
                # print "group selected!"
                # self.drawn = False
            self.update(self.boundingRect())
        return QGraphicsItemGroup.itemChange(self, change, value)
    # end def
    
    def removeSelectedItems(self):
        for item in self.childItems():
            if not item.isSelected():
                # print "before", item.parentItem()
                self.removeFromGroup(item)
                # print "after", item.parentItem()
                try:
                    item.restoreParent()
                except:
                    pass
                    # print item.
                item.setSelected(False) 
            # end if
        # end for
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
        self.pathHelixList = []
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
        self.QGIGroupBreakPoint = PathHelixGroupSelection(boxtype=SquareMoveBox,\
                                                          constraint='x',\
                                                          parent=self)
        self.font = QFont("Times", 30, QFont.Bold)
        self.label = QGraphicsTextItem("Part 1")
        self.label.setVisible(False) 
        self.label.setFont(self.font)
        self.label.setParentItem(self)
        self.label.setPos(0, 0)
        self.label.setTextInteractionFlags(Qt.TextEditorInteraction)
        self.label.inputMethodEvent = self.handleLabelChange
        self.selectionLock = None
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
        self.label.setVisible(True) 
        
        vh = self.part.getVirtualHelix(number)
        count = self.part.getVirtualHelixCount()
        # add PathHelixHandle
        x = 0#5*self.handleRadius
        xoff = -6*self.handleRadius
        y = count * (styles.PATH_BASE_HEIGHT + styles.PATH_HELIX_PADDING)
        phhY = ((styles.PATH_BASE_HEIGHT-(styles.PATHHELIXHANDLE_RADIUS*2))/2)
        phh = PathHelixHandle(vh, QPointF(xoff, y+phhY), self)
        self.numToPathHelixHandle[number] = phh
        self.pathHelixList.append(number)
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
        del self.pathHelixList[self.pathHelixList.index(number)]
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

    def reorderHelices(self, first, last, delta):
        """
        Reorder helices by moving helices pathHelixList[first:last]
        by a distance delta in the list. Notify each PathHelix and
        PathHelixHandle of its new location.
        """
        firstIndex = self.pathHelixList.index(first)
        lastIndex = self.pathHelixList.index(last)+1
        if delta < 0:  # move group earlier in the list
            newIndex = max(0, delta+firstIndex)
            self.pathHelixList = self.pathHelixList[0:newIndex] +\
                                 self.pathHelixList[firstIndex:lastIndex] +\
                                 self.pathHelixList[newIndex:firstIndex] +\
                                 self.pathHelixList[lastIndex:]
        else: # move group later in list
            newIndex = min(len(self.pathHelixList), delta+lastIndex)
            self.pathHelixList = self.pathHelixList[:firstIndex] +\
                                 self.pathHelixList[lastIndex:newIndex] +\
                                 self.pathHelixList[firstIndex:lastIndex] +\
                                 self.pathHelixList[newIndex:]
        # for i in range(len(self.pathHelixList)):
        #     num = self.pathHelixList[i]
        #     y = (i+1) * (styles.PATH_BASE_HEIGHT + styles.PATH_HELIX_PADDING)
        #     phhY = ((styles.PATH_BASE_HEIGHT-(styles.PATHHELIXHANDLE_RADIUS*2))/2)
        #     self.numToPathHelixHandle[num].setY(y+phhY)
        #     self.numToPathHelix[num].setY(y)
        i = 0
        for num in self.pathHelixList:
            y = (i+1) * (styles.PATH_BASE_HEIGHT + styles.PATH_HELIX_PADDING)
            phhY = ((styles.PATH_BASE_HEIGHT-(styles.PATHHELIXHANDLE_RADIUS*2))/2)
            self.numToPathHelixHandle[num].setY(y+phhY)
            self.numToPathHelix[num].setY(y)
            i += 1
            
    def handleLabelChange(self, event):
        """handleLabelChange is example of how we might handle changes
        to the name in the editor"""
        pass
        # print "", self.label.toPlainText()
        # self.label.setPlainText(self.label.toPlainText() + " cool")
        # QGraphicsTextItem.inputMethodEvent(self.label,event)
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