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
# import Qt stuff into the module namespace with PySide, PyQt4 independence
util.qtWrapImport('QtCore', globals(), ['pyqtSignal', 'QObject'])
util.qtWrapImport('QtGui', globals(), [ 'QUndoCommand', 'QUndoStack'])

class Oligo(QObject):
    def __init__(self):
        super(Oligo, self).__init__()
        self._part = None
        self._strands = []
        self._length = 0
        self._isLoop = False

    ### SIGNALS ###
    notifyMergedStrandsWithNewOligoSignal = pyqtSignal(QObject)  # new oligo
    appearanceChangedSignal = pyqtSignal(QObject)  # self
    sequenceAddedSignal = pyqtSignal(QObject)  # self
    sequenceClearedSignal = pyqtSignal(QObject)  # self

    ### SLOTS ###

    ### METHODS ###
    def part(self):
        return self._part

    def strands(self):
        return self._strands

    def length(self):
        return self._length

    def isLoop(self):
        return self._isLoop

    ### COMMANDS ###
    