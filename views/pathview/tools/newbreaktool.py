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
from controllers.breaktooloperation import BreakToolOperation

class NewBreakTool(AbstractPathTool):
    """
    Break tool is used to clear strands.
    """
    # And we actually use those PathHelixGroup events
    mouseMovePathHelixGroupUnused = True
    mouseReleasePathHelixGroupUnused = True
    mousePressPathHelixGroupUnused = False
    logger = None

    def __init__(self, controller):
        super(NewBreakTool, self).__init__(controller)
        self.currentOperation = None

    def mousePressPathHelix(self, pathHelix, event):
        # initial setup / check input state
        pathHelix.scene().views()[0].addToPressList(pathHelix)
        undoStack = pathHelix.vhelix().undoStack()
        dest = pathHelix.vBaseAtPoint(event.pos())
        # do the operation
        if self.currentOperation != None: self.currentOperation.end()
        self.currentOperation = BreakToolOperation(dest, undoStack)
        if self.logger: self.logger.write("mousePressPathHelix>Break\n")

    def mouseReleasePathHelix(self, pathHelix, event):
        if isinstance(self.currentOperation, BreakToolOperation):
            if self.logger: self.logger.write("mouseRelPathHelix>Break\n")
            self.currentOperation.end()
            self.currentOperation = None
        else:
            if self.logger: self.logger.write("mouseRelPathHelix>NOP\n")

