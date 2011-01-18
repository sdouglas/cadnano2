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
mouseQGraphicsScence.py

Created by Nick Conway on 2011-01-17.
Copyright (c) 2010 . All rights reserved.
"""

import sys
import math

from PyQt4.QtCore import *
from PyQt4.QtGui import *

class mouseQGraphicsScene(QGraphicsScene):
    """
        This function setsup the events associated with a QGraphicsView
        related to mouse panning and zoom
    """
    def __init__(self, myQGraphicsView):
        """
            on initialization we need to bind the Ctrl/command key to 
            enable manipulation of the view 
        """
        super(mouseQGraphicsScene, self).__init__() 
        self.myGView = myQGraphicsView
        self.myGView.mouseMoveEvent = lambda event: self.panMove(event)
        self.noDrag = QGraphicsView.NoDrag
        self.yesDrag = QGraphicsView.ScrollHandDrag
        self.myGView.setDragMode(self.noDrag)
        self.transformEnable = False
        self.dollyZoomEnable = False
        self.x0 = 0
        self.y0 = 0
    # end def
    
    def mouseMoveEvent(self,event):
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
        else:
            QGraphicsView.mouseMoveEvent(self,event)
    # end def
    
    def keyPressEvent(self,event):
        if event.key() == Qt.Key_Control:
            event.accept()
            print "control pressed"
            self.transformEnable = True    
        # end if
        else:
            QGraphicsScene.keyPressEvent(self, event)
        # end else
    # end def    
    
    def keyReleaseEvent(self,event):
        if event.key() == Qt.Key_Control:
            event.accept()
            print "control released"
            self.transformEnable = False
            self.panDisable()
        # end if
        else:
            QGraphicsScene.keyPressEvent(self, event)
        # end else
    # end def
    
    def wheelEvento(self,event):
        if self.transformEnable == True:
            #print "wheel zoom"
            self.wheel_zoom(event)
        # end if    
    #end def
    
    # def mouseMoveEvent(self,event):
    #     if self.dollyZoomEnable == True and self.transformEnable == True:
    #         #print "dolly_zoom"
    #         self.dolly_zoom(event)
    #     # end if    
    # #end def
    
    
    def mousePressEvent(self,event):
        if self.transformEnable == True:
            which_buttons = event.buttons()
            if which_buttons == Qt.LeftButton:
                # print "panning on"
                self.panEnable()
                self.x0 = event.pos().x()
                self.y0 = event.pos().y()
            #elif which_buttons == Qt.RightButton:
                #self.dollyZoomEnable = True       
        # end if
        else:
            QGraphicsScene.mousePressEvent(self, event)
        # end else
    #end def
    
    def mouseReleaseEvent(self,event):
        if self.transformEnable == True:
            which_buttons = event.buttons()
            #print "panning off"
            if which_buttons == Qt.LeftButton:
                self.panDisable()
            #elif which_buttons == Qt.RightButton:
            #    self.dollyZoomEnable = False
        # end if
        else:
            QGraphicsScene.mouseReleaseEvent(self, event)
        # end else
    #end def
    
    def panEnable(self):
        #print "dragging enabled"
        self.myGView.setDragMode(self.yesDrag)
    # end def
    
    def panDisable(self):
        #print "dragging disabled"
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
    
# end class