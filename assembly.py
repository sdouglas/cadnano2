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

"""
assembly.py

Created by Nick Conway on 2011-01-19.
Copyright (c) 2011 __Wyss Institute__. All rights reserved.
"""

class Assembly(self):
    """
    """
    def __init__(self):
        self.id = self.createAsmID()
        self.name = "Asm" + str(0)
        self.color = 0xFFFFFFFF
        self.annotation
        self.object_instances_dict = {}   # default dictionary as a list?     
    # end def
    
    def createPartID(self):
        """
        create a unique part id for a part

        Parameters
        ----------
        filename: filename of json file

        See Also
        --------

        Examples
        -------- 
        """
    # end def
    
    def createAsmID(self):
        """
        load a json file, decides between current filetype and legacy caDNAno 1.0 filetype

        Parameters
        ----------
        filename: filename of json file

        See Also
        --------

        Examples
        -------- 
        """
    # end def
    
    def setPosition(partid, pos):
        """
        load a json file, decides between current filetype and legacy caDNAno 1.0 filetype

        Parameters
        ----------
        instance_index: index in the object instance list
        partid: part id
        pos: list of coordinates

        See Also
        --------

        Examples
        -------- 
        """
    # end def
    
    def getPostion(instance_index):
        """
        get the position of the part

        Parameters
        ----------
        instance_index: index in the object instance list
        partid: part id
        pos: list of coordinates

        See Also
        --------

        Examples
        -------- 
        """
    # end def
    
    def addPart(self,my_part):
        """
        load a json file, decides between current filetype and legacy caDNAno 1.0 filetype

        Parameters
        ----------
        my_part: Part Object

        See Also
        --------

        Examples
        -------- 
        """
        self.object_instances[my_part.id].append
    # end def
    
    def removePart(self,my_part):
        """
        remove a part from the object instance dictionary, and if it is the last instance of the part, del the part from memory?

        Parameters
        ----------
        my_part: Part Object

        See Also
        --------

        Examples
        -------- 
        """
    # end def
# end class
        