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
document.py
Created by Jonathan deWerd on 2011-01-26.
"""

import json
from views import styles
from .dnahoneycombpart import DNAHoneycombPart
from .dnasquarepart import DNASquarePart
from .enum import LatticeType

import util
# import Qt stuff into the module namespace with PySide, PyQt4 independence
util.qtWrapImport('QtCore', globals(), ['pyqtSignal', 'QObject'])
util.qtWrapImport('QtGui', globals(), [ 'QUndoCommand'])

class Document(QObject):
    def __init__(self, incompleteArchivedDict=None, legacyJsonImport=False):
        super(Document, self).__init__()
        self._parts = []
        self._selectedPart = None
        self._controller = None
        self._importedFromJson = legacyJsonImport
    
    def fsck(self):
        for p in self._parts:
            p.fsck()

    def controller(self):
        return self._controller

    def setController(self, cont):
        self._controller = cont

    def addDnaHoneycombPart(self):
        """
        Create and store a new DNAPart and instance, and return the instance.
        """
        dnapart = None
        if len(self._parts) == 0:
            dnapart = DNAHoneycombPart(maxRow=styles.HONEYCOMB_PART_MAXROWS,\
                                       maxCol=styles.HONEYCOMB_PART_MAXCOLS)
            self.addPart(dnapart)
        return dnapart

    def addDnaSquarePart(self):
        """
        Create and store a new DNAPart and instance, and return the instance.
        """
        dnapart = None
        if len(self._parts) == 0:
            dnapart = DNASquarePart(maxRow=styles.SQUARE_PART_MAXROWS,\
                                    maxCol=styles.SQUARE_PART_MAXCOLS)
            self.addPart(dnapart)
        return dnapart

    def parts(self):
        return self._parts

    partAdded = pyqtSignal(object)
    def addPart(self, part):
        undoStack = self.undoStack()
        c = self.AddPartCommand(self, part)
        if undoStack!=None:
            self.undoStack().push(c)
        else:
            c.redo()
        return c.part()

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
                self._part._setDocument(self._doc)
                self._doc.setSelectedPart(self._part)
                self._doc.partAdded.emit(self._part)

        def undo(self):
            self._part._setDocument(None)
            self._doc._parts.remove(self._part)
            self._part.partRemoved.emit()

    def undoStack(self):
        if self.controller():
            return self.controller().undoStack()
        return None

    ################### Transient (doesn't get saved) State ##################
    selectedPartChanged = pyqtSignal(object)

    def selectedPart(self):
        return self._selectedPart

    def setSelectedPart(self, newPart):
        if self._selectedPart == newPart:
            return
        self._selectedPart = newPart
        self.selectedPartChanged.emit(newPart)

    ########################## Archive / Unarchive ###########################
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
            self.addPart(part)
