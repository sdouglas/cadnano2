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
util
Created by Jonathan deWerd.
"""
from traceback import extract_stack
from random import Random
import sys
from os import path
from cadnano import app
import platform

prng = Random()



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
    if app().usesPySide():
        pyWrapper = 'PySide'
        # pyWrapper = 'PyQt4'
    else:
        pyWrapper = 'PyQt4'
    if name == None:
        name = ''
    else:
        name = '.' + name
    _temp = __import__(pyWrapper + name, \
                        globaldict, locals(), fromlist, -1)
    for key in fromlist:
        if pyWrapper == 'PySide' and key in ('pyqtSignal', 'pyqtSlot', 'QString',\
                                             'QStringList'):
            if key == 'pyqtSignal':
                globaldict[key] = getattr(_temp, 'Signal') 
            elif key == 'pyqtSlot':
                globaldict[key] = getattr(_temp, 'Slot')
            elif key == 'QString':
                globaldict[key] = str
            elif key == 'QStringList':
                globaldict[key] = list
        else:
            canary = object()
            binding = getattr(_temp, key, canary)
            if binding == canary:
                raise KeyError("Couldn't import key '%s' from module '%s'"%(key, pyWrapper+name))
            globaldict[key] = binding
    # end for
# end def

# from PyQt4.QtGui import QGraphicsItem, QColor
qtWrapImport('QtGui', globals(), [ 'QGraphicsItem', 'QColor', 'QMouseEvent',\
                                   'QGraphicsSceneMouseEvent'])

def clamp(x, minX, maxX):
    if x < minX:
        return minX
    if x > maxX:
        return maxX
    else:
        return x

def trace(n):
    """Prints a stack trace n frames deep"""
    s = extract_stack()
    for f in s[-n-1:-1]:
        # f is a stack frame like
        # ('/path/script.py', 42, 'funcname', 'current = line - of / code')
        print (path.basename(f[0])+':%i'%f[1]).ljust(30) + f[2]

def defineEventForwardingMethodsForClass(classObj, forwardedEventSuffix, eventNames):
    """Automatically defines methods of the form eventName0Event(self, event) on
    classObj that call self.activeTool().eventName0ForwardedEventSuffix(self, event).
    Note that self here is the 2nd argument of eventName0ForwardedEventSuffix which 
    will be defined with 3 arguments, the first of which will implicitly be the
    activeTool(). If self.activeTool() does not implement eventName0ForwardedEventSuffix,
    no error is raised.
    """
    for evName in eventNames:
        delegateMethodName = evName + forwardedEventSuffix
        eventMethodName = evName + 'Event'
        forwardDisablingPropertyName = delegateMethodName + 'Unused'
        
        def makeTemplateMethod(eventMethodName, delegateMethodName):
            def templateMethod(self, event):
                activeTool = self.activeTool()
                if activeTool and not getattr(activeTool, forwardDisablingPropertyName, False):
                    delegateMethod = getattr(activeTool, delegateMethodName, None)
                    if delegateMethod:
                        delegateMethod(self, event)
                    else:
                        superMethod = getattr(QGraphicsItem, eventMethodName)
                        excludeSuperCallBecauseOfTypeIntolerance = \
                                 isinstance(event, QMouseEvent) and\
                                 not isinstance(event, QGraphicsSceneMouseEvent)
                        if not excludeSuperCallBecauseOfTypeIntolerance:
                            superMethod(self, event)
                else:
                    superMethod = getattr(QGraphicsItem, eventMethodName)
                    superMethod(self, event)
            return templateMethod
        eventHandler = makeTemplateMethod(eventMethodName, delegateMethodName)
        setattr(classObj, eventMethodName, eventHandler)

def strToDna(sequenceStr):
    """
    Returns str having been reduced to capital ACTG
    """
    return "".join(c.capitalize() if c in 'actgACTG' else '' for c in sequenceStr)

def rcomp(seqStr):
    """
    Returns the reversed complement of the sequence in seqStr
    """
    seqStr = strToDna(seqStr)
    return "".join({'A':'T', 'T':'A', 'C':'G', 'G':'C'}[c] for c in reversed(seqStr))

def isWindows():
    if platform.system() == 'Windows':
        return True
    else:
        return False

def isMac():
    if platform.system() == 'Darwin':
        return True
    else:
        return False
        
def isLinux():
    if platform.system() == 'Linux':
        return True
    else:
        return False
