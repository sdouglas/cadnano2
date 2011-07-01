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
recordinggraphicsitem.py

Created by Shawn on 2011-07-01.
"""

import util


util.qtWrapImport('QtCore', globals(), ['Qt', 'QEvent', 'QString', 'QRectF'])
util.qtWrapImport('QtGui', globals(), ['QGraphicsItem', 'QGraphicsObject'])

class SceneType:
    Slice = 0
    Path = 1

class RecordableQGraphicsItem(object):
    """QGraphicsItems that need to report actions to the test recorder
    via sceneEvent should also inherit from this class."""

    def __init__(self, controller, sceneType):
        """docstring for __init__"""
        print "init RecordableQGraphicsItem"
        self.controller = controller
        self.sceneType = sceneType
        self.recordingEnabled = False
        if self.controller.testRecorder:
            self.recordingEnabled = True

    def sceneEvent(self, event):
        """Included for unit testing in order to grab events that are sent
        via QGraphicsScene.sendEvent()."""
        if self.recordingEnabled:
            if self.sceneType == SceneType.Slice:
                pass
                # self.controller.testRecorder.pathSceneEvent(event, self.number())
            if self.sceneType == SceneType.Path:
                pass
                # self.controller.testRecorder.sliceSceneEvent(event, self.number())
        if event.type() == QEvent.MouseButtonPress:
            self.mousePressEvent(event)
            return True
        elif event.type() == QEvent.MouseButtonRelease:
            self.mouseReleaseEvent(event)
            return True
        elif event.type() == QEvent.MouseMove:
            self.mouseMoveEvent(event)
            return True
        QGraphicsObject.sceneEvent(self, event)
        return False
