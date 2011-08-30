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

import util, sys
from model.strand import Strand
util.qtWrapImport('QtCore', globals(), ['QObject', 'pyqtSignal'] )
util.qtWrapImport('QtGui', globals(), ['QUndoCommand'] )
nextStrandDebugIdentifier = 0

class XOverStrand3(Strand):
    """ Covers one base on one strand. This base exposes its 5' end to other
    bases on the strand and has a 3' covalent bond to a base on another
    strand represented by a XOverStrand5 object. In interactions that consider
    the crossover as a whole (drawing the line from one PathHelix to another,
    for instance) this strand takes responsibility for the crossover as a
    whole. """
    logger = None
    kind = 'xovr3'
    def __init__(self, vBase):
        """ In order to create a XOverStrand3 / XOverStrand5 pair, first create
        the XOverStrand3. Thin simply call xover3.conn3() to get the
        corresponding XOverStrand5. """
        Strand.__init__(self)
        self._vBase = vBase
        self._pt5 = None  # Temporary destination (in PHG coords)
        partner = XOverStrand5(vBase=None)
        Strand.setConn3(self, partner)
        self.isBeingDeleted = False
    def __repr__(self):
        return "XOverStrand3(%s)"%(self.vBase())
    def numBases(self):
        return 1
    def idxs(self):
        idx = self.vBase().vIndex()
        return (idx, idx + 1)
    def exposedEndsAt(self, vBase):
        if vBase == self._vBase:
            return '5L' if vBase.drawn5To3() else '5R'
        return ''
    def vStrand(self):
        """ Since the XOverStrand only represents the 3' end of the crossover
        in its role as a Strand, """
        return self.vBase().vStrand()
        
    def setConn3(self, newBase):
        raise TypeError("A XOverStrand3's 3' end is always connected to its "\
                        "corresponding XOverStrand5, possibly on a different"\
                        " strand")
    def isFloating(self):
        return self.conn3().isFloating()

    def vBase(self):
        return self._vBase
    def setVBase(self, newBase, undoStack=None):
        com = XOverStrand3.SetVBaseCommand(self, newBase)
        if undoStack != None: undoStack.push(com)
        else:                 com.redo()
    class SetVBaseCommand(QUndoCommand):
        def __init__(self, strand, newVBase):
            QUndoCommand.__init__(self)
            self.strand = strand
            self.newVBase = newVBase
            self.oldVBase = strand.vBase
        def redo(self):
            strand = self.strand
            strand._vBase = self.newVBase
            strand.didMove.emit(strand)
        def undo(self):
            strand = self.strand
            strand._vBase = self.oldVBase
            strand.didMove.emit(strand)

    def pt5(self):
        """ A floating crossover's destination. A floating crossover is a
        crossover which has a defined vBase3 but has xo.vBase5()==None, created
        during force-crossover creation where the 5' end tracks the mouse until
        it is placed over a valid vBase). This is the point under the mouse in
        PathHelixGroup's coordinates. """
        return self._pt5
    def setPt5(self, newPt5):
        self._pt5 = newPt5
        self.didMove.emit(self)
    def removalWillBePushed(self, useUndoStack, undoStack):
        partner = self.conn3()
        partnerXoverVBase = partner.vBase()
        if partnerXoverVBase == None or\
           self.conn3().isBeingDeleted or self.isBeingDeleted:
            return None
        if self.conn5() != None:
            self.setConn5(None, useUndoStack, undoStack)
        if self.conn3().conn3() != None:
            self.conn3().setConn3(None, useUndoStack, undoStack)
        self.isBeingDeleted = True
        partnerIdx = partnerXoverVBase.vIndex()
        partnerXoverVBase.vStrand().clearStrand(partnerIdx, partnerIdx + 1,\
                                                useUndoStack, undoStack)
        self.isBeingDeleted = False

class XOverStrand5(Strand):
    """ The partner of a XOverStrand3. To create a XOverStrand5 that is
    properly connected to a XOverStrand3, first create the XOverStrand3 and
    then call xover3.conn3() to get the corresponding XOverStrand5 object. """
    kind = 'xovr5'
    def __init__(self, vBase):
        Strand.__init__(self)
        self._vBase = vBase
        self.isBeingDeleted = False
    def __repr__(self):
        return "XOverStrand5(%s)"%(self.vBase())
    numBases = XOverStrand3.__dict__['numBases']  # The great method heist
    idxs = XOverStrand3.__dict__['idxs']
    vStrand = XOverStrand3.__dict__['vStrand']
    vBase = XOverStrand3.__dict__['vBase']
    setVBase = XOverStrand3.__dict__['setVBase']
    def exposedEndsAt(self, vBase):
        if vBase == self._vBase:
            return 'R3' if self.vStrand().drawn5To3() else 'L3'
        return ''
    def setConn5(self, newConn):
        raise TypeError("The 5' end of the 5' base of a crossover is"\
                        "already occupied by definition")
    # end def

    def isFloating(self):
        if self._vBase == None:
            return True
        else: 
            return False

    def removalWillBePushed(self, useUndoStack, undoStack):
        partnerXoverVBase = self.conn5().vBase()
        if partnerXoverVBase == None or\
           self.conn5().isBeingDeleted or self.isBeingDeleted:
            return None
        if self.conn3() != None:
            self.setConn3(None, useUndoStack, undoStack)
        if self.conn5().conn5() != None:
            self.conn5().setConn5(None, useUndoStack, undoStack)
        self.isBeingDeleted = True
        partnerIdx = partnerXoverVBase.vIndex()
        partnerXoverVBase.vStrand().clearStrand(partnerIdx, partnerIdx + 1,\
                                                useUndoStack, undoStack)
        self.isBeingDeleted = False