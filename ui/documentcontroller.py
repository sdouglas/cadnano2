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

from PyQt4.QtGui import *
from PyQt4.QtCore import SIGNAL
from documentwindow import DocumentWindow
from slicehelixgroup import SliceHelixGroup

class DocumentController():
    """
    The document controller. Hooks high level (read file/write file, add
    submodel, etc) UI elements to their corresponding actions in the model
    """
    def __init__(self):
        from data.assembly import AssemblyNode
        from data.part import PartNode
        from treemodel import TreeModel
        from idbank import IdBank
        
        #for example: self.parts[object_id] = Part()
        self.parts = {}
        #for example: self.assemblies[object_id] = Assembly()
        self.assemblies = {}

        self.idbank = IdBank()

        self.undoStack = QUndoStack()
        self.win = DocumentWindow(doc=self)
        self.win.show()

        # Configure the treeview
        self.treemodel = TreeModel()
        self.win.treeview.setDragDropMode(QAbstractItemView.InternalMove)
        self.win.treeview.setAllColumnsShowFocus(True)
        self.win.treeview.setModel(self.treemodel)

        # self.win.connect(self.win.actionNewHoneycombPart,\
        #              SIGNAL("triggered()"),\
        #              self.honeycombClicked)
        # self.win.connect(self.win.actionNewSquarePart,\
        #              SIGNAL("triggered()"),\
        #              self.squareClicked)
        # self.win.connect(self.win.actionNew,\
        #              SIGNAL("triggered()"),\
        #              self.newClicked)
        # self.win.connect(self.win.actionOpen,\
        #              SIGNAL("triggered()"),\
        #              self.openClicked)
        # self.win.connect(self.win.actionClose,\
        #              SIGNAL("triggered()"),\
        #              self.closeClicked)
        # self.win.connect(self.win.actionSave,\
        #              SIGNAL("triggered()"),\
        #              self.saveClicked)
        # self.win.connect(self.win.actionSVG,\
        #              SIGNAL("triggered()"),\
        #              self.svgClicked)
                     
                     
        self.win.actionNewHoneycombPart.triggered.connect(self.honeycombClicked)
        self.win.actionNewSquarePart.triggered.connect(self.squareClicked)
        self.win.actionNew.triggered.connect(self.newClicked)
        self.win.actionOpen.triggered.connect(self.openClicked)
        self.win.actionClose.triggered.connect(self.closeClicked)
        self.win.actionSave.triggered.connect(self.saveClicked)
        self.win.actionSVG.triggered.connect(self.svgClicked)
    # end def

    def createConnections():
        """
        """
        #self.win.connect(self.treeview.selectionModel(), SIGNAL("currentChange()"), self.win, SLOT(updateUi))
        # QItemSelectionModel.currentChange emits the previous and current selected QModelIndex, but we don't use those values
        self.treeview.selectionModel().currentChange.connect(self.updateUi)
        
        
        # self.win.connect(self.treemodel, SIGNAL(dataChanged()) , self.win, SLOT(setDirty))
        # self.win.connect(self.treemodel, SIGNAL(rowsRemoved()) , self.win, SLOT(setDirty))
        # self.win.connect(self.treemodel, SIGNAL(modelReset()) , self.win, SLOT(setDirty))
        self.treemodel.dataChanged.connect(self.win.setWindowModified)
        self.treemodel.rowsRemoved.connect(self.win.setWindowModified)
        self.treemodel.modelReset.connect(self.win.setWindowModified)
        
        slotForAction = {}
        # slotForAction[actionNew] = SLOT(self.fileNew)
        # slotForAction[actionOpen] = SLOT(self.fileOpen)
        # slotForAction[actionSave] = SLOT(self.fileSave)
        # slotForAction[actionSave_As] = SLOT(self.fileSaveAs)
        # slotForAction[actionQuit] = SLOT(self.close)
        # slotForAction[actionAdd] = SLOT(self.editAdd)
        # slotForAction[actionDelete] = SLOT(self.editDelete)
        # slotForAction[actionCut] = SLOT(self.editCut)
        # slotForAction[actionPaste] = SLOT(self.editPaste)
        # slotForAction[actionMoveUp] = SLOT(self.editMoveUp())
        # slotForAction[actionMoveDown] = SLOT(self.editMoveDown())
        # slotForAction[actionPromote] = SLOT(self.editPromote())
        # slotForAction[actionDemote] = SLOT(self.editDemote())
        
        slotForAction[actionNew] = self.newClicked
        slotForAction[actionOpen] = self.openClicked
        slotForAction[actionSave] = self.SaveClicked
        slotForAction[actionSave_As] = self.saveAsClicked
        slotForAction[actionQuit] = self.closeClicked
        slotForAction[actionAdd] = self.addClicked
        slotForAction[actionDelete] = self.deleteClicked
        slotForAction[actionCut] = self.cutClicked
        slotForAction[actionPaste] = self.pasteClicked
        slotForAction[actionMoveUp] = self.moveUpClicked
        slotForAction[actionMoveDown] = self.moveDownClicked
        slotForAction[actionPromote] = self.promoteClicked
        slotForAction[actionDemote] = self.demoteClicked
        
        for key in slotForAction:
            #self.win.connect(key, SIGNAL("triggered()"), slotForAction[key])
            key.triggered.connect(slotForAction[key])
        # end for
        
    
    # end def


    def newClicked(self):
        """docstring for newClicked"""
        print "new clicked"
    # end def


    def openClicked(self):
        """docstring for openClicked"""
        print "open clicked"
    # end def


    def closeClicked(self):
        """docstring for closeClicked"""
        print "close clicked"
    # end def


    def saveClicked(self):
        """docstring for saveClicked"""
        print "save clicked"
        # saved = False
        # if self.treemodel.filename == None:
        #     self.saveAsClicked()
        # # end if
        # else:
        #     try:
        #         self.treemodel.save()
        #         self.setDirty = False
        #         #self.win.setWindowTitle()
        #         saved = True
        #     except:
        #         print "Failed to save"
        # # end else
        # self.updateUi()
        # return saved
    # end def

    
    def saveAsClicked():
        """"""
        filename = self.treemodel.filename
        if filename == None:
            directory = "."
        # end if
        else:
            directory = QFileInfo(filename).path()
        # end else
        filename = QFileDialog.getSaveFileName(self.win, \
                                                "%s - Save As" % QApplication.applicationName(),\
                                                directory, \
                                                "%s (*.json)" % QApplication.applicationName() )
        if filename.isEmpty():
            return False
        # end if
        if not filename.toLower().endswith(".json"):
            filename += ".json"
        # end if
        self.treemodel.filename = filename
        return self.saveClicked()
    # end def

    def svgClicked(self):
        """docstring for svgClicked"""
        print "svg clicked"
    # end def


    def honeycombClicked(self):
        """docstring for honeycombClicked"""
        print "+honeycomb clicked"
        self.addHoneycombHelixGroup()
    # end def


    def squareClicked(self):
        """docstring for squareClicked"""
        print "+square clicked"
    # end def


    def addHoneycombHelixGroup(self, nrows=20, ncolumns=20):
        """docstring for addHoneycombHelixGroup"""
        shg = SliceHelixGroup(nrows, ncolumns, "honeycomb")
        self.win.slicescene.addItem(shg)
        # phg = PathHelixGroup("honeycomb")
        # connect(shg.addHelix, SIGNAL("triggered()"), phg.addHelix)
        
        # index = self.win.treeview.currentIndex()
        # if self.treemodel.insertRow(0, index):
        #     index = self.treemodel.index(0, 0, index)
        #     self.setCurrentIndex(index)
        #     self.treeview.edit(index)
        #     self.win.setWindowModified(True)
        #     self.updateUi()
    # end def


    def addClicked(self):
        index = self.win.treeview.currentIndex()
        if self.treemodel.insertRow(0, index):
            index = self.treemodel.index(0, 0, index)
            self.setCurrentIndex(index)
            self.win.treeview.edit(index)
            self.win.setWindowModified(True)
            self.updateUi()
        #end if
    # end def


    def deleteClicked(self):
        index = self.win.treeview.currentIndex()
        if not index.isValid():
            return
        name = self.treemodel.data(index).toString()
        rows = self.treemodel.rowCount(index)
        if rows == 0:
            message = "<p>Delete '%s'" % name
        # end if    
        elif rows == 1:
            message = "<p>Delete '%s' and its child (and " +\
                         "grandchildren etc.)" % name
        # end elif
        elif rows > 1:
            message = "<p>Delete '%s' and its %d children (and " +\
                         "grandchildren etc.)" % (name, rows)
        
        # end elif
        if not self.okToDelete(this, QString("Delete"), QString(message) ) :
            return
        self.treemodel.removeRow(index.row(), index.parent())
        self.win.setWindowModified(True)
        self.updateUi()
    # end def

    def okToDelete(parent, title,text, detailedText):
        """
        """
        messageBox = QMessageBox(parent)
        if parent:
            messageBox.setWindowModality(Qt.WindowModal)
        # end if
        messageBox.setIcon(QMessageBox.Question)
        messageBox.setWindowTitle( QString("%1 - %2").arg(QApplication.applicationName()).arg(title) )
        messageBox.setText(text)
        if not detailedText.isEmpty():
            messageBox.setInformativeText(detailedText)
        # end if
        deleteButton = messageBox.addButton(QString("&Delete"), QMessageBox.AcceptRole)
        messageBox.addButton(QString("Do &Not Delete"),QMessageBox.RejectRole)
        messageBox.setDefaultButton(deleteButton)
        messageBox.exec_()
        return messageBox.clickedButton() == deleteButton
    # end def


    def okToClear(savedata, parent, title,text, detailedText):
        """
        savedata is a function pointer
        """
        assert savedata and parent
        messageBox = QMessageBox(parent)
        if parent:
            messageBox.setWindowModality(Qt.WindowModal)
        # end if
        messageBox.setIcon(QMessageBox.Question)
        messageBox.setWindowTitle( QString("%1 - %2").arg(QApplication.applicationName()).arg(title) )
        messageBox.setText(text)
        if not detailedText.isEmpty():
            messageBox.setInformativeText(detailedText)
        # end if
        
        saveButton = messageBox.addButton(QMessageBox.Save)
        messageBox.addButton(QMessageBox.Save)
        messageBox.addButton(QMessageBox.Discard)
        messageBox.addButton(QMessageBox.Cancel)
        messageBox.setDefaultButton(saveButton)
        messageBox.exec_()
        if messageBox.clickedButton() == messageBox.button(QMessageBox.Cancel):
            return False
            if messageBox.clickedButton() == messageBox.button(QMessageBox.Save):
                return parent.savedata() # how to return the function (lambda?)
        return True 
    # end def

    def createAction(icon, text, parent, shortcutkey):
        """
        returns a QAction object
        """
        action = QAction(QIcon(icon), text, parent)
        if not shorcutkey.isEmpty():
            action.setShortcut(shortcutkey)
        # end if
        return action
    # end def


    def updateUi():
        """
        """
        self.win.actionSave.setEnabled(isWindowModified)
        rows = self.treemodel.rowCount()
        self.win.actionSave_As.setEnabled(self.win.isWindowModified() or rows)
        self.win.actionHideOrShowItems.setEnabled(rows)
        enable = self.treeview.currentIndex().isValid()
        
        actions = [self.win.actionDelete, self.win.actionMoveUp, self.win.actionMoveDown, \
                    self.win.actionCut,self.win.actionPromote, self.win.actionDemote]
        for action in actions:
            action.setEnabled(enable)
        # end for
        self.win.actionStartOrStop.setEnabled(rows);
        self.win.actionPaste.setEnabled(self.treemodel.hasCutItem())
    #endif


    def cutClicked():
        index = self.win.treeview.currentIndex()
        self.win.setCurrentIndex(self.treemodel.cut(index))
        self.win.actionPaste.setEnabled(self.treemodel.hasCutItem())
    # end def


    def pasteClicked():
        index = self.win.treeview.currentIndex()
        self.win.setCurrentIndex(self.treemodel.paste(index))
    # end def


    def moveUpClicked():
        index = self.win.treeview.currentIndex()
        self.win.setCurrentIndex(self.treemodel.moveUp(index))
    # end def


    def moveDownClicked():
        index = self.win.treeview.currentIndex()
        self.win.setCurrentIndex(self.treemodel.moveDown(index))
    # end def


    def promoteClicked():
        index = self.win.treeview.currentIndex()
        self.win.setCurrentIndex(self.treemodel.promote(index))
    #end def


    def demoteClicked():
        index = self.win.treeview.currentIndex()
        self.win.setCurrentIndex(self.treemodel.demote(index))
    #end def


    def hideOrShowNode(hide, index):
        """"""
        hideThisOne = hide #and self.treemodel.isChecked(index)
        if index.isValid():
            self.win.treeview.setRowHidden(index.row(), index.parent(), hideThisOne)
        # end if
        if not hideThisOne:
            for row in range(self.treemodel.rowCount(index)):
                self.hideOrShowNode(hide, self.treemodel.index(row, 0, index))
            # end for
        # end if
# end class
