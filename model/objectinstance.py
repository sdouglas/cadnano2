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

import util
util.qtWrapImport('QtCore', globals(), ['pyqtSignal', 'QObject'])
util.qtWrapImport('QtGui', globals(), [])

class ObjectInstance(QObject):

    def __init__(self, referenceObject, parent):
        super(ObjectInstance, self).__init__(referenceObject)
        self._parent = parent   # parent is either a document or assembly
        self._object = referenceObject
        self._position = [0, 0, 0, 0, 0, 0]  # x, y, z,phi, theta, psi
    # end def

    ### SIGNALS ###
    objinstanceDestroyedSignal = pyqtSignal(QObject)  # self
    objinstanceMovedSignal = pyqtSignal(QObject)  # self
    objinstanceParentChangedSignal = pyqtSignal(QObject)  # new parent

    ### SLOTS ###

    ### METHODS ###
    def undoStack(self):
        return self._document.undoStack()

    def destroy(self):
        # QObject also emits a destroyed() Signal
        self.setParent(None)
        self.deleteLater()
    # end def

    def reference(self):
        return self._object
    # end def

    def parent(self):
        return self._parent

    def position(self):
        return self._position

    def shallowCopy(self):
        oi = ObjectInstance(self._object, self._parent)
        oi._position = list(self._position)
        return oi
    # end def

    def deepCopy(self, referenceObject, parent):
        oi = ObjectInstance(referenceObject, parent)
        oi._position = list(self._position)
        return oi
    # end def
    ### COMMANDS ###
