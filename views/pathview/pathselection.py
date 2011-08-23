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
        self.parent = parent
        self.setParentItem(parent)
        self.setFiltersChildEvents(True)
        self.setHandlesChildEvents(True)
        self.setFlag(QGraphicsItem.ItemIsSelectable)
        self.setFlag(QGraphicsItem.ItemIsFocusable) # for keyPressEvents
        self.setFlag(QGraphicsItem.ItemHasNoContents)
        
        self.pen = QPen(styles.bluestroke, styles.PATH_SELECTBOX_STROKE_WIDTH)
        self._phg = parent
        
        self.selectionbox = boxtype(self)
        self.drawMe = False
        self.dragEnable = False
        self.dragged = False
        self._r0 = 0  # save original mousedown
        self._r = 0  # latest position for moving

        self.lastKid = 0
        self.addedToPressList = False

        if constraint == 'y':
            self.getR = self.getY
            self.translateR = self.translateY
        else:
            self.getR = self.getX
            self.translateR = self.translateX
    # end def

    def phg(self):
        return self._phg

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
            thePart = self._phg.part()
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
            self.dragEnable = True
            self.setSelected(True)
            self.selectionbox.resetTransform()
            
            self.isSelecting = False
            
            self.selectionbox.refreshPath()
            self.selectionbox.resetTransform()
            self.selectionbox.show()
            
            # for some reason we need to skip the first mouseMoveEvent
            self.dragged = False
                
            # self._r0 = self.getR(self.mapToScene(QPointF(event.pos())))
            # self._r = self._r0
            if self.addedToPressList == False:
                self.addedToPressList = True
                self.scene().views()[0].addToPressList(self)
    # end def

    def mouseMoveEvent(self, event):
        temp = self.childItems()[0]
        # print self.isSelected(), temp.isSelected()
        if self.dragEnable == True:
            rf = self.getR(self.mapToScene(QPointF(event.pos())))
            # for some reason we need to skip the first mouseMoveEvent
            if self.dragged == False:
                self.dragged = True
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
        self.dragEnable = False
        # now do stuff
        # print "maybe process", self.isSelected()
        if self.isSelected() and not (self._r0 == 0 and self._r == 0):
            # print "process the box"
            self.selectionbox.processSelectedItems(self._r0, self._r)
        # end if
        # print [item.number() for item in self.childItems()]
        self._r0 = 0  # reset
        self._r = 0  # reset
        # print "press release"
        self.addedToPressList = False
    # end def
    
    def clearSelection(self, value):
        if value == False:
            self.selectionbox.hide()
            self.selectionbox.resetTransform()
            self.removeSelectedItems()
            self.phg().selectionLock = None
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
                if self.lastKid > 1 and \
                    (qApp.mouseButtons() | Qt.LeftButton) and \
                    self.addedToPressList == True:
                    self.removeChild(self.childItems()[self.lastKid-1])
                else: 
                    self.clearSelection(value)
                    return
        elif change == QGraphicsItem.ItemChildAddedChange:
            self.lastKid += 1
            if self.addedToPressList == False:
                self.addedToPressList = True
                self.scene().views()[0].addToPressList(self)
            # print [item.number() for item in self.childItems()]
            return
        elif change == QGraphicsItem.ItemChildRemovedChange:
            self.lastKid -= 1 
            # print [item.number() for item in self.childItems()]
            return
        return QGraphicsItemGroup.itemChange(self, change, value)
    # end def

    def removeChild(self, child):
        """docstring for removeSelectedItems"""
        # if not child.isSelected():
        # call this first before removing from the group to 
        # prevent unecessary change events

        self.removeFromGroup(child)
        try:
            child.restoreParent()
        except:
            print type(child.parentObject()), "Parent Error"
    # end def


    def removeSelectedItems(self):
        """docstring for removeSelectedItems"""
        for item in self.childItems():
            if not item.isSelected():
                # call this first before removing from the group to 
                # prevent unecessary change events
                
                self.removeFromGroup(item)
                try:
                    item.restoreParent()
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
    helixHeight = styles.PATH_HELIX_HEIGHT + styles.PATH_HELIX_PADDING
    radius = styles.PATHHELIXHANDLE_RADIUS
    penWidth = styles.SLICE_HELIX_HILIGHT_WIDTH
    boxPen = QPen(styles.bluestroke, penWidth)

    def __init__(self, itemGroup):
        super(PathHelixHandleSelectionBox, self).__init__(itemGroup.phg())
        self.itemGroup = itemGroup
        self.rect = itemGroup.boundingRect()
        self.phg = itemGroup.phg()
        self.setParentItem(itemGroup.phg())
        self.hide()
        self.setPen(self.boxPen)
        self.setZValue(styles.ZPATHHELIX+2)
    # end def

    def refreshPath(self):
        self.prepareGeometryChange()
        self.setPath(self.painterPath())
    # end def

    def painterPath(self):
        iG = self.itemGroup
        rect = self.mapRectFromItem(iG,iG.childrenBoundingRect() )
        path = QPainterPath()
        path.addRoundedRect(rect, self.radius, self.radius)
        path.moveTo(rect.right(),\
                         rect.center().y())
        path.lineTo(rect.right() + self.radius / 2,\
                         rect.center().y())
        return path
    # end def

    def processSelectedItems(self, rStart, rEnd):
        """docstring for processSelectedItems"""
        margin = styles.PATHHELIXHANDLE_RADIUS
        delta = (rEnd - rStart)  # r delta
        midHeight = (self.boundingRect().height()) / 2 - margin
        if abs(delta) < midHeight:  # move is too short for reordering
            return
        if delta > 0:  # moved down, delta is positive
            indexDelta = int((delta - midHeight) / self.helixHeight)
        else:  # moved up, delta is negative
            indexDelta = int((delta + midHeight) / self.helixHeight)
        # sort on y to determine the extremes of the selection group
        items = sorted(self.itemGroup.childItems(), key=lambda phh: phh.y())
        self.phg.reorderHelices(items[0].number(),\
                                   items[-1].number(),\
                                   indexDelta)
    # end def
# end class

class BreakpointHandleSelectionBox(QGraphicsItem):
    def __init__(self, itemGroup, parent=None):
        super(BreakpointHandleSelectionBox, self).__init__(parent)
        self.itemGroup = itemGroup
        self.rect = itemGroup.boundingRect()
        self.phg = itemGroup.phg()
        self.setParentItem(itemGroup.phg())
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

    def processSelectedItems(self, rStart, rEnd):
        """docstring for processSelectedItems"""
        pass
# end class