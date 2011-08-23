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
util.qtWrapImport('QtGui', globals(), [ 'QPen', \
                                        'QGraphicsItem', \
                                        'QGraphicsItemGroup',\
                                        ])

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
        self._r0 = 0  # save original mousedown
        self._r = 0  # latest position for moving

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
            self.selectionbox.resetTransform()

            # this code block is a HACK to update the boundingbox of the group
            temp = self.childItems()
            if temp != None and temp[0] != None:
                item = temp[0]
                self.removeFromGroup(item)
                item.restoreParent()
                self.addToGroup(item)

            self.selectionbox.setRect(self.boundingRect())
            self.selectionbox.resetTransform()
            self.selectionbox.drawMe = True
            
            # for some reason we need to skip the first mouseMoveEvent
            self.dragged = False
                
            # self._r0 = self.getR(self.mapToScene(QPointF(event.pos())))
            # self._r = self._r0
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
        self.selectionbox.drawMe = False
        self.selectionbox.resetTransform()
        self.dragEnable = False
        # now do stuff
        if self.isSelected():
            self.selectionbox.processSelectedItems(self._r0, self._r)
        # end if
        self._r0 = 0  # reset
        self._r = 0  # reset
    # end def
    
    def clearSelection(self, value):
        if value == False:
            self.selectionbox.drawMe = False
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
            self.clearSelection(value)
        return QGraphicsItemGroup.itemChange(self, change, value)
    # end def

    def removeChild(self, child):
        """docstring for removeSelectedItems"""
        if not child.isSelected():
            # call this first before removing from the group to 
            # prevent unecessary change events
            child.setSelected(False)
            
            self.removeFromGroup(child)
            try:
                child.restoreParent()
            except:
                pass
    # end def


    def removeSelectedItems(self):
        """docstring for removeSelectedItems"""
        for item in self.childItems():
            if not item.isSelected():
                # call this first before removing from the group to 
                # prevent unecessary change events
                item.setSelected(False) 
                
                self.removeFromGroup(item)
                try:
                    item.restoreParent()
                except:
                    pass
            # end if
        # end for
    # end def
# end class


class PathHelixHandleSelectionBox(QGraphicsItem):
    """
    docstring for PathHelixHandleSelectionBox
    """
    helixHeight = styles.PATH_HELIX_HEIGHT + styles.PATH_HELIX_PADDING
    radius = styles.PATHHELIXHANDLE_RADIUS
    penWidth = styles.SLICE_HELIX_HILIGHT_WIDTH

    def __init__(self, itemGroup):
        super(PathHelixHandleSelectionBox, self).__init__(itemGroup.phg())
        self.itemGroup = itemGroup
        self.rect = itemGroup.boundingRect()
        self.phg = itemGroup.phg()
        self.setParentItem(itemGroup.phg())
        self.drawMe = False
        self.pen = QPen(styles.bluestroke, self.penWidth)
        self.setZValue(styles.ZPATHHELIX+2)
    # end def

    def paint(self, painter, option, widget=None):
        if self.drawMe == True:
            painter.setPen(self.pen)
            painter.drawRoundedRect(self.rect, self.radius, self.radius)
            painter.drawLine(self.rect.right(),\
                             self.rect.center().y(),\
                             self.rect.right() + self.radius / 2,\
                             self.rect.center().y())
    # end def

    def boundingRect(self):
        return self.rect
    # end def

    def setRect(self, rect):
        self.rect = self.mapRectFromItem(self.itemGroup,rect)

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