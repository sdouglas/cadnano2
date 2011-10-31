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


import util
from itertools import imap
from operator import attrgetter, methodcaller
from collections import defaultdict
import parts.Part
# import Qt stuff into the module namespace with PySide, PyQt4 independence
util.qtWrapImport('QtCore', globals(), ['pyqtSignal', 'QObject'])
util.qtWrapImport('QtGui', globals(), [])

class Assembly(QObject):
    """
    An Assembly is a collection of components, comprised recursively of
    various levels of individual parts and sub-assembly modules.

    The purpose of an Assembly object in Cadnano is to arrange Parts into
    larger groups (which may be connected or constrained in specific ways)
    to facilitate the modeling of more complex designs than a single part.
    """

    def __init__(self, document):
        super(Assembly, self).__init__(document)
        self._document = document
        self._objInstanceList = []   # This is a list of member parts

        # This is a list of ObjectInstances of this
        # particular assembly ONLY
        # an Assembly can not have an ObjectIntanceList that contains itself
        # that would be a circular reference
        self._assemblyInstances = []
    # end def

    ### SIGNALS ###
    assemblyInstanceAddedSignal = pyqtSignal(QObject)  # new oligo
    assemblyDestroyedSignal = pyqtSignal(QObject)  # self

    ### SLOTS ###

    ### METHODS ###
    def undoStack(self):
        return self._document.undoStack()

    def destroy(self):
        # QObject also emits a destroyed() Signal
        self.setParent(None)
        self.deleteLater()
    # end def

    def document(self):
        return self._document
    # end def

    def objects(self):
        for obj in self._objInstanceList:
            yield obj
    # end def

    def instances(self):
        for inst in self._assemblyInstances:
            yield inst
    # end def

    def deepCopy(self):
        """
        Deep copy the assembly by cloning the 

        This leaves alone assemblyInstances, and only

        To finish the job this deepCopy Assembly should be incorporated into
        a new ObjectInstance and therefore an assemblyInstance
        """
        doc = self._document
        asm = Assembly(doc)
        newObjInstList = asm._objInstanceList
        objInstances = self.objects()

        # create a dictionary mapping objects (keys) to lists of 
        # ObjectInstances ([value1, value2])
        # this uniquifies the creation of new Assemblies
        objectDict = defaultdict(list)
        f1 = methodcaller('reference')
        for x in objInstances:
            obj = f1(x)
            objectDict[obj].append(x)
        # end 

        # copy the all the objects
        f2 = methodcaller('deepCopy')
        for key, value in objectDict:
            # create a new object 
            newObj = f2(key)
            # copy all of the instances relevant to this new object
            newInsts = [objInst.deepCopy(newObj, asm) for objInst in value]
            # add these to the list in the assembly
            newObjInstList.extend(newInsts)
            # add Object to the document
            doc.addObject(newObj)
        # end for
        return asm
    # end def

    def addInstance(self, assemblyInstance):
        self._assemblyInstances.extend(assemblyInstance)
    # end def


    ### COMMANDS ###
    