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

from code import interact
import sys, os
from os import path
PySide_loaded = None

def usesPySide(self):
    if self.PySide_loaded == None:
        try:
            import PySide
            self.PySide_loaded = True
        except ImportError:
            self.PySide_loaded = False
    return self.PySide_loaded
# end def

def usePySide():
    try:
        import PySide
        PySide_loaded = True
    except ImportError:
        PySide_loaded = False
    return PySide_loaded
# end def

# from PyQt4.QtCore import *
# from PyQt4.QtGui import *
def qtWrapImport(name, globaldict, fromlist):
    """
    special function that allows for the import of PySide or PyQt modules
    as available
    
    name is the name of the Qt top level class such as QtCore, or QtGui
    
    globaldict is a the module level global namespace dictionary returned from
    calling the globals() method
    
    fromlist is a list of subclasses such as [QFont, QColor], or [QRectF]
    """
    pyWrapper = None
    if usePySide():
        # pyWrapper = 'PySide'
        pyWrapper = 'PyQt4'
    else:
        pyWrapper = 'PyQt4'
    _temp = __import__(pyWrapper + '.' +  name, \
                        globaldict, locals(), fromlist, -1)
    for key in dir(_temp):
        if pyWrapper == 'PySide':
            if key == 'pyqtSignal':
                globaldict[key] = getattr(_temp, 'Signal') 
            elif key == 'pyqtSlot':
                globaldict[key] = getattr(_temp, 'Slot')
        else:
            globaldict[key] = getattr(_temp, key)
    # end for
# end def

# import Qt stuff into the module namespace with PySide, PyQt4 independence
qtWrapImport('QtGui', globals(),  ['QApplication', 'QUndoGroup', 'QIcon'])


class CADnano(QApplication):
    sharedApp = None  # This class is a singleton.
    usesPySide = usesPySide     # This is bad that this can work
    dontAskAndJustDiscardUnsavedChanges = False
    shouldPerformBoilerplateStartupScript = False
    PySide_loaded = PySide_loaded
    
    def __init__(self, argv):
        if argv == None:
            argv = ["cadnano",]
        super(CADnano, self).__init__(argv)
        assert(not CADnano.sharedApp)
        CADnano.sharedApp = self
        self.guiInitialized = False
    
    def initGui(self):
        if self.guiInitialized:
            return
        self.guiInitialized = True
        argv = sys.argv
        self.setWindowIcon(QIcon('ui/images/cadnano2-app-icon.png'))
        self.undoGroup = QUndoGroup()
        #self.setApplicationName(QString("CADnano"))
        self.documentControllers = set() # Open documents
        self.v = {}  # Newly created VirtualHelix register themselves here under their idnum.
        self.ph = {}
        self.phg = None
        self.d = self.newDocument(isFirstNewDoc=True)
        if "-i" in argv:
            print "Welcome to CADnano's debug mode!"
            print "Some handy locals:"
            print "\ta\tCADnano.app() (the shared CADnano application object)"
            print "\td()\tthe last created Document"
            print "\tv\tmaps the numbers of recently created VirtualHelixes to the VHs themselves"
            print "\tph\tmaps virtual helix numbers to pathhelix"
            print "\tphg()\tthe last initialized PathHelixGroup"
            print "\tpySide()\ttrue iff the app is using PySide"
            print "\tquit()\tquit (for when the menu fails)"
            interact('', local={'a':self,\
                                'd':lambda : self.d,\
                                'v':self.v,\
                                'ph':self.ph,\
                                'phg':lambda : self.phg,\
                                'pySide':self.usesPySide})
    # end def

    def isInMaya(self):
        return False

    def newDocument(self, isFirstNewDoc=False):
        from ui.documentcontroller import DocumentController
        defaultFile = os.environ.get('CADNANO_DEFAULT_DOCUMENT', None)
        if defaultFile and isFirstNewDoc:
            defaultFile = path.expanduser(defaultFile)
            defaultFile = path.expandvars(defaultFile)
            from model.decoder import decode
            doc = decode(file(defaultFile).read())
            print "Loaded default document: %s"%doc
            dc = DocumentController(doc, defaultFile)
        else:
            dc = DocumentController()  # DocumentController is responsible for adding
                                       # itself to app.documentControllers
        return dc.document()

# Convenience. No reason to feel guilty using it - CADnano is a singleton.
def app(appArgs=None):
    if not CADnano.sharedApp:
        CADnano.sharedApp = CADnano(appArgs)
    if os.environ.get('CADNANO_DISCARD_UNSAVED', False):
        CADnano.sharedApp.dontAskAndJustDiscardUnsavedChanges = True
    if os.environ.get('CADNANO_DEFAULT_DOCUMENT', False):
        CADnano.sharedApp.shouldPerformBoilerplateStartupScript = True
    return CADnano.sharedApp