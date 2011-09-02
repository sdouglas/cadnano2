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
import sys
from abstractpathtool import AbstractPathTool
from controllers.penciltooloperation import PencilToolOperation
from controllers.forcetooloperation import ForceToolOperation

util.qtWrapImport('QtCore', globals(), ['Qt', 'QPointF'])
util.qtWrapImport('QtGui', globals(), [ 'QGraphicsItem', 'QBrush', 'QFont',
                                        'QGraphicsSimpleTextItem', 'QPen',\
                                        'QPolygonF', 'QPainterPath'])

class NewPencilTool(AbstractPathTool):
    """
    PencilTool allows for creation of new staple or scaffold strands
    by clicking and dragging on empty bases.
    """
    # And we actually use those PathHelixGroup events
    mouseMovePathHelixGroupUnused = False
    mouseReleasePathHelixGroupUnused = False
    mousePressPathHelixGroupUnused = False
    logger = None

    def __init__(self, controller):
        super(NewPencilTool, self).__init__(controller)
        self.currentOperation = None

    def mousePressPathHelix(self, pathHelix, event):
        pathHelix.scene().views()[0].addToPressList(pathHelix)
        forceToolActive = isinstance(self.currentOperation, ForceToolOperation)
        rightClick = event.button() & Qt.RightButton
        leftClick = event.buttons() & Qt.LeftButton
        pos = pathHelix.mapFromScene(event.scenePos())
        if forceToolActive:
            if self.logger: self.logger.write("mousePressPathHelix>ForceEnd\n")
            self.currentOperation.end()
            self.currentOperation = None
        elif rightClick:
            if self.logger: self.logger.write("mousePressPathHelix>Force\n")
            dest = pathHelix.vBaseAtPoint(pos)
            undoStack = pathHelix.vhelix().undoStack()
            self.currentOperation = ForceToolOperation(dest, undoStack)
        elif leftClick:
            if self.logger: self.logger.write("mousePressPathHelix>Pencil\n")
            if self.currentOperation != None:
                self.currentOperation.end()
            dest = pathHelix.vBaseAtPoint(pos)
            useLeft = pathHelix.userClickedLeftHalfOfVBase(event.pos())
            undoStack = pathHelix.vhelix().undoStack()
            self.currentOperation = PencilToolOperation(dest, useLeft, undoStack)

    def hoverMovePathHelix(self, pathHelix, event):
        if self.logger: self.logger.write("hover>")
        self.mouseMovePathHelix(pathHelix, event)
        self.updateLocation(pathHelix, pathHelix.mapToScene(QPointF(event.pos())))

    def mouseMovePathHelix(self, pathHelix, event):
        pos = pathHelix.mapFromScene(event.scenePos())
        if isinstance(self.currentOperation, PencilToolOperation):
            if self.logger: self.logger.write("mouseMovePathHelix>Pencil\n")
            dest = pathHelix.vBaseAtPoint(pos)
            dest._vStrand = self.currentOperation.startVBase.vStrand()
            self.currentOperation.updateDestination(dest)
        elif isinstance(self.currentOperation, ForceToolOperation):
            if self.logger: self.logger.write("mouseMovePathHelix>Force\n")
            phg = pathHelix.pathHelixGroup()
            pt = pathHelix.mapToScene(pos)
            dest = phg.vBaseAtPoint(pt)
            if dest == None:
                self.currentOperation.updateFloatingDestination(pt)
            else:
                self.currentOperation.updateDestination(dest)
        else:
            if self.logger: self.logger.write("mouseMovePathHelix>NOP\n")

    def hoverMovePathHelixGroup(self, phg, event):
        if self.logger: self.logger.write("hover>")
        self.mouseMovePathHelixGroup(phg, event)

    def mouseMovePathHelixGroup(self, phg, event):
        if isinstance(self.currentOperation, ForceToolOperation):
            if self.logger: self.logger.write("mouseMovePHG>Force\n")
            self.currentOperation.updateFloatingDestination(event.pos())
        else:
            if self.logger: self.logger.write("mouseMovePathHelix>NOP\n")

    def mouseReleasePathHelix(self, pathHelix, event):
        if isinstance(self.currentOperation, PencilToolOperation):
            if self.logger: self.logger.write("mouseRelPathHelix>Pencil\n")
            self.currentOperation.end()
            self.currentOperation = None
        else:
            if self.logger: self.logger.write("mouseRelPathHelix>NOP\n")
