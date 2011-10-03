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
activeslicehandle.py
Created by Shawn on 2011-02-05.
"""

from exceptions import IndexError
from controllers.itemcontrollers.activesliceitemcontroller import ActiveSliceItemController
from views import styles
import util

# import Qt stuff into the module namespace with PySide, PyQt4 independence
util.qtWrapImport('QtCore', globals(), ['QPointF', 'QRectF', 'Qt', 'QObject',\
                                        'pyqtSignal', 'pyqtSlot', 'QEvent'])
util.qtWrapImport('QtGui', globals(), ['QBrush', 'QFont', 'QGraphicsItem',\
                                       'QGraphicsSimpleTextItem', 'QPen',\
                                       'QDrag', 'QUndoCommand', 'QGraphicsRectItem'])


class ActiveSliceItem(QGraphicsRectItem):
    """ActiveSliceItem for the Slice View"""
    _baseWidth = styles.PATH_BASE_WIDTH
    _brush = QBrush(styles.activeslicehandlefill)
    _labelbrush = QBrush(styles.orangestroke)
    _pen = QPen(styles.activeslicehandlestroke,\
                styles.SLICE_HANDLE_STROKE_WIDTH)
    _font = QFont(styles.thefont, 12, QFont.Bold)

    def __init__(self, partItem, activeBaseIndex):
        super(ActiveSliceItem, self).__init__(partItem)
        self._partItem = partItem
        self.setFlag(QGraphicsItem.ItemHasNoContents)
        
        self._controller = ActiveSliceItemController(self, partItem.part())
    # end def
    
    ### SLOTS ###
    def updateRectSlot(self, part):
        pass
    # end def
    
    def updateIndexSlot(self, newActiveSliceZIndex):
        newlyActiveVHs = set()
        part = self.part()
        activeBaseIdx = part.activeBaseIndex()

        for vhi in self._partItem._virtualHelixHash.itervalues():
            isActiveNow = vhi.virtualHelix().hasStrandAtIdx(activeBaseIdx)
            vhi.setActiveSliceView(isActiveNow)
    # end def
    
    def strandChangedSlot(self, vh):
        partItem = self._partItem
        vhi = partItem.getVirtualHelixItemByCoord(*vh.coords())
        
        isActiveNow = vh.hasStrandAtIdx(partItem.part().activeBaseIndex())
        vhi.setActiveSliceView(isActiveNow)
    # end def
    
    ### METHODS ###
    def part(self):
        return self._partItem.part()
    # end def
    
    def removed(self):
        self._partItem = None
        self._controller.disconnectSignals()
        self.controller = None
    # end def