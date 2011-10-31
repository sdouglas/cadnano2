#!/usr/bin/env python
# encoding: utf-8

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
main.py

Created by Shawn Douglas on 2010-09-26.
"""

import sys
import os
sys.path.insert(0, '.')
argv = [s for s in sys.argv]

if "-t" in argv:
    os.environ['CADNANO_IGNORE_ENV_VARS_EXCEPT_FOR_ME'] = 'YES'
from cadnano import app as getAppInstance

if "-p" not in sys.argv:
    # Having our own NSApplication doesn't play nice with
    # collecting profile data.
    try:
        # If we are in Mac OS X, initialize Mac OS X specific stuff
        supportsPythonObjCBridge = False
        import objc
        supportsPythonObjCBridge = True
    except Exception, e:
        print e
    if supportsPythonObjCBridge:
        from osx.CNApplicationDelegate import sharedDelegate as appDelegate
    # else:
    #     from applicationdelegate import ApplicationDelegate


app = getAppInstance()
app.initGui()
if __name__ == '__main__':
    if "-p" in sys.argv:
        print "Collecting profile data into cadnano.profile"
        import cProfile
        cProfile.run('app.exec_()', 'cadnano.profile')
        print "Done collecting profile data. Use -P to print it out."
        exit()
    elif "-P" in sys.argv:
        from pstats import Stats
        s = Stats('cadnano.profile')
        print "Internal Time Top 10:"
        s.sort_stats('cumulative').print_stats(10)
        print ""
        print "Total Time Top 10:"
        s.sort_stats('time').print_stats(10)
        exit()
    elif "-t" in sys.argv:
        from tests.runall import main as runTests
        runTests(useXMLRunner=False)
        exit()
    app.exec_()
