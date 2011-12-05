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
pathselection.py

Created by Nick on 2011-06-27.
"""

from views import styles
from math import floor
import util

# import Qt stuff into the module namespace with PySide, PyQt4 independence
util.qtWrapImport('QtCore', globals(), ['Qt', 'QPointF', 'QEvent'])
util.qtWrapImport('QtGui', globals(), [ 'QPen', 'QBrush', 'QColor', 'qApp',\
                                        'QGraphicsItem', \
                                        'QGraphicsItemGroup',\
                                        'QGraphicsPathItem', 'QPainterPath'])

class SelectionItemGroup(QGraphicsItemGroup):
    """
    SelectionItemGroup
    """
    def __init__(self, boxtype, constraint='y', parent=None):
        super(SelectionItemGroup, self).__init__(parent)
        self._viewroot = parent
        self.setFiltersChildEvents(True)
        self.setHandlesChildEvents(True)
        self.setFlag(QGraphicsItem.ItemIsSelectable)
        self.setFlag(QGraphicsItem.ItemIsFocusable) # for keyPressEvents
        self.setFlag(QGraphicsItem.ItemHasNoContents)

        self._pen = QPen(styles.bluestroke, styles.PATH_SELECTBOX_STROKE_WIDTH)

        self.selectionbox = boxtype(self)

        self._dragEnable = False
        self._dragged = False
        self._baseClick = 0 #  special tri-state counter to enable deselection on click away 

        self._r0 = 0  # save original mousedown
        self._r = 0  # latest position for moving

        # self._lastKid = 0

        # this keeps track of mousePressEvents within the class
        # to aid in intellignetly removing items from the group 
        self._addedToPressList = False

        self._pendingToAddDict = {}

        if constraint == 'y':
            self.getR = self.selectionbox.getY
            self.translateR = self.selectionbox.translateY
        else:
            self.getR = self.selectionbox.getX
            self.translateR = self.selectionbox.translateX

        self._normalSelect = True
        self._instantAdd = False
        
        self.setZValue(styles.ZPATHSELECTION)
    # end def

    def pendToAdd(self, item):
        self._pendingToAddDict[item] = True
    # end def

    def isPending(self, item):
        return item in self._pendingToAddDict
    # end def

    def pendToRemove(self, item):
        if item in self._pendingToAddDict:
            del self._pendingToAddDict[item]
    # end def

    def setNormalSelect(self, boolVal):
        self._normalSelect = boolVal
    # end def

    def isNormalSelect(self):
        return self._normalSelect
    # end def

    def processPendingToAddList(self):
        doc = self._viewroot.document()
        if len(self._pendingToAddDict) == 0:
            pass
        else:
            for item in self._pendingToAddDict:
                item.modelSelect(doc)
                self.addToGroup(item)

        self._pendingToAddDict = {}
        doc.updateSelection()
    # end def
    
    def setInstantAdd(self, boolval):
        if boolval:
            self._baseClick = 0
            self._instantAdd = 1
        else:
            self._instantAdd = 0
    # end def

    def paint(self, painter, option, widget=None):
        # painter.setBrush(QBrush(QColor(255,128,255,128)))
        painter.setPen(QPen(styles.redstroke))
        painter.drawRect(self.boundingRect())
        pass
    # end def

    def selectionLock(self):
        return self._viewroot.selectionLock()
    # end def

    def setSelectionLock(self, selectionGroup):
        self._viewroot.setSelectionLock(selectionGroup)
    # end def

    # def keyPressEvent(self, event):
    #     """
    #     Must intercept invalid input events.  Make changes here
    #     """
    # 
    #     a = event.key()
    #     if a in [Qt.Key_Backspace, Qt.Key_Delete]:
    #         thePart = self._partItem.part()
    #         vhList = [thePart.getVirtualHelix(i.number()) for i in self.childItems()]
    #         self.clearSelection(False)
    #         thePart.removeVirtualHelicesAt(vhList)
    #         # print "getting delete events "
    #         return
    #     else:
    #         return QGraphicsItemGroup.keyPressEvent(self, event)
    # # end def

    def mousePressEvent(self, event):
        print "select mp"
        self._instantAdd = 1
        if event.button() != Qt.LeftButton:
            QGraphicsItemGroup.mousePressEvent(self, event)
        else:
            self._dragEnable = True

            # required to get the itemChanged event to work 
            # correctly for this
            self.setSelected(True)

            # self.selectionbox.resetTransform()
            self.selectionbox.resetPosition()
            self.selectionbox.refreshPath()

            # self.selectionbox.resetTransform()
            self.selectionbox.resetPosition()
            self.selectionbox.show()

            # for some reason we need to skip the first mouseMoveEvent
            self._dragged = False

            if self._addedToPressList == False:
                self._addedToPressList = True
                self.scene().views()[0].addToPressList(self)
    # end def

    def mouseMoveEvent(self, event):
        if self._dragEnable == True:
            # map the item to the scene coordinates
            # to help keep coordinates uniform
            rf = self.getR(self.mapFromScene(QPointF(event.scenePos())))
            # for some reason we need to skip the first mouseMoveEvent
            if self._dragged == False:
                self._dragged = True
                self._r0 = rf
            # end if
            else:
                delta = self.selectionbox.delta(rf, self._r0)
                self.translateR(delta)
            # end else
            self._r = rf
        # end if
        else:
            QGraphicsItemGroup.mouseMoveEvent(self, event)
        # end else
    # end def

    def customMouseRelease(self, event):
        """docstring for customMouseRelease"""
        self.selectionbox.hide()
        self.selectionbox.resetTransform()
        self._dragEnable = False
        # now do stuff
        if not (self._r0 == 0 and self._r == 0):
            self.selectionbox.processSelectedItems(self._r0, self._r)
        # end if
        self._r0 = 0  # reset
        self._r = 0  # reset
        print "mouse release", self._baseClick, self._instantAdd
        self._addedToPressList = False
        # if self._baseClick == 0:
        #     self._addedToPressList = True
        #     self._baseClick = 1
        #     self.scene().views()[0].addToPressList(self)
        # elif self._baseClick == 1 and self._instantAdd != 1:
        #     self._baseClick = 0
        #     print "clear due to click"
        #     self._instantAdd = 2
        #     self.clearSelection(False)
        if self._instantAdd != 1:
            print "clear due to click"
            self._instantAdd = 0
            self.clearSelection(False)
        else:
            self._instantAdd = 2
            self._addedToPressList = True
            self.scene().views()[0].addToPressList(self)
    # end def

    def clearSelection(self, value):
        if value == False:
            self.selectionbox.hide()
            self.selectionbox.resetPosition()
            self.removeSelectedItems()
            self._viewroot.setSelectionLock(None)
            self.clearFocus() # this is to disable delete keyPressEvents
        # end if
        else:
            self.setFocus() # this is to get delete keyPressEvents
        self.update(self.boundingRect())
    # end def

    def itemChange(self, change, value):
        """docstring for itemChange"""
        # if change == QGraphicsItem.ItemSelectedHasChanged:
        if change == QGraphicsItem.ItemSelectedChange:
            if value == False and self._instantAdd == 0:
                print "clear due to deselect"
                self.clearSelection(False)
                return False
            else:
                print "clear instant add"
                if self._addedToPressList == False:
                    self._addedToPressList = True
                    self.scene().views()[0].addToPressList(self)
                    self._instantAdd = 0
                return True
        elif change == QGraphicsItem.ItemChildAddedChange:
            if self._addedToPressList == False:
                # self._lastKid += 1
                print "kid added"
                self._instantAdd = 1
                self.setParentItem(self.selectionbox.boxParent())
                self._addedToPressList = True
                self.scene().views()[0].addToPressList(self)
            return
        return QGraphicsItemGroup.itemChange(self, change, value)
    # end def

    def removeChild(self, child):
        """
        remove only the child and ask it to 
        restore it's original parent
        """
        doc = self._viewroot.document()
        tPos = child.scenePos()
        self.removeFromGroup(child)
        child.modelDeselect(doc)
    # end def

    def removeSelectedItems(self):
        """docstring for removeSelectedItems"""
        doc = self._viewroot.document()
        for item in self.childItems():
            self.removeFromGroup(item)
            item.modelDeselect(doc)
            # if not item.isSelected():
            #     # call this first before removing from the group to 
            #     # prevent unecessary change events
            #     self.removeFromGroup(item)
            #     item.modelDeselect(doc)
            # end if
        # end for
    # end def

    def reParent(self, boolval):
        if boolval:
            self._tempList = [item for item in self.childItems()]
            for item in self._tempList:
                item.tempReparent()
            # end for
        else:
            for item in self._tempList:
                self.addToGroup(item)
            # end for
