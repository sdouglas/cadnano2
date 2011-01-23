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

from PyQt4.QtCore import *
from PyQt4.QtGui import *
import SliceHelixGroup


class DocumentController():
    """
    Manages interactions between the Document widgets/UI and the Document 
    model.
    """

    # We store mainWindow because a controller's got to have
    # references to both the layer above (UI) and the layer below (model)
    def __init__(self, win):
        self.mainWindow = win
        # Connect actions to slots
        win.connect(win.actionNewHoneycombPart,\
                     SIGNAL("triggered()"),\
                     self.honeycombClicked)
        win.connect(win.actionNewSquarePart,\
                     SIGNAL("triggered()"),\
                     self.squareClicked)
        win.connect(win.actionNew,\
                     SIGNAL("triggered()"),\
                     self.newClicked)
        win.connect(win.actionOpen,\
                     SIGNAL("triggered()"),\
                     self.openClicked)
        win.connect(win.actionClose,\
                     SIGNAL("triggered()"),\
                     self.closeClicked)
        win.connect(win.actionSave,\
                     SIGNAL("triggered()"),\
                     self.saveClicked)
        win.connect(win.actionSVG,\
                     SIGNAL("triggered()"),\
                     self.svgClicked)

    def newClicked(self):
        """docstring for newClicked"""
        print "new clicked"
    # end def

    def openClicked(self):
        """docstring for openClicked"""
        print "open clicked"
        # self.parts, self.assemblies = self.parts json_io.load(self.treeModel)
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
        hc = SliceHelixGroup.SliceHelixGroup(nrows, ncolumns, "honeycomb")
        self.mainWindow.slicescene.addItem(hc)