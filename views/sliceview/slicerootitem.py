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

from controllers.viewrootcontroller import ViewRootController

import util
util.qtWrapImport('QtCore', globals(), ['pyqtSignal', 'QObject'])
util.qtWrapImport('QtGui', globals(), ['QGraphicsRectItem'])


class SliceRootItem(QGraphicsRectItem):
    """
    PathRootItem is the root item in the PathView. It gets added directly
    to the pathscene by DocumentWindow. It receives two signals
    (partAddedSignal and selectedPartChangedSignal) via its ViewRootController.

    PathRootItem must instantiate its own controller to receive signals
    from the model.
    """
    def __init__(self, rect, parent, window, document):
        super(SliceRootItem, self).__init__(rect, parent)
        self._window = window
        self._document = document
        self._controller = ViewRootController(self, document)
        self._pathRootItem = None

    ### SIGNALS ###

    ### SLOTS ###
    def partAddedSlot(self, part):
        """
        Receives notification from the model that a part has been added.
        Views that subclass AbstractView should override this method.
        """
        print "SliceRootItem.partAddedSlot!"
        return

        if part.crossSectionType() == LatticeType.Honeycomb:
            self.sliceGraphicsItem = HoneycombSliceGraphicsItem(part,
                                        controller=win.sliceToolManager,
                                        parent=win.sliceroot)
        else:
            self.sliceGraphicsItem = SquareSliceGraphicsItem(part,
                                        controller=win.sliceToolManager,
                                        parent=win.sliceroot)


        win = self._window
        win.sliceToolManager.activeSliceLastSignal.connect(
                      self.pathHelixGroup.activeSliceHandle().moveToLastSlice)
        win.sliceToolManager.activeSliceFirstSignal.connect(
                     self.pathHelixGroup.activeSliceHandle().moveToFirstSlice)

        for vh in part.getVirtualHelices():
            xos = vh.get3PrimeXovers(StrandType.Scaffold)
            for xo in xos:
                toBase = (xo[1][0], xo[1][2])
                self.pathHelixGroup.createXoverItem(
                                            xo[0], toBase, StrandType.Scaffold)
            xos = vh.get3PrimeXovers(StrandType.Staple)
            for xo in xos:
                toBase = (xo[1][0], xo[1][2])
                self.pathHelixGroup.createXoverItem(
                                            xo[0], toBase, StrandType.Staple)
        # end for
        self.setActivePart(part)



    def selectedPartChangedSlot(self):
        """docstring for selectedPartChangedSlot"""
        pass

    ### METHODS ###
    def setPathRootItem(self, pathRoot):
        """docstring for setPathRootItem"""
        self._pathRootItem = pathRoot

