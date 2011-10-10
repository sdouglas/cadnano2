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
from cadnano import app
from views import styles

import util
# import Qt stuff into the module namespace with PySide, PyQt4 independence
util.qtWrapImport('QtCore', globals(), ['Qt'])
util.qtWrapImport('QtGui', globals(),  ['QGraphicsView', 'qApp', 'QPen'])

# for OpenGL mode
try:
    from OpenGL import GL
    from PyQt4.QtOpenGL import QGLWidget, QGLFormat, QGL
except:
    GL = False

GL = False

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
        """
        On initialization, we need to bind the Ctrl/command key to
        enable manipulation of the view.
        """
        QGraphicsView.__init__(self, parent)
        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.setRubberBandSelectionMode(Qt.IntersectsItemShape)
        self.setStyleSheet("QGraphicsView { background-color: rgb(96.5%, 96.5%, 96.5%); }")
        # Pan and dolly defaults
        self._transformEnable = False
        self._dollyZoomEnable = False
        self._noDrag = QGraphicsView.RubberBandDrag
        self._yesDrag = QGraphicsView.ScrollHandDrag
        self.setDragMode(self._noDrag)
        self._x0 = 0
        self._y0 = 0
        self._scale_size = 1.0
        self._scale_limit_max = 3.0
        self._scale_limit_min = 0.41
        self._scaleUpRate = 0.01
        self._scaleDownRate = 0.01
        self._scaleFitFactor = 1  # sets initial zoom level
        self._last_scale_factor = 0.0
        self.sceneRootItem = None  # the item to transform
        # Keyboard panning
        self._key_pan_delta_x = styles.PATH_BASE_WIDTH * 21
        self._key_pan_delta_y = styles.PATH_HELIX_HEIGHT + styles.PATH_HELIX_PADDING/2
        # Modifier keys and buttons
        self._key_mod = Qt.Key_Control
        self._button_pan = Qt.LeftButton
        self._button_pan_alt = Qt.MidButton
        self._button_zoom = Qt.RightButton
        # Misc
        self._pressList = []  # bookkeeping to handle passing mouseevents
        self.toolbar = None  # custom hack for the paint tool palette
        
        if GL:
            self.setViewport(QGLWidget(QGLFormat(QGL.SampleBuffers)))
            self.setViewportUpdateMode(QGraphicsView.FullViewportUpdate)
        else:
            self.setViewportUpdateMode(QGraphicsView.MinimalViewportUpdate)
    # end def

    def setScaleFitFactor(self, value):
        """docstring for setScaleFitFactor"""
        self._scaleFitFactor = value

    def setKeyPan(self, button):
        """Set the class pan button remotely"""
        self._button_pan = button
    # end def

    def addToPressList(self, item):
        """docstring for addToPressList"""
        self._pressList.append(item)
    # end def

    def keyPanDeltaX(self):
        """Returns the distance in scene space to move the sceneRootItem when
        panning left or right."""
        # PyQt isn't aware that QGraphicsObject isa QGraphicsItem and so
        # it returns a separate python object if, say, childItems() returns
        # a QGraphicsObject casted to a QGraphicsItem. If this is the case,
        # we can still find the QGraphicsObject thusly:
        candidateDxDeciders = list(self.sceneRootItem.childItems())
        candidateDxDeciders = candidateDxDeciders +\
                           [cd.toGraphicsObject() for cd in candidateDxDeciders]
        for cd in candidateDxDeciders:
            if cd == None:
                continue
            keyPanDXMethod = getattr(cd, 'keyPanDeltaX', None)
            if keyPanDXMethod != None:
                return keyPanDXMethod()
        return 100

    def keyPanDeltaY(self):
        """Returns the distance in scene space to move the sceneRootItem when
        panning left or right."""
        candidateDyDeciders = list(self.sceneRootItem.childItems())
        candidateDyDeciders = candidateDyDeciders +\
                           [cd.toGraphicsObject() for cd in candidateDyDeciders]
        for cd in candidateDyDeciders:
            if cd == None:
                continue
            keyPanDYMethod = getattr(cd, 'keyPanDeltaY', None)
            if keyPanDYMethod != None:
                return keyPanDYMethod()
        return 100

    def keyPressEvent(self, event):
        """docstring for keyPressEvent"""
        if event.key() == self._key_mod:
            self._transformEnable = True
            QGraphicsView.keyPressEvent(self, event)
        elif event.key() == Qt.Key_Left:
            self.sceneRootItem.translate(self.keyPanDeltaX(), 0)
        elif event.key() == Qt.Key_Up:
            self.sceneRootItem.translate(0,self.keyPanDeltaY())
        elif event.key() == Qt.Key_Right:
            self.sceneRootItem.translate(-self.keyPanDeltaX(),0)
        elif event.key() == Qt.Key_Down:
            self.sceneRootItem.translate(0, -self.keyPanDeltaY())
        else:
            QGraphicsView.keyPressEvent(self, event)
        # end else
    # end def

    def keyReleaseEvent(self, event):
        """docstring for keyReleaseEvent"""
        if event.key() == self._key_mod:
            self._transformEnable = False
            self._dollyZoomEnable = False
            self.panDisable()
        # end if
        else:
            QGraphicsView.keyReleaseEvent(self, event)
        # end else
    # end def

    def enterEvent(self, event):
        self.setFocus()
        self.setDragMode(self._noDrag)
        QGraphicsView.enterEvent(self, event)

    def leaveEvent(self, event):
        self.clearFocus()
        QGraphicsView.leaveEvent(self, event)

    def mouseMoveEvent(self, event):
        """
        Must reimplement mouseMoveEvent of QGraphicsView to allow
        ScrollHandDrag due to the fact that events are intercepted
        breaks this feature.
        """
        if self._transformEnable == True:
            
            # self._skipEvent = False if self._skipEvent == True else True
            
            if self.dragMode() == self._yesDrag:
                # Add stuff to handle the pan event
                xf = event.posF().x()
                yf = event.posF().y()
                factor = self.transform().m11()
                self.sceneRootItem.translate((xf - self._x0)/factor,\
                                             (yf - self._y0)/factor)
                # self.translate((xf - self._x0)/factor,\
                #                             (yf - self._y0)/factor)
                self._x0 = xf
                self._y0 = yf
            elif self._dollyZoomEnable == True:
                self.dollyZoom(event)
        # adding this allows events to be passed to items underneath
        QGraphicsView.mouseMoveEvent(self, event)
    # end def

    def mousePressEvent(self, event):
        """docstring for mousePressEvent"""
        if self._transformEnable == True and qApp.keyboardModifiers():
            which_buttons = event.buttons()
            if which_buttons in [self._button_pan, self._button_pan_alt]:
                self.panEnable()
                self._x0 = event.posF().x()
                self._y0 = event.posF().y()
            elif which_buttons == self._button_zoom:
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
        """If panning, stop. If handles were pressed, release them."""
        if self._transformEnable == True:
            # QMouseEvent.button() returns the button that triggered the event
            which_button = event.button()
            if which_button in [self._button_pan, self._button_pan_alt]:
                self.panDisable()
            elif which_button == self._button_zoom:
                self._dollyZoomEnable = False
            else:
                QGraphicsView.mouseReleaseEvent(self, event)
        # end if
        else:
            if len(self._pressList):  # Notify any pressed items to release
                event_pos = event.pos()
                for item in self._pressList:
                    try:
                        item.customMouseRelease(event_pos)
                    except:
                        item.mouseReleaseEvent(event)
                #end for
                self._pressList = []
            # end if
            QGraphicsView.mouseReleaseEvent(self, event)
    #end def

    def panEnable(self):
        """Enable ScrollHandDrag Mode in QGraphicsView (displays a hand
        pointer)"""
        self.setDragMode(self._yesDrag)
    # end def

    def panDisable(self):
        """Disable ScrollHandDrag Mode in QGraphicsView (displays a hand
        pointer)"""
        self.setDragMode(self._noDrag)
    # end def

    def wheelEvent(self, event):
        """docstring for wheelEvent"""
        self.wheelZoom(event)
    #end def

    def wheelZoom(self, event):
        """docstring for wheelZoom"""
        self.safeScale(event.delta())

    def safeScale(self, delta):
        currentScaleLevel = self.transform().m11()
        scaleFactor = 1 + delta * \
           (self._scaleDownRate if delta < 0 else self._scaleUpRate) * \
           (app().prefs.zoomSpeed/100.)
        newScaleLevel = currentScaleLevel * scaleFactor
        newScaleLevel = util.clamp(currentScaleLevel * scaleFactor,\
                              self._scale_limit_min,\
                              self._scale_limit_max)
        scaleChange = newScaleLevel / currentScaleLevel
        self.scale(scaleChange, scaleChange)
    
    def scaleUp(self, factor):
        if self._scale_limit_max > self._scale_size:
            scaleFactor = factor * self._scaleUpRate
            self.scale(scaleFactor, scaleFactor)
            self._scale_size *= self.scaleFactor

    def dollyZoom(self, event):
        """docstring for dollyZoom"""
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
                    self.scaleUp()
                # end else
                else:  # else id smaller zoom out
                    self.scaleDown()
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
        self._scale_limit_min = self._scale_size*self._scaleFitFactor

        # use this if you want to reset the zoom in limit
        # self._scale_limit_max = 3.0*self._scale_size

        self._last_scale_factor = 0.0
    # end def

    def zoomToFit(self):
        # Auto zoom to center the scene
        thescene = self.sceneRootItem.scene()
        # order matters?
        self.sceneRootItem.resetTransform() # zero out translations
        self.resetTransform() # zero out scaling
        if self.toolbar:  # HACK: move toolbar so it doesn't affect sceneRect
            self.toolbar.setPos(0, 0)
        thescene.setSceneRect(thescene.itemsBoundingRect())
        scene_rect = thescene.sceneRect()
        if self.toolbar:  # HACK, pt2: move toolbar back
            self.toolbar.setPos(self.mapToScene(0, 0))
        self.fitInView(scene_rect, Qt.KeepAspectRatio) # fit in view
        self.resetScale() # adjust scaling so that translation works
        # adjust scaling so that the items don't fill 100% of the view 
        # this is good for selection
        self.scale(self._scaleFitFactor, self._scaleFitFactor)
        self._scale_size *= self._scaleFitFactor
    # end def

    def paintEvent(self, event):
        if self.toolbar:
            self.toolbar.setPos(self.mapToScene(0, 0))
        QGraphicsView.paintEvent(self, event)
#end class
