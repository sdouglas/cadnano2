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


class AbstractDecoratorGraphicsItem(QGraphicsPathItem):
    def __init__(self, parent):
        """The parent should be a VirtualHelixGraphicsItem."""
        if self.__class__ == AbstractDecoratorGraphicsItem:
            e = "AbstractDecoratorGraphicsItem should be subclassed."
            raise NotImplementedError(e)
        super(AbstractDecoratorGraphicsItem, self).__init__(parent)
        self._strand = None
        self._oligo = None

    ### SIGNALS ###

    ### SLOTS ###
    def strandResizedSlot(self):
        """docstring for strandResizedSlot"""
        pass

    def sequenceAddedSlot(self, oligo):
        """docstring for sequenceAddedSlot"""
        pass

    def decoratorRemovedSlot(self, oligo):
        """docstring for sequenceClearedSlot"""
        pass

    ### METHODS ###
    def connectSignals(self):
        self._strand.decoratorDestroyedSignal.connect(self.decoratorRemovedSlot)
        self._oligo.sequenceAddedSignal.connect(self.sequenceAddedSlot)
        self._oligo.sequenceClearedSignal.connect(self.sequenceClearedSlot)

    def disconnectSignals(self):
        self._strand.resizedSignal.disconnect(self.strandResizedSlot)
        self._oligo.sequenceAddedSignal.disconnect(self.sequenceAddedSlot)
        self._oligo.sequenceClearedSignal.disconnect(self.sequenceClearedSlot)

    ### COMMANDS ###
