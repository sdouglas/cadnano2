# The MIT License
#
# Copyright (c) 2010 Wyss Institute at Harvard University
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

import ui.treeModel as TM

class PartNode(TM.Node):
    """
    """
    def __init__(self, name, id_hash, parent=None,node_type="part"):
        """
        """
        super(TM.Node,self).__init__()
        
        self.parent = parent
        self.children = []
        
        self.name = name
        self.ntype = "part" # the type of node i.e. Assembly, Part, etc
        self.id = id_hash
        self.checked = True
        self.locked = False 
        self.done = False
        
    # end def
    
    def addToTable(self, table_dict):
        """
        add the node to the node type's dictionary
        """
        table_dict[self.id] = Part()
    # end def
    
# end class

class Part(object):
    """
    """
    def __init__(self, name, id_hash, parent=None, node_type="assembly"):
        super(object,self).__init__()
        """
        self.color = 0xFFFFFFFF
        self.annotation = []
        # this is gonna be a list of non-specific attributes for an assembly
        self.object_instances = defaultdict(list)  # default dictionary as a list?
        """
    # end def
# end class