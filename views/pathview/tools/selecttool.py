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
import sys
from abstractpathtool import AbstractPathTool

util.qtWrapImport('QtCore', globals(), ['Qt', 'QPointF'])
util.qtWrapImport('QtGui', globals(), ['QGraphicsItem', 'QBrush', 'QFont',
                                       'QGraphicsSimpleTextItem', 'QPen',
                                       'QPolygonF', 'QPainterPath'])


class SelectTool(AbstractPathTool):
    """
    SelectTool is the default tool. It allows editing of breakpoints
    (by clicking and dragging) and toggling of crossovers.
    """
    # And we actually use those PartGraphicsItem events
    mouseMovePartGraphicsItemUnused = False
    mouseReleasePartGraphicsItemUnused = False
    mousePressPartGraphicsItemUnused = False
    logger = None

    def __init__(self, controller):
        super(SelectTool, self).__init__(controller)
        self.currentOperation = None

    def hoverMovePartGraphicsItem(self, part, event):
        if self.logger: self.logger.write("hover>")
        self.mouseMovePartGraphicsItem(part, event)

    def mouseMovePartGraphicsItem(self, part, event):
        if self.logger: self.logger.write("mouseMoveVirtualHelixGraphicsItem>NOP\n")

    def hoverMoveVirtualHelixGraphicsItem(self, pathHelix, event):
        if self.logger: self.logger.write("hover>")
        self.mouseMoveVirtualHelixGraphicsItem(pathHelix, event)
        self.updateLocation(pathHelix, pathHelix.mapToScene(QPointF(event.pos())))

    def mousePressVirtualHelixGraphicsItem(self, pathHelix, event):
        # initial setup / check input state
        pathHelix.makeSelfActiveHelix()
        pathHelix.scene().views()[0].addToPressList(pathHelix)
        dest = pathHelix.vBaseAtPoint(event.pos())
        useLeft = pathHelix.userClickedLeftHalfOfVBase(event.pos())
        undoStack = pathHelix.vhelix().undoStack()
        shiftClick = event.modifiers() & Qt.ShiftModifier
        altClick = event.modifiers() & Qt.AltModifier
        # do the operation
        if self.currentOperation != None: self.currentOperation.end()
        self.currentOperation = SelectToolOperation(dest, useLeft, undoStack)
        if shiftClick:
            if self.logger: self.logger.write("mousePressVirtualHelixGraphicsItem>Join\n")
            self.currentOperation.actionMergeWithAdjacent(dest)
            self.currentOperation.end()
            self.currentOperation = None
        elif altClick:
            if self.logger: self.logger.write("mousePressVirtualHelixGraphicsItem>Extend\n")
            self.currentOperation.actionExpandStrandToFillAvailableSpace(dest)
            self.currentOperation.end()
            self.currentOperation = None
        else:
            if self.logger: self.logger.write("mousePressVirtualHelixGraphicsItem>Select\n")

    def mouseMoveVirtualHelixGraphicsItem(self, pathHelix, event):
        if isinstance(self.currentOperation, SelectToolOperation):
            if self.logger: self.logger.write("mouseMoveVirtualHelixGraphicsItem>Select\n")
            dest = pathHelix.vBaseAtPoint(event.pos())
            dest.vStrand = self.currentOperation.startVBase.vStrand
            self.currentOperation.updateDestination(dest)
        else:
            if self.logger: self.logger.write("mouseMoveVirtualHelixGraphicsItem>NOP\n")

    def mouseReleaseVirtualHelixGraphicsItem(self, pathHelix, event):
        if isinstance(self.currentOperation, SelectToolOperation):
            if self.logger: self.logger.write("mouseRelVirtualHelixGraphicsItem>Select\n")
            self.currentOperation.end()
            self.currentOperation = None
        else:
            if self.logger: self.logger.write("mouseRelVirtualHelixGraphicsItem>NOP\n")