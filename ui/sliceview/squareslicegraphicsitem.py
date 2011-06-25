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
squareslicegraphicsitem.py

Created by Nick Conway on 2010-06-23.
"""

from honeycombslicegraphicsitem import HoneycombSliceGraphicsItem
from PyQt4.QtCore import QRectF

class SquareSliceGraphicsItem(HoneycombSliceGraphicsItem):
    """
    SquareSliceGraphicsItem
    """
    
    def __init__(self, part, controller=None, parent=None):
        HoneycombSliceGraphicsItem.__init__(self, part, controller, parent)

    def upperLeftCornerForCoords(self, row, col):
        x = col*2*self.radius
        y = row*2*self.radius
        return (x, y)

    def _updateGeometry(self, newCols, newRows):
        self._rect = QRectF(0, 0,\
                           (newCols)*self.radius*2,\
                           (newRows)*self.radius*2)

