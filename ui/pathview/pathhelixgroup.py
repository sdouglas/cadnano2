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
from .pathhelix import PathHelix
from handles.activeslicehandle import ActiveSliceHandle
from handles.pathhelixhandle import PathHelixHandle
from model.enum import EndType, LatticeType, StrandType
import ui.styles as styles
from handles.pathhelixhandle import PathHelixHandle
from handles.crossoverhandle import XoverHandle
from handles.loophandle import LoopHandleGroup
from cadnano import app

# from PyQt4.QtCore import QRectF, QPointF, QEvent, pyqtSlot, QObject, Qt
# from PyQt4.QtCore import pyqtSignal
# from PyQt4.QtGui import QBrush, QPen, qApp, QGraphicsTextItem, QFont, QColor
# from PyQt4.QtGui import QGraphicsItem, QGraphicsObject
# from PyQt4.QtGui import QGraphicsItemGroup, QUndoCommand

import util
# import Qt stuff into the module namespace with PySide, PyQt4 independence
util.qtWrapImport('QtCore', globals(), ['QObject', 'pyqtSignal', 'pyqtSlot', \
                                        'QRectF', 'QPointF', 'QEvent', \
                                        'QObject', 'Qt'] )
util.qtWrapImport('QtGui', globals(), [ 'QBrush', 'QPen', 'qApp', \
                                        'QGraphicsTextItem', 'QFont', \
                                        'QColor', 'QGraphicsItem', \
                                        'QGraphicsObject', \
                                        'QGraphicsItemGroup', 'QUndoCommand'])

