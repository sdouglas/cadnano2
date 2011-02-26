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

        self.noDrag = QGraphicsView.NoDrag
        self.yesDrag = QGraphicsView.ScrollHandDrag
        self.setDragMode(self.noDrag)
        self.transformEnable = False
        self.dollyZoomEnable = False
        #print self.transformationAnchor()
        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)

        # self.horizontalScrollBar().setMaximum(800)
        # self.horizontalScrollBar().setMinimum(-800)
        #self.setSceneRect(-200,200,800,800)
        self.x0 = 0
        self.y0 = 0
        self.scale_size = 1.0
        self.scale_limit_max = 3.0
        self.scale_limit_min = .41
        self.last_scale_factor = 0.0
        self.key_mod = Qt.Key_Control
        self.key_pan = Qt.LeftButton
        self.key_pan_alt = Qt.MidButton
        self.key_zoom = Qt.RightButton
        self.sceneRootItem = None
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
        self.key_pan = button
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
        if event.key() == self.key_mod:
            self.transformEnable = True
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
        if event.key() == self.key_mod:
            self.transformEnable = False
            self.dollyZoomEnable = False
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
        if self.transformEnable == True:
            if self.dragMode() == self.yesDrag:
                """
                Add stuff to handle the pan event
                """
                xf = event.x()
                yf = event.y()
                self.sceneRootItem.translate((xf - self.x0)/self.scale_size,\
                                            (yf - self.y0)/self.scale_size)
                self.x0 = xf
                self.y0 = yf
            elif self.dollyZoomEnable == True:
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
        #if self.transformEnable == True:
        if self.transformEnable == True and qApp.keyboardModifiers():
            which_buttons = event.buttons()
            if which_buttons in [self.key_pan, self.key_pan_alt]:
                self.panEnable()
                self.x0 = event.pos().x()
                self.y0 = event.pos().y()
            elif which_buttons == self.key_zoom:
                self.dollyZoomEnable = True
                self.last_scale_factor = 0
                # QMouseEvent.y() returns the position of the mouse cursor
                # relative to the widget
                self.y0 = event.y()
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
        if self.transformEnable == True:
            # QMouseEvent.button() returns the button that triggered the event
            which_button = event.button()
            if which_button in [self.key_pan, self.key_pan_alt]:
                self.panDisable()
            elif which_button == self.key_zoom:
                self.dollyZoomEnable = False
            else:
                QGraphicsView.mouseReleaseEvent(self, event)
        # end if
        else:
            QGraphicsView.mouseReleaseEvent(self, event)
    #end def

    def panEnable(self):
        """Enable ScrollHandDrag Mode in QGraphicsView (displays a hand
        pointer)"""
        self.setDragMode(self.yesDrag)
    # end def

    def panDisable(self):
        """Disable ScrollHandDrag Mode in QGraphicsView (displays a hand
        pointer)
        
        """
        self.setDragMode(self.noDrag)
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
            if self.scale_limit_max > self.scale_size:
                self.scale(1.25, 1.25)
                self.scale_size *= 1.25
            # end if
        # end if
        else:
            if self.scale_limit_min < self.scale_size:
                self.scale(.8, .8)
                self.scale_size *= 0.8
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
        denom = abs(yf - self.y0)
        if denom > 0:
            scale_factor = (self.height() / 2) % denom
            if self.last_scale_factor != scale_factor:
                self.last_scale_factor = scale_factor
                # zoom in if mouse y position is getting bigger
                if yf - self.y0 > 0:
                    if self.scale_limit_max > self.scale_size:
                        self.scale(1.25, 1.25)
                        self.scale_size *= 1.25
                    # end if
                # end else
                else:  # else id smaller zoom out
                    if self.scale_limit_min < self.scale_size:
                        self.scale(.8, .8)
                        self.scale_size *= 0.8
                    # end if
                # end else
        # end if
    # end def
#end class
