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
from mouseQGraphicsView import *

class CadnanoMainWindow(QMainWindow, ui_mainwindow.Ui_MainWindow):
    def __init__(self, parent=None):
        super(CadnanoMainWindow, self).__init__(parent)
        self.setupUi(self)

        self.slicescene = QGraphicsScene()
        self.sliceGraphicsView.setScene(self.slicescene)

        # self.pathscene = PathScene(self)
        # self.pathGraphicsView.setScene(self.pathscene)
        self.connect(self.actionNewHoneycombPart, SIGNAL("triggered()"), self.honeycombClicked)
        self.connect(self.actionNewSquarePart, SIGNAL("triggered()"),self.squareClicked)

        self.connect(self.actionNew, SIGNAL("triggered()"),self.newClicked)
        self.connect(self.actionOpen, SIGNAL("triggered()"),self.openClicked)
        self.connect(self.actionClose, SIGNAL("triggered()"),self.closeClicked)
        self.connect(self.actionSave, SIGNAL("triggered()"),self.saveClicked)
        self.connect(self.actionSVG, SIGNAL("triggered()"),self.svgClicked)
    # end def

    def newClicked(self):
        """docstring for honeycombClicked"""
        print "new clicked"
    # end def

    def openClicked(self):
        """docstring for honeycombClicked"""
        print "open clicked"
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

def main():
    app = QApplication(sys.argv)
    window = CadnanoMainWindow()
    window.show()
    app.exec_()

if __name__ == '__main__':
    main()

