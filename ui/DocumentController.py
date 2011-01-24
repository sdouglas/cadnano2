#!/usr/bin/env python
# encoding: utf-8

# The MIT License
#
# Copyright (c) 2010 Wyss Institute at Harvard University
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

from ui.DocumentWindow import *
from PyQt4.QtGui import *
from ui.treeModel import TreeModel
from idbank import IdBank

class DocumentController():
    """
    The document controller. Hooks high level (read file/write file, add
    submodel, etc) UI elements to their corresponding actions in the model
    """
    def __init__(self):
        """
        
        """
        
        
        #for example: self.parts[object_id] = Part()
        self.parts = {}
        #for example: self.assemblies[object_id] = Assembly()
        self.assemblies = {}

        self.idbank = IdBank()

        self.undoStack = QUndoStack()
        self.win = DocumentWindow(doc=self)
        self.win.show()

        self.treeModel = TreeModel()
        self.win.treeWidget.setModel(self.treeModel)

        self.win.connect(self.win.actionNewHoneycombPart,\
                     SIGNAL("triggered()"),\
                     self.honeycombClicked)
        self.win.connect(self.win.actionNewSquarePart,\
                     SIGNAL("triggered()"),\
                     self.squareClicked)
        self.win.connect(self.win.actionNew,\
                     SIGNAL("triggered()"),\
                     self.newClicked)
        self.win.connect(self.win.actionOpen,\
                     SIGNAL("triggered()"),\
                     self.openClicked)
        self.win.connect(self.win.actionClose,\
                     SIGNAL("triggered()"),\
                     self.closeClicked)
        self.win.connect(self.win.actionSave,\
                     SIGNAL("triggered()"),\
                     self.saveClicked)
        self.win.connect(self.win.actionSVG,\
                     SIGNAL("triggered()"),\
                     self.svgClicked)
                     
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
        hc = SliceHelixGroup.SliceHelixGroup(nrows, ncolumns, "honeycomb")
        self.win.slicescene.addItem(hc)
        index = self.treeView.currentIndex()
        if self.treeModel.insertRow(0, index):
            index = self.treeModel.index(0, 0, index)
            self.setCurrentIndex(index)
            self.treeView.edit(index)
            setDirty()
            updateUi()
    # end def
    
    def addClicked(self):
        index = self.treeView.currentIndex()
        if self.treeModel.insertRow(0, index):
            index = self.treeModel.index(0, 0, index)
            self.setCurrentIndex(index)
            self.treeView.edit(index)
            setDirty()
            updateUi()
        #end if
    # end def
    
    def deleteClicked(self):
        index = self.treeView.currentIndex()
        if not index.isValid():
            return
        name = self.treeModel.data(index).toString()
        rows = self.treeModel.rowCount(index)
        if rows == 0:
            message = "<p>Delete '%s'" % name
        # end if    
        elif rows == 1:
            message = "<p>Delete '%s' and its child (and "
                         "grandchildren etc.)" % name
        # end elif
        elif rows > 1:
            message = "<p>Delete '%s' and its %d children (and "
                         "grandchildren etc.)" % (name, rows)
        
        # end elif
        if not self.okToDelete(this, QString("Delete"), QString(message) ) :
            return
        self.treeModel.removeRow(index.row(), index.parent())
        setDirty()
        updateUi()
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
    
# end class