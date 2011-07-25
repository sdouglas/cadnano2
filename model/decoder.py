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
from .dnahoneycombpart import DNAHoneycombPart
from .dnasquarepart import DNASquarePart
from .document import Document
from .virtualhelix import VirtualHelix
from json_io import doc_from_legacy_dict
from exceptions import ImportError

classNameToClassMap = {}
classNameToClassMap['DNAHoneycombPart'] = DNAHoneycombPart
classNameToClassMap['DNASquarePart'] = DNASquarePart
classNameToClassMap['Document'] = Document
classNameToClassMap['VirtualHelix'] = VirtualHelix

class Decoder(object):
    """Has to be a class because it carries state (object ids)"""
    def __init__(self):
        self.idToObj=[]
        self.objsWithDeferredInit=[]
    def decode(self,string):
        try:
            import cjson
            packageObject = cjson.decode(string)
        except ImportError:
            import json
            packageObject = json.loads(string)
        if packageObject.get('.format', None) != 'caDNAno2':
            return doc_from_legacy_dict(packageObject)
        pkObjs = packageObject[".objects"]
        objs = []
        for i in range(len(pkObjs)):
            objs.append(pkObjs[str(i)])
        objs.append(packageObject[".root"])
        for i in range(len(objs)):
            archivedDict = objs[i]
            archivedClassName = archivedDict.get('.class', None)
            if not archivedClassName:
                raise TypeError("trying to decode object from non-object dict (no .class) %s"%archivedDict)
            archivedClass = classNameToClassMap.get(archivedClassName, None)
            if archivedClass==None:
                raise TypeError("I don't know how to unarchive a %s; it isn't in my classNameToClassMap."%archivedClassName)
            # The dict is incomplete because obj refs haven't been resolved
            # to point at objects yet; all objects must exist before we can reliably
            # fetch the object that an obj ref (entry like {".":123}) points to!
            newObj = archivedClass(incompleteArchivedDict=archivedDict)
            self.objsWithDeferredInit.append((archivedClass, archivedDict, newObj))
            self.idToObj.append(newObj)
        self.objsWithDeferredInit.sort(key=lambda x: x[0].finishInitPriority)
        
        # and a map function speeds up by 50%
        def refResolve((objClass, objDict, obj)):
            completeArchivedDict = self.resolveRefsIn(objDict)
            # This time the argument passed is called completeArchivedDict because
            # refs have been resolved by resolveRefsIn
            obj.finishInitWithArchivedDict(completeArchivedDict)
        map(refResolve, self.objsWithDeferredInit)
        
        return self.idToObj[-1]  # The root object
            
    def resolveRefsIn(self, obj):
        if isinstance(obj, (int, long, float, complex, str, unicode)):
            return obj
        if isinstance(obj, dict):
            if len(obj)==1 and obj.get(".", None)!=None:
                return self.idToObj[obj["."]]
            # ret = {}
            # for k,v in obj.iteritems():
            #     ret[k] = self.resolveRefsIn(v)
            # return ret
  
            # using map on to do the above
            dicToList = lambda dic: list((k, v) for (k, v) in dic.iteritems())
            resolveRefsInList = lambda (k,v): (k, self.resolveRefsIn(v))
            return dict(map(resolveRefsInList, dicToList(obj)))
        if isinstance(obj, (list, tuple)):
            # ret = []
            # for v in obj:
            #     ret.append(self.resolveRefsIn(v))
            # return ret
            return map(self.resolveRefsIn, obj)
        raise TypeError("Cannot resolve refs in (%s)%s; unfamiliar type"%(type(obj),obj))
                
    
    class DecodingStub():
        def __init__(self, idnum):
            self.idnum = idnum
        def initWithDecoder(self, dec):
            pass


def decode(str):
    d = Decoder()
    return d.decode(str)
