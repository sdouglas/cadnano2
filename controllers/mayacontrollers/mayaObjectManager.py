###############################################################################
#  
# Copyright 2011 Autodesk, Inc.  All rights reserved.
#  
# The MIT License
#  
# Permission is hereby granted, free of charge, to any person obtaining a copy of
# this software and associated documentation files ( the "Software" ), to deal in
# the Software without restriction, including without limitation the rights to
# use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies
# of the Software, and to permit persons to whom the Software is furnished to do
# so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
# 
###############################################################################

"""
mayaObjectManager.py
Created by Alex Tessier on 2011-08
A singleton manager for tracking maya to cn and reverse
lookups
"""
from cadnano import app
import maya.cmds as cmds
import util
util.qtWrapImport('QtCore', globals(), ['QObject', 'pyqtSignal'] )

class Mom:
    class __impl(QObject):
        """ Implementation of the singleton interface """
        #preDecoratorSelectedSignal = pyqtSignal(object)
        strandCount = 0
        selectionCountCache = 0
        def myId(self):
            return id(self)

    # storage for the instance reference
    __instance = None
    # uses DNACylinderShape as as the key, stores strand objects
    mayaToCn = {}
    # uses strand objects as the key, stores a list of maya nodes
    cnToMaya = {}
    # uses stapleModIndicatorMesh% objects as the key,
    # stores a objec with data (virualHelixItem object, baseNumber, strand object)
    decoratorToVirtualHelixItem = {}
    # uses strand object as the key, stores stand id
    idStrandMapping = {}
    
    # MayaNames
    helixTransformName  = "DNAShapeTransform"
    helixNodeName       = "HalfCylinderHelixNode"
    helixMeshName       = "DNACylinderShape"
    helixShaderName     = "DNAStrandShader"
    
    decoratorTransformName  = "stapleDecoratorTransform"
    decoratorNodeName       = "spStapleModIndicator"
    decoratorMeshName       = "stapleModIndicatorMesh"
    decoratorShaderName     = "stapleModeIndicatorShader"
    
    def staplePreDecoratorSelected(self, listNames):
        selectionList = []
        for name in listNames:
            if self.decoratorToVirtualHelixItem.has_key(name):
                (virualHelixItem, baseIdx, strand) = \
                                        self.decoratorToVirtualHelixItem[name]
                selectionList.append((virualHelixItem.row(),
                                                virualHelixItem.col(),
                                                baseIdx))
        if len(selectionList) == 0 and self.__instance.selectionCountCache == 0:
            # a dumb cache check to prevent deselection to be brotcaseted too
            # many times, but could couse problems
            return

        # XXX - [SB] we want to only send the signal to "active part" but
        # not sure how to get that
        for doc in app().documentControllers:
            if doc.win.actionModify.isChecked():
                for partItem in doc.win.solidroot.partItems():
                    partModel = partItem.part()
                    partModel.selectPreDecorator(selectionList)
        self.__instance.selectionCountCache = len(selectionList)

    def removeDecoratorMapping(self, id):
        key1 = "%s%s" % (self.decoratorMeshName, id)
        key2 = "%s%s" % (self.decoratorTransformName, id)
        if self.decoratorToVirtualHelixItem.has_key(key1):
            del self.decoratorToVirtualHelixItem[key1]
        if self.decoratorToVirtualHelixItem.has_key(key2):
            del self.decoratorToVirtualHelixItem[key2]

    def removeIDMapping(self, id, strand):
        key1 = "%s%s" % (self.helixMeshName, id)
        key2 = "%s%s" % (self.helixNodeName, id)
        if self.mayaToCn.has_key(key1):
            del self.mayaToCn[key1]
        if self.mayaToCn.has_key(key2):
            del self.mayaToCn[key2]
        self.deleteStrandMayaID(strand)
    
    def strandMayaID(self, strand):
        if(strand in self.idStrandMapping):
            return self.idStrandMapping[strand]
        else:
            self.__instance.strandCount += 1
            # XXX [SB+AT] NOT THREAD SAFE
            while cmds.objExists("%s%s" %
                                 (self.helixTransformName, self.__instance.strandCount)):
                self.__instance.strandCount += 1
            val = "%d" % self.strandCount
            self.idStrandMapping[strand] = val
            return val

    def deleteStrandMayaID(self, strand):
        if self.cnToMaya.has_key(strand):
            del self.cnToMaya[strand]
        if self.idStrandMapping.has_key(strand):
            del self.idStrandMapping[strand]

    def __init__(self):
        if Mom.__instance is None:
            Mom.__instance = Mom.__impl()
            #super(Mom, self).__init__()
        self.__dict__['_Mom__instance'] = Mom.__instance

    def __getattr__(self, attr):
        return getattr(self.__instance, attr)

    def __setattr__(self, attr, value):
        return setattr(self.__instance, attr, value)