# end class


class VirtualHelixHandleSelectionBox(QGraphicsPathItem):
    """
    docstring for VirtualHelixHandleSelectionBox
    """
    _helixHeight = styles.PATH_HELIX_HEIGHT + styles.PATH_HELIX_PADDING
    _radius = styles.VIRTUALHELIXHANDLEITEM_RADIUS
    _penWidth = styles.SLICE_HELIX_HILIGHT_WIDTH
    _boxPen = QPen(styles.bluestroke, _penWidth)

    def __init__(self, itemGroup):
        """
        The itemGroup.parentItem() is expected to be a partItem
        """
        super(VirtualHelixHandleSelectionBox, self).__init__(itemGroup.parentItem())
        self._itemGroup = itemGroup
        self._rect = itemGroup.boundingRect()
        self.hide()
        self.setPen(self._boxPen)
        self.setZValue(styles.ZPATHSELECTION)
        self._bounds = None
        self._pos0 = QPointF()
    # end def

    def getY(self, pos):
        pos = self._itemGroup.mapToScene(QPointF(pos))
        return pos.y()
    # end def

    def translateY(self, delta):
         self.setY(delta)
     # end def

    def refreshPath(self):
        self.prepareGeometryChange()
        self.setPath(self.painterPath())
        self._pos0 = self.pos()
    # end def

    def painterPath(self):
        iG = self._itemGroup
        # the childrenBoundingRect is necessary to get this to work
        rect = self.mapRectFromItem(iG,iG.childrenBoundingRect() )
        radius = self._radius

        path = QPainterPath()
        path.addRoundedRect(rect, radius, radius)
        path.moveTo(rect.right(),\
                         rect.center().y())
        path.lineTo(rect.right() + radius / 2,\
                         rect.center().y())
        return path
    # end def

    def processSelectedItems(self, rStart, rEnd):
        """docstring for processSelectedItems"""
        margin = styles.VIRTUALHELIXHANDLEITEM_RADIUS
        delta = (rEnd - rStart)  # r delta
        midHeight = (self.boundingRect().height()) / 2 - margin
        helixHeight = self._helixHeight

        if abs(delta) < midHeight:  # move is too short for reordering
            return
        if delta > 0:  # moved down, delta is positive
            indexDelta = int((delta - midHeight) / helixHeight)
        else:  # moved up, delta is negative
            indexDelta = int((delta + midHeight) / helixHeight)
        # sort on y to determine the extremes of the selection group
        items = sorted(self._itemGroup.childItems(), key=lambda vhhi: vhhi.y())
        partItem = items[0].partItem()
        partItem.reorderHelices(items[0].number(),\
                                items[-1].number(),\
                                indexDelta)
    # end def

    def boxParent(self):
        temp = self._itemGroup.childItems()[0].partItem()
        self.setParentItem(temp)
        return temp
    # end def

    def bounds(self):
        return self._bounds
    # end def

    def delta(self, yf, y0):
        return yf-y0
    # end def

    def resetPosition(self):
        self.setPos(self._pos0)
    # end def
