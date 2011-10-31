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

import sys
from os import path, environ
from code import interact
PySide_loaded = None

saved_argv = sys.argv


def usesPySide(*args):
    return False
    global PySide_loaded
    if PySide_loaded != None:
        return PySide_loaded
    try:
        import PySide
        PySide_loaded = True
        print "Using PySide"
    except ImportError:
        PySide_loaded = False
        print "Using PyQt"
    return PySide_loaded
# end def

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
    if usesPySide():
        pyWrapper = 'PySide'
        #pyWrapper = 'PyQt4'
    else:
        pyWrapper = 'PyQt4'
    _temp = __import__(pyWrapper + '.' + name,
                        globaldict, locals(), fromlist, -1)
    for key in dir(_temp):
        if pyWrapper == 'PySide':
            if key == 'pyqtSignal':
                globaldict[key] = getattr(_temp, 'Signal')
            elif key == 'pyqtSlot':
                globaldict[key] = getattr(_temp, 'Slot')
            else:
                globaldict[key] = getattr(_temp, key)
        else:
            globaldict[key] = getattr(_temp, key)
    # end for
# end def

# import Qt stuff into the module namespace with PySide, PyQt4 independence
qtWrapImport('QtGui', globals(),  ['qApp', 'QApplication', 'QIcon',
                                   'QUndoGroup'])
qtWrapImport('QtCore', globals(), ['QObject', 'QCoreApplication'])


class Cadnano(QObject):
    sharedApp = None  # This class is a singleton.
    usesPySide = usesPySide     # This is bad that this can work
    dontAskAndJustDiscardUnsavedChanges = False
    shouldPerformBoilerplateStartupScript = False
    PySide_loaded = PySide_loaded

    def __init__(self):
        argv = saved_argv
        if QCoreApplication.instance() == None:
            self.qApp = QApplication(argv)
            assert(QCoreApplication.instance() != None)
            self.qApp.setOrganizationDomain("cadnano.org")
        super(Cadnano, self).__init__()
        assert(not Cadnano.sharedApp)
        Cadnano.sharedApp = self
        self.guiInitialized = False

    def initGui(self):
        if self.guiInitialized:
            return
        self.guiInitialized = True
        from views.preferences import Preferences
        self.prefs = Preferences()
        argv = sys.argv
        qApp.setWindowIcon(QIcon('ui/mainwindow/images/cadnano2-app-icon.png'))
        self.undoGroup = QUndoGroup()
        self.documentControllers = set()  # Open documents
        self.activeDocument = None
        self.vh = {}  # Newly created VirtualHelix register here by idnum.
        self.vhi = {}
        self.partItem = None
        self.d = self.newDocument(isFirstNewDoc=True)
        if "-i" in argv:
            print "Welcome to cadnano's debug mode!"
            print "Some handy locals:"
            print "\ta\tcadnano.app() (the shared cadnano application object)"
            print "\td()\tthe last created Document"
            print ("\tv\tmaps the numbers of recently created " +
                  "VirtualHelixes to the VHs themselves")
            print "\tph\tmaps virtual helix numbers to virtualHelixItem"
            print "\tpartItem()\tthe last initialized PartItem"
            print "\tpySide()\ttrue iff the app is using PySide"
            print "\tquit()\tquit (for when the menu fails)"
            interact('', local={'a': self,
                                'd': lambda: self.d,
                                'vh': self.vh,
                                'vhi': self.vhi,
                                'pi': lambda: self.partItem,
                                'pySide': self.usesPySide})

    def isInMaya(self):
        return QCoreApplication.instance().applicationName().contains(
                                                    "Maya", Qt.CaseInsensitive)
    def exec_(self):
        if hasattr(self, 'qApp'):
            self.qApp.exec_()

    def newDocument(self, isFirstNewDoc=False):
        from controllers.documentcontroller import DocumentController
        defaultFile = environ.get('CADNANO_DEFAULT_DOCUMENT', None)
        if defaultFile and isFirstNewDoc:
            defaultFile = path.expanduser(defaultFile)
            defaultFile = path.expandvars(defaultFile)
            dc = DocumentController()
            doc = dc.document()
            from model.decoder import decode
            decode(doc, file(defaultFile).read())
            print "Loaded default document: %s" % doc
        else:
            docCtrlrCount = len(self.documentControllers)
            if docCtrlrCount == 0:  # first dc
                # dc adds itself to app.documentControllers
                dc = DocumentController()
            elif docCtrlrCount == 1:  # dc already exists
                dc = list(self.documentControllers)[0]
                dc.newDocument()  # tell it to make a new doucment
        return dc.document()

    def prefsClicked(self):
        print "prefsClicked"
        self.prefs.showDialog()

def ignoreEnv():
    return environ.get('CADNANO_IGNORE_ENV_VARS_EXCEPT_FOR_ME', False)

def app(appArgs=None):
    if not Cadnano.sharedApp:
        Cadnano.sharedApp = Cadnano()
    if environ.get('CADNANO_DISCARD_UNSAVED', False) and not ignoreEnv():
        Cadnano.sharedApp.dontAskAndJustDiscardUnsavedChanges = True
    if environ.get('CADNANO_DEFAULT_DOCUMENT', False) and not ignoreEnv():
        Cadnano.sharedApp.shouldPerformBoilerplateStartupScript = True
    return Cadnano.sharedApp
