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
part
Created by Jonathan deWerd on 2011-01-26.
"""
from exceptions import NotImplementedError
from PyQt4.QtCore import QObject
from cadnano import app

class Part(QObject):
    def __init__(self, id, *args, **kargs):
        super(Part, self).__init__()
        self._id = id
        self._document = kargs.get('document', None)
        app().p = self
    
    def document(self):
        return self._document
    
    def undoStack(self):
        return self.document().undoStack()
        
    def simpleRep(self, encoder):
        """Returns a representation in terms of simple JSON-encodable types
        or types that implement simpleRep"""
        raise NotImplementedError

    @classmethod
    def fromSimpleRep(cls, rep):
        """Instantiates one of the parent class from the simple
        representation rep"""
        raise NotImplementedError
    def resolveSimpleRepIDs(self,idToObj):
        raise NotImplementedError  # It's up to children to implement serialization

    def id(self):
        """docstring for id"""
        return self._id
