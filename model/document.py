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
from .dnapartinstance import DNAPartInstance
from PyQt4.QtCore import QObject, pyqtSignal
from PyQt4.QtGui import QUndoStack

class Document(QObject):    
    def __init__(self):
        super(Document, self).__init__()
        self._parts = []
        self._selectedPart = None
        self._undoStack = QUndoStack()

    def addDnaHoneycombPart(self):
        """
        Create and store a new DNAPart and instance, and return the instance.
        """
        dnapart = DNAHoneycombPart(document=self)
        self._parts.append(dnapart)
        self.setSelectedPart(dnapart)
        return dnapart

    def undoStack(self):
        return self._undoStack

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
    def simpleRep(self,encoder):
        """Returns a representation in terms of simple JSON-encodable types
        or types that implement simpleRep"""
        ret = {".class": "CADNanoDocument"}
        ret["parts"] = self._parts
        ret["dnaPartInstances"] = self._dnaPartInstances
        return ret

    @classmethod
    def fromSimpleRep(cls, dct):
        ret = Document()
        ret._parts = dct['parts']
        ret._dnaPartInstances = dct['dnaPartInstances']
        return ret
    def resolveSimpleRepIDs(self,idToObj):
        pass  # Document owns its parts and dnaPartInstances
              # so we didn't need to make weak refs to them

