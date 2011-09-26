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
util.qtWrapImport('QtGui', globals(), [ 'QUndoCommand', 'QUndoStack'])


class Document(QObject):
    def __init__(self):
        super(Document, self).__init__()
        self._undoStack = QUndoStack()
        self._parts = []
        self._assemblies = []
        self._controller = None
        self._selectedPart = None

    ### SIGNALS ###
    partAddedSignal = pyqtSignal(object, object)  # part, controller
    selectedPartChangedSignal = pyqtSignal(object)  # part

    ### SLOTS ###

    ### METHODS ###
    # accessors
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

    def selectedPart(self):
        return self._selectedPart

    def setSelectedPart(self, newPart):
        if self._selectedPart == newPart:
            return
        self._selectedPart = newPart
        self.selectedPartChangedSignal.emit(newPart)

    ### PUBLIC METHODS FOR QUERYING THE MODEL ###

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
            dnapart = DNASquarePart(document=self)
            self._addPart(dnapart)
        return dnapart

    def removeAllParts(self):
        """Used to reset the document. Not undoable."""
        while len(self._parts) > 0:
            part = self._parts.pop()
            part._setDocument(None)
            part.partRemoved.emit()

    ### PRIVATE SUPPORT METHODS ###
    def _addPart(self, part):
        """Add part to the document via AddPartCommand."""
        undoStack = self.undoStack()
        c = self.AddPartCommand(self, part)
        if undoStack != None:
            self.undoStack().push(c)
        else:
            c.redo()
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
                self._doc.setSelectedPart(self._part)
                self._doc.partAddedSignal.emit(self._part, self._doc._controller)

        def undo(self):
            self._part._setDocument(None)
            self._doc._parts.remove(self._part)
            self._part.partRemoved.emit()

    ### SERIALIZE / DESERIALIZE ###
    def fillSimpleRep(self, sr):
        sr['.class'] = "Document"
        sr['parts'] = self._parts

    # First objects that are being unarchived are sent
    # ClassNameFrom.classAttribute(incompleteArchivedDict)
    # which has only strings and numbers in its dict and then,
    # sometime later (with ascending finishInitPriority) they get
    # finishInitWithArchivedDict, this time with all entries
    finishInitPriority = 0.0
    def finishInitWithArchivedDict(self, completeArchivedDict):
        for part in completeArchivedDict['parts']:
            self._addPart(part)        