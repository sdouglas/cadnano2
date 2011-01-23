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

"""
DocWindow.py
"""

import sys
import math

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from ui import ui_mainwindow
from ui import Styles
from ui import SliceHelixGroup
from ui import DocumentController, PathController, SliceController
from CustomQGraphicsView import *


class DocWindow(QMainWindow, ui_mainwindow.Ui_MainWindow):
    '''docstring for DocWindow'''
    def __init__(self, parent=None, doc=None):
        super(DocWindow, self).__init__(parent)
        self.document = doc
        # Document setup
        self.setupUi(self)
        self.documentController = DocumentController.DocumentController(self)
        # Slice setup
        self.slicescene = QGraphicsScene()
        self.sliceGraphicsView.setScene(self.slicescene)
        self.sliceController = SliceController.SliceController(self)
        # Path setup
        self.pathscene = QGraphicsScene()
        self.pathGraphicsView.setScene(self.pathscene)
        self.pathController = PathController.PathController(self)
