#!/usr/bin/env python
# encoding: utf-8

# The MIT License
# 
# Copyright (c) 2010 Wyss Institute at Harvard University
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
mouseEventFilter.py

Created by Nick Conway on 2011-01-17.
Copyright (c) 2010 . All rights reserved.
"""

import sys
import math

from PyQt4.QtCore import *
from PyQt4.QtGui import *

class mouseEventFilter(QObject):
    def __init__(self, myQGraphicsView,myQGraphicsScene):
        """
            on initialization we need to bind the Ctrl/command key to 
            enable manipulation of the view 
        """
        super(QObject, self).__init__() 
        self.myGView = myQGraphicsView
        self.myGScene = myQGraphicsScene
        
        #self.myGView.mousePressEvent = lambda event: event.accept()
        #self.myGView.mouseReleaseEvent = lambda event: event.accept()
        #self.myGview.mouseMoveEvent = lambda event: event.ignore()
        #self.myGView.mouseMoveEvent = lambda event: self.panMove(event)
        self.x0 = 0
        self.y0 = 0
        self.noDrag = QGraphicsView.NoDrag
        self.yesDrag = QGraphicsView.ScrollHandDrag
        self.myGView.setDragMode(self.noDrag)
        self.transformEnable = False
        self.dollyZoomEnable = False

    # end def
    
    def eventFilter(self,  obj,  event):
        if event.type() == QEvent.KeyPress:
            if event.key() == Qt.Key_Control:
                self.transformEnable = True
                # print "control pressed"
                return True
        elif event.type() == QEvent.KeyRelease:
            if event.key() == Qt.Key_Control:    
                self.transformEnable = False
                # print "control released"
                self.panDisable()
                return True
        elif event.type() == QEvent.Wheel:
            self.wheelHandler(event)
            return True
        if self.transformEnable == True:
            # print "somethinf worked"
            # print event.type() , QEvent.MouseButtonPress, QEvent.MouseButtonRelease
            if event.type() == QEvent.MouseButtonPress:
                # print "MousePress filter"
                self.mousePressHandler(event)
                return True
            elif event.type() == QEvent.MouseButtonRelease:
                # print "MouseRelease filter"    
                self.mouseReleaseHandler(event)
                return True
            elif event.type() == QEvent.MouseMove:
                self.panMove(event)
                return True
            else:
                return False
        else:
            ## print "Somethign else" 
            return False
    # end def
    
    def wheelHandler(self,event):
        #if self.transformEnable == True:
            ## print "wheel zoom"
        self.wheel_zoom(event)
        # end if    
    #end def
    
    def panMove(self,event):
        """
            Must reimplement mouseMoveEvent of QGraphicsView to allow ScrollHandDrag due
            to the fact that events are intercepted breaks this feature.
        """
        if self.transformEnable == True:
            # print "Mouse Move 1", self.yesDrag, self.myGView.dragMode()
            if self.myGView.dragMode() == self.yesDrag: 
                event.accept()
                """
                Add stuff to handle the pan event
                """
                # print "Mouse Move 2", self.x0, self.y0
                xf = event.pos().x()
                yf = event.pos().y()
                self.myGView.translate(xf-self.x0,yf-self.y0)
                self.x0 = xf
                self.y0 = yf
    # end def
    
    def mousePressHandler(self,event):
        if self.transformEnable == True:
            which_buttons = event.buttons()
            if which_buttons == Qt.LeftButton:
                # print "panning on"
                self.panEnable()
                self.x0 = event.pos().x()
                self.y0 = event.pos().y()
            #elif which_buttons == Qt.RightButton:
            #    self.dollyZoomEnable = True
    #end def
    
    def mouseReleaseHandler(self,event):
        if self.transformEnable == True:
            which_buttons = event.buttons()
            # print "panning off"
            if which_buttons == Qt.LeftButton:
                self.panDisable()
            # elif which_buttons == Qt.RightButton:
            #    self.dollyZoomEnable = False
        # end if
    #end def
    
    def panEnable(self):
        # print "dragging enabled"
        self.myGView.setDragMode(self.yesDrag)
    # end def
    
    def panDisable(self):
        ## print "dragging disabled"
        self.myGView.setDragMode(self.noDrag)
    # end def
    
    def wheel_zoom(self,event):
        if event.delta() > 0: # rotated away from the user
            self.myGView.scale(1.25,1.25)
        # end if
        else: 
            self.myGView.scale(.8,.8)
        # end else
    # end def
    
    def dolly_zoom(self,event):
        y0 = event.lastPos().y()
        yf = event.pos().y()
        if yf-y0 > 0:       # if mouse y position is getting bigger zoom in
            #self.myGView.scale(1.25,1.25)
            pass
        # end else
        else: # else id smaller zoom out
            #self.myGView.scale(.8,.8)
            pass
        # end else 
    # end def
      
#end class