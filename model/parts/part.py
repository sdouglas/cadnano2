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


class Part(QObject):
    _step = 21  # this is the period of the part lattice

    def __init__(self, document):
        """
        Parts are always parented to the document.  
        Parts know about their oligos, and the internal geometry of a part
        Copying a part recursively copies all elements in a part:
            VirtualHelices, Strands, etc
        
        PartInstances are parented to either the document or an assembly
        PartInstances know global position of the part
        Copying a PartInstance only creates a new PartInstance with the same
        Part(), with a mutable parent and position field
        
        """
        super(Part, self).__init__(document)
        self._document = None
        self._partInstances = []    # This is a list of ObjectInstances
        self._oligos = {}
        self._bounds = (0, 2*self._step)
    # end def

    ### SIGNALS ###
    partInstanceAddedSignal = pyqtSignal(QObject)  # self
    partDestroyedSignal = pyqtSignal(QObject)  # self
    sequenceClearedSignal = pyqtSignal(QObject)  # self

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

    def oligos(self):
        return self._oligos

    def addOligo(selg, oligo):
        self._oligos[oligo] = True

    def removeOligo(self, oligo):
        self._oligo[oligo] = False
        self.destroyOligo(oligo)

    def destroyOligo(self, oligo):
        del self._oligo[oligo]

    def bounds(self):
        """Return the latice indice bounds relative to the origin."""
        return self._bounds

    ### COMMANDS ###
    