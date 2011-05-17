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
partnode.py

Created by Nick Conway on 2011-01-19.
"""

from ui.treeview.treemodel import Node

class PartNode(Node):
    """
    """
    ntype = "part" # the type of node i.e. Assembly, Part, etc
    
    def __init__(self, name="", part_inst=None, node_attribute=None, parent=None):
        """
        """
        super(PartNode,self).__init__(parent)    
        self.parent = parent
        self.children = []
        
        if name == "":
            self.name = "Part.1"
            #print "adding Part"
        # end if
        else:
            self.name = name
        # end else
        
        if self.parent != None:
            #print "added Part!"
            self.parent.addChild(self)
        #end if
        
        self.object_instance = part_inst
    # end def
        
# end class