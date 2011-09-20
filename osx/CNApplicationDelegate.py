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
This file houses the code that allows the opening of cadnano files by dragging
to the icon in the dock or double clicking on the icon.
"""

import objc, os
from Foundation import *
from AppKit import *
from controllers.documentcontroller import DocumentController
# from model.decoder import decode
from cadnano import app as sharedCadnanoObj

class CNApplicationDelegate(NSObject):
    def application_openFile_(self, app, f):
        if f == "main.py":  # ignore
            return
        extension = os.path.splitext(f)[1].lower()
        if extension not in ('.nno', '.json', '.cadnano'):
            print "Could not open file %s (bad extension %s)"%(f, extension)
            return
        doc = decode(file(str(f)).read())
        DocumentController(doc, str(f))
        return None

    def application_openFiles_(self, app, fs):
        if fs.isKindOfClass_(NSCFString):
            self.application_openFile_(app, fs)
            return
        for f in fs:
            self.application_openFiles_(app, f)

    def applicationShouldTerminate_(self, app):
        for dc in sharedCadnanoObj().documentControllers:
            if not dc.maybeSave():
                return NSTerminateCancel
        return NSTerminateNow

sharedDelegate = CNApplicationDelegate.alloc().init()
NSApplication.sharedApplication().setDelegate_(sharedDelegate)
