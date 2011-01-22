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
    def __init__(self, name, node_type, id_hash, parent=None):
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

    def writeNodeAndChildren(writer, treemodel):
        """
        This needs to be written for all types of tags
        """
        if self != treemodel.root:
            writer.writeStartElement(json_io.NodeTag)
            writer.writeAttribute(NameAttribute, node.name())
            writer.writeAttribute(DoneAttribute, "1" if node.isDone()) else "0")
            while more:
                writer.writeStartElement(WhenTag)
                writer.writeEndElement() 
            # end while
        # end if
        for child in self.children:
            child.writeNodeAndChildren(writer, treemodel)
        # end for
        if self != treemodel.root:
            writer.writeEndElement() 
        # end if
    # end def
    
    
# end class