class PathHelixGroup(QGraphicsObject):
    """
    PathHelixGroup maintains data and state for a set of object that provide
    an interface to the schematic view of a DNA part. These objects include
    the PathHelix, PathHelixHandles, and ActiveSliceHandle.
    """
    handleRadius = styles.SLICE_HELIX_RADIUS
    _scafColor = QColor(0, 102, 204)
    _scafPen = QPen(_scafColor, 2)
    _nobrush = QBrush(Qt.NoBrush)
    
    def __init__(self, part,\
                       controller=None,\
                       parent=None):
        super(PathHelixGroup, self).__init__(parent)
        # Subviews, GraphicsItem business
        self.rect = QRectF()  # Set by _set_pathHelixList
        self._label=None; self.label()  # Poke the cache so the label actually exists
        
        # Properties
        self._XOverLabels = None
        self._pathHelixList = []  # Primary property
        self.activeHelix = None
        self._part = None
        self.phhSelectionGroup = SelectionItemGroup(\
                                         boxtype=PathHelixHandleSelectionBox,\
                                         constraint='y',\
                                         parent=self)
        self.setPart(part)
        self._controller = controller
        self._activeSliceHandle = ActiveSliceHandle(self)
        self._stapColor = QColor(0, 72, 0)
        self._stapPen = QPen(self._stapColor, 2)
        self.loopHandleGroup = LoopHandleGroup(parent=self)
        self.xoverGet = XoverHandle()
        self.setZValue(styles.ZPATHHELIXGROUP)
        self.selectionLock = None
        self.setAcceptHoverEvents(True)
        app().phg = self  # Convenience for the command line -i mode

    def __str__(self):
        return "I am a PHG!"

    def part(self):
        return self._part

    def activeTool(self):
        return self.controller().activeTool()
    
    def getActiveHelix(self):
        return self.activeHelix
    
    def setActiveHelix(self, newActivePH):
        self.activeHelix = newActivePH
        neighborVHs = newActivePH.vhelix().neighbors()
        for ph in self._pathHelixList:
            showHandles = ph==newActivePH or ph.vhelix() in neighborVHs
            ph.setPreXOverHandlesVisible(showHandles)
    
    def notifyLoopHandleGroupAfterUpdate(self, pathhelix):
        """
        Called by setActiveHelix and loophandlegroup after the vhelix has 
        calculated its new loop positions.
        """
        self.loopHandleGroup.updateActiveHelix(pathhelix)

    def setPart(self, newPart):
        if self._part:
            self._part.selectionWillChange.disconnect(self.selectionWillChange)
        newPart.selectionWillChange.connect(self.selectionWillChange)
        self._part = newPart
        if newPart:
            self.selectionWillChange(newPart.selection())

    def controller(self):
        return self._controller

    def activeSliceHandle(self):
        return self._activeSliceHandle  

    def label(self):
        if self._label:
            return self._label
        font = QFont("Times", 30, QFont.Bold)
        label = QGraphicsTextItem("Part 1")
        label.setVisible(False)
        label.setFont(font)
        label.setParentItem(self)
        label.setPos(0, -70)
        label.setTextInteractionFlags(Qt.TextEditorInteraction)
        label.inputMethodEvent = None
        self._label = label
        return label
    
    def pathHelixAtScenePos(self, pos):
        for p in self._pathHelixList:
            pt = p.mapFromScene(pos)
            if p.boundingRect().contains(pt):
                return p
        return None

    def displayedVHs(self):
        """Returns the list (ordered top to bottom) of VirtualHelix
        that the receiver is displaying"""
        return [ph.vhelix() for ph in self._pathHelixList]

    displayedVHsChanged = pyqtSignal()
    def setDisplayedVHs(self, vhrefs):
        """Spawns or destroys PathHelix such that displayedVHs
        has the same VirtualHelix in the same order as vhrefs
        (though displayedVHs always returns a list of VirtualHelix
        while setDisplayedVHs can take any vhref)"""
        # print "I got called"
        assert(self.part())  # Can't display VirtualHelix that aren't there!
        new_pathHelixList = []
        vhToPH = dict(((ph.vhelix(), ph) for ph in self._pathHelixList))
        for vhref in vhrefs:
            vh = self.part().getVirtualHelix(vhref)
            ph = vhToPH.get(vh, None)
            if ph == None:
                ph = PathHelix(vh, self)
            new_pathHelixList.append(ph)
        # print [x.number() for x in new_pathHelixList]
        self._set_pathHelixList(new_pathHelixList)
        # print "updating disp vhs"
        self.displayedVHsChanged.emit()

    def __pathHelixList(self):
        return self._pathHelixList

    def _set_pathHelixList(self, newList):
        """Give me a list of PathHelix and I'll parent them
        to myself if necessary, position them in a column, adopt
        their handles, and position them as well."""
        y = 0  # How far down from the top the next PH should be
        leftmostExtent = 0
        rightmostExtent = 0
        self.label().setVisible(True)
        for ph in self._pathHelixList:
            if not ph in newList:
                scene = ph.scene()
                handle = ph.handle()
                if handle.focusRing:
                    scene.removeItem(handle.focusRing)
                scene.removeItem(handle)
                scene.removeItem(ph)
        for ph in newList:
            ph.setParentItem(self)
            ph.setPos(0, y)
            ph_height = ph.boundingRect().height()
            step = ph_height + styles.PATH_HELIX_PADDING
            phh = ph.handle()
            if phh.parentItem() != self.phhSelectionGroup:
                phh.setParentItem(self)
            phhr = phh.boundingRect()
            phh.setPos(-2 * phhr.width(), y + (ph_height - phhr.height()) / 2)
            leftmostExtent = min(leftmostExtent, -2 * phhr.width())
            rightmostExtent = max(rightmostExtent, ph.boundingRect().width())
            y += step
        # end for
        self.prepareGeometryChange()
        self.geometryChanged.emit()
        self.rect = QRectF(leftmostExtent,\
                           -40,\
                           -leftmostExtent + rightmostExtent,\
                           y + 40)
        for ph in self._pathHelixList:
            vhbm = getattr(ph, 'vhelixBasesModifiedCallbackObj', None)
            if vhbm:
                ph.vhelix().basesModified.disconnect(vhbm)
        for ph in newList:
            def vhbmCallbackCreator(self, vh):
                def vhbmCallback():
                    self.vhelixBasesModified(vh)
                return vhbmCallback
            vhbm = vhbmCallbackCreator(self, ph.vhelix())
            ph.vhelix().basesModified.connect(vhbm)
        self._pathHelixList = newList
        self.vhToPathHelix = dict(((ph.vhelix(), ph) for ph in newList))
        self.scene().views()[0].zoomToFit()

    def paint(self, painter, option, widget=None):
        # painter.save()
        painter.setBrush(Qt.NoBrush)
        self.drawXovers(painter)
        # painter.restore()

    def drawXovers(self, painter):
        """Return a QPainterPath ready to paint the crossovers"""    
        for ph in self._pathHelixList:
            for strandType in (StrandType.Scaffold, StrandType.Staple):
                for ((fromhelix, fromindex), dest) in \
                                 ph.vhelix().get3PrimeXovers(strandType):
                    if type(dest) in (list, tuple):
                        toVH, toIndex = dest
                        toPH = self.getPathHelix(toVH)
                        floatPos = None
                    else:
                        toPH, toIndex = None, None
                        floatPos = dest
                    path = self.xoverGet.getXover(self,\
                                                  strandType,\
                                                  ph,\
                                                  fromindex,\
                                                  toPH,\
                                                  toIndex,\
                                                  floatPos)
                    # draw the line
                    # reload scaffold strand pen
                    if strandType==StrandType.Scaffold:
                        pen = self._scafPen
                    else:
                        pen = self._stapPen
                        color = ph.vhelix().colorOfBase(strandType, fromindex)
                        pen.setColor(color)
                        oligoLength = ph.vhelix().numberOfBasesConnectedTo(strandType, fromindex)
                        tooLong = oligoLength>styles.oligoLenAboveWhichDrawnDashed
                        pen.setStyle(Qt.DashLine if tooLong else Qt.SolidLine)
                    painter.setPen(pen)
                    painter.drawPath(path[0])
                    
                    # draw labels
                    painter.setPen(QPen(styles.XOVER_LABEL_COLOR))
                    painter.setFont(styles.XOVER_LABEL_FONT)
                    painter.drawText(path[1], Qt.AlignCenter, str(ph.number()))
                    
                    # test to see if we need to draw the to label for the xover
                    # this comes in handy when drawing forced xovers
                    if toPH != None:
                        painter.drawText(path[2], 
                                        Qt.AlignCenter, str(toPH.number()))
                # end for
            # end for strandType in scaf, stap
        # end for
    # end def

    geometryChanged = pyqtSignal()

    def boundingRect(self):
        # rect set only by _set_pathHelixList
        return self.rect

    def moveHelixNumToIdx(self, num, idx):
        """Reinserts helix with number() num such that
        it's at position idx in _pathHelixList"""
        vhs = [vh.number() for vh in self.displayedVHs()]
        vhs.remove(num)
        vhs.insert(idx, num)
        self.setDisplayedVHs(vhs)
        
    def renumber(self):
        self.part().matchHelixNumberingToPhgDisplayOrder(self)
    # end def

    def zoomToFit(self):
        # Auto zoom to center the scene
        thescene = self.scene()
        theview = thescene.views()[0]
        theview.zoomToFit()

    def virtualHelixAtCoordsChangedEvent(self, row, col):
        c = (row, col)
        self._set_pathHelixList([ph for ph in self._pathHelixList if ph.vhelix().coord()!=c])

    # Slot called when the slice view's (actually the part's) selection changes
    def selectionWillChange(self, newSelection):
        self.setDisplayedVHs(newSelection)

    def getPathHelix(self, vhref):
        """Given the helix number, return a reference to the PathHelix."""
        vh = self.part().getVirtualHelix(vhref)
        for ph in self._pathHelixList:
            if ph.vhelix() == vh:
                return ph
        return None
    
    def vhelixBasesModified(self, vhelix):
        self.update()
        ph = self.getPathHelix(vhelix)
        self.notifyLoopHandleGroupAfterUpdate(ph)

    def reorderHelices(self, first, last, indexDelta):
        """
        Reorder helices by moving helices _pathHelixList[first:last]
        by a distance delta in the list. Notify each PathHelix and
        PathHelixHandle of its new location.
        """
        # print "called reorderHelices", first, last, indexDelta
        # vhs = self.displayedVHs()
        # vhsToMove = vhs[first:last]
        # del vhs[first:last]  

        helixNumbers = [ph.number() for ph in self._pathHelixList]
        firstIndex = helixNumbers.index(first)
        lastIndex = helixNumbers.index(last) + 1
        # print "indices", firstIndex, lastIndex
        if indexDelta < 0:  # move group earlier in the list
            newIndex = max(0, indexDelta + firstIndex)
            listPHs = self._pathHelixList[0:newIndex] +\
                                 self._pathHelixList[firstIndex:lastIndex] +\
                                 self._pathHelixList[newIndex:firstIndex] +\
                                 self._pathHelixList[lastIndex:]
        else:  # move group later in list
            newIndex = min(len(self._pathHelixList), indexDelta + lastIndex)
            listPHs = self._pathHelixList[:firstIndex] +\
                                 self._pathHelixList[lastIndex:newIndex] +\
                                 self._pathHelixList[firstIndex:lastIndex] +\
                                 self._pathHelixList[newIndex:]
        
        listVHs = [ph.vhelix() for ph in listPHs]
        self.setDisplayedVHs(listVHs)
    # end def
