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
# from controllers.itemcontrollers.abstractitemcontroller import AbstractItemController


class AbstractStrandItemController(object):
    def __init__(self, strandItem, modelStrand):
        if self.__class__ == AbstractStrandItemController:
            e = "AbstractStrandItemController should be subclassed."
            raise NotImplementedError(e)
        self._strandItem = strandItem
        self._modelOligo = modelStrand.oligo()
        self._modelStrand = modelStrand
        
        # don't call this here as super call in subclass will install two signals
        # self.connectSignals()
    # end def
    
    def reconnectOligoSignals(self, newOligo):
        self.disconnectOligoSignals()
        self.connectOligoSignals()
    # end def
    
    def connectSignals(self):
        mS = self._modelStrand
        sI = self._strandItem
        
        AbstractStrandItemController.connectOligoSignals(self)
        mS.strandHasNewOligoSignal.connect(sI.strandHasNewOligoSlot)
        mS.strandRemovedSignal.connect(sI.strandRemovedSlot)
        mS.strandDestroyedSignal.connect(sI.strandDestroyedSlot)
        mS.strandDecoratorAddedSignal.connect(sI.strandDecoratorAddedSlot)
    # end def
    
    def connectOligoSignals(self):
        sI = self._strandItem
        mO = self._modelStrand.oligo()
        self._modelOligo = mO
        
        mO.oligoAppearanceChangedSignal.connect(sI.oligoAppeareanceChangedSlot)
    # end def

    def disconnectSignals(self):
        mS = self._modelStrand
        sI = self._strandItem
        
        AbstractStrandItemController.disconnectOligoSignals(self)
        mS.strandHasNewOligoSignal.disconnect(sI.strandHasNewOligoSlot)
        mS.strandRemovedSignal.disconnect(sI.strandRemovedSlot)
        mS.strandDestroyedSignal.disconnect(sI.strandDestroyedSlot)
        mS.strandDecoratorAddedSignal.disconnect(sI.strandDecoratorAddedSlot)
    # end def
    
    def disconnectOligoSignals(self):
        sI = self._strandItem
        mO = self._modelOligo
        mO.oligoAppearanceChangedSignal.disconnect(sI.oligoAppeareanceChangedSlot)
    # end def