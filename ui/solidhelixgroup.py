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
solidhelixgroup.py

Created by Nick Conway on 2011-02-04.
For use controlling 3D solid models generated in Maya
"""
from PyQt4.QtCore import pyqtSignal, pyqtSlot


class SolidHelixGroup(object):
    """
    A Solid Hinstance is meant to store helix data in Maya 
    representing a pathhelixgroup.
    
    column nodes all have the same X coordinate
    row nodes can have slightly different Y coordinates (offset) for convenience of data representation
    as is the case of the honeycomb representation
    
    Parameters
    ----------
    rows: rows grid size
    cols: columns grid size

    See Also
    --------

    Examples
    --------
    """

    # store slice nodes in hash accessible by "row,col" keys
    def __init__(self, dnaPartInst, type="honeycomb", controller=None, parent=None):
        """
        Parameters
        ----------
        rows: rows grid size
        cols: columns grid size

        See Also
        --------

        Examples
        --------
        """
        self.number_hash = {}
        

    # end def
    
    def handleScaffoldChange(self,number):
        """"""
        self.number
        
    # end def
    
    @pyqtSlot(int,int,int)
    def handleNewHelix(self, row, col, number):
        """
        Retrieve reference to new VirtualHelix vh based on number relayed
        by the signal event. Next, create a new PathHelix associated 
        with vh and draw it on the screen.
        """
        self.number_hash[number] = True
    # end def
# end class