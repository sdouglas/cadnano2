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

#from model.document import Document
#from model.encoder import encode
#from model.decoder import decode
#d=Document()
#s=encode(d)
#dd=decode(s)
#s==encode(dd)

"""
encoder.py
"""
import json
from StringIO import StringIO

class Encoder(json.JSONEncoder):
    def __init__(self):
        super(Encoder,self).__init__()
        self._objects = []
        self._objToIndex = {}  # Maps objects to their index in the _objects array
        
    def dump(self, io):
        io.write('{".format":"caDNAno2",.root=')
            
    def dumps(self):
        out = StringIO()
        self.dump(out)
        return out.getvalue()
        
    def default(self, obj):
        # If you just hit the assert below,
        # something (probably a circular strong reference) is misdesigned.
        # Use weak references (storing IDs not objects) to break the loop.
        assert(obj not in self._alreadyEncoded)      
        assert(self._alreadyEncoded.add(obj) == None)
        if hasattr(obj, "simpleRep"):
            sr = obj.simpleRep(self)
            if obj in self._objToId:
                sr = {'.id':self._objToId[obj]}
            else:
                sr['.id'] = self._nextID
                self._nextID += 1
            return sr
        else:
            return json.JSONEncoder.default(self, obj)

    def idForObject(obj):
        if obj in self._objToId:
            return self._objToId[obj]
        else:
            self._nextID += 1
            return self._nextID-1


def encode(root):
    return json.dumps(root, cls=Encoder)
