#!/usr/bin/env python
# encoding: utf-8

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
main.py

Created by Shawn Douglas on 2010-09-26.
Copyright (c) 2010 . All rights reserved.
"""

import sys
import math

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from ui import Styles, SliceHelixGroup, ui_mainwindow
from data import json_io


class CadnanoMainWindow(QMainWindow, ui_mainwindow.Ui_MainWindow):
    def __init__(self, parent=None):
        super(CadnanoMainWindow, self).__init__(parent)
        self.setupUi(self)

        self.slicescene = QGraphicsScene()
        self.sliceGraphicsView.setScene(self.slicescene)
        self.treeModel = TreeModel()
        self.parts = {}
        self.assemblies = {}

        # self.pathscene = PathScene(self)
        # self.pathGraphicsView.setScene(self.pathscene)
        self.connect(self.actionNewHoneycombPart,\
                     SIGNAL("triggered()"),\
                     self.honeycombClicked)
        self.connect(self.actionNewSquarePart,\
                     SIGNAL("triggered()"),\
                     self.squareClicked)

        self.connect(self.actionNew,\
                     SIGNAL("triggered()"),\
                     self.newClicked)
        self.connect(self.actionOpen,\
                     SIGNAL("triggered()"),\
                     self.openClicked)
        self.connect(self.actionClose,\
                     SIGNAL("triggered()"),\
                     self.closeClicked)
        self.connect(self.actionSave,\
                     SIGNAL("triggered()"),\
                     self.saveClicked)
        self.connect(self.actionSVG,\
                     SIGNAL("triggered()"),\
                     self.svgClicked)
    # end def

    def newClicked(self):
        """docstring for honeycombClicked"""
        print "new clicked"
    # end def

    def openClicked(self):
        """docstring for honeycombClicked"""
        print "open clicked"
        # self.parts, self.assemblies = self.parts json_io.load(self.treeModel)
    # end def

    def closeClicked(self):
        """docstring for honeycombClicked"""
        print "close clicked"
    # end def

    def saveClicked(self):
        """docstring for honeycombClicked"""
        print "save clicked"
    # end def

    def svgClicked(self):
        """docstring for honeycombClicked"""
        print "svg clicked"
    # end def

    def honeycombClicked(self):
        """docstring for honeycombClicked"""
        self.addHoneycombShape()

    def squareClicked(self):
        """docstring for squareClicked"""

    def addHoneycombShape(self, nrows=20, ncolumns=20):
        hc = SliceHelixGroup.SliceHelixGroup(nrows, ncolumns, "honeycomb")
        self.slicescene.addItem(hc)

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
        messageBox.exec()
        return messageBox.clickedButton() == deleteButton
    # end def

# end class

def main():
    app = QApplication(sys.argv)
    window = CadnanoMainWindow()
    window.show()
    app.exec_()

if __name__ == '__main__':
    main()
