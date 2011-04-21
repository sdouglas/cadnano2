#!/usr/bin/env python
# encoding: utf-8

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
CustomQGraphicsView.py
.. module:: CustomQGraphicsView
   :platform: Unix, Windows, Mac OS X
   :synopsis: A Custom QGraphicsView module to allow focus input events
   like mouse clicks and panning and zooming
   
.. moduleauthor::  Nick Conway on 2011-01-17.
Copyright (c) 2010 . All rights reserved.

"""
from PyQt4.QtCore import *
from PyQt4.QtGui import *


class CustomQGraphicsView(QGraphicsView):
    """
    Base class for QGraphicsViews with Mouse Zoom and Pan support via the
    Control/Command shortcut key.

    A QGraphics View stores info on the view and handles mouse events for
    zooming and panning

    Ctrl-MidMouseButton = Pan
    Ctrl-RightMouseButton = Dolly Zoom
    MouseWheel = Zoom

    Parameters
    ----------
    parent: type of QWidget, such as QWidget.splitter() for the type of
    View its has

    See Also
    --------

    Examples
    --------

    For details on these and other miscellaneous methods, see below.
    """
    def __init__(self, parent=None):
        """on initialization we need to bind the Ctrl/command key to
        enable manipulation of the view

        Args:
           self

        Kwargs:
           parent (QWidget): type of QWidget, such as QWidget.splitter() for the type of
           View its has

        Returns:
           self

        Raises:
           None
        
        """
        super(QGraphicsView, self).__init__(parent)

        self._noDrag = QGraphicsView.NoDrag
        self._yesDrag = QGraphicsView.ScrollHandDrag
        self.setDragMode(self._noDrag)
        self._transformEnable = False
        self._dollyZoomEnable = False
        #print self.transformationAnchor()
        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        # self.setAlignment(Qt.AlignHCenter)
        # self.horizontalScrollBar().setMaximum(800)
        # self.horizontalScrollBar().setMinimum(-800)
        #self.setSceneRect(-200,200,800,800)
        self._x0 = 0
        self._y0 = 0
        self._scale_size = 1.0
        self._scale_limit_max = 3.0
        self._scale_limit_min = .41
        self._last_scale_factor = 0.0
        self._key_mod = Qt.Key_Control
        self._key_pan = Qt.LeftButton
        self._key_pan_alt = Qt.MidButton
        self.key_zoom = Qt.RightButton
        self.sceneRootItem = None
        
        self._pressList = []
        self.setStyleSheet("QGraphicsView { background-color: rgb(96.5%, 96.5%, 96.5%); }")
        # self.setStyleSheet("QGraphicsView { background-color: #FF0000; }")
        # self.setStyleSheet("QGraphicsView { background-color: rgba(255, 0, 0, 75%); }")
    # end def

    def setKeyPan(self, button):
        """Set the class pan button remotely

        Args:
           self
           button: QtGui.Qt Namespace button identifier

        Kwargs:
            None

        Returns:
           None

        Raises:
           None
           
        """
        self._key_pan = button
    # end def

    def addToPressList(self, item):
        self._pressList.append(item)
    # end def

    def keyPressEvent(self, event):
        """
        Args:
           self
           event (QKeyEvent): the event

        Kwargs:
            None

        Returns:
           None

        Raises:
           None
        """
        if event.key() == self._key_mod:
            self._transformEnable = True
        else:
            QGraphicsView.keyPressEvent(self, event)
        # end else
    # end def

    def keyReleaseEvent(self, event):
        """
        Args:
           self
           event (QKeyEvent): the event

        Kwargs:
            None

        Returns:
           None

        Raises:
           None
        """
        if event.key() == self._key_mod:
            self._transformEnable = False
            self._dollyZoomEnable = False
            self.panDisable()
        # end if
        else:
            QGraphicsView.keyReleaseEvent(self, event)
        # end else
    # end def
    
    def enterEvent(self,event):
        self.setFocus(True)
        QGraphicsView.enterEvent(self,event)

    def leaveEvent(self,event):
        self.setFocus(False)
        QGraphicsView.leaveEvent(self,event)

    def mouseMoveEvent(self, event):
        """Must reimplement mouseMoveEvent of QGraphicsView to allow
        ScrollHandDrag due to the fact that events are intercepted
        breaks this feature.

        Args:
           self
           event (QMouseEvent): the event

        Kwargs:
            None

        Returns:
           None

        Raises:
           None
        
        """
        if self._transformEnable == True:
            if self.dragMode() == self._yesDrag:
                """
                Add stuff to handle the pan event
                """
                xf = event.posF().x()
                yf = event.posF().y()
                self.sceneRootItem.translate((xf - self._x0)/self._scale_size,\
                                            (yf - self._y0)/self._scale_size)
                self._x0 = xf
                self._y0 = yf
            elif self._dollyZoomEnable == True:
                self.dollyZoom(event)
            #else:
            #    QGraphicsView.mouseMoveEvent(self, event)
        #else:
        # adding this allows events to be passed to items underneath
        QGraphicsView.mouseMoveEvent(self, event)
    # end def

    def mousePressEvent(self, event):
        """This takes a QMouseEvent for the event
        Args:
           self
           event (QMouseEvent): the event

        Kwargs:
            None

        Returns:
           None

        Raises:
           None
        
        """
        #if self._transformEnable == True:
        if self._transformEnable == True and qApp.keyboardModifiers():
            which_buttons = event.buttons()
            if which_buttons in [self._key_pan, self._key_pan_alt]:
                self.panEnable()
                self._x0 = event.posF().x()
                self._y0 = event.posF().y()
            elif which_buttons == self.key_zoom:
                self._dollyZoomEnable = True
                self._last_scale_factor = 0
                # QMouseEvent.y() returns the position of the mouse cursor
                # relative to the widget
                self._y0 = event.posF().y()
            else:
                QGraphicsView.mousePressEvent(self, event)
        else:
            QGraphicsView.mousePressEvent(self, event)
    #end def

    def mouseReleaseEvent(self, event):
        """This takes a QMouseEvent for the event

        Args:
           self
           event (QMouseEvent): the event

        Kwargs:
            None

        Returns:
           None

        Raises:
           None
        
        """
        if self._transformEnable == True:
            # QMouseEvent.button() returns the button that triggered the event
            which_button = event.button()
            if which_button in [self._key_pan, self._key_pan_alt]:
                self.panDisable()
            elif which_button == self.key_zoom:
                self._dollyZoomEnable = False
            else:
                QGraphicsView.mouseReleaseEvent(self, event)
        # end if
        else:
            if len(self._pressList):
                event_pos = event.pos()
                for item in self._pressList:
                    item.mouseUp(event_pos)
                #end for
                self._pressList = []
            # end if 
            QGraphicsView.mouseReleaseEvent(self, event)
    #end def
    
    # def resizeEvent(self,event):
    #     h_new = event.size().height()
    #     h_old = event.oldSize().height()
    #     self.resetScale(height_old, height_new)
    # # end def

    def panEnable(self):
        """Enable ScrollHandDrag Mode in QGraphicsView (displays a hand
        pointer)"""
        self.setDragMode(self._yesDrag)
    # end def

    def panDisable(self):
        """Disable ScrollHandDrag Mode in QGraphicsView (displays a hand
        pointer)
        
        """
        self.setDragMode(self._noDrag)
    # end def

    def wheelEvent(self, event):
        """This takes a QMouseEvent for the event

        Args:
           self
           event (QMouseEvent): the event

        Kwargs:
            None

        Returns:
           None

        Raises:
           None
        
        """
        self.wheelZoom(event)
    #end def

    def wheelZoom(self, event):
        """This takes a QMouseEvent for the event

        Args:
           self
           event (QMouseEvent): the event

        Kwargs:
            None

        Returns:
           None

        Raises:
           None
        
        """
        if event.delta() > 0:  # rotated away from the user
            if self._scale_limit_max > self._scale_size:
                self.scale(1.25, 1.25)
                #self.centerOn(1.25*event.x(),1.25*event.y())
                #self.centerOn(QPointF(0.8*event.globalX(),0.8*event.globalY()))
                self._scale_size *= 1.25
            # end if
        # end if
        else:
            if self._scale_limit_min < self._scale_size:
                self.scale(.8, .8)
                #self.translate(event.x(),event.y())
                #self.centerOn(QPointF(1.25*event.globalX(),1.25*event.globalY()))
                #self.centerOn(QPointF(0.8*event.x(),0.8*event.y()))
                self._scale_size *= 0.8
            # end if
        # end else
    # end def

    def dollyZoom(self, event):
        """This takes a QMouseEvent for the event

        Args:
           self
           event (QMouseEvent): the event

        Kwargs:
            None

        Returns:
           None

        Raises:
           None
        
        """
        # QMouseEvent.y() returns the position of the mouse cursor relative
        # to the widget
        yf = event.y()
        denom = abs(yf - self._y0)
        if denom > 0:
            scale_factor = (self.height() / 2) % denom
            if self._last_scale_factor != scale_factor:
                self._last_scale_factor = scale_factor
                # zoom in if mouse y position is getting bigger
                if yf - self._y0 > 0:
                    if self._scale_limit_max > self._scale_size:
                        self.scale(1.25, 1.25)
                        self._scale_size *= 1.25
                    # end if
                # end else
                else:  # else id smaller zoom out
                    if self._scale_limit_min < self._scale_size:
                        self.scale(.8, .8)
                        self._scale_size *= 0.8
                    # end if
                # end else
        # end if
    # end def
    
    def resetScale(self):
        """
        reset the scale to 1
        """
        # use the transform value if you want to get how much the view 
        # has been scaled
        self._scale_size = self.transform().m11() 
        
        # self._scale_limit_min = 0.41*self._scale_size
        # make it so fitting in view is zoomed minimum
        # still gives you one zoom level out before violates limit
        self._scale_limit_min = self._scale_size
        
        # use this if you want to reset the zoom in limit
        # self._scale_limit_max = 3.0*self._scale_size
        
        self._last_scale_factor = self._scale_size    
    # end def
    
    def zoomToFit(self):
        # Auto zoom to center the scene
        thescene = self.sceneRootItem.scene()
        # order matters?
        self.sceneRootItem.resetTransform() # zero out translations
        self.resetTransform() # zero out scaling
        scene_rect = thescene.sceneRect()
        self.updateSceneRect(scene_rect)
        
        self.fitInView(scene_rect, Qt.KeepAspectRatio) # fit in view
        # theview.ensureVisible(self.mapRectToScene(new_rect))
        #theview.ensureVisible(scene_rect)

        self.resetScale() # adjust scaling so that translation works
    # end def
#end class
