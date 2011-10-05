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
import util
util.qtWrapImport('QtCore', globals(), ['QObject', 'pyqtSignal'] )

class Mom:
    class __impl(QObject):
        """ Implementation of the singleton interface """
        preDecoratorSelectedSignal = pyqtSignal(object, int)
        def myId(self):
            return id(self)

    # storage for the instance reference
    __instance = None
    # uses DNACylinderShape as as the key, stores strand objects
    mayaToCn = {}
    # uses strand objects as the key, stores a list of maya nodes
    cnToMaya = {}
    # uses stapleModIndicatorMesh% objects as the key,
    # stores a objec with data (solidHelix object, baseNumber, strand object)
    stapleModToSolidHelix = {}

    def staplePreDecoratorSelected(self, name):
        if self.stapleModToSolidHelix.has_key(name):
            modData = self.stapleModToSolidHelix[name]
            self.__instance.preDecoratorSelectedSignal.emit(modData[2], modData[1])

    def removeStapleModMapping(self, id):
        key1 = "stapleModIndicatorMesh%s" % id
        key2 = "stapleModIndicatorTransform%s" % id
        if self.stapleModToSolidHelix.has_key(key1):
            del self.stapleModToSolidHelix[key1]
        if self.stapleModToSolidHelix.has_key(key2):
            del self.stapleModToSolidHelix[key2]

    def removeIDMapping(self, id, strand):
        key1 = "DNACylinderShape%s" % id
        key2 = "HalfCylinderHelixNode%s" % id
        if self.mayaToCn.has_key(key1):
            del self.mayaToCn[key1]
        if self.mayaToCn.has_key(key2):
            del self.mayaToCn[key2]
        if self.cnToMaya.has_key(strand):
            del self.cnToMaya[strand]
    
    def __init__(self):
        
        if Mom.__instance is None:
            Mom.__instance = Mom.__impl()
            #super(Mom, self).__init__()

        self.__dict__['_Mom__instance'] = Mom.__instance

    def __getattr__(self, attr):
        return getattr(self.__instance, attr)

    def __setattr__(self, attr, value):
        return setattr(self.__instance, attr, value)
