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
idbank.py

Created by Nick Conway on 2011-01-19.
"""

from collections import deque


class IdBank(object):
    """
    A way to issue keys and remove keys.  Removed keys are available for
    reissue.
    This should be fast as typically users shouldn't be deleting lots of
    items, so we store the previosuly used ids in a deque.
    """
    def __init__(self):
        """
        docstring for __init__.
        """
        super(object, self).__init__()
        self.id_count = 0
        self.removed_ids = deque()
        self.id_dict = {}
        self.id_dict_import = {}
        self.import_ids = []
    # end def

    def isIdIssued(self, id_hash):
        """
        check if key was issued
        """
        return id_hash in self.id_dict
    # end def

    def issue(self):
        """
        Creates a new id for a unique element/part/assembly
        """
        try:
            removed_ids.popleft()
        except:
            self.id_count += 1  # increase the hash key
            self.id_dict[self.id_count] = True
            return self.id_count
    # end def

    def remove(self, id_hash):
        """
        assumes id_hash is an issued hash
        I could create a dictionary of issue key's as well to check
        To be used when deleting parts and assemblies
        If someone undoes this with an UNDO/REDO, it shouldn't matter if the
        item get assigned a different id to previous.
        """
        try:
            if id_hash < self.removed_ids[0]:
                self.removed_ids.appendleft(id_hash)
            else:
                self.removed_ids.append(id_hash)
        except:  # deque is empty so just append the key anyway
            self.removed_ids.append(id_hash)
    # end def

    def deleteDeep(self, id_hash):
        """
        To be used to UNDO the creation of a id/key
        """
        try:
            del self.id_dict[id_hash]
        except:
            print "key not there"
        if self.id_count > 0:
            self.id_count -= 1
        else:
            print "can't undo anymore"
    # end def

    def importIssue(self, id_hash):
        """
        issue new ideas for a file import, does not preserve the id's in the
        file this could be implemented, but I don't think it matters nor
        saves time
        """
        # see if we've already encountered the hash
        if id_hash in self.id_dict:  # might not need the if
            return self.id_dict_import[id_hash]
        # end if
        else:
            temp = self.issue()
            self.id_dict_import[id_hash] = temp
            self.imported_ids.append(temp)  # record the new id issued
            return temp
        # end else
    # end def

    def importInit(self):
        """
        clears the dictionary that keeps track of imported keys
        """
        # clears memory asssociated with these potentially large variables
        del self.id_dict_import
        del self.imported_ids

        self.id_dict_import = {}
        self.imported_ids = []  # store the import start id for easy UNDO/REDO
    # end def

    def undoImport(self):
        """
        For undoing an import
        """
        for id_hash in self.imported_ids:
            self.deleteDeep(id_hash)
        # end for
    # end def
# end class
