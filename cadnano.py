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

import sys, imp, util
import os.path
from glob import glob
from code import interact

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))+"/include")

global sharedApp
sharedApp = None

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
    def isGui(self):
        return False
# end def

def app(appArgs=None):
    global sharedApp
    if sharedApp != None:
        return sharedApp
    return initAppWithoutGui(appArgs)

def initAppWithoutGui(appArgs=sys.argv):
    global sharedApp
    sharedApp = HeadlessCadnano()
    loadAllPlugins()
    return sharedApp

def initAppWithGui(appArgs=sys.argv):
    import util
    util.qtFrameworkList = ['PyQt', 'PySide']
    from cadnanoqt import CadnanoQt
    global sharedApp
    sharedApp = CadnanoQt(appArgs)
    sharedApp.finishInit()
    if util.isWindows():
        pass
        # import ctypes
        # myappid = 'harvard.cadnano.cadnano2.2' # arbitrary string
        # ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
    return sharedApp
    
def initAppMaya(appArgs=sys.argv):
    import util
    util.qtFrameworkList = ['PyQt', 'PySide']
    from cadnanoqt import CadnanoQt
    global sharedApp
    sharedApp = CadnanoQt(appArgs)
    return sharedApp
# end def

def path():
    return os.path.abspath(os.path.dirname(__file__))

# maps plugin path (extension stripped) -> plugin module
loadedPlugins = {}

def unloadedPlugins():
    """ Returns a list of plugin paths that have yet to
    be loaded but are in the top level of one of the
    search directories specified in pluginDirs"""
    internalPlugins = os.path.join(path(), 'plugins')
    pluginDirs = [internalPlugins]
    results = []
    for pluginDir in pluginDirs:
        if not os.path.isdir(pluginDir):
            continue
        for dirent in os.listdir(pluginDir):
            f = os.path.join(pluginDir, dirent)
            isfile = os.path.isfile(f)
            hasValidSuffix = dirent.endswith(('.py', '.so'))
            if isfile and hasValidSuffix:
                results.append(f)
            if os.path.isdir(f) and\
               os.path.isfile(os.path.join(f, '__init__.py')):
                results.append(f)
    return filter(lambda x: x not in loadedPlugins, results)

def loadPlugin(f):
    path, fname = os.path.split(f)
    name, ext = os.path.splitext(fname)
    pluginKey = os.path.join(path, name)
    try:
        mod = loadedPlugins[pluginKey]
        return mod
    except KeyError:
        pass
    file, filename, data = imp.find_module(name, [path])
    mod = imp.load_module(name, file, filename, data)
    loadedPlugins[pluginKey] = mod
    return mod

def loadAllPlugins():
    loadedAPlugin = False
    for p in unloadedPlugins():
        loadPlugin(p)
        loadedAPlugin = True
    return loadedAPlugin