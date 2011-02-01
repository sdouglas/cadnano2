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
decoder
Created by Jonathan deWerd on 2011-01-26.
"""
import json
from .dnapart import DNAPart
from .document import Document
from .partinstance import PartInstance

classNameToClassMap = {}
classNameToClassMap['DNAPart'] = DNAPart
classNameToClassMap['CADNanoDocument'] = Document
classNameToClassMap['PartInstance'] = PartInstance

class Decoder(object):
    """Has to be a class because it carries state (object ids)"""
    def __init__(self):
        self.idToObj={}
        self.objsWthWeakRefsToResolve=[]
    def decode(self,str):
        rootObj = json.loads(str, object_hook=lambda x: self.decodeObj(self,x))
        for o in self.objsWthWeakRefsToResolve:
            o.resolveSimpleRepIDs(self.idToObj)
    def decodeObj(self,dct):
        if '.class' in dct:
            obj = classNameToClassMap[dct['.class']].fromSimpleRep(dct)
            objsWthWeakRefsToResolve.append(obj)
            if '.id' in dct:
                ii = dct['id']
                assert(ii not in self.idToObj)
                self.idToObj[dct['.id']] = obj
        return dct


def decode(str):
    d = Decoder()
    return d.decode(str)
