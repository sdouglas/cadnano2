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
cadnano
Created by Jonathan deWerd on 2011-01-29.
"""
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from code import interact

class caDNAno(QApplication):
    sharedApp = None  # This class is a singleton.
    def __init__(self, argv):
        if argv == None:
            argv = ["cadnano",]
        super(caDNAno, self).__init__(argv)
        assert(not caDNAno.sharedApp)
        caDNAno.sharedApp = self
        self.setWindowIcon(QIcon('ui/images/cadnano2-app-icon.png'))
        self.undoGroup = QUndoGroup()
        #self.setApplicationName(QString("caDNAno"))
        self.documentControllers = set() # Open documents
        d = self.newDocument()
        self.v = None
        self.ph = None
        self.phg = None
        if "-i" in argv:
            self.d = d
            self.v = {}  # Newly created VirtualHelix register themselves here under their idnum.
            self.ph = {}
            self.phg = None
            print "Welcome to caDNAno's debug mode!"
            print "Some handy locals:"
            print "\ta\tcaDNAno.app() (the shared caDNAno application object)"
            print "\td\tthe last created Document"
            print "\tv\tmaps the numbers of recently created VirtualHelixes to the VHs themselves"
            print "\tph\tmaps virtual helix numbers to pathhelix"
            print "\tphg()\tthe last initialized PathHelixGroup"
            print "\tquit()\tquit (for when the menu fails)"
            interact(local={'a':self, 'd':d, 'v':self.v, 'ph':self.ph, 'phg':lambda : self.phg})
        
    def isInMaya(self):
        return False
        
    def newDocument(self):
        from ui.documentcontroller import DocumentController
        dc = DocumentController() # DocumentController is responsible for adding
                                  # itself to app.documentControllers
        return dc.document()

# Convenience. No reason to feel guilty using it - caDNAno is a singleton.
def app(appArgs=None):
    if not caDNAno.sharedApp:
        caDNAno.sharedApp = caDNAno(appArgs)
    return caDNAno.sharedApp