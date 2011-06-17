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
from .dnahoneycombpart import DNAHoneycombPart
from PyQt4.QtCore import QObject, pyqtSignal
from PyQt4.QtGui import QUndoStack

class Document(QObject):    
    def __init__(self, incompleteArchivedDict=None):
        super(Document, self).__init__()
        self._parts = []
        self._selectedPart = None
        self._controller = None
    
    def controller(self):
        return self._controller
    
    def setController(self, cont):
        self._controller = cont

    def addDnaHoneycombPart(self):
        """
        Create and store a new DNAPart and instance, and return the instance.
        """
        dnapart = DNAHoneycombPart()
        self.addPart(dnapart)
        return dnapart
    
    def parts(self):
        return self._parts
        
    partAdded = pyqtSignal(object)
    def addPart(self, part):
        self._parts.append(part)
        part._setDocument(self)
        self.setSelectedPart(part)
        self.partAdded.emit(part)

    def undoStack(self):
        return self.controller().undoStack()

    ############################ Transient (doesn't get saved) State ############################
    selectedPartChanged = pyqtSignal(object)

    def selectedPart(self):
        return self._selectedPart
    
    def setSelectedPart(self, newPart):
        if self._selectedPart == newPart:
            return
        self._selectedPart = newPart
        self.selectedPartChanged.emit(newPart)


    ############################ Archive / Unarchive ############################
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
