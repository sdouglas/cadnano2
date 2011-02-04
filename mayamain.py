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
paths = ['/Users/shawn/Desktop/cadnano2',\
         '/Users/nick/oldnick/python_scripts/cadnano/cadnano2']
for p in paths:
    if p not in sys.path:
        sys.path.append(p)
# end if

def getDefaultModules():
    """
    gets a list modules that are 
    installed Maya or Qt modules
    The list was compiled through printing and additional trial
    and error to add some additional modules at the bottom of 
    the list
    
    Could do this with sets, but I failed the first try so forget it
    """
    f = open(pathadder+'/mayadefaultmodules.txt','r')
    defaultmodules = {}
    for line in f:
        key = line.rstrip('\n')
        defaultmodules[key] = True
    #end for
    f.close()
    del(f)
    return defaultmodules
# end def

def removeModules(moddict):
    """
    removes modules related to the program but not 
    installed Maya or Qt modules
    """
    for key in sys.modules.keys():
        if not moddict.has_key(key):
            try:
                del(sys.modules[key])
                print "module %s deleted" % key
            except:
                print "module %s doesn't exist" % key
        # end if
    # end for
# end def


"""
removes a list of modules created for this program
This allows reloading the program in Maya without having to restart
"""
defmods = getDefaultModules()
removeModules(defmods)

# begin program
import cadnanomaya
caDNAno = cadnanomaya.caDNAno

#import pymel.core as pm
caDNAno()

