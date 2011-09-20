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
import util

# import Qt stuff into the module namespace with PySide, PyQt4 independence
util.qtWrapImport('QtCore', globals(), ['pyqtSignal', 'QString', 'QFileInfo',
                                        'QStringList', 'Qt', 'QEvent'])
util.qtWrapImport('QtGui', globals(), ['QUndoStack', 'QFileDialog',
                                        'QAction', 'QApplication',
                                        'QMessageBox', 'QKeySequence',
                                        'QDialog', 'QMainWindow',
                                        'QDockWidget'])


class DocumentController():
    """
    Connects UI buttons to their corresponding actions in the model.
    """
    def __init__(self):
        """docstring for __init__"""
        # set data items to none
        self._window = None
        self._undoStack = None
        self._filename = None
        self._hasNoAssociatedFile = None
        self._sliceViewInstance = None
        self._pathViewInstance = None
        self._solidView = None
        self._activePart = None
        # setup undostack
        # connectSignalsToSlots

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
        pass

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
    def getDocument(self):
        """docstring for getDocument"""
        pass

    def setDocument(self):
        """docstring for setDocument"""
        pass

    # part related
    def getActivePart(self):
        """docstring for getActivePart"""
        pass

    def setActivePart(self):
        """docstring for setActivePart"""
        pass