# end class

################################ Events ################################
forwardedEvents = ('hoverMove', 'mousePress', 'mouseRelease')
util.defineEventForwardingMethodsForClass(PathHelixGroup, 'PathHelixGroup', forwardedEvents)


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
        self.pen = QPen(styles.bluestroke, styles.PATH_SELECTBOX_STROKE_WIDTH)
        self.drawMe = False
        self.drawn = False
        self._phg = parent
        self.selectionbox = boxtype(self)
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
        self.selectionbox.translate(0, (yf - self._r))
    # end def

    def translateX(self, xf):
        self.selectionbox.translate((xf - self._r), 0)
    # end def

    def paint(self, painter, option, widget=None):
        pass
    # end def

    def mousePressEvent(self, event):
        if event.button() != Qt.LeftButton:
            QGraphicsItemGroup.mousePressEvent(self, event)
        else:
            self.dragEnable = True
            self.selectionbox.resetTransform()

            # this code block is a HACK to update the boundingbox of the group
            if self.childItems()[0] != None:
                item = self.childItems()[0]
                self.removeFromGroup(item)
                item.restoreParent()
                self.addToGroup(item)

            self.selectionbox.setRect(self.boundingRect())
            self.selectionbox.drawMe = True
            self._r0 = self.getR(event.scenePos())
            self._r = self._r0
            self.scene().views()[0].addToPressList(self)
    # end def

    def mouseMoveEvent(self, event):
        if self.dragEnable == True:
            rf = self.getR(event.scenePos())
            self.translateR(rf)
            self._r = rf
        else:
            QGraphicsItemGroup.mouseMoveEvent(self, event)
    # end def

    def customMouseRelease(self, event):
        """docstring for customMouseRelease"""
        if self.isSelected():
            self.selectionbox.processSelectedItems(self._r0, self._r)
        # end if
        self.selectionbox.drawMe = False
        self.selectionbox.resetTransform()
        self.dragEnable = False
    # end def

    def itemChange(self, change, value):
        """docstring for itemChange"""
        if change == QGraphicsItem.ItemSelectedHasChanged:
            if value == False:
                # self.drawMe = False
                self.selectionbox.drawMe = False
                self.selectionbox.resetTransform()
                self.removeSelectedItems()
                self.phg().selectionLock = None
            # end if
            else:
                pass
            self.update(self.boundingRect())
        return QGraphicsItemGroup.itemChange(self, change, value)
    # end def

    def removeSelectedItems(self):
        """docstring for removeSelectedItems"""
        for item in self.childItems():
            if not item.isSelected():
                self.removeFromGroup(item)
                try:
                    item.restoreParent()
                except:
                    pass
                item.setSelected(False)
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

    def __init__(self, itemGroup, parent=None):
        super(PathHelixHandleSelectionBox, self).__init__(parent)
        self.itemGroup = itemGroup
        self.rect = itemGroup.boundingRect()
        self.parent = itemGroup.phg()
        self.setParentItem(itemGroup.phg())
        self.drawMe = False
        self.pen = QPen(styles.bluestroke, self.penWidth)
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
        self.rect = rect

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
        self.parent.reorderHelices(items[0].number(),\
                                   items[-1].number(),\
                                   indexDelta)
    # end def
    
# end class

class BreakpointHandleSelectionBox(QGraphicsItem):
    def __init__(self, itemGroup, parent=None):
        super(BreakpointHandleSelectionBox, self).__init__(parent)
        self.itemGroup = itemGroup
        self.rect = itemGroup.boundingRect()
        self.parent = itemGroup.phg()
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
