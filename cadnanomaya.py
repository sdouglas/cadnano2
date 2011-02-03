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
cadnanomaya
Created by Nick Conway on 2011-02-03.
modified from cadnano.py
"""
from PyQt4 import QtCore
from PyQt4 import QtGui

class caDNAno(QtCore.QObject):
    sharedApp = None  # This class is a singleton.
    def __init__(self):
        super(caDNAno, self).__init__()
        assert(not caDNAno.sharedApp)
        caDNAno.sharedApp = self
        self.app = QtGui.qApp
        #self.setWindowIcon(QIcon('ui/images/cadnano2-app-icon.png'))
        self.undoGroup = QtGui.QUndoGroup()
        #self.setApplicationName(QString("caDNAno"))
        self.documentControllers = set() # Open documents
        self.newDocument()

    def newDocument(self):
        from ui.mayacontroller import DocumentController
        DocumentController() # DocumentController is responsible for adding
                             # itself to app.documentControllers

# Convenience. No reason to feel guilty using it - caDNAno is a singleton.
def app():
    return caDNAno.sharedApp