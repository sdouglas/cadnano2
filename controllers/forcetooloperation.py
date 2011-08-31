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
util.qtWrapImport('QtCore', globals(), ['QObject'])
from model.xoverstrand import XOverStrand3
from operation import Operation
from model.vbase import VBase

class ForceToolOperation(Operation):
    logger = None #sys.stdout
    def __init__(self, startVBase, undoStack):
        Operation.__init__(self, undoStack)
        self.startVBase = startVBase
        self.strand = XOverStrand3(startVBase)
        self.undoIdxBeforeEverything = undoStack.index()
        self.install3()
        self.undoIdxBeforeInstall5 = undoStack.index()
        self.lastDestination = None  # None = floating
        if self.logger != None:
            self.logger.write('ForceToolOperation.__init__(%s, %s)\n'%\
                                     (startVBase, undoStack))
        self.strand.conn3().isBeingDragged = True

    def updateDestination(self, newVBase5):
        if self.lastDestination == newVBase5 or newVBase5 == self.startVBase:
            return
        self.lastDestination = newVBase5
        self.rewind(self.undoIdxBeforeInstall5)
        self.install5()
        if self.logger != None:
            self.logger.write('ForceToolOperation.updateDestination(%s)\n'%\
                                     newVBase5)

    def updateFloatingDestination(self, newPt5):
        self.lastDestination = None
        self.rewind(self.undoIdxBeforeInstall5)
        self.strand.setPt5(newPt5)
        self.strand.conn3().setVBase(None)
        if self.logger != None:
            self.logger.write('ForceToolOperation.updateFloatingDest(%s)\n'%\
                                     newPt5)

    def install3(self):
        startVBase = self.startVBase
        vstr, idx = startVBase.vStrand(), startVBase.vIndex()
        vstr.addStrand(self.strand,\
                       useUndoStack=True, undoStack=self.undoStack)
        if vstr.drawn5To3():
            vstr.connectStrand(idx - 1, idx,\
                               useUndoStack=True, undoStack=self.undoStack)
        else:
            vstr.connectStrand(idx + 1, idx,\
                               useUndoStack=True, undoStack=self.undoStack)

    def install5(self):
        newVBase5 = self.lastDestination
        self.strand.conn3().setVBase(newVBase5)
        vstr, idx = newVBase5.vStrand(), newVBase5.vIndex()
        vstr.addStrand(self.strand.conn3(),\
                       useUndoStack=True, undoStack=self.undoStack)
        if vstr.drawn5To3():
            vstr.connectStrand(idx, idx + 1,\
                               useUndoStack=True, undoStack=self.undoStack)
        else:
            vstr.connectStrand(idx, idx - 1,\
                               useUndoStack=True, undoStack=self.undoStack)

    def end(self):
        if self.logger != None:
            self.logger.write('ForceToolOperation.end()\n')
        self.rewind(self.undoIdxBeforeEverything)
        if self.lastDestination == None:
            del self.strand
            print "Failed ForceToolOperation.end(): self.lastDestination == None"
            return
        self.undoStack.beginMacro('ForceTool')
        self.install3()
        self.install5()
        self.undoStack.endMacro()
        self.strand.conn3().isBeingDragged = False