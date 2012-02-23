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

class XoverItemController(object):
    def __init__(self, xoverItem, modelStrand5p):
        self._xoverItem = xoverItem
        self._modelStrand5p = modelStrand5p
        self._modelOligo = modelStrand5p.oligo()
        self.connectSignals()
    # end def

    def reconnectOligoSignals(self):
        """
        use this for whenever a strands oligo changes
        """
        self.disconnectSignals()
        self.connectSignals()
    # end def

    def reconnectSignals(self, strand):
        self.disconnectSignals()
        self._modelStrand5p = strand
        self.connectSignals()
    # end def

    def connectSignals(self):
        xI = self._xoverItem
        s5p = self._modelStrand5p
        mO = s5p.oligo()
        self._modelOligo = mO

        s5p.strand5pHasSwappedSignal.connect(xI.strandSwapSlot)
        s5p.strandHasNewOligoSignal.connect(xI.strandHasNewOligoSlot)
        mO.oligoAppearanceChangedSignal.connect(xI.oligoAppearanceChangedSlot)
        s5p.strandXover5pRemovedSignal.connect(xI.xover5pRemovedSlot)
    # end def

    def disconnectSignals(self):
        xI = self._xoverItem
        s5p = self._modelStrand5p
        mO = self._modelOligo

        s5p.strand5pHasSwappedSignal.disconnect(xI.strandSwapSlot)
        s5p.strandHasNewOligoSignal.disconnect(xI.strandHasNewOligoSlot)
        mO.oligoAppearanceChangedSignal.disconnect(xI.oligoAppearanceChangedSlot)
        s5p.strandXover5pRemovedSignal.connect(xI.xover5pRemovedSlot)
    # end def
