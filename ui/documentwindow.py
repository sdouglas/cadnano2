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
documentwindow.py
"""

import sys
import math

from PyQt4.QtCore import *
from PyQt4.QtGui import *
import ui_mainwindow
import slicehelixgroup
import pathcontroller, slicecontroller


class DocumentWindow(QMainWindow, ui_mainwindow.Ui_MainWindow):
    '''docstring for DocumentWindow'''
    def __init__(self, parent=None, doc=None):
        super(DocumentWindow, self).__init__(parent)
        self.document = doc
        self.setupUi(self)
        # Slice setup
        self.slicescene = QGraphicsScene()
        self.sliceGraphicsView.setScene(self.slicescene)
        self.sliceController = slicecontroller.SliceController(self)
        # Path setup
        self.pathscene = QGraphicsScene()
        self.pathGraphicsView.setScene(self.pathscene)
        self.pathController = pathcontroller.PathController(self)
        # treeview setup
        self.treeview.setSelectionBehavior(QTreeView.SelectItems)
        # Edit menu setup
        self.undoStack = doc.undoStack
        self.editMenu = self.menuBar().addMenu("Edit")
        self.undoAction = doc.undoStack.createUndoAction(self)
        self.redoAction = doc.undoStack.createRedoAction(self)
        self.editMenu.addAction(self.undoAction)
        self.editMenu.addAction(self.redoAction)
    # end def

    def setCurrentIndex(self,index):
        if index.isValid():
            self.treeview.scrollTo(index)
            self.treeview.setCurrentIndex(index)
        # end if
    # end def
