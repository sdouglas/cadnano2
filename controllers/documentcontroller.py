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
from model.encoder import encode
from model.decoder import decode
from model.enum import StrandType
from model.enum import LatticeType
from views.documentwindow import DocumentWindow
from views.pathview.pathhelixgroup import PathHelixGroup
from views.sliceview.honeycombslicegraphicsitem import HoneycombSliceGraphicsItem
from views.sliceview.squareslicegraphicsitem import SquareSliceGraphicsItem
from views.pathview.handles.activeslicehandle import ActiveSliceHandle
from views import styles

if app().isInMaya():
	from views.solidview.solidhelixgroup import SolidHelixGroup

import util
# import Qt stuff into the module namespace with PySide, PyQt4 independence
util.qtWrapImport('QtCore', globals(), ['pyqtSignal', 'QString', \
                                        'QStringList', 'QFileInfo', 'Qt'])
util.qtWrapImport('QtGui', globals(), ['QUndoStack', 'QFileDialog',\
                                        'QAction', 'QApplication', \
                                        'QMessageBox', 'QKeySequence' ])

class DocumentController():
    """
    The document controller. Hooks high level (read file/write file, add
    submodel, etc) UI elements to their corresponding actions in the model
    """
    def __init__(self, doc=None, fname=None):
        app().documentControllers.add(self)
        self._undoStack = QUndoStack()
        self._undoStack.setClean()
        self._undoStack.cleanChanged.connect(\
            self.undoStackCleanStatusChangedSlot)
        self._filename = fname if fname else "untitled.nno"
        self._activePart = None
        self.sliceGraphicsItem = None
        self.pathHelixGroup = None
        self._hasNoAssociatedFile = fname == None
        self.win = DocumentWindow(docCtrlr=self)
        self.win.closeEvent = self.closer
        self.connectWindowEventsToSelf()
        self.win.show()
        self._document = None
        self.setDocument(Document() if not doc else doc)        
        app().undoGroup.addStack(self.undoStack())
        self.win.setWindowTitle(self.documentTitle()+'[*]')
        self.solidHelixGrp = None

    def closer(self, event):
        if self.maybeSave():
            if app().testRecordMode:
                self.win.sliceController.testRecorder.generateTest()
            event.accept()
        else:
            event.ignore()

    def documentTitle(self):
        fname = os.path.basename(str(self.filename()))
        if not self.undoStack().isClean():
            fname += '[*]'
        return fname

    def filename(self):
        return self._filename

    def setFilename(self, proposedFName):
        if self._filename == proposedFName:
            return True
        self._filename = proposedFName
        self._hasNoAssociatedFile = False
        self.win.setWindowTitle(self.documentTitle())
        return True

    def activePart(self):
        if self._activePart == None:
            self._activePart = self._document.selectedPart()
        return self._activePart

    def setActivePart(self, part):
        # should be document.selectedPart
        self._activePart = part

    def document(self):
        return self._document

    def setDocument(self, doc):
        
        self._document = doc
        doc.setController(self)
        doc.partAdded.connect(self.docPartAddedEvent)
        for p in doc.parts():
            self.docPartAddedEvent(p)

    def undoStack(self):
        return self._undoStack

    def connectWindowEventsToSelf(self):
        """Organizational method to collect signal/slot connectors."""
        self.win.actionNewHoneycombPart.triggered.connect(self.hcombClicked)
        self.win.actionNewSquarePart.triggered.connect(self.squareClicked)
        self.win.actionNew.triggered.connect(app().newDocument)
        self.win.actionOpen.triggered.connect(self.openClicked)
        self.win.actionClose.triggered.connect(self.closeClicked)
        self.win.actionSave.triggered.connect(self.saveClicked)
        self.win.actionSVG.triggered.connect(self.svgClicked)
        self.win.actionAutoStaple.triggered.connect(self.autoStapleClicked)
        self.win.actionCSV.triggered.connect(self.exportCSV)
        self.win.actionPreferences.triggered.connect(app().prefsClicked)
        self.win.actionSave_As.triggered.connect(self.saveAsClicked)
        # self.win.actionQuit.triggered.connect(self.closeClicked)
        # self.win.actionAdd.triggered.connect(self.addClicked)
        # self.win.actionDelete.triggered.connect(self.deleteClicked)
        # self.win.actionCut.triggered.connect(self.cutClicked)
        # self.win.actionPaste.triggered.connect(self.pasteClicked)
        # self.win.actionMoveUp.triggered.connect(self.moveUpClicked)
        # self.win.actionMoveDown.triggered.connect(self.moveDownClicked)
        # self.win.actionPromote.triggered.connect(self.promoteClicked)
        # self.win.actionDemote.triggered.connect(self.demoteClicked)
    # end def

    def undoStackCleanStatusChangedSlot(self):
        self.win.setWindowModified(not self.undoStack().isClean())
        # The title changes to include [*] on modification
        self.win.setWindowTitle(self.documentTitle())

    def newClicked(self):
        """Create a new document window"""
        # Will create a new Document object and will be
        # be kept alive by the app's document list
        DocumentController()

    def openClicked(self):
        """docstring for openClicked"""
        # self.filesavedialog = None
        # self.openFile('/Users/nick/Downloads/nanorobot.v2.json')
        # return
        if util.isWindows(): # required for native looking file window
            fname = QFileDialog.getOpenFileName(None, "Open Document", "/",\
                        "CADnano1 / CADnano2 Files (*.nno *.json *.cadnano)")
            self.filesavedialog = None
            self.openFile(fname)
        else: # access through non-blocking callback
            fdialog = QFileDialog ( self.win, \
                                "Open Document",\
                                "/", \
                                "CADnano1 / CADnano2 Files (*.nno *.json *.cadnano)")
            fdialog.setAcceptMode(QFileDialog.AcceptOpen)
            fdialog.setWindowFlags(Qt.Sheet)
            fdialog.setWindowModality(Qt.WindowModal)
            # fdialog.exec_()  # or .show(), or .open()
            self.filesavedialog = fdialog
            self.filesavedialog.filesSelected.connect(self.openFile)
            fdialog.open()  # or .show(), or .open()

    def openFile(self, selected):
        if isinstance(selected, QStringList) or isinstance(selected, list):
            fname = selected[0]
        else:
            fname = selected
        if not fname or os.path.isdir(fname):
            return False
        fname = str(fname)
        doc = decode(file(fname).read())
        DocumentController(doc, fname)
        if self.filesavedialog != None:
            self.filesavedialog.filesSelected.disconnect(self.openFile)
            del self.filesavedialog # manual garbage collection to prevent hang (in osx)
    # end def

    def exportSequenceCSV(self, fname):
        """Export all staple sequences to CSV file fnane."""
        output = self.activePart().getStapleSequences()
        f = open(fname, 'w')
        f.write(output)
        f.close()
    # end def

    def exportCSV(self):
        fname = self.filename()
        if fname == None:
            directory = "."
        else:
            directory = QFileInfo(fname).path()
        if util.isWindows(): # required for native looking file window
            fname = QFileDialog.getSaveFileName(self.win,
                                "%s - Export As" % QApplication.applicationName(),\
                                directory, \
                                "(*.csv)"\
                                 )
            self.filesavedialog = None
            self.exportFile(fname)
        else:  # access through non-blocking callback
            fdialog = QFileDialog ( self.win, \
                                "%s - Export As" % QApplication.applicationName(),\
                                directory, \
                                "(*.csv)")
            fdialog.setAcceptMode(QFileDialog.AcceptSave)
            fdialog.setWindowFlags(Qt.Sheet)
            fdialog.setWindowModality(Qt.WindowModal)
            # fdialog.exec_()  # or .show(), or .open()
            self.filesavedialog = fdialog
            self.filesavedialog.filesSelected.connect(self.exportFile) 
            fdialog.open()
    # end def

    def exportFile(self, selected):
        if isinstance(selected, QStringList) or isinstance(selected, list):
            fname = selected[0]
        else:
            fname = selected
        if fname.isEmpty() or os.path.isdir(fname):
            return False
        fname = str(fname)
        if not fname.lower().endswith(".csv"):
            fname += ".csv"
        # self.setFilename(fname)
        if self.filesavedialog != None:
            self.filesavedialog.filesSelected.disconnect(self.exportFile)
            del self.filesavedialog # manual garbage collection to prevent hang (in osx)
        return self.exportSequenceCSV(fname)
    # end def

    def closeClicked(self):
        """This will trigger a Window closeEvent"""
        if util.isWindows():
            self.win.close()

    def maybeSave(self):
        """
        Save on quit, check if document changes have occured.
        """
        if app().dontAskAndJustDiscardUnsavedChanges:
            return True
        if not self.undoStack().isClean():    # document dirty?
            savebox = QMessageBox( QMessageBox.Warning,   "Application", \
                "The document has been modified.\n Do you want to save your changes?", \
                QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel, \
                self.win, \
                Qt.Dialog | Qt.MSWindowsFixedSizeDialogHint | Qt.Sheet)
            savebox.setWindowModality(Qt.WindowModal)
            save = savebox.button(QMessageBox.Save)
            discard = savebox.button(QMessageBox.Discard)
            cancel = savebox.button(QMessageBox.Cancel)
            save.setShortcut("Ctrl+S")
            discard.setShortcut(QKeySequence("D,Ctrl+D"))
            cancel.setShortcut(QKeySequence("C,Ctrl+C,.,Ctrl+."))
            ret = savebox.exec_()
            del savebox  # manual garbage collection to prevent hang (in osx)
            if ret == QMessageBox.Save:
                return self.saveAsClicked()
            elif ret == QMessageBox.Cancel:
                return False
        return True

    def writeToFile(self, filename=None):
        if filename == None:
            assert(not self._hasNoAssociatedFile)
            filename = self.filename()
        try:
            f = open(filename, 'w')
            encode(self._document, f)
            f.close()
        except IOError:
            flags = Qt.Dialog | Qt.MSWindowsFixedSizeDialogHint | Qt.Sheet
            errorbox = QMessageBox(QMessageBox.Critical,\
                                   "CaDNAno",\
                                   "Could not write to '%s'."%filename,\
                                   QMessageBox.Ok,\
                                   self.win,\
                                   flags)
            errorbox.setWindowModality(Qt.WindowModal)
            errorbox.open()
            return False
        self.undoStack().setClean()
        self.setFilename(filename)
        return True

    def saveClicked(self):
        if self._hasNoAssociatedFile or self._document._importedFromJson:
            self.openSaveFileDialog()
            return
        self.writeToFile()

    def saveAsClicked(self):
        self.openSaveFileDialog()

    def openSaveFileDialog(self):
        fname = self.filename()
        if fname == None:
            directory = "."
        else:
            directory = QFileInfo(fname).path()
        if util.isWindows(): # required for native looking file window
            fname = QFileDialog.getSaveFileName(self.win, 
                                "%s - Save As" % QApplication.applicationName(),\
                                directory, \
                                "%s (*.nno)" % QApplication.applicationName(), \
                                 )
            self.writeToFile(fname)
        else:  # access through non-blocking callback
            fdialog = QFileDialog ( self.win, \
                                "%s - Save As" % QApplication.applicationName(),\
                                directory, \
                                "%s (*.nno)" % QApplication.applicationName())
            fdialog.setAcceptMode(QFileDialog.AcceptSave)
            fdialog.setWindowFlags(Qt.Sheet)
            fdialog.setWindowModality(Qt.WindowModal)
            # fdialog.exec_()  # or .show(), or .open()
            self.filesavedialog = fdialog
            self.filesavedialog.filesSelected.connect(self.saveFileDialogCallback) 
            fdialog.open()

    def saveFileDialogCallback(self, selected):
        if isinstance(selected, QStringList) or isinstance(selected, list):
            fname = selected[0]
        else:
            fname = selected
        if fname.isEmpty() or os.path.isdir(fname):
            return False
        fname = str(fname)
        if not fname.lower().endswith(".nno"):
            fname += ".nno"
        if self.filesavedialog != None:
            self.filesavedialog.filesSelected.disconnect(self.saveFileDialogCallback)
            del self.filesavedialog # prevents hang
        self.writeToFile(fname)
    # end def

    def svgClicked(self):
        """docstring for svgClicked"""
        print "svg clicked"
    # end def

    def hcombClicked(self):
        """docstring for hcombClicked"""
        self.addHoneycombHelixGroup()
    # end def

    def squareClicked(self):
        """docstring for squareClicked"""
        self.addSquareHelixGroup()
    # end def

    def autoStapleClicked(self):
        self.activePart().autoStaple()

    ############# Spawning / Destroying HoneycombSliceGraphicsItems ##########
    ##################### and PathHelixGroups for Parts ######################
    def docPartAddedEvent(self, part):
        if part.crossSectionType() == LatticeType.Honeycomb:
            self.sliceGraphicsItem = HoneycombSliceGraphicsItem(part,\
                                        controller=self.win.sliceController,\
                                        parent=self.win.sliceroot)
        else:
            self.sliceGraphicsItem = SquareSliceGraphicsItem(part,\
                                        controller=self.win.sliceController,\
                                        parent=self.win.sliceroot)
        self.pathHelixGroup = PathHelixGroup(part,\
                                         controller=self.win.pathController,\
                                         parent=self.win.pathroot)
                                         
        if app().isInMaya():
            self.solidHelixGrp = SolidHelixGroup(part, controller=self.win.pathController, htype=part.crossSectionType())

        self.win.sliceController.activeSliceLastSignal.connect(\
                      self.pathHelixGroup.activeSliceHandle().moveToLastSlice)
        self.win.sliceController.activeSliceFirstSignal.connect(\
                     self.pathHelixGroup.activeSliceHandle().moveToFirstSlice)
        self.win.pathController.setActivePath(self.pathHelixGroup)
        self.win.actionFrame.triggered.connect(self.pathHelixGroup.zoomToFit)

        for vh in part.getVirtualHelices():
            xos = vh.get3PrimeXovers(StrandType.Scaffold)
            for xo in xos:
                toBase = (xo[1][0], xo[1][2])
                self.pathHelixGroup.createXoverItem(xo[0], toBase, StrandType.Scaffold)
            xos = vh.get3PrimeXovers(StrandType.Staple)
            for xo in xos:
                toBase = (xo[1][0], xo[1][2])
                self.pathHelixGroup.createXoverItem(xo[0], toBase, StrandType.Staple)
        # end for
        self.setActivePart(part)
        
    # end def
    
    def addHoneycombHelixGroup(self):
        """Adds a honeycomb DNA part to the document. Dimensions are set by
        the Document addDnaHoneycombPart method."""
        dnaPart = self._document.addDnaHoneycombPart()
        self.setActivePart(dnaPart)
        if app().testRecordMode:
            self.win.sliceController.testRecorder.setPart(dnaPart.crossSectionType())
    # end def

    def addSquareHelixGroup(self):
        """Adds a square DNA part to the document. Dimensions are set by
        the Document addDnaSquarePart method."""
        dnaPart = self._document.addDnaSquarePart()
        self.setActivePart(dnaPart)
        if app().testRecordMode:
            self.win.sliceController.testRecorder.setPart(dnaPart.crossSectionType())
    # end def

    def createAction(self, icon, text, parent, shortcutkey):
        """
        returns a QAction object
        """
        action = QAction(QIcon(icon), text, parent)
        if not shortcutkey.isEmpty():
            action.setShortcut(shortcutkey)
        return action
# end class
