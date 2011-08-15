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

util.qtWrapImport('QtCore', globals(), ['QObject'])
from model.normalstrand import NormalStrand
from operation import Operation

class PencilToolOperation(Operation):
    """ Handles interactive strand creation / destruction in the manner of the
    pencil tool """
    def __init__(self, startVBase, undoStack):
        """ Begin a session of pencil-tool interaction """
        Operation.__init__(self)
        self.newStrand = NormalStrand(startVBase, startVBase)
        self.startVBase = startVBase
        self.newStrandInVfbPool = False
        self.updateOperationWithDestination(startVBase)

    def updateOperationWithDestination(self, newDestVBase):
        """ Looks at self.startVBase and newDestVBase then calls the appropriate
        actionWhatever method on self. """
        dragStartBase, dragEndBase = self.startVBase, newDestVBase
        dragStartExposedEnds = dragStartBase.exposedEnds()
        dragStartStrand = dragStartBase.strand()
        dragEndExposedEnds = dragEndBase.exposedEnds()
        dragEndStrand = dragEndBase.strand()
        vStrand = dragStartBase.vStrand
        
        if dragStartBase < dragEndBase:
            leftBase, rightBase = dragStartBase, dragEndBase
            leftExposedEnds = dragStartExposedEnds
            rightExposedEnds = dragEndExposedEnds
            lStrand, rStrand = dragStartStrand, dragEndStrand
            dragDirection = 1  # To the right
            dragStartEndpt, dragEndEndpt = 'R', 'L'
        else:
            leftBase, rightBase = dragEndBase, dragStartBase
            leftExposedEnds = dragEndExposedEnds
            rightExposedEnds = dragStartExposedEnds
            lStrand, rStrand = dragEndStrand, dragStartStrand
            dragDirection = -1  # To the left
            dragStartEndpt, dragEndEndpt = 'L', 'R'
        numBases = rightBase.vIndex - leftBase.vIndex + 1  # >= 2
        draggingFromAnEndpt = bool(dragStartExposedEnds)
        draggingToAnEndpt = bool(dragEndExposedEnds)
        draggingFromInsideAStrand = not draggingFromAnEndpt and\
                                    dragStartStrand != None

        if draggingFromAnEndpt:
            if dragStartBase == dragEndBase:
                return self.actionNone()
            if dragStartBase == dragStartStrand.vBaseL:
                if dragEndBase < dragStartStrand.vBaseR:
                    if hasattr(dragStartStrand, 'changeRange'):
                        self.actionResizeStrand(dragStartStrand,\
                                                dragEndBase,\
                                                dragStartStrand.vBaseR)
                    else:
                        self.actionAddStrand(None,\
                                             dragEndBase,\
                                             dragStartStrand.vBaseR,\
                                             dragStartStrand.connR())
                else:
                    self.actionClearRange(dragStartBase.vIndex,
                                          dragEndBase.vIndex)
            elif dragStartBase == dragStartStrand.vBaseR:
                if dragEndBase > dragStartStrand.vBaseL:
                    if hasattr(dragStartStrand, 'changeRange'):
                        self.actionResizeStrand(dragStartStrand,\
                                                dragStartStrand.vBaseL,\
                                                dragEndBase)
                    else:
                        self.actionAddStrand(dragStartStrand.connR(),\
                                             dragStartStrand.vBaseL,\
                                             dragEndBase)
                else:
                    self.actionClearRange(dragEndBase.vIndex + 1,\
                                          dragStartBase.vIndex + 1)
            else:
                assert(False)  # We aren't dragging from an endpt after all?
        elif draggingFromInsideAStrand:
            if dragStartBase == dragEndBase:
                self.actionClearRange
        

    def putNewStrandInVfbPoolIfNecessary(self):
        if not self.newStrandInVfbPool:
            self.startVBase.part().addVfbStrands([self.newStrand])
            self.newStrandInVfbPool

    def removeNewStrandFromVfbPoolIfNecessary(self):
        if self.newStrandInVfbPool:
            self.startVBase.part().removeVfbStrands([self.newStrand])
            self.newStrandInVfbPool = False

    def actionNone(self):
        self.rewind()
        self.removeNewStrandFromVfbPoolIfNecessary()

    def actionAddStrand(self, lConnection, startBase, endBase, rConnection):
        self.rewind()
        self.newStrand.changeRange()
        self.putNewStrandInVfbPoolIfNecessary()

    def actionJustConnect(self, lStrand, rStrand):
        """ Just connect the right exposed end of lStrand to the left exposed
        end of rStrand """
        lStrand.setConnR(rStrand, useUndoStack=True, undoStack=self.undoStack)

    def actionResizeStrand(self, strand, newL, newR):
        strand.changeRange(newL, newR, self.undoStack)

    def actionClearRange(self, firstIdx, afterLastIdx):
        pass