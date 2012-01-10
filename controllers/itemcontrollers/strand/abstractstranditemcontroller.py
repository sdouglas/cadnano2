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
# from controllers.itemcontrollers.abstractitemcontroller import AbstractItemController


class AbstractStrandItemController(object):
    def __init__(self, strandItem, modelStrand):
        """
        Do not call connectSignals here.  subclasses
        will install two sets of signals.
        """
        if self.__class__ == AbstractStrandItemController:
            e = "AbstractStrandItemController should be subclassed."
            raise NotImplementedError(e)
        self._strandItem = strandItem
        self._modelStrand = modelStrand
        self._modelOligo = modelStrand.oligo()
    # end def

    def reconnectOligoSignals(self):
        self.disconnectOligoSignals()
        self.connectOligoSignals()
    # end def

    def connectSignals(self):
        """Connects modelStrant signals to strandItem slots."""
        mS = self._modelStrand
        sI = self._strandItem

        AbstractStrandItemController.connectOligoSignals(self)
        util.observe(mS, 'strandHasNewOligoSignal', sI.strandHasNewOligoSlot)
        util.observe(mS, 'strandRemovedSignal', sI.strandRemovedSlot)

        mS.strandInsertionAddedSignal.connect(sI.strandInsertionAddedSlot)
        mS.strandInsertionChangedSignal.connect(sI.strandInsertionChangedSlot)
        mS.strandInsertionRemovedSignal.connect(sI.strandInsertionRemovedSlot)
        mS.strandDecoratorAddedSignal.connect(sI.strandDecoratorAddedSlot)
        mS.strandDecoratorChangedSignal.connect(sI.strandDecoratorChangedSlot)
        mS.strandDecoratorRemovedSignal.connect(sI.strandDecoratorRemovedSlot)
        mS.strandModifierAddedSignal.connect(sI.strandModifierAddedSlot)
        mS.strandModifierChangedSignal.connect(sI.strandModifierChangedSlot)
        mS.strandModifierRemovedSignal.connect(sI.strandModifierRemovedSlot)
        
        mS.selectedChangedSignal.connect(sI.selectedChangedSlot)
    # end def

    def connectOligoSignals(self):
        sI = self._strandItem
        mO = self._modelStrand.oligo()
        self._modelOligo = mO
        util.observe(mO, 'oligoAppearanceChangedSignal', sI.oligoAppearanceChangedSlot)
    # end def

    def disconnectSignals(self):
        mS = self._modelStrand
        sI = self._strandItem

        AbstractStrandItemController.disconnectOligoSignals(self)
        util.unObserve(mS, 'strandHasNewOligoSignal', sI.strandHasNewOligoSlot)
        mS.strandRemovedSignal.disconnect(sI.strandRemovedSlot)

        mS.strandInsertionAddedSignal.disconnect(sI.strandInsertionAddedSlot)
        mS.strandInsertionChangedSignal.disconnect(sI.strandInsertionChangedSlot)
        mS.strandInsertionRemovedSignal.disconnect(sI.strandInsertionRemovedSlot)
        mS.strandDecoratorAddedSignal.disconnect(sI.strandDecoratorAddedSlot)
        mS.strandDecoratorChangedSignal.disconnect(sI.strandDecoratorChangedSlot)
        mS.strandDecoratorRemovedSignal.disconnect(sI.strandDecoratorRemovedSlot)
        mS.strandModifierAddedSignal.disconnect(sI.strandModifierAddedSlot)
        mS.strandModifierChangedSignal.disconnect(sI.strandModifierChangedSlot)
        mS.strandModifierRemovedSignal.disconnect(sI.strandModifierRemovedSlot)
        
        mS.selectedChangedSignal.disconnect(sI.selectedChangedSlot)
    # end def

    def disconnectOligoSignals(self):
        sI = self._strandItem
        mO = self._modelOligo
        util.unObserve(mO, 'oligoAppearanceChangedSignal', sI.oligoAppearanceChangedSlot)
    # end def