# end class

class EndpointHandleSelectionBox(QGraphicsPathItem):
    _penWidth = styles.SLICE_HELIX_HILIGHT_WIDTH
    _boxPen = QPen(styles.selected_color, _penWidth)
    _baseWidth = styles.PATH_BASE_WIDTH

    def __init__(self, itemGroup):
        """
        The itemGroup.parentItem() is expected to be a partItem
        """
        super(EndpointHandleSelectionBox, self).__init__(itemGroup.parentItem())
        self._itemGroup = itemGroup
        self._rect = itemGroup.boundingRect()
        self.hide()
        self.setPen(self._boxPen)
        self.setZValue(styles.ZPATHSELECTION)
        self._bounds = (0,0)
        self._pos0 = QPointF()
    # end def

    def getX(self, pos):
        return pos.x()
    # end def

    def translateX(self, delta):
        self.setX(self._baseWidth*delta)
    # end def

    def resetPosition(self):
        self.setPos(self._pos0)

    def delta(self, xf, x0):
        boundL, boundH = self._bounds
        delta = int(floor((xf-x0) / self._baseWidth))
        if delta > 0 and delta > boundH:
            delta = boundH
        elif delta < 0 and abs(delta) > boundL:
            delta = -boundL
        return delta

    def refreshPath(self):
        tempLow, tempHigh = self._itemGroup._viewroot.document().getSelectionBounds()
        self._bounds = (tempLow, tempHigh)
        self.prepareGeometryChange()
        self.setPath(self.painterPath())
        self._pos0 = self.pos()
    # end def

    def painterPath(self):
        bw = self._baseWidth
        iG = self._itemGroup
        # the childrenBoundingRect is necessary to get this to work
        rect = self.mapRectFromItem(iG,iG.childrenBoundingRect() )
        if rect.width() < bw:
            rect.adjust(-bw/4, 0, bw/2, 0)
        path = QPainterPath()
        path.addRect(rect)
        # path.addRoundedRect(rect, radius, radius)
        # path.moveTo(rect.right(),\
        #                  rect.center().y())
        # path.lineTo(rect.right() + radius / 2,\
        #                  rect.center().y())
        return path
    # end def

    def processSelectedItems(self, rStart, rEnd):
        """docstring for processSelectedItems"""
        self._itemGroup.reParent(True)
        delta = self.delta(rEnd, rStart)
        self._itemGroup._viewroot.document().resizeSelection(delta)
        self._itemGroup.reParent(False)
    # end def

    def boxParent(self):
        temp = self._itemGroup.childItems()[0].partItem()
        self.setParentItem(temp)
        return temp
    # end def

    def bounds(self):
        return self._bounds
    # end def
# end class
