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
crossoverhandle.py
Created by Shawn on 2011-05-03.
"""

from model.enum import StrandType
from views import styles

import util
# import Qt stuff into the module namespace with PySide, PyQt4 independence
util.qtWrapImport('QtCore', globals(), ['QPointF', 'QRectF', 'Qt'])
util.qtWrapImport('QtGui', globals(), [ 'QGraphicsItem', 'QGraphicsItemGroup', \
                                        'QBrush', 'QFont', 'QPen', \
                                        'QGraphicsObject'])

# There's a bug where C++ will free orphaned
# graphics items out from under pyqt. To avoid
# this, "mother" adopts orphaned graphics items.
mother = QGraphicsItemGroup()

class AbstractPathTool(QGraphicsObject):
    """
    Abstract base class to be subclassed by all other pathview tools.

    AbstractPathTool is an abstract class for tools that can handle events
    forwarded in the style of util.defineEventForwardingMethodsForClass.
    
    In other words, the activeTool() gets events from various graphics objects
    in the pathview and then makes the corresponding changes to the model.
    
    The displayed content then updates automatically via notifications from
    the model.
    * the activeTool gets events from graphics items and does the work
      (changes the model). Possible future configuration of the activeTool()
      can be done on the instances of various tools kept in the controller,
      like selectTool.
    * graphics items that make up the view sit back and watch the model,
      updating when it changes
    """
    
    dontAllowCrossoverToNonSegmentedBase = False

    _baseWidth = styles.PATH_BASE_WIDTH
    _toolRect = QRectF(0, 0,\
                       _baseWidth, _baseWidth)  # protected not private
    _rect = QRectF(-styles.PATH_BASE_HL_STROKE_WIDTH,\
                   -styles.PATH_BASE_HL_STROKE_WIDTH,\
                   _baseWidth + 2*styles.PATH_BASE_HL_STROKE_WIDTH,\
                   _baseWidth + 2*styles.PATH_BASE_HL_STROKE_WIDTH)
    _pen = QPen(styles.redstroke, styles.PATH_BASE_HL_STROKE_WIDTH)
    _brush = QBrush(Qt.NoBrush)
    
    def __init__(self, controller, parent=None):
        super(AbstractPathTool, self).__init__(parent)
        self._active = False
        self._controller = controller
        self._lastLocation = None
    
    ######################## Drawing #######################################
    def paint(self, painter, option, widget=None):
        painter.setPen(self._pen)
        painter.setBrush(self._brush)
        painter.drawRect(self._toolRect)
    
    def boundingRect(self):
        return self._rect
    
    ######################### Positioning and Parenting ####################
    def lastLocation(self):
        """A tuple (PathHelix, QPoint) representing the last
        known location of the mouse for purposes of positioning
        the graphic of a new tool on switching tools (the tool
        will have updateLocation(*oldTool.lastLocation()) called
        on it)"""
        return self._lastLocation
    
    def hoverEnterPathHelix(self, pathHelix, event):
        self.updateLocation(pathHelix, pathHelix.mapToScene(QPointF(event.pos())))

    def hoverLeavePathHelix(self, pathHelix, event):
        self.updateLocation(None, pathHelix.mapToScene(QPointF(event.pos())))
    
    def hoverMovePathHelix(self, pathHelix, event, flag=None):
        self.updateLocation(pathHelix, pathHelix.mapToScene(QPointF(event.pos())))
    
    def updateLocation(self, pathHelix, scenePos, *varargs):
        """Takes care of caching the location so that a tool switch
        outside the context of an event will know where to
        position the new tool and snaps self's pos to the upper
        left hand corner of the base the user is mousing over"""
        if pathHelix:
            if self.parentObject() != pathHelix:
                self.setParentItem(pathHelix)
            self._lastLocation = (pathHelix, scenePos)
            posItem = pathHelix.mapFromScene(scenePos)
            pos = self.helixPos(posItem)
            if pos != None:
                if pos != self.pos():
                    self.setPos(pos)
                self.update(self.boundingRect())
                if not self.isVisible():
                    self.show()
                    pass
        else:
            self._lastLocation = None
            if self.isVisible():
                self.hide()
            if self.parentItem() != mother:
                self.setParentItem(mother)

    def setActive(self, willBeActive, oldTool=None):
        """
        Called by PathController.setActiveTool when the tool becomes
        active. Used, for example, to show/hide tool-specific ui elements.
        """
        if self.isActive() and not willBeActive:
            self.setParentItem(mother)
            self.hide()

    def isActive(self):
        """Returns isActive"""
        return self._active != mother
    
    def widgetClicked(self):
        """Called every time a widget representing self gets clicked,
        not just when changing tools."""
        pass
    
    ####################### Coordinate Utilities ###########################
    def baseAtPoint(self, pathHelix, pt):
        """Returns the (strandType, baseIdx) corresponding
        to pt in pathHelix."""
        x, strandIdx = self.helixIndex(pt)
        vh = pathHelix.vhelix()
        if vh.evenParity():
            strandType = (StrandType.Scaffold, StrandType.Staple)[util.clamp(strandIdx, 0, 1)]
        else:
            strandType = (StrandType.Staple, StrandType.Scaffold)[util.clamp(strandIdx, 0, 1)]
        return (strandType, x)
    
    def helixIndex(self, point):
        """
        Returns the (row, col) of the base which point
        lies within.
        point is in PathHelix coordinates.
        """
        x = int(int(point.x()) / self._baseWidth)
        y = int(int(point.y()) / self._baseWidth)
        return (x, y)
    # end def

    def helixPos(self, point):
        """
        Snaps a point to the upper left corner of the base
        it is within.
        point is in PathHelix coordinates
        """
        col = int(int(point.x()) / self._baseWidth)
        row = int(int(point.y()) / self._baseWidth)
        # Doesn't know numBases, can't check if point is too far right
        if col < 0 or row < 0 or row > 1:
            return None
        return QPointF(col*self._baseWidth, row*self._baseWidth)
    # end def
# end class
