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

from parts.honeycombpart import HoneycombPart
from parts.squarepart import SquarePart
import util
util.qtWrapImport('QtCore', globals(), ['pyqtSignal', 'QObject'])
util.qtWrapImport('QtGui', globals(), ['QUndoCommand', 'QUndoStack'])


class Document(QObject):
    """
    The Document class is the root of the model. It has two main purposes:
    1. Serve as the parent all Part objects within the model.
    2. Track all sub-model actions on its undoStack.
    """
    def __init__(self):
        super(Document, self).__init__()
        self._undoStack = QUndoStack()
        self._parts = []
        self._assemblies = []
        self._controller = None
        
        # the dictionary maintains what is selected
        self._selectionDict = {}
        # the added list is what was recently selected or deselected
        self._selectedChangedDict = {}

    ### SIGNALS ###
    documentPartAddedSignal = pyqtSignal(QObject)  # part
    
    # dict of tuples of objects using the reference as the key, and the value is
    # a tuple with meta data
    # in the case of strands the metadata would be which endpoints of selected
    # e.g. { objectRef: (value0, value1),  ...}
    documentSelectedChangedSignal = pyqtSignal(dict)   # dict of tuples of items and data 
    ### SLOTS ###

    ### ACCESSORS ###
    def undoStack(self):
        """
        This is the actual undoStack to use for all commands. Any children
        needing to perform commands should just ask their parent for the
        undoStack, and eventually the request will get here.
        """
        return self._undoStack

    def parts(self):
        """Returns a list of parts associated with the document."""
        return self._parts

    def assemblies(self):
        """Returns a list of assemblies associated with the document."""
        return self._assemblies

    ### PUBLIC METHODS FOR QUERYING THE MODEL ###
    def addToSelection(self, obj, value):
       self._selectionDict[obj] = value
       self._selectedChangedDict[obj] = value
    # end def
    
    def removeFromSelection(self, obj):
        if obj in self._selectionDict:
            del self._selectionDict[obj]
            self._selectedChangedDict[obj] = (False, False)
    # end def
    
    def selectionDict(self):
        return self._selectionDict
    # end def
    
    def isModelSelected(self, obj):
        return obj in self._selectionDict
    # end def
    
    def updateSelection(self):
        """
        do it this way in the future when we have a better signaling architecture between views
        """
        # self.documentSelectedChangedSignal.emit(self._selectedChangedDict)
        """
        For now, individual objects need to emit signals
        """
        for obj, value in self._selectedChangedDict.iteritems():
            obj.selectedChangedSignal.emit(obj, value)
        # end for
        self._selectedChangedDict = {}
    # end def

    ### PUBLIC METHODS FOR EDITING THE MODEL ###
    def addHoneycombPart(self):
        """
        Create and store a new DNAPart and instance, and return the instance.
        """
        dnapart = None
        if len(self._parts) == 0:
            dnapart = HoneycombPart(document=self)
            self._addPart(dnapart)
        return dnapart

    def addSquarePart(self):
        """
        Create and store a new DNAPart and instance, and return the instance.
        """
        dnapart = None
        if len(self._parts) == 0:
            dnapart = SquarePart(document=self)
            self._addPart(dnapart)
        return dnapart

    def removeAllParts(self):
        """Used to reset the document. Not undoable."""
        for part in self._parts:
            part.remove(useUndoStack=False)
    # end def

    def removePart(self, part):
        self._parts.remove(part)

    ### PUBLIC SUPPORT METHODS ###
    def setController(self, controller):
        """Called by DocumentController setDocument method."""
        self._controller = controller

    ### PRIVATE SUPPORT METHODS ###
    def _addPart(self, part, useUndoStack=True):
        """Add part to the document via AddPartCommand."""
        c = self.AddPartCommand(self, part)
        util.execCommandList(self, [c], desc="Add part", useUndoStack=useUndoStack)
        return c.part()

    ### COMMANDS ###
    class AddPartCommand(QUndoCommand):
        """
        Undo ready command for deleting a part.
        """
        def __init__(self, document, part):
            QUndoCommand.__init__(self)
            self._doc = document
            self._part = part

        def part(self):
            return self._part

        def redo(self):
            if len(self._doc._parts) == 0:
                self._doc._parts.append(self._part)
                self._part.setDocument(self._doc)
                self._doc.documentPartAddedSignal.emit(self._part)

        def undo(self):
            self._part.setDocument(None)
            self._doc._parts.remove(self._part)
            self._part.partRemovedSignal.emit(self._part)
