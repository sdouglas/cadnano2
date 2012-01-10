#!/usr/bin/env python
# encoding: utf-8

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

from exceptions import NotImplementedError
import util
util.qtWrapImport('QtGui', globals(), ['QGraphicsPathItem'])


class AbstractStrandItem(QGraphicsPathItem):
    def __init__(self, parent):
        """The parent should be a VirtualHelixItem."""
        if self.__class__ == AbstractStrandItem:
            raise NotImplementedError("AbstractStrandItem should be subclassed.")
        super(AbstractStrandItem, self).__init__(parent)
        self._strand = None
        self._oligo = None

    ### SIGNALS ###

    ### SLOTS ###
    def oligoAppeareanceChanged(self):
        """docstring for oligoAppeareanceChanged"""
        pass

    def hasNewOligoSlot(self, oligo):
        """docstring for hasNewOligoSlot"""
        self._oligo = oligo
        # redraw

    def strandRemovedSlot(self, strand):
        """docstring for strandRemovedSlot"""
        pass

    def decoratorAddedSlot(self, decorator):
        """docstring for decoratorAddedSlot"""
        pass

    ### METHODS ###
    def connectSignals(self):
        self._oligo.appearanceChangedSignal.connect(self.oligoAppeareanceChanged)
        util.observe(self._strand, 'strandHasNewOligoSignal', self.hasNewOligoSlot)
        self._strand.destroyedSignal.connect(self.strandRemovedSlot)
        self._strand.decoratorAddedSignal.connect(self.decoratorAddedSlot)

    def disconnectSignals(self):
        self._oligo.appearanceChangedSignal.disconnect(self.oligoAppeareanceChanged)
        util.unObserve(self._strand, 'strandHasNewOligoSignal', self.hasNewOligoSlot)
        self._strand.destroyedSignal.disconnect(self.strandRemovedSlot)
        self._strand.decoratorAddedSignal.disconnect(self.decoratorAddedSlot)

    ### COMMANDS ###
