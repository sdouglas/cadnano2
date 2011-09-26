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

class Assembly(QObject):
    def __init__(self, document, partList=None):
        super(Assembly, self).__init__(document)
        self._document = document
        self._parts = partList          # This is a list of member parts
        self._assemblyInstances = []    # This is a list of ObjectInstances
    # end def

    ### SIGNALS ###
    assemblyInstanceAddedSignal = pyqtSignal(QObject)  # new oligo
    assemblyDestroyedSignal = pyqtSignal(QObject)  # self

    ### SLOTS ###

    ### METHODS ###
    def undoStack(self):
        return self._document.undoStack()

    def destroy(self):
        # QObject also emits a destroyed() Signal
        self.setParent(None)
        self.deleteLater()
    # end def
    
    def document(self):
        return self._document
    # end def
    
    def parts(self):
        for part in self._parts:
            yield part
    # end def

    def instances(self):
        for inst in self._assemblyInstances:
            yield inst
    # end def
    
    ### COMMANDS ###
    