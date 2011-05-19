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
virtualhelix.py
Created by Jonathan deWerd.
"""
from json import dumps

class Encoder:
    def __init__(self, io):
        self.indentLevel = 0
        self.spacing = True
        self.io = io
        self.deferredObjects = []
        self.objToDeferredIdMap = {}
    
    def writeRootObject(self, rootObject):
        io.write('{".format":"caDNAno2",.root=')
        self.writeObject(rootObject)
        io.write('\n,.objs=')
        self.writeObject(self.deferredObjects)
        io.write('}')
        
    
    def writeObject(obj):
        if type(obj)=='list' or type(obj)=='tuple':
            self.io.write('[')
            self.indentLevel += 1
            first = True
            for o in obj:
                if first:
                    first = False
                else
                    self.io.write(',')
                if self.spacing:
                    self.io.write('\n'+'  '*self.indentLevel)
                self.writeObject(o, io, self.indentLevel)
            self.indentLevel -= 1
            io.write(']')
        elif type(obj)==type({}):
            self.io.write('{')
            indentLevel += 1
            first = True
            for k in obj:
                if first:
                    first = False
                else
                    self.io.write(",")
                if self.spacing:
                    self.io.write('\n'+'\t'*self.indentLevel)
                self.writeObject(k)
                self.io.write(':')
                self.writeObject(obj[k])
            indentLevel -= 1
            self.io.write('}')
        elif type(obj) in ('str', 'int', 'float', 'long'):
            self.io.write(dumps(obj))
        else:
            objId = self.objToDeferredIdMap.get(obj,-1)
            if objId == -1:
                objId = len(self.deferredObjects)
                self.deferredObjects.append(obj)
            self.io.write('{".id=":'+str()+'}')
            
            
            

class Serializable:
    # In order to conform to Serializable, the receiver must support creating
    # an uninitialized instance through the following mechanism:
    #
    # emptyInstance = SerializableClass(deferInit=True)
    #
    # The idea is that a DAG of objects gets unpacked (but the objects have their
    # init routine deferred). Then the "real" init, initFromSimpleRep, is called,
    # and the chicken/egg problem with cycles of objects is avoided because other
    # objects already exist (though they may not be valid <=> actually initialized)
    
    def simpleRep(self, encoder):
        """Returns a representation of the receiver as a dictionary containing
        1) a .class:"ClassName" entry linking to a class that can handle deserialization
        2) only numbers, strings, descendents of Serializable, arrays, and
        dictionaries (recursively) """
        raise NotImplementedError

    def initFromSimpleRep(self, decoder):
        """Instantiates one of the parent class from the simple
        representation rep. Calls super if necessary."""
        raise NotImplementedError


    ############################# Internals ############################
    def writeJson(self, io):
        e = Encoder()
        e.writeRootObject(self)
        del e
        
        
    
    def writeObject(self, obj, io, indentLevel=0, spacing=True):
        if type(obj)=='list' or type(obj)=='tuple':
            io.write('[')
            indentLevel += 1
            for o in obj:
                if spacing:
                    io.write('  '*indentLevel)
                self.writeObject(o, io, indentLevel)
                io.write(',')
            io.write(']')
        if type(obj)==type({}):
            io.write('{')
            indentLevel += 1
            for k in obj:
                writeObject()
            io.write('}')
            
        
    def jsonRep(self):
        out = StringIO()
        self.writeJson(out)
        return out.getvalue()
    