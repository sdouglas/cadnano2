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
util.qtWrapImport('QtCore', globals(), ['pyqtSignal', 'QObject', 'Qt'])
util.qtWrapImport('QtGui', globals(), ['QUndoStack'])

class Strand(QObject):
    
    def __init__(self, vstrand, indexL, indexR):
        super(Strand, self).__init__(vstrand)
        self._oligo = None
        self._vstrand = vstrand
        
        self._strand5p = None
        self._strand3p = None
        self.vBaseIndexL = indexL
        self.vBaseIndexR = indexR
        
        
        self._decorators = {}
        self._sequence = None
        self._note = None
    # end def
    
    ### SIGNALS ###
    hasNewOligoSignal = pyqtSignal(QObject)
    destroyedSignal = pyqtSignal(QObject)
    resizedSignal = pyqtSignal(QObject, int)
    xover3pCreatedSignal = pyqtSignal(QObject, int)
    xover3pDestroyedSignal = pyqtSignal(QObject, int)
    decoratorCreatedSignal = pyqtSignal(QObject, QObject, int)
    decoratorDestroySignal = pyqtSignal(QObject, int)
    
    ### SLOTS ###
    
    
    ### Methods ###
    def undoStack(self):
        return self._vstrand.undoStack()
    
    def vstrand(self):
        return self._vstrand
    # end def
    
    def oligo(self):
        return self._oligo
    # end def
    
    def setNewOligo(self, newOligo):
        
    # end def
    
    def destroy(self):
        
    # end def
    
    def resize(self):
    
    # end def
    
    def merge(self, idx):
        
    # end def
    
    def split(self, idx):
        
    # end def
    
    def copy(self):
        
    # end def
    
    def addSequence(self):
        
    # end def
    
    