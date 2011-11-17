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
import util

# import Qt stuff into the module namespace with PySide, PyQt4 independence
util.qtWrapImport('QtCore', globals(), ['Qt', 'QPointF', 'QEvent'])
util.qtWrapImport('QtGui', globals(), [ 'QPen', 'qApp',\
                                        'QGraphicsItem', \
                                        'QGraphicsItemGroup',\
                                        'QGraphicsPathItem', 'QPainterPath'])

class SelectionItemGroup(QGraphicsItemGroup):
    """
    SelectionItemGroup
    """
    def __init__(self, boxtype, constraint='y', parent=None):
        super(SelectionItemGroup, self).__init__(parent)
        self.setParentItem(parent)
        self.setFiltersChildEvents(True)
        self.setHandlesChildEvents(True)
        self.setFlag(QGraphicsItem.ItemIsSelectable)
        self.setFlag(QGraphicsItem.ItemIsFocusable) # for keyPressEvents
        self.setFlag(QGraphicsItem.ItemHasNoContents)

        self._pen = QPen(styles.bluestroke, styles.PATH_SELECTBOX_STROKE_WIDTH)
        self._partItem = parent

        self.selectionbox = boxtype(self)
        
        self._dragEnable = False
        self._dragged = False
        self._r0 = 0  # save original mousedown
        self._r = 0  # latest position for moving

        self._lastKid = 0

        # this keeps track of mousePressEvents within the class
        # to aid in intellignetly removing items from the group 
        self._addedToPressList = False

        if constraint == 'y':
            self.getR = self.getY
            self.translateR = self.translateY
        else:
            self.getR = self.getX
            self.translateR = self.translateX
    # end def

    def partItem(self):
        return self._partItem

    def getY(self, pos):
        return pos.y()
    # end def

    def getX(self, pos):
        return pos.x()
    # end def

    def translateY(self, yf):
        # print  yf, self._r, (yf - self._r)
        self.selectionbox.translate(0, (yf - self._r))
    # end def

    def translateX(self, xf):
        self.selectionbox.translate((xf - self._r), 0)
    # end def

    def paint(self, painter, option, widget=None):
        # painter.setPen(QPen(styles.redstroke))
        # painter.drawRect(self.boundingRect())
        pass
    # end def

    def keyPressEvent(self, event):
        """
        Must intercept invalid input events.  Make changes here
        """

        a = event.key()
        if a in [Qt.Key_Backspace, Qt.Key_Delete]:
            thePart = self._partItem.part()
            vhList = [thePart.getVirtualHelix(i.number()) for i in self.childItems()]
            self.clearSelection(False)
            thePart.removeVirtualHelicesAt(vhList)
            # print "getting delete events "
            return
        else:
            return QGraphicsItemGroup.keyPressEvent(self, event)
    # end def

    def mousePressEvent(self, event):
        if event.button() != Qt.LeftButton:
            QGraphicsItemGroup.mousePressEvent(self, event)
        else:
            self._dragEnable = True

            # required to get the itemChanged event to work 
            # correctly for this
            self.setSelected(True)

            self.selectionbox.resetTransform()

            self.selectionbox.refreshPath()
            self.selectionbox.resetTransform()
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
            rf = self.getR(self.mapToScene(QPointF(event.pos())))
            # for some reason we need to skip the first mouseMoveEvent
            if self._dragged == False:
                self._dragged = True
                self._r0 = rf
            # end if
            else:
                self.translateR(rf)
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
        # print "maybe process", self.isSelected()
        if not (self._r0 == 0 and self._r == 0):
            # print "process the box"
            self.selectionbox.processSelectedItems(self._r0, self._r)
        # end if
        # print [item.number() for item in self.childItems()]
        self._r0 = 0  # reset
        self._r = 0  # reset
        # print "press release"
        self._addedToPressList = False
    # end def

    def clearSelection(self, value):
        if value == False:
            self.selectionbox.hide()
            self.selectionbox.resetTransform()
            self.removeSelectedItems()
            self.partItem().setSelectionLock(None)
            self.clearFocus() # this is to disable delete keyPressEvents
        # end if
        else:
            self.setFocus() # this is to get delete keyPressEvents
        self.update(self.boundingRect())
    # end def

    def itemChange(self, change, value):
        """docstring for itemChange"""
        if change == QGraphicsItem.ItemSelectedHasChanged:
            if value == False:
                if self._lastKid > 1 and \
                    (qApp.mouseButtons() | Qt.LeftButton) and \
                    self._addedToPressList == True:
                    self.removeChild(self.childItems()[self._lastKid -1])
                else: 
                    self.clearSelection(value)
                    return
        elif change == QGraphicsItem.ItemChildAddedChange:
            self._lastKid += 1
            if self._addedToPressList == False:
                self._addedToPressList = True
                self.scene().views()[0].addToPressList(self)
            # print [item.number() for item in self.childItems()]
            return
        elif change == QGraphicsItem.ItemChildRemovedChange:
            self._lastKid -= 1 
            # print [item.number() for item in self.childItems()]
            return
        return QGraphicsItemGroup.itemChange(self, change, value)
    # end def

    def removeChild(self, child):
        """
        remove only the child and ask it to 
        restore it's original parent
        """
        tPos = child.pos()
        # self.removeFromGroup(child)
        try:
            child.restoreParent(tPos)
        except:
            print type(child.parentObject()), "Parent Error"
    # end def


    def removeSelectedItems(self):
        """docstring for removeSelectedItems"""
        for item in self.childItems():
            if not item.isSelected():
                # call this first before removing from the group to 
                # prevent unecessary change events
                tPos = item.pos()
                # self.removeFromGroup(item)
                try:
                    item.restoreParent(tPos)
                except:
                    print type(item.parentObject()), "Parent Error"
            # end if
        # end for
    # end def
# end class


class PathHelixHandleSelectionBox(QGraphicsPathItem):
    """
    docstring for PathHelixHandleSelectionBox
    """
    _helixHeight = styles.PATH_HELIX_HEIGHT + styles.PATH_HELIX_PADDING
    _radius = styles.VIRTUALHELIXHANDLEITEM_RADIUS
    _penWidth = styles.SLICE_HELIX_HILIGHT_WIDTH
    _boxPen = QPen(styles.bluestroke, _penWidth)

    def __init__(self, itemGroup):
        super(PathHelixHandleSelectionBox, self).__init__(itemGroup.partItem())
        self._itemGroup = itemGroup
        self._rect = itemGroup.boundingRect()
        self._partItem = itemGroup.partItem()
        self.setParentItem(itemGroup.partItem())
        self.hide()
        self.setPen(self._boxPen)
        self.setZValue(styles.ZPATHHELIX+2)
    # end def

    def refreshPath(self):
        self.prepareGeometryChange()
        self.setPath(self.painterPath())
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
        self._partItem.reorderHelices(items[0].number(),\
                                   items[-1].number(),\
                                   indexDelta)
    # end def
# end class

class BreakpointHandleSelectionBox(QGraphicsPathItem):
    _penWidth = styles.SLICE_HELIX_HILIGHT_WIDTH
    _boxPen = QPen(styles.bluestroke, _penWidth)
    
    def __init__(self, itemGroup):
        super(BreakpointHandleSelectionBox, self).__init__(itemGroup.partItem())
        self._itemGroup = itemGroup
        self._rect = itemGroup.boundingRect()
        self._partItem = itemGroup.partItem()
        self.setParentItem(itemGroup.partItem())
        self.hide()
        self.setPen(self._boxPen)
        self.setZValue(styles.ZPATHHELIX+2)
    # end def
    
    def refreshPath(self):
        self.prepareGeometryChange()
        self.setPath(self.painterPath())
    # end def
    
    def painterPath(self):
        iG = self._itemGroup
        # the childrenBoundingRect is necessary to get this to work
        rect = self.mapRectFromItem(iG,iG.childrenBoundingRect() )

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
        pass
# end class