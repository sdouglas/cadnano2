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

import os.path
from cadnano import app
from model.document import Document
from views.documentwindow import DocumentWindow
import util
util.qtWrapImport('QtCore', globals(), [])
util.qtWrapImport('QtGui', globals(), [])


class DocumentController():
    """
    Connects UI buttons to their corresponding actions in the model.
    """
    def __init__(self, doc=None, fname=None):
        """docstring for __init__"""
        # init variables
        self._document = None
        self._undoStack = None
        self._filename = fname
        self._hasNoAssociatedFile = None
        self._sliceViewInstance = None
        self._pathViewInstance = None
        self._solidView = None
        self._activePart = None
        # setup window
        self.win = DocumentWindow(docCtrlr=self)
        self.win.closeEvent = self.closeEventHandler
        self.connectWindowSignalsToSelf()
        self.win.show()
        self.setDocument(Document() if not doc else doc)

    ### SLOTS ###
    def undoStackCleanChangedSlot(self):
        """docstring for undoStackCleanChangedSlot"""
        pass

    def actionNewSlot(self):
        """docstring for actionNewSlot"""
        pass

    def actionOpenSlot(self):
        """docstring for actionOpenSlot"""
        pass

    def actionCloseSlot(self):
        """docstring for actionCloseSlot"""
        pass

    def actionSaveSlot(self):
        """docstring for actionSaveSlot"""
        pass

    def actionSaveAsSlot(self):
        """docstring for actionSaveAsSlot"""
        pass

    def actionSVGSlot(self):
        """docstring for actionSVGSlot"""
        pass

    def actionCSVSlot(self):
        """docstring for actionCSVSlot"""
        pass
        
    def actionPrefsSlot(self):
        """docstring for actionPrefsSlot"""
        app().prefsClicked

    def actionModifySlot(self):
        """docstring for actionModifySlot"""
        pass

    def actionAutostapleSlot(self):
        """docstring for actionAutostapleSlot"""
        pass

    def actionModifySlot(self):
        """docstring for actionModifySlot"""
        pass

    def actionAddHoneycombPartSlot(self):
        """docstring for actionAddHoneycombPartSlot"""
        pass

    def actionAddSquarePartSlot(self):
        """docstring for actionAddSquarePartSlot"""
        pass

    ### METHODS ###
    def connectWindowSignalsToSelf(self):
        """docstring for connectWindowEventSignalsToSlots"""
        self.win.actionNew.triggered.connect(self.actionNewSlot)
        self.win.actionOpen.triggered.connect(self.actionOpenSlot)
        self.win.actionClose.triggered.connect(self.actionCloseSlot)
        self.win.actionSave.triggered.connect(self.actionSaveSlot)
        self.win.actionSave_As.triggered.connect(self.actionSaveAsSlot)
        self.win.actionSVG.triggered.connect(self.actionSVGSlot)
        self.win.actionAutoStaple.triggered.connect(self.autoStapleClicked)
        self.win.actionCSV.triggered.connect(self.actionCSVSlot)
        self.win.actionPreferences.triggered.connect(self.actionPrefsSlot)
        self.win.actionModify.triggered.connect(self.actionModifySlot)
        self.win.actionNewHoneycombPart.triggered.connect(\
            self.actionAddHoneycombPartSlot)
        self.win.actionNewSquarePart.triggered.connect(\
            self.actionAddSquarePartSlot)

    def windowCloseEventHandler(self, event):
        """Intercept close events when user attempts to close the window."""
        if self.maybeSave():
            event.accept()
            if app().isInMaya():
                self.windock.setVisible(False)
                del self.windock
            app().documentControllers.remove(self)
        else:
            event.ignore()

    # slot callbacks
    def actionNewSlotCallback(self):
        """docstring for actionNewSlotCallback"""
        pass

    def saveFileDialogCallback(self):
        """docstring for saveFileDialogCallback"""
        pass

    def openAfterMaybeSaveCallback(self):
        """docstring for openAfterMaybeSaveCallback"""
        pass

    # window related
    def windowCloseMethod(self):
        """docstring for windowCloseMethod"""
        pass

    def windowChangedMethod(self):
        """docstring for windowChangedMethod"""
        pass

    # maya window related
    def setupMayaWindow(self):
        """docstring for setupMayaWindow"""
        pass

    # file input
    def getDocumentTitle(self):
        """docstring for getDocumentTitle"""
        pass

    def getFilename(self):
        """docstring for getFilename"""
        pass

    def setFilename(self):
        """docstring for setFilename"""
        pass

    def openAfterMaybeSave(self):
        """docstring for openAfterMaybeSave"""
        pass

    def openAfterMaybeSaveCallback(self):
        """docstring for openAfterMaybeSaveCallback"""
        pass

    # file output
    def maybeSave(self):
        """docstring for maybeSave"""
        pass

    def writeDocumentToFile(self, filename):
        """docstring for writeDocumentToFile"""
        pass

    def saveFileDialog(self):
        """docstring for saveFileDialog"""
        pass

    def saveFileDialogCallback(self):
        """docstring for saveFileDialogCallback"""
        pass

    # document related
    def document(self):
        """docstring for document"""
        return self._document

    def setDocument(self, doc):
        """docstring for setDocument"""
        self._document = doc

    # part related
    def activePart(self):
        """docstring for activePart"""
        return self._activePart

    def setActivePart(self, part):
        """docstring for setActivePart"""
        self._activePart = part
