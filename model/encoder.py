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

# See bottom of file for public API
"""
encoder.py
"""
import json
from StringIO import StringIO
from util import *
import re

class Encoder(object):
                              
    simpleTypes = (int, long, float, complex, str, unicode, type(None))
    
    def __init__(self, rootObj):
        self._objects = []
        self._objToIndex = {}  # Maps objects to their index in the _objects array
        self.root = rootObj
        self.indentLevel = 0
        
    def dump(self, io):
        self.io = io
        io.write('{".format":"caDNAno2", ".root":')
        self.encodeObj(self.root, useRef=False)
        io.write(', ".objects":{\n ')
        i = 0
        while i < len(self._objects):
            io.write('%s"%i":'%('\n,' if i>0 else '', i))
            self.encodeObj(self._objects[i], useRef=False)
            i += 1
        io.write('}}')
    # end def
    
    def dumps(self):
        out = StringIO()
        self.dump(out)
        return out.getvalue()
    
    def encodeNum(self, n):
        self.io.write(json.dumps(n))
    # end def
    
    def encodeStr(self, s):
        self.io.write(json.dumps(s))
    # end def
    
    def encodeDict(self, d):
        io = self.io
        io.write('{')
        first = True
        self.indentLevel += 1
        simp = self.approxStrLength(d) < 50
        for k in d:
            if first:
                first = False
            else:
                io.write(',')
            if not simp:
                io.write('\n'+'\t'*self.indentLevel)
            self.encodeObj(k, useRef=True)
            io.write(':')
            self.encodeObj(d[k], useRef=True)
        self.indentLevel -= 1
        io.write('}')
    # end def
    
    def encodeArr(self, a):
        io = self.io
        io.write('[')
        first = True
        self.indentLevel += 1
        simp = self.approxStrLength(a) < 50
        for o in a:
            if first:
                first = False
            else:
                io.write(',')
            if not simp:
                io.write('\n'+'\t'*self.indentLevel)
            self.encodeObj(o, useRef=True)
        self.indentLevel -= 1
        io.write(']')
    # end def

    def encodeObj(self, o, useRef=True):
        io = self.io
        if o==None:
            io.write('null')
            return
        otherEncoder = self.typeToOtherEncoder.get(type(o), None)
        if otherEncoder:
            return otherEncoder(self, o)
        if useRef:
            idno = self._objToIndex.get(o, None)
            if idno == None:
                idno = len(self._objects)
                self._objects.append(o)
                self._objToIndex[o] = idno
            io.write('{".":%i}'%idno)
            return
        d = {}
        o.fillSimpleRep(d)
        self.indentLevel += 1
        io.write('{".class":"%s"'%d[".class"])
        del d[".class"]
        simp = self.approxStrLength(d) < 30
        for k in d:
            io.write(',')
            if not simp:
                io.write('\n'+'\t'*self.indentLevel)
            self.encodeObj(k, useRef=True)
            io.write(':')
            self.encodeObj(d[k], useRef=True)
        self.indentLevel -= 1
        io.write('}')
    # end def
    
    # Class level dictionary
    typeToOtherEncoder = {int:encodeNum, long:encodeNum,\
                          float:encodeNum, complex:encodeNum,\
                          str:encodeStr, dict:encodeDict,\
                          unicode:encodeStr,
                          list:encodeArr, tuple:encodeArr}
    
    # For formatting purposes, it is often convenient to know
    # if an array or dict should be broken over multiple lines
    # or not.
    def approxStrLength(self, item):
        """Rougly estimates the number of characters required
        to print item inline"""
        if isinstance(item, (int, long, float, complex, type(None), type(True), type(False))):
            return 5
        if isinstance(item, (str, unicode)):
            return len(item) + 2
        if isinstance(item, (tuple, list)):
            sublength = 0
            for o in item:
                sublength += self.approxStrLength(o)
            return sublength + 2 + 2*len(item)
        if isinstance(item, dict):
            sublength = 0
            for k,v in item.iteritems():
                sublength += self.approxStrLength(k) + self.approxStrLength(v)
            return sublength + 2 + 3*len(item)
        return 5  # Refs, mostly
    # end def




################## Public API ####################
def encode(root, encodeIntoStream=None):
    """Writes the serialized representation of root
    to encodeIntoStream (by calling .write('str') on
    it many times). If encodeIntoStream is none, returns
    the python string of the serialized representation."""
    e = Encoder(root)
    if encodeIntoStream==None:
        return e.dumps()
    else:
        e.dump(encodeIntoStream)
