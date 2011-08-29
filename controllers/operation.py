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
util.qtWrapImport('QtCore', globals(), ['QObject'])
from model.normalstrand import NormalStrand

class Operation(QObject):
    """ Handles multi-step interactions with the model """
    def __init__(self, undoStack):
        QObject.__init__(self)
        # No good will come of interactive strand creation without an undo stack
        assert(undoStack != None)
        self.undoStack = undoStack
        self.undoStackIdxBeforeOperation = undoStack.index()

    def rewind(self, toIdx=None):
        if toIdx == None:
            toIdx = self.undoStackIdxBeforeOperation
        while self.undoStack.index() > toIdx:
            self.undoStack.undo()

    def end(self):
        pass