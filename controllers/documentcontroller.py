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
from model.io.decoder import decode
from model.io.encoder import encode
from views.documentwindow import DocumentWindow
import util
util.qtWrapImport('QtCore', globals(), ['QFileInfo', 'QRect', 'QString',
                                        'QStringList', 'QSize', 'Qt'])
util.qtWrapImport('QtGui', globals(), ['QDockWidget', 'QKeySequence',
                                       'QFileDialog', 'QMessageBox'])
util.qtWrapImport('QtGui', globals(), ['QApplication', 'QDialog', 
                                       'QDockWidget', 'QFileDialog',
                                       'QKeySequence', 'QGraphicsItem',
                                       'QMainWindow',
                                       'QMessageBox', 'QPainter',
                                       'QStyleOptionGraphicsItem'])
util.qtWrapImport('QtSvg', globals(), ['QSvgGenerator'])

class DocumentController():
    """
    Connects UI buttons to their corresponding actions in the model.
    """
    ### INIT METHODS ###
    def __init__(self):
        """docstring for __init__"""
        # initialize variables
        self._document = Document()
        self._activePart = None
        self._filename = None
        self._hasNoAssociatedFile = True
        self._pathViewInstance = None
        self._sliceViewInstance = None
        self._undoStack = None
        self.win = None
        self.fileopendialog = None
        self.filesavedialog = None
        # call other init methods
        self._initWindow()
        if app().isInMaya():
            self._initMaya()
        app().documentControllers.add(self)

    def _initWindow(self):
        """docstring for initWindow"""
        self.win = DocumentWindow(docCtrlr=self)
        self._connectWindowSignalsToSelf()
        self.win.show()

    def _initMaya(self):
        """
        Initialize Maya-related state. Delete Maya nodes if there
        is an old document left over from the same session. Set up
        the Maya window.
        """
        # There will only be one document
        if (app().activeDocument and app().activeDocument.win and
                                not app().activeDocument.win.close()):
            return
        del app().activeDocument
        app().deleteAllMayaNodes()
        app().activeDocument = self

        import maya.OpenMayaUI as OpenMayaUI
        import sip
        ptr = OpenMayaUI.MQtUtil.mainWindow()
        mayaWin = sip.wrapinstance(long(ptr), QMainWindow)
        self.windock = QDockWidget("cadnano")
        self.windock.setFeatures(QDockWidget.DockWidgetMovable
                                 | QDockWidget.DockWidgetFloatable)
        self.windock.setAllowedAreas(Qt.LeftDockWidgetArea
                                     | Qt.RightDockWidgetArea)
        self.windock.setWidget(self.win)
        mayaWin.addDockWidget(Qt.DockWidgetArea(Qt.LeftDockWidgetArea),
                                self.windock)
        self.windock.setVisible(True)

    def _connectWindowSignalsToSelf(self):
        """This method serves to group all the signal & slot connections
        made by DocumentController"""
        self.win.actionNew.triggered.connect(self.actionNewSlot)
        self.win.actionOpen.triggered.connect(self.actionOpenSlot)
        self.win.actionClose.triggered.connect(self.actionCloseSlot)
        self.win.actionSave.triggered.connect(self.actionSaveSlot)
        self.win.actionSave_As.triggered.connect(self.actionSaveAsSlot)
        self.win.actionSVG.triggered.connect(self.actionSVGSlot)
        self.win.actionAutoStaple.triggered.connect(self.actionAutostapleSlot)
        self.win.actionExportStaples.triggered.connect(self.actionExportStaplesSlot)
        self.win.actionPreferences.triggered.connect(self.actionPrefsSlot)
        self.win.actionModify.triggered.connect(self.actionModifySlot)
        self.win.actionNewHoneycombPart.triggered.connect(\
            self.actionAddHoneycombPartSlot)
        self.win.actionNewSquarePart.triggered.connect(\
            self.actionAddSquarePartSlot)
        self.win.closeEvent = self.windowCloseEventHandler

    ### SLOTS ###
    def undoStackCleanChangedSlot(self):
        """The title changes to include [*] on modification."""
        self.win.setWindowModified(not self.undoStack().isClean())
        self.win.setWindowTitle(self.documentTitle())

    def actionNewSlot(self):
        """
        1. If document is has no parts, do nothing.
        2. If document is dirty, call maybeSave and continue if it succeeds.
        3. Create a new document and swap it into the existing ctrlr/window.
        """
        if len(self._document.parts()) == 0:
            print "No existing parts, so no new document"
            return  # no parts
        if self.maybeSave() == False:
            return  # user canceled in maybe save
        else:  # user did not cancel
            if self.filesavedialog != None:
                self.filesavedialog.finished.connect(self.newClickedCallback)
            else:  # user did not save
                self.newClickedCallback()  # finalize new

    def actionOpenSlot(self):
        """
        1. If document is untouched, proceed to open dialog.
        2. If document is dirty, call maybesave and continue if it succeeds.
        Downstream, the file is selected in openAfterMaybeSave,
        and the selected file is actually opened in openAfterMaybeSaveCallback.
        """
        if self.maybeSave() == False:
            return  # user canceled in maybe save
        else:  # user did not cancel
            if hasattr(self, "filesavedialog"): # user did save
                if self.filesavedialog != None:
                    self.filesavedialog.finished.connect(self.openAfterMaybeSave)
                else:
                    self.openAfterMaybeSave()  # windows
            else:  # user did not save
                self.openAfterMaybeSave()  # finalize new

    def actionCloseSlot(self):
        """This will trigger a Window closeEvent."""
        if util.isWindows():
            self.win.close()

    def actionSaveSlot(self):
        """SaveAs if necessary, otherwise overwrite existing file."""
        if self._hasNoAssociatedFile:
            self.saveFileDialog()
            return
        self.writeDocumentToFile()

    def actionSaveAsSlot(self):
        """Open a save file dialog so user can choose a name."""
        self.saveFileDialog()

    def actionSVGSlot(self):
        """docstring for actionSVGSlot"""
        fname = os.path.basename(str(self.filename()))
        if fname == None:
            directory = "."
        else:
            directory = QFileInfo(fname).path()

        fdialog = QFileDialog(
                    self.win,
                    "%s - Save As" % QApplication.applicationName(),
                    directory,
                    "%s (*.svg)" % QApplication.applicationName())
        fdialog.setAcceptMode(QFileDialog.AcceptSave)
        fdialog.setWindowFlags(Qt.Sheet)
        fdialog.setWindowModality(Qt.WindowModal)
        self.svgsavedialog = fdialog
        self.svgsavedialog.filesSelected.connect(self.saveSVGDialogCallback)
        fdialog.open()

    class DummyChild(QGraphicsItem):
        def boundingRect(self):
            return QRect(200, 200) # self.parentObject().boundingRect()
        def paint(self, painter, option, widget=None):
            pass

    def saveSVGDialogCallback(self, selected):
        if isinstance(selected, QStringList) or isinstance(selected, list):
            fname = selected[0]
        else:
            fname = selected
        if fname.isEmpty() or os.path.isdir(fname):
            return False
        fname = str(fname)
        if not fname.lower().endswith(".svg"):
            fname += ".svg"
        if self.svgsavedialog != None:
            self.svgsavedialog.filesSelected.disconnect(self.saveSVGDialogCallback)
            del self.svgsavedialog  # prevents hang
            self.svgsavedialog = None

        generator = QSvgGenerator()
        generator.setFileName(fname)
        generator.setSize(QSize(200, 200))
        generator.setViewBox(QRect(0, 0, 2000, 2000))
        painter = QPainter()

        # Render through scene
        # painter.begin(generator)
        # self.win.pathscene.render(painter)
        # painter.end()

        # Render item-by-item
        painter = QPainter()
        styleOption = QStyleOptionGraphicsItem()
        q = [self.win.pathroot]
        painter.begin(generator)
        while q:
            graphicsItem = q.pop()
            transform = graphicsItem.itemTransform(self.win.sliceroot)[0]
            painter.setTransform(transform)
            if graphicsItem.isVisible():
                graphicsItem.paint(painter, styleOption, None)
                q.extend(graphicsItem.childItems())
        painter.end()

    def actionExportStaplesSlot(self):
        """
        Triggered by clicking Export Staples button. Opens a file dialog to
        determine where the staples should be saved. The callback is
        exportStaplesCallback which collects the staple sequences and exports
        the file.
        """
        fname = self.filename()
        if fname == None:
            directory = "."
        else:
            directory = QFileInfo(fname).path()
        if util.isWindows():  # required for native looking file window
            fname = QFileDialog.getSaveFileName(
                            self.win,
                            "%s - Export As" % QApplication.applicationName(),
                            directory,
                            "(*.csv)")
            self.saveStaplesDialog = None
            self.exportFile(fname)
        else:  # access through non-blocking callback
            fdialog = QFileDialog(
                            self.win,
                            "%s - Export As" % QApplication.applicationName(),
                            directory,
                            "(*.csv)")
            fdialog.setAcceptMode(QFileDialog.AcceptSave)
            fdialog.setWindowFlags(Qt.Sheet)
            fdialog.setWindowModality(Qt.WindowModal)
            self.saveStaplesDialog = fdialog
            self.saveStaplesDialog.filesSelected.connect(self.exportStaplesCallback)
            fdialog.open()
    # end def

    def actionPrefsSlot(self):
        """docstring for actionPrefsSlot"""
        app().prefsClicked()

    def actionAutostapleSlot(self):
        """docstring for actionAutostapleSlot"""
        self.activePart().autoStaple()

    def actionModifySlot(self):
        """
        Notifies that part root items that parts should respond to modifier
        selection signals. 
        """
        # uncomment for debugging
        # isChecked = self.win.actionModify.isChecked()
        # self.win.pathroot.setModifyState(isChecked)
        # self.win.sliceroot.setModifyState(isChecked)
        if app().isInMaya():
            isChecked = self.win.actionModify.isChecked()
            self.win.pathroot.setModifyState(isChecked)
            self.win.sliceroot.setModifyState(isChecked)
            self.win.solidroot.setModifyState(isChecked)

    def actionAddHoneycombPartSlot(self):
        """docstring for actionAddHoneycombPartSlot"""
        part = self._document.addHoneycombPart()
        self.setActivePart(part)

    def actionAddSquarePartSlot(self):
        """docstring for actionAddSquarePartSlot"""
        part = self._document.addSquarePart()
        self.setActivePart(part)

    ### ACCESSORS ###
    def document(self):
        return self._document

    def setDocument(self, doc):
        """
        Sets the controller's document, and informs the document that
        this is its controller.
        """
        self._document = doc
        doc.setController(self)

    def activePart(self):
        if self._activePart == None:
            self._activePart = self._document.selectedPart()
        return self._activePart

    def setActivePart(self, part):
        self._activePart = part

    def undoStack(self):
        return self._document.undoStack()

    ### PRIVATE SUPPORT METHODS ###
    def newDocument(self, doc=None, fname=None):
        """Creates a new Document, reusing the DocumentController."""
        if app().isInMaya():
            app().deleteAllMayaNodes()
        self._document.removeAllParts()  # clear out old parts
        self._document.undoStack().clear()  # reset undostack
        self._filename = fname if fname else "untitled.nno"
        self._hasNoAssociatedFile = fname == None
        self._activePart = None
        self.win.setWindowTitle(self.documentTitle() + '[*]')

    def saveFileDialog(self):
        fname = self.filename()
        if fname == None:
            directory = "."
        else:
            directory = QFileInfo(fname).path()
        if util.isWindows():  # required for native looking file window
            fname = QFileDialog.getSaveFileName(
                            self.win,
                            "%s - Save As" % QApplication.applicationName(),
                            directory,
                            "%s (*.json)" % QApplication.applicationName())
            self.writeDocumentToFile(fname)
        else:  # access through non-blocking callback
            fdialog = QFileDialog(
                            self.win,
                            "%s - Save As" % QApplication.applicationName(),
                            directory,
                            "%s (*.json)" % QApplication.applicationName())
            fdialog.setAcceptMode(QFileDialog.AcceptSave)
            fdialog.setWindowFlags(Qt.Sheet)
            fdialog.setWindowModality(Qt.WindowModal)
            self.filesavedialog = fdialog
            self.filesavedialog.filesSelected.connect(
                                                self.saveFileDialogCallback)
            fdialog.open()
    # end def

    ### SLOT CALLBACKS ###
    def actionNewSlotCallback(self):
        """
        Gets called on completion of filesavedialog after newClicked's 
        maybeSave. Removes the dialog if necessary, but it was probably
        already removed by saveFileDialogCallback.
        """
        if self.filesavedialog != None:
            self.filesavedialog.finished.disconnect(self.actionNewSlotCallback)
            del self.filesavedialog  # prevents hang (?)
            self.filesavedialog = None
        self.newDocument()

    def exportStaplesCallback(self, selected):
        """Export all staple sequences to selected CSV file."""
        if isinstance(selected, QStringList) or isinstance(selected, list):
            fname = selected[0]
        else:
            fname = selected
        if fname.isEmpty() or os.path.isdir(fname):
            return False
        fname = str(fname)
        if not fname.lower().endswith(".csv"):
            fname += ".csv"
        if self.saveStaplesDialog != None:
            self.saveStaplesDialog.filesSelected.disconnect(self.exportStaplesCallback)
            # manual garbage collection to prevent hang (in osx)
            del self.saveStaplesDialog
            self.saveStaplesDialog = None
        # write the file
        output = self.activePart().getStapleSequences()
        with open(fname, 'w') as f:
            f.write(output)
    # end def

    def newClickedCallback(self):
        """
        Gets called on completion of filesavedialog after newClicked's 
        maybeSave. Removes the dialog if necessary, but it was probably
        already removed by saveFileDialogCallback.
        """

        if self.filesavedialog != None:
            self.filesavedialog.finished.disconnect(self.newClickedCallback)
            del self.filesavedialog  # prevents hang (?)
            self.filesavedialog = None
        self.newDocument()

    def openAfterMaybeSaveCallback(self, selected):
        """
        Receives file selection info from the dialog created by
        openAfterMaybeSave, following user input.

        Extracts the file name and passes it to the decode method, which
        returns a new document doc, which is then set as the open document
        by newDocument. Calls finalizeImport and disconnects dialog signaling.
        """
        if isinstance(selected, QStringList) or isinstance(selected, list):
            fname = selected[0]
        else:
            fname = selected
        if not fname or os.path.isdir(fname):
            return False
        fname = str(fname)
        self.newDocument(fname=fname)
        decode(self._document, file(fname).read())
        if hasattr(self, "filesavedialog"): # user did save
            if self.fileopendialog != None:
                self.fileopendialog.filesSelected.disconnect(\
                                              self.openAfterMaybeSaveCallback)
            # manual garbage collection to prevent hang (in osx)
            del self.fileopendialog
            self.fileopendialog = None

    def saveFileDialogCallback(self, selected):
        """If the user chose to save, write to that file."""
        if isinstance(selected, QStringList) or isinstance(selected, list):
            fname = selected[0]
        else:
            fname = selected
        if fname.isEmpty() or os.path.isdir(fname):
            return False
        fname = str(fname)
        if not fname.lower().endswith(".json"):
            fname += ".json"
        if self.filesavedialog != None:
            self.filesavedialog.filesSelected.disconnect(
                                                self.saveFileDialogCallback)
            del self.filesavedialog  # prevents hang
            self.filesavedialog = None
        self.writeDocumentToFile(fname)

    ### EVENT HANDLERS ###
    def windowCloseEventHandler(self, event):
        """Intercept close events when user attempts to close the window."""
        if self.maybeSave():
            event.accept()
            if app().isInMaya():
                self.windock.setVisible(False)
                del self.windock
                self.windock = None
            app().documentControllers.remove(self)
        else:
            event.ignore()

    ### FILE INPUT ##
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

    def openAfterMaybeSave(self):
        """
        This is the method that initiates file opening. It is called by
        actionOpenSlot to spawn a QFileDialog and connect it to a callback
        method.
        """
        if util.isWindows():  # required for native looking file window
            fname = QFileDialog.getOpenFileName(
                        None,
                        "Open Document", "/",
                        "cadnano1 / cadnano2 Files (*.nno *.json *.cadnano)")
            self.filesavedialog = None
            self.openAfterMaybeSaveCallback(fname)
        else:  # access through non-blocking callback
            fdialog = QFileDialog(
                        self.win,
                        "Open Document",
                        "/",
                        "cadnano1 / cadnano2 Files (*.nno *.json *.cadnano)")
            fdialog.setAcceptMode(QFileDialog.AcceptOpen)
            fdialog.setWindowFlags(Qt.Sheet)
            fdialog.setWindowModality(Qt.WindowModal)
            self.fileopendialog = fdialog
            self.fileopendialog.filesSelected.connect(self.openAfterMaybeSaveCallback)
            fdialog.open()

    ### FILE OUTPUT ###
    def maybeSave(self):
        """Save on quit, check if document changes have occured."""
        if app().dontAskAndJustDiscardUnsavedChanges:
            return True
        if not self.undoStack().isClean():    # document dirty?
            savebox = QMessageBox(QMessageBox.Warning,   "Application",
                "The document has been modified.\nDo you want to save your changes?",
                QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel,
                self.win,
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
                return self.actionSaveAsSlot()
            elif ret == QMessageBox.Cancel:
                return False
        return True

    def writeDocumentToFile(self, filename=None):
        if filename == None:
            assert(not self._hasNoAssociatedFile)
            filename = self.filename()
        try:
            with open(filename, 'w') as f:
                helixOrderList = self.win.pathroot.getSelectedPartOrderedVHList()
                encode(self._document, helixOrderList, f)
        except IOError:
            flags = Qt.Dialog | Qt.MSWindowsFixedSizeDialogHint | Qt.Sheet
            errorbox = QMessageBox(QMessageBox.Critical,
                                   "cadnano",
                                   "Could not write to '%s'." % filename,
                                   QMessageBox.Ok,
                                   self.win,
                                   flags)
            errorbox.setWindowModality(Qt.WindowModal)
            errorbox.open()
            return False
        self.undoStack().setClean()
        self.setFilename(filename)
        return True

