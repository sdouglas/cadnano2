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
from idbank import IdBank
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

import util
# import Qt stuff into the module namespace with PySide, PyQt4 independence
util.qtWrapImport('QtCore', globals(), ['pyqtSignal', 'QString', \
                                        'QStringList', 'QFileInfo', 'Qt'])
util.qtWrapImport('QtGui', globals(), ['QUndoStack', 'QFileDialog',\
                                        'QAction', 'QApplication'])

if app().isInMaya():
    from .mayawindow import DocumentWindow
    from solidview.solidhelixgroup import SolidHelixGroup


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
        self._filename = fname if fname else "untitled.cn2"
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

    def closer(self, event):
        if self.win.maybeSave():
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
        return True

    def activePart(self):
        return self._activePart

    def setActivePart(self, part):
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
        # self.win.actionSave_As.triggered.connect(self.saveAsClicked)
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
        
        self.filesavedialog = None
        self.openFile('/Users/nick/Downloads/nanorobot.v2.json')
        return
        
        if util.isWindows(): # required for native looking file window
            fname = QFileDialog.getOpenFileName(None, "Open Document", "/",\
                        "CADnano1 / CADnano2 Files (*.cn2 *.json *.cadnano)")
            self.filesavedialog = None
            self.openFile(fname)                
        else: # access through non-blocking callback
            fdialog = QFileDialog ( self.win, \
                                "Open Document",\
                                "/", \
                                "CADnano1 / CADnano2 Files (*.cn2 *.json *.cadnano)")
            fdialog.setAcceptMode(QFileDialog.AcceptOpen)
            fdialog.setWindowFlags(Qt.Sheet)
            fdialog.setWindowModality(Qt.WindowModal)
            # fdialog.exec_()  # or .show(), or .open()
            self.filesavedialog = fdialog
            self.filesavedialog.filesSelected.connect(self.openFile) 
            fdialog.open()  # or .show(), or .open()

    def openFile(self, selected):
        if isinstance(selected, QStringList):
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

    def closeClicked(self):
        """This will trigger a Window closeEvent"""
        print "close clicked"
        if util.isWindows():
            self.win.close()

    def saveClicked(self):
        if self._hasNoAssociatedFile:
            return self.saveAsClicked()
        f = open(self.filename(), 'w')
        encode(self._document, f)
        f.close()
        self.undoStack().setClean()

    def saveAsClicked(self):
        fname = self.filename()
        if fname == None:
            directory = "."
        else:
            directory = QFileInfo(fname).path()
        if util.isWindows(): # required for native looking file window
            fname = QFileDialog.getSaveFileName(self.win, 
                                "%s - Save As" % QApplication.applicationName(),\
                                directory, \
                                "%s (*.cn2)" % QApplication.applicationName(), \
                                 )
            self.filesavedialog = None
            self.saveFile(fname)
        else:  # access through non-blocking callback
            fdialog = QFileDialog ( self.win, \
                                "%s - Save As" % QApplication.applicationName(),\
                                directory, \
                                "%s (*.cn2)" % QApplication.applicationName())
            fdialog.setAcceptMode(QFileDialog.AcceptSave)
            fdialog.setWindowFlags(Qt.Sheet)
            fdialog.setWindowModality(Qt.WindowModal)
            # fdialog.exec_()  # or .show(), or .open()
            self.filesavedialog = fdialog
            self.filesavedialog.filesSelected.connect(self.saveFile) 
            fdialog.open()

    def saveFile(self, selected):
        if isinstance(selected, QStringList):
            fname = selected[0]
        else:
            fname = selected
        if fname.isEmpty() or os.path.isdir(fname):
            return False
        fname = str(fname)
        if not fname.lower().endswith(".cn2"):
            fname += ".cn2"
        self.setFilename(fname)
        if self.filesavedialog != None:
            self.filesavedialog.filesSelected.disconnect(self.saveFile)
            del self.filesavedialog # manual garbage collection to prevent hang (in osx)
        return self.saveClicked()
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
            solhg = SolidHelixGroup(dnaPartInst,\
                                    controller=self.win.pathController)
            # need to create a permanent class level reference to this so
            # it doesn't get garbage collected
            self.solidlist.append(solhg)
            self.pathHelixGroup.scaffoldChange.connect(solhg.handleScaffoldChange)

        self.win.sliceController.activeSliceLastSignal.connect(\
                      self.pathHelixGroup.activeSliceHandle().moveToLastSlice)
        self.win.sliceController.activeSliceFirstSignal.connect(\
                     self.pathHelixGroup.activeSliceHandle().moveToFirstSlice)
        self.win.pathController.setActivePath(self.pathHelixGroup)

        for vh in part.getVirtualHelices():
            xos = vh.get3PrimeXovers(StrandType.Scaffold)
            for xo in xos:
                self.pathHelixGroup.createXoverItem(xo[0], xo[1], StrandType.Scaffold)
            xos = vh.get3PrimeXovers(StrandType.Staple)
            for xo in xos:
                self.pathHelixGroup.createXoverItem(xo[0], xo[1], StrandType.Staple)
        # end for
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
