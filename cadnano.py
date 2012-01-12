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

def ignoreEnv():
    return environ.get('CADNANO_IGNORE_ENV_VARS_EXCEPT_FOR_ME', False)

# The global application object used when cadnano is run as a python module
class HeadlessCadnano(object):
    undoGroup = None
    def isInMaya(self):
        return False
    class prefs():
        squareRows = 50
        squareCols = 50

sharedApp = None
headless = True
def app(appArgs=None):
    global sharedApp
    if sharedApp != None:
        return sharedApp
    return initAppWithoutGui(appArgs)

def initAppWithoutGui(appArgs=sys.argv):
    global sharedApp
    sharedApp = HeadlessCadnano()
    return sharedApp

def initAppWithGui(appArgs=sys.argv):
    import util
    util.qtFrameworkList = ['PyQt', 'PySide']
    from cadnanoqt import CadnanoQt
    global sharedApp
    global headless
    headless = False
    sharedApp = CadnanoQt(appArgs)
    sharedApp.finishInit()
    if environ.get('CADNANO_DISCARD_UNSAVED', False) and not ignoreEnv():
        sharedApp.dontAskAndJustDiscardUnsavedChanges = True
    if environ.get('CADNANO_DEFAULT_DOCUMENT', False) and not ignoreEnv():
        sharedApp.shouldPerformBoilerplateStartupScript = True
    return sharedApp

