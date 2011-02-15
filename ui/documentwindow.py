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

from PyQt4.QtCore import *
from PyQt4.QtGui import *
import ui_mainwindow
import slicehelixgroup
import pathcontroller
import slicecontroller
from cadnano import app

class SliceRoot(QGraphicsItem):
    def __init__(self,rectsource=None, parent = None, scene=None):
        super(SliceRoot, self).__init__()
        self.parent = parent 
        self.scene = scene
        self.rect = rectsource.sceneRect()
        
    def paint(self, painter, option, widget):
        pass
        
    def boundingRect(self):
        return self.rect
# end class
        
class DocumentWindow(QMainWindow, ui_mainwindow.Ui_MainWindow):
    '''docstring for DocumentWindow'''
    def __init__(self, parent=None, docCtrlr=None):
        super(DocumentWindow, self).__init__(parent)
        self.controller = docCtrlr
        self.setupUi(self)
        # Slice setup
        self.slicescene = QGraphicsScene()

        self.sliceroot = SliceRoot(rectsource=self.slicescene)
        self.slicescene.addItem(self.sliceroot) 
        
        self.sliceGraphicsView.setScene(self.slicescene)
        
        self.sliceGraphicsView.viewRootItem = self.sliceroot
        
        self.sliceController = slicecontroller.SliceController(self)
        # Path setup
        self.pathscene = QGraphicsScene()
        self.pathGraphicsView.setScene(self.pathscene)
        self.pathController = pathcontroller.PathController(self)
        # Edit menu setup
        self.undoStack = docCtrlr.undoStack
        self.editMenu = self.menuBar().addMenu("Edit")
        self.undoAction = docCtrlr.undoStack.createUndoAction(self)
        self.redoAction = docCtrlr.undoStack.createRedoAction(self)
        self.editMenu.addAction(self.undoAction)
        self.editMenu.addAction(self.redoAction)
        
    def focusInEvent(self):
       app().undoGroup.setActiveStack(self.controller.undoStack)
