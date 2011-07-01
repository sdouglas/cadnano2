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
skiptool.py
Created by Nick on 2011-05-03.
"""
from abstractpathtool import AbstractPathTool
import ui.styles as styles
from ui.pathview.handles.loophandle import SkipItem

import util
# import Qt stuff into the module namespace with PySide, PyQt4 independence
util.qtWrapImport('QtGui', globals(), [ 'QPen'] )

class SkipTool(AbstractPathTool):
    def __init__(self, controller, parent=None):
        """
        This class inherits from the PathTool class for the majority of
        methods/behaviours.  Essentially it adds merely decorator graphics
        custimazation of behaviour and data structure access particular to
        skip insertion on a mouseclick.

        Its parent should be *always* be a PathHelix.
        """
        super(SkipTool, self).__init__(controller, parent)
        self._skipItem = SkipItem()
        _pen = QPen(styles.redstroke, 2)
        self.baseWidth = styles.PATH_BASE_WIDTH
        self.hide()
        self.setZValue(styles.ZPATHTOOL)
    # end def

    def paint(self, painter, option, widget=None):
        painter.setPen(self._pen)
        painter.setBrush(self._brush)
        painter.drawRect(self._toolRect)
        painter.setPen(self._skipItem.getPen())
        painter.drawPath(self._skipItem.getSkip())
    # end def

    def mousePressPathHelix(self, ph, event):
        vh = ph.vhelix()
        posScene = event.scenePos()
        posItem = self.parentObject().mapFromScene(posScene)
        indexp = self.helixIndex(posItem)
        mouseDownBase = ph.baseAtLocation(posItem.x(),\
                                                posItem.y())
        # print "SkipTool clicked at: (%d, %d) on helix %d" % \
        #     (indexp[0], indexp[1], self.parentObject().number())
        # create a new SkipHandle by adding through the parentObject
        # create a new LoopHandle by adding through the     parentObject
        if mouseDownBase:
            loopsize = vh.hasLoopOrSkipAt(*mouseDownBase)
            if loopsize > 0:    # toggle from loop
                vh.installLoop(mouseDownBase[0],mouseDownBase[1],-1)
            elif loopsize < 0:    # skip already there
                vh.installLoop(mouseDownBase[0],mouseDownBase[1],0)
            elif vh.hasStrandAt(*mouseDownBase):
                vh.installLoop(mouseDownBase[0],mouseDownBase[1],-1)
            ph.makeSelfActiveHelix()
    # end def
# end class
