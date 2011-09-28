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
from model.enum import StrandType

util.qtWrapImport('QtCore', globals(), ['pyqtSignal', 'QObject'])
util.qtWrapImport('QtGui', globals(), [ 'QUndoCommand', 'QUndoStack'])


class Part(QObject):
    """
    A Part is a group of VirtualHelix items that are on the same lattice.
    Parts are the model component that most directly corresponds to a
    DNA origami design.
    """

    _step = 21  # this is the period of the part lattice

    def __init__(self, document):
        """
        Parts are always parented to the document.
        Parts know about their oligos, and the internal geometry of a part
        Copying a part recursively copies all elements in a part:
            VirtualHelices, Strands, etc

        PartInstances are parented to either the document or an assembly
        PartInstances know global position of the part
        Copying a PartInstance only creates a new PartInstance with the same
        Part(), with a mutable parent and position field.
        """
        super(Part, self).__init__(document)
        self._document = document
        self._partInstances = []    # This is a list of ObjectInstances
        self._oligos = {}
        self._virtualHelices = {}   # should this be a list or a dictionary?  I think dictionary
        self._bounds = (0, 2*self._step)
    # end def

    ### SIGNALS ###
    partParentChangedSignal = pyqtSignal(QObject)  # self
    partInstanceAddedSignal = pyqtSignal(QObject)  # self
    partDestroyedSignal = pyqtSignal(QObject)  # self
    sequenceClearedSignal = pyqtSignal(QObject)  # self

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

    def setDocument(self, document):
        """docstring for setDocument"""
        self._document = document

    def oligos(self):
        return self._oligos

    def addOligo(selg, oligo):
        self._oligos[oligo] = True

    def removeOligo(self, oligo):
        self._oligo[oligo] = False
        self.destroyOligo(oligo)

    def destroyOligo(self, oligo):
        del self._oligo[oligo]

    def bounds(self):
        """Return the latice indice bounds relative to the origin."""
        return self._bounds
    # end def
    
    def newPart(self):
        """
        reimplement this method for each type of Part
        """
        return Part(self._document)
    # end def
    
    def shallowCopy(self):
        part = self.newPart()
        part._virtualHelices = dict(self._virtualHelices)
        part._oligos = dict(self._oligos)
        part._bounds = (self._bounds[0], self._bounds[1])
        part._partInstances = list(self._partInstances)
        return part
    # end def
    
    def deepCopy(self):
        """
        1) Create a new part
        2) copy the VirtualHelices
        3) Now you need to map the ORIGINALs Oligos onto the COPY's Oligos
        To do this you can for each Oligo in the ORIGINAL
            a) get the strand5p() of the ORIGINAL
            b) get the corresponding strand5p() in the COPY based on
                i) lookup the hash idNum of the ORIGINAL strand5p() VirtualHelix
                ii) get the StrandSet() that you created in Step 2 for the 
                StrandType of the original using the hash idNum
        """
        # 1) new part
        part = self.newPart()
        for key, vhelix in self._virtualHelices:
            # 2) Copy VirtualHelix 
            part._virtualHelices[key] = vhelix.deepCopy(part)
        # end for
        # 3) Copy oligos
        for oligo, val in self._oligos:
            strandGenerator = oligo.strand5p().generator3pStrand()
            strandType = oligo.strand5p().strandType()
            newOligo = oligo.deepCopy(part)
            lastStrand = None
            for strand in strandGenerator:
                idNum = strand.virtualHelix().number()
                newVHelix = part._virtualHelices[idNum]
                newStrandSet = newVHelix().getStrand(strandType)
                newStrand = strand.deepCopy(newStrandSet, newOligo)
                if lastStrand:
                    lastStrand.set3pConnection(newStrand)
                else: 
                    # set the first condition
                    newOligo.setStrand5p(newStrand)
                newStrand.set5pConnection(lastStrand)
                newStrandSet.addStrand(newStrand)
                lastStrand = newStrand
            # end for
            # check loop condition
            if oligo.isLoop():
                s5p = newOligo.strand5p()
                lastStrand.set3pconnection(s5p)
                s5p.set5pconnection(lastStrand)
            # add to part
            oligo.add()
        # end for
        return part
    # end def
    
    ### COMMANDS ###
    