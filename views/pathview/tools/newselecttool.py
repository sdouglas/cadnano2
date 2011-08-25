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
select
"""

import util
import sys
from abstractpathtool import AbstractPathTool
from controllers.selecttooloperation import SelectToolOperation

util.qtWrapImport('QtCore', globals(), ['Qt', 'QPointF'])
util.qtWrapImport('QtGui', globals(), ['QGraphicsItem', 'QBrush', 'QFont',
                                       'QGraphicsSimpleTextItem', 'QPen',
                                       'QPolygonF', 'QPainterPath'])

class NewSelectTool(AbstractPathTool):
    """
    SelectTool is the default tool. It allows editing of breakpoints
    (by clicking and dragging) and toggling of crossovers.
    """
    # And we actually use those PathHelixGroup events
    mouseMovePathHelixGroupUnused = False
    mouseReleasePathHelixGroupUnused = False
    mousePressPathHelixGroupUnused = False
    logger = None

    def __init__(self, controller):
        super(NewSelectTool, self).__init__(controller)
        self.currentOperation = None

    def mousePressPathHelix(self, pathHelix, event):
        pathHelix.scene().views()[0].addToPressList(pathHelix)
        # rightClick = event.button() & Qt.RightButton
        # leftClick = event.buttons() & Qt.LeftButton
        if self.logger: self.logger.write("mousePressPathHelix>Select\n")
        if self.currentOperation != None:
            self.currentOperation.end()
        dest = pathHelix.vBaseAtPoint(event.pos())
        undoStack = pathHelix.vhelix().undoStack()
        self.currentOperation = SelectToolOperation(dest, undoStack)

    def hoverMovePathHelix(self, pathHelix, event):
        if self.logger: self.logger.write("hover>")
        self.mouseMovePathHelix(pathHelix, event)
        self.updateLocation(pathHelix, pathHelix.mapToScene(QPointF(event.pos())))

    def mouseMovePathHelix(self, pathHelix, event):
        if isinstance(self.currentOperation, SelectToolOperation):
            if self.logger: self.logger.write("mouseMovePathHelix>Select\n")
            dest = pathHelix.vBaseAtPoint(event.pos())
            dest.vStrand = self.currentOperation.startVBase.vStrand
            self.currentOperation.updateDestination(dest)
        else:
            if self.logger: self.logger.write("mouseMovePathHelix>NOP\n")

    def hoverMovePathHelixGroup(self, phg, event):
        if self.logger: self.logger.write("hover>")
        self.mouseMovePathHelixGroup(phg, event)

    def mouseMovePathHelixGroup(self, phg, event):
        if self.logger: self.logger.write("mouseMovePathHelix>NOP\n")

    def mouseReleasePathHelix(self, pathHelix, event):
        if isinstance(self.currentOperation, SelectToolOperation):
            if self.logger: self.logger.write("mouseRelPathHelix>Select\n")
            self.currentOperation.end()
            self.currentOperation = None
        else:
            if self.logger: self.logger.write("mouseRelPathHelix>NOP\n")
