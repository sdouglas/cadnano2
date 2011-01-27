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
DNAPart.py
"""

import json
from .part import Part

class DNAPart(Part):
    def __init__(self,*args,**kwargs):
        super(DNAPart,self).__init__(self,*args,**kwargs)
        #The instance variables are private for a reason: accessors are important in a model!
        self._virtualHelices = []
        self._name = kwargs.get('name','untitled')
        self._staples = []
        self._scaffolds = []
    def simpleRep(self):
        """
        Provides a representation of the receiver in terms of simple
        (container,atomic) classes and other objects implementing simpleRep
        """
        ret = {'.class':"DNAPart"}
        ret["virtualHelices"] = self._virtualHelices
        ret["name"] = self._name
        ret["staples"] = self._staples
        ret["scaffolds"] = self._scaffolds
        return ret
    @classmethod
    def fromSimpleRep(cls,rep):
        ret = DNAPart()
        ret._virtualHelices = rep['virtualHelices']
        ret._name = rep['name']
        ret._staples = rep['staples']
        ret._scaffolds = rep['scaffolds']
        return ret
