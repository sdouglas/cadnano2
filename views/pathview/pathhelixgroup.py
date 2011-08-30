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

from cadnano import app
from handles.activeslicehandle import ActiveSliceHandle
from handles.pathhelixhandle import PathHelixHandle
from handles.pathhelixhandle import PathHelixHandle
from handles.crossoverhandle import XoverHandlePair
from handles.inserthandle import InsertHandleGroup
from model.enum import EndType, LatticeType, StrandType

from itertools import product
from handles.prexoveritem import PreXoverItem

from .pathhelixgraphicsitem import PathHelix

from .pathselection import SelectionItemGroup
from .pathselection import PathHelixHandleSelectionBox
from .pathselection import BreakpointHandleSelectionBox
import util
from views import styles
import threading, weakref


# import Qt stuff into the module namespace with PySide, PyQt4 independence
util.qtWrapImport('QtCore', globals(), ['QObject', 'pyqtSignal', 'pyqtSlot',\
                                        'QRectF', 'QPointF', 'QEvent',\
                                        'QObject', 'Qt', 'QThread'])
util.qtWrapImport('QtGui', globals(), ['QBrush', 'QPen', 'qApp',\
                                       'QGraphicsTextItem', 'QFont',\
                                       'QColor', 'QGraphicsItem', 'QPainter',\
                                       'QGraphicsObject', 'QPicture',\
                                       'QGraphicsItemGroup', 'QUndoCommand',\
                                       'QStyleOptionGraphicsItem'])


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
        self.rect = QRectF()  # Set by _setPathHelixList
        # self._label=None; self.label()  # Poke the cache so the label actually exists
        # Properties
        self._XOverLabels = None
        self._pathHelixes = []  # Primary property
        self.activeHelix = None
        self._part = None
        self._preXOverHandles = None
        self._XOverCacheEnvironment = None

        #Picture Cache
        self.dummyChild = self.DummyChild(self)
        self.pictureCache = None
        #self.pictureThread = self.PaintingCacheUpdateThread(self)
        #self.pictureThread.start()
        #Selections
        self.phhSelectionGroup = SelectionItemGroup(\
                                         boxtype=PathHelixHandleSelectionBox,\
                                         constraint='y',\
                                         parent=self)
        self.setPart(part)
        self._controller = controller
        self._activeSliceHandle = ActiveSliceHandle(self)
        self._stapColor = QColor(0, 72, 0)
        self._stapPen = QPen(self._stapColor, 2)
        
        self.floatingXover = XoverHandlePair(self, None, None)
        self.xovers = {}
        
        self.setZValue(styles.ZPATHHELIXGROUP)
        self.selectionLock = None
        self.setAcceptHoverEvents(True)
        app().phg = self  # Convenience for the command line -i mode
        self._part.partRemoved.connect(self.destroy)  # connect destructor
        self.dragging = False
    # end def

    def destroy(self):
        self._part.partRemoved.disconnect(self.destroy)
        self.scene().removeItem(self)
        self.setPart(None)
    # end def

    def __str__(self):
        return "I am a PathHelixGroup!"

    def part(self):
        return self._part

    def activeTool(self):
        return self.controller().activeTool()

    def getActiveHelix(self):
        return self.activeHelix

    # def setActiveHelix(self, newActivePH):
    #     self.activeHelix = newActivePH
    #     neighborVHs = newActivePH.vhelix().neighbors()
    #     for ph in self._pathHelixes:
    #         showHandles = ph==newActivePH# or ph.vhelix() in neighborVHs
    #         ph.setPreXOverHandlesVisible(showHandles)
    # # end def
    
    def setActiveHelix(self, newActivePH):
        self.activeHelix = newActivePH
        self.setPreXOverHandlesVisible(newActivePH, True)
    # end def
    
    def preXOverHandlesVisible(self):
        return self._preXOverHandles != None
    # end def
    
    def setPreXOverHandlesVisible(self, ph, shouldBeVisible):
        """
        self._preXoverHandles list references prexovers parented to other
        PathHelices such that only the activeHelix maintains the list of
        visible prexovers
        
        A possible more efficient solution is to maintain the list _preXoverHandles
        in pathhelixgroup, in fact this method should live in pathhelixgroup
        """
        if ph == None:
            return
        # end if
        areVisible = self._preXOverHandles != None
        vh = ph.vhelix()
        phg = self
        part = self.part()
        
        # clear PCHs
        # for pch in self._preXOverHandles:
        #     if pch.scene():
        #         pch.scene().removeItem(pch)
        if areVisible:
            map(lambda pch: pch.remove() if pch.scene() else None, self._preXOverHandles)

            self._preXOverHandles = None
            part.virtualHelixAtCoordsChanged.disconnect(\
                                                   self.updatePreXOverHandles)

        if shouldBeVisible:
            self._preXOverHandles = []
            for strandType, facingRight in \
                    product(('vStrandScaf', 'vStrandStap'), (True, False)):
                # Get potential crossovers in (fromVBase, toVBase) format
                potentialXOvers = vh.potentialCrossoverList(facingRight, getattr(vh,strandType)())
                numBases = vh.numBases()
                # assert(all(index < numBases for neighborVH, index in potentialXOvers))
                
                for (fromVBase, toVBase) in potentialXOvers:
                    # create one half
                    pch = PreXoverItem(ph, fromVBase, toVBase, not facingRight)
                    # add to list
                    self._preXOverHandles.append(pch)
                    # create the complement
                    otherPH = phg.pathHelixForVHelix(toVBase.vHelix())
                    pch = PreXoverItem(otherPH, toVBase, fromVBase, not facingRight)
                    # add to list
                    self._preXOverHandles.append(pch)
                # end for
            # end for
            part.virtualHelixAtCoordsChanged.connect(self.updatePreXOverHandles)
        self._XOverCacheEnvironment = (vh.neighbors(), vh.numBases())
    # end def

    def updatePreXOverHandles(self):
        cacheConstructionEnvironment = self._XOverCacheEnvironment
        ph = self.getActiveHelix()
        if ph == None:
            return
        vh = ph.vhelix()
        currentEnvironment = (vh.neighbors(), vh.numBases())
        if cacheConstructionEnvironment != currentEnvironment and\
           self.preXOverHandlesVisible():
            self.setPreXOverHandlesVisible(ph, False)
            self.setPreXOverHandlesVisible(ph, True)
    # end def

    def setPart(self, newPart):
        if self._part:
            self._part.selectionWillChange.disconnect(self.selectionWillChange)
            self._part.dimensionsDidChange.disconnect(self.partDimensionsChanged)
            self._part.createXover.disconnect(self.createXoverItem)
            self._part.updateFloatingXover.disconnect(self.updateFloatingXoverItem)
            self._part.needsFittingToView.disconnect(self.zoomToFit)
        self._part = newPart
        if newPart != None:
            newPart.selectionWillChange.connect(self.selectionWillChange)
            newPart.dimensionsDidChange.connect(self.partDimensionsChanged)
            newPart.createXover.connect(self.createXoverItem)
            newPart.updateFloatingXover.connect(self.updateFloatingXoverItem)
            newPart.needsFittingToView.connect(self.zoomToFit)
            self.selectionWillChange(newPart.selection())

    def controller(self):
        return self._controller

    def activeSliceHandle(self):
        return self._activeSliceHandle

    def createXoverItem(self, Base3p, Base5p, strandtype):
        """
        Base3p is the tuple (3 prime vhelix, index),
        Base5p is the (5 prime vhelix, index)
        strandtype is Strandtype.Scaffold or Strandtype.Staple
        """
        fromBase = (Base3p[0], strandtype, Base3p[1])
        toBase = (Base5p[0], strandtype, Base5p[1])
        key = (fromBase, toBase)
        if not key in self.xovers:
            self.xovers[key] = XoverHandlePair(self, fromBase, toBase)

    def updateFloatingXoverItem(self, fromBase, toPt):
        self.floatingXover.setFromBase(fromBase)
        self.floatingXover.setToPoint(toPt)

    def pathHelixAtScenePos(self, pos):
        for p in self._pathHelixes:
            pt = p.mapFromScene(pos)
            if p.boundingRect().contains(pt):
                return p
        return None
    # end def

    def vBaseAtPoint(self, pos):
        ph = self.pathHelixAtScenePos(pos)
        if ph == None:
            return None
        return ph.vBaseAtPoint(ph.mapFromItem(self, pos))

    def pathHelixForVHelix(self, vh):
        for p in self._pathHelixes:
            if p.vhelix() == vh:
                return p
        return None

    def pointForVBase(self, vBase):
        ph = self.pathHelixForVHelix(vBase.vHelix())
        if ph == None:
            return None
        return ph.mapToItem(self, ph.pointForVBase(vBase))

    def displayedVHs(self):
        """Returns the list (ordered top to bottom) of VirtualHelix
        that the receiver is displaying"""
        return [ph.vhelix() for ph in self._pathHelixes]

    # TODO: consider refactoring to have this signal actually emit a list of 
    # changed VHs
    displayedVHsChanged = pyqtSignal()
    def setDisplayedVHs(self, vhrefs, zoomToFit=True):
        """
        Spawns or destroys PathHelix such that displayedVHs has the same
        VirtualHelix in the same order as vhrefs (though displayedVHs always
        returns a list of VirtualHelix while setDisplayedVHs can take any 
        vhref)
        """
        if self.part() != None:
            new_pathHelixList = []
            vhToPH = dict(((ph.vhelix(), ph) for ph in self._pathHelixes))
            for vhref in vhrefs:
                vh = self.part().getVirtualHelix(vhref)
                ph = vhToPH.get(vh, None)
                if ph == None:
                    ph = PathHelix(vh, self)
                new_pathHelixList.append(ph)
            self._setPathHelixList(new_pathHelixList, zoomToFit=zoomToFit)
            self.displayedVHsChanged.emit()

    def partDimensionsChanged(self):
        self._setPathHelixList(self._pathHelixList())

    def _pathHelixList(self):
        return self._pathHelixes

    def topmostPathHelix(self):
        if len(self._pathHelixList())==0:
            return None
        return self._pathHelixList()[0]

    def _setPathHelixList(self, newList, zoomToFit=True):
        """
        Give me a list of PathHelix and I'll parent them to myself if
        necessary, position them in a column, adopt their handles, and
        position them as well.
        """
        y = 0  # How far down from the top the next PH should be
        leftmostExtent = 0
        rightmostExtent = 0
        # self.label().setVisible(True)
        for ph in self._pathHelixes:
            if not ph in newList:
                scene = ph.scene()
                handle = ph.handle()
                if handle.focusRing:
                    scene.removeItem(handle.focusRing)
                scene.removeItem(handle)
                scene.removeItem(ph)
        for ph in newList:
            ph.setParentItem(self.dummyChild)
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
            self.updatePreXOverHandles()
        # end for
        self.prepareGeometryChange()
        self.rect = QRectF(leftmostExtent,\
                           -40,\
                           -leftmostExtent + rightmostExtent,\
                           y + 40)
        self.geometryChanged.emit()
        for ph in self._pathHelixes:
            vhbm = getattr(ph, 'vhelixBasesModifiedCallbackObj', None)
            if vhbm:
                ph.vhelix().basesModifiedSignal.disconnect(vhbm)
        for ph in newList:
            def vhbmCallbackCreator(self, vh):
                def vhbmCallback():
                    self.vhelixBasesModified(vh)
                return vhbmCallback
            vhbm = vhbmCallbackCreator(self, ph.vhelix())
            ph.vhelix().basesModifiedSignal.connect(vhbm)
        self._pathHelixes = newList
        for ph in self._pathHelixes:
            # this emits the signal to update the views
            ph.positionInPhgChanged()
        self.vhToPathHelix = dict(((ph.vhelix(), ph) for ph in newList))
        if zoomToFit:
            self.scene().views()[0].zoomToFit()
    # end def

    def paint(self, painter, option, widget=None):
        pass
        #dc = self.dummyChild
        #if self.pictureCache != None and dc.isVisible():
        #    dc.hide()
        #elif self.pictureCache == None and not dc.isVisible():
        #    dc.show()
        #if self.pictureCache != None:
        #    painter.drawPicture(0, 0, self.pictureCache)

    geometryChanged = pyqtSignal()

    def boundingRect(self):
        # rect set only by _setPathHelixList
        return self.rect

    def moveHelixNumToIdx(self, num, idx):
        """Reinserts helix with number() num such that
        it's at position idx in _pathHelixList"""
        vhs = [vh.number() for vh in self.displayedVHs()]
        vhs.remove(num)
        vhs.insert(idx, num)
        self.setDisplayedVHs(vhs, zoomToFit=False)

    def renumber(self):
        self.part().matchHelixNumberingToPhgDisplayOrder(self)
    # end def

    def keyPanDeltaY(self):
        """How far an an arrow key should move the scene (in scene space)
        for a single press"""
        phs = self._pathHelixes
        if not len(phs) > 1:
            return 5
        dy = phs[0].pos().y() - phs[1].pos().y()
        dummyRect = QRectF(0, 0, 1, dy)
        return self.mapToScene(dummyRect).boundingRect().height()

    def keyPanDeltaX(self):
        """How far a single press of the left or right arrow key should move
        the scene (in scene space)"""
        phs = self._pathHelixes
        return phs[0].keyPanDeltaX() if phs else 5

    def zoomToFit(self):
        # Auto zoom to center the scene
        thescene = self.scene()
        theview = thescene.views()[0]
        theview.zoomToFit()

    def virtualHelixAtCoordsChangedEvent(self, row, col):
        c = (row, col)
        self._setPathHelixList([ph for ph in self._pathHelixes if ph.vhelix().coord()!=c])

    # Slot called when the slice view's (actually the part's) selection changes
    def selectionWillChange(self, newSelection):
        self.setDisplayedVHs(newSelection, zoomToFit=False)

    class PaintingCacheUpdateThread(QThread):
        def __init__(self, phg):
            # threading.Thread.__init__(self)
            QThread.__init__(self)
            self.phg = weakref.proxy(phg)
            # self.setDaemon(True)
        def run(self):
            phg = self.phg
            while True:
                try:
                    part = phg.part()
                    if part == None:
                        continue
                    modificationCV = part.modificationCondition
                    modificationCV.acquire()
                    modificationCV.wait()
                    phg.pictureCache = None
                    modificationCV.release()
                    phg.fillPictureCache()
                except ReferenceError as e:
                    break
            print "Picture thread terminated."

    def fillPictureCache(self):
        print "Picture cache: %s"%str(self.pictureCache)
        recording = QPicture()
        painter = QPainter()
        painter.begin(recording)
        part = self.part()
        dummyStyleOption = QStyleOptionGraphicsItem()
        if part == None: return
        q = [self.dummyChild]
        try:
            part.lock.acquireRead(0)
            while q:
                part.lock.release()
                part.lock.acquireRead(0)
                graphicsItem = q.pop()
                # the transform that maps graphicsItem coordinates to our own
                painter.setTransform(graphicsItem.itemTransform(self)[0])
                graphicsItem.paint(painter, dummyStyleOption, None)
                q.extend(graphicsItem.childItems())
        except RuntimeError:
            print "Lock timed out -- aborting"
        finally:
            try:
                part.lock.release()
            except ValueError:
                pass  # Catch double-releasing, which doesn't concern us
            painter.end()
        self.pictureCache = recording
        print "Picture cache: %s"%str(self.pictureCache)

    def prepareGeometryChange(self):
        super(PathHelixGroup, self).prepareGeometryChange()
        self.dummyChild.prepareGeometryChange()

    class DummyChild(QGraphicsItem):
        """
        A PathHelixGroup can switch between rendering its children and
        rendering from a QPicture cache (filled by fillPictureCache inside a
        PaintingCacheUpdateThread)
        """
        def boundingRect(self):
            return self.parentObject().boundingRect()
        def paint(self, painter, option, widget=None):
            pass

    def getPathHelix(self, vhref):
        """Given the helix number, return a reference to the PathHelix."""
        if self.part() != None:
            vh = self.part().getVirtualHelix(vhref)
            for ph in self._pathHelixes:
                if ph.vhelix() == vh:
                    return ph
        return None

    def vhelixBasesModified(self, vhelix):
        self.update()
        ph = self.getPathHelix(vhelix)

    def reorderHelices(self, first, last, indexDelta):
        """
        Reorder helices by moving helices _pathHelixList[first:last]
        by a distance delta in the list. Notify each PathHelix and
        PathHelixHandle of its new location.
        """
        helixNumbers = [ph.number() for ph in self._pathHelixes]
        firstIndex = helixNumbers.index(first)
        lastIndex = helixNumbers.index(last) + 1
        if indexDelta < 0:  # move group earlier in the list
            newIndex = max(0, indexDelta + firstIndex)
            listPHs = self._pathHelixes[0:newIndex] +\
                                 self._pathHelixes[firstIndex:lastIndex] +\
                                 self._pathHelixes[newIndex:firstIndex] +\
                                 self._pathHelixes[lastIndex:]
        else:  # move group later in list
            newIndex = min(len(self._pathHelixes), indexDelta + lastIndex)
            listPHs = self._pathHelixes[:firstIndex] +\
                                 self._pathHelixes[lastIndex:newIndex] +\
                                 self._pathHelixes[firstIndex:lastIndex] +\
                                 self._pathHelixes[newIndex:]
        listVHs = [ph.vhelix() for ph in listPHs]
        self.setDisplayedVHs(listVHs, zoomToFit=False)
    # end def

    clearCursors = pyqtSignal()
    def mousePressDefault(self, event):
        """
        Default function that gets called thanks to utils
        util.defineEventForwardingMethodsForClass
        
        currently not used but serves as an example method
        """
        self.clearCursors.emit()
    # end def

    # These methods are required since hover events are accepted
    # and no additional event handler exists in order to prevent additional
    # phg redraws
    def hoverEnterEvent(self, event):
        pass
        # QGraphicsItem.hoverEnterEvent(self, event)
    # end def
    
    def hoverLeaveEvent(self, event):
        pass
        # QGraphicsItem.hoverEnterEvent(self, event)
    # end def
# end class

################################ Events ################################
forwardedEvents = ('hoverMove', 'mousePress', 'mouseRelease')
util.defineEventForwardingMethodsForClass(PathHelixGroup, 'PathHelixGroup', forwardedEvents)

