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
    logger = sys.stdout
    def __init__(self, startVBase, useUndoStack=True, undoStack=None):
        Operation.__init__(self, useUndoStack, undoStack)
        self.startVBase = startVBase
        self.useUndoStack = useUndoStack
        self.undoStack = undoStack
        self.strand = XOverStrand3(startVBase)
        startVBase.vStrand().addStrand(self.strand,\
                                       useUndoStack=self.useUndoStack,\
                                       undoStack=undoStack)
        if useUndoStack:
            self.undoIdxBeforeInstall = undoStack.index()
        self.lastDestination = None  # None = floating
        if self.logger != None:
            self.logger.write('ForceToolOperation.__init__(%s, %s)\n'%\
                                     (startVBase, undoStack))

    def updateDestination(self, newVBase5):
        if self.lastDestination == newVBase5:
            return
        self.lastDestination = newVBase5
        if self.useUndoStack:
            self.rewind(self.undoIdxBeforeInstall)
        self.strand.conn3().setVBase(newVBase5)
        newVBase5.vStrand().addStrand(self.strand.conn3(),\
                                      useUndoStack=self.useUndoStack,\
                                      undoStack=self.undoStack)
        if self.logger != None:
            self.logger.write('ForceToolOperation.updateDestination(%s)\n'%\
                                     newVBase5)

    def updateFloatingDestination(self, newPt5):
        self.lastDestination = None
        if self.useUndoStack:
            self.rewind(self.undoIdxBeforeInstall)
        self.strand.setPt5(newPt5)
        self.strand.conn3().setVBase(None)
        if self.logger != None:
            self.logger.write('ForceToolOperation.updateFloatingDest(%s)\n'%\
                                     newPt5)

    def end(self):
        if self.logger != None:
            self.logger.write('ForceToolOperation.end()\n')
