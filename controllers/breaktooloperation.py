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

import sys
import util
from model.strands.normalstrand import NormalStrand
from model.strands.vbase import VBase
from operation import Operation


class BreakToolOperation(Operation):
    """
    Handles interactive strand creation / destruction in the manner of the
    BreakTool.
    """
    logger = None

    def __init__(self, vBase, undoStack):
        """
        Perform strand break if:
        1. vBase is present
        2. vBase is part of a strand
        3. strand is a NormalStrand
        4. vBase is not a strand start or end
        """
        if vBase == None: return
        if vBase.strand() == None: return
        if not isinstance(vBase.strand(), NormalStrand): return
        idx = vBase.vNext3().vIndex() if vBase.drawn5To3() else vBase.vIndex()
        if idx in vBase.strand().idxs(): return
        Operation.__init__(self, undoStack)
        self.actionBreakVstrandAt(vBase.vStrand(), idx)
        if self.logger: self.logger.write('BreakToolOperation(%s)\n'%vBase)

    def actionBreakVstrandAt(self, vStrand, idx):
        """
        Install strand break at vBase, leaving vBase as the 3' end of the
        original strand.
        """
        vStrand.clearStrand(idx, idx, useUndoStack=True, undoStack=self.undoStack)
