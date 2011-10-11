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

class Modifier(object):
    """
    Modifiers do affect an applied sequence and do not store a sequence
    themselves.  They cause a base changed to another sequence.
    Modifiers DO NOT affect the length of a strand
    """
    def __init__(self, idx):
        if self.__class__ == Modifier:
            e = "Modifier should be subclassed."
            raise NotImplementedError(e)
        self._mType = None
        self._lowIdx  = idx
        self._highIdx = self._lowIdx
        self._privateSequence = None
    # end def

    def length(self):
        """
        This is the length of a sequence that is immutable by the strand
        """
        return self._highIdx - self._lowIdx + 1
        
    def modifierType(self):
        return self._mtype
# end class