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
honeycombslicegraphicsitem.py

Created by Shawn Douglas on 2010-06-15.
"""

from slicegraphicsitem import SliceGraphicsItem

import util
# import Qt stuff into the module namespace with PySide, PyQt4 independence
util.qtWrapImport('QtCore', globals(), ['QRectF'] )

root3 = 1.732051
class HoneycombSliceGraphicsItem(SliceGraphicsItem):
    """
    HoneycombSliceGraphicsItem
    """
    
    def __init__(self, part, controller=None, parent=None):
        SliceGraphicsItem.__init__(self, part, controller, parent)

    def _upperLeftCornerForCoords(self, row, col):
        x = col*self.radius*root3
        if ((row % 2) ^ (col % 2)): # odd parity
            y = row*self.radius*3 + self.radius
        else:                       # even parity
            y = row*self.radius*3
        return (x, y)

    def _updateGeometry(self, newCols, newRows):
        self._rect = QRectF(0, 0,\
                           (newCols)*self.radius*root3,\
                           (newRows)*self.radius*3)

# end class