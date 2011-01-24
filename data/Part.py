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
from idbank import IdBank

class PartNode(TM.Node):
    """
    """
    def __init__(self, name, obj_id, inst_id, parent=None,node_type="part"):
        """
        """
        super(TM.Node,self).__init__()
        
        self.parent = parent
        self.children = []
        
        self.name = name
        self.ntype = "part" # the type of node i.e. Assembly, Part, etc
        self.object_id = obj_id
        self.instance_id = inst_id
    # end def
    
# end class

class Part(object):
    """
    """
    def __init__(self, name, obj_id, parent=None, node_type="part"):
        super(object,self).__init__()
        """
        this is gonna be a list of non-specific attributes for an assembly
        self.object_instances = defaultdict(list)  # default dictionary as a list?
        """
        self.name = name
        self.parent = parent# or parent hash?
        self.node_type = "part"
        self.color = 0
        self.annotation = ""
        
        self.object_id = obj_id
        self.instance_id_bank = IdBank()    # generate instances of themselves
        
        # this contains instances of this specific assembly, and other views
        # like: self.instances[id] = [treeNode, SliceObjectView, PathObjectView]
        self.instances = {}                 # this contains instances of this specific assembly
        
        self.VHelixList = []
        self.staples = []
    
    # end def
        """
    # end def
# end class