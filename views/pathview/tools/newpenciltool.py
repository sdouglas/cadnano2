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
penciltool
"""

import util
from abstractpathtool import AbstractPathTool
from controllers.penciltooloperation import PencilToolOperation
util.qtWrapImport('QtCore', globals(), ['Qt'])
util.qtWrapImport('QtGui', globals(), [ 'QGraphicsItem', 'QBrush', 'QFont',
                                        'QGraphicsSimpleTextItem', 'QPen',\
                                        'QPolygonF', 'QPainterPath'])

class NewPencilTool(AbstractPathTool):
    """PencilTool allows for creation of new staple or scaffold strands
    by clicking and dragging on empty bases."""
    # And we actually use those PathHelixGroup events
    mouseMovePathHelixGroupUnused = False
    mouseReleasePathHelixGroupUnused = False
    mousePressPathHelixGroupUnused = False
    
    def __init__(self, controller):
        super(NewPencilTool, self).__init__(controller)
        self.currentOperation = None

    def mousePressPathHelix(self, pathHelix, event):
        draggingForceCrossover = False
        if pathHelix:
            phg = pathHelix.pathHelixGroup()
            draggingForceCrossover = phg.dragging
        if event.button() & Qt.RightButton or draggingForceCrossover:
            print "No force crossover support yet"
            # ForceTool.mousePressPathHelix(self, pathHelix, event)
        elif event.buttons() & Qt.LeftButton:
            if self.currentOperation != None:
                self.currentOperation.end()
            dest = pathHelix.vBaseAtPoint(event.pos())
            undoStack = pathHelix.vhelix().undoStack()
            self.currentOperation = PencilToolOperation(dest, undoStack)

    def mouseMovePathHelix(self, pathHelix, event):
        if self.currentOperation == None:
            return
        dest = pathHelix.vBaseAtPoint(event.pos())
        dest.vStrand = self.currentOperation.startVBase.vStrand
        self.currentOperation.updateOperationWithDestination(dest)

    def mouseReleasePathHelix(self, pathHelix, event):
        if self.currentOperation != None:
            self.currentOperation.end()
            self.currentOperation = None
