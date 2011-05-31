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
import sys
from os import path

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
        
        def makeTemplateMethod(eventMethodName, delegateMethodName):
            def templateMethod(self, event):
                activeTool = self.activeTool()
                if activeTool:
                    delegateMethod = getattr(activeTool, delegateMethodName, None)
                    if delegateMethod:
                        delegateMethod(self, event)
                else:
                    QGraphicsItem.hoverLeaveEvent(self, event)
            return templateMethod
        eventHandler = makeTemplateMethod(eventMethodName, delegateMethodName)
        setattr(classObj, eventMethodName, eventHandler)