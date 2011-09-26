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
util.qtWrapImport('QtGui', globals(), [ 'QUndoCommand', 'QUndoStack'])


class PartInstance(QObject):

    def __init__(self, part, parent=None):
        super(PartInstance, self).__init__(parent)
        self._parent = parent   # parent is either a document or assembly
        self._part = part
        self._position = [0, 0, 0, 0, 0, 0]  # x, y, z,phi, theta, psi
    # end def

    ### SIGNALS ###
    partInstanceDestroyedSignal = pyqtSignal(QObject)  # self
    partInstanceMovedSignal = pyqtSignal(QObject)  # self
    partInstanceParentChangedSignal = pyqtSignal(QObject)  # new parent

    ### SLOTS ###

    ### METHODS ###
    def undoStack(self):
        return self._document.undoStack()

    def destroy(self):
        # QObject also emits a destroyed() Signal
        self.setParent(None)
        self.deleteLater()
    # end def

    def parent(selfr):

    def position(self):
        return self._position

    def bounds(self):
        """Return the latice indice bounds relative to the origin."""
        return self._bounds

    ### COMMANDS ###
