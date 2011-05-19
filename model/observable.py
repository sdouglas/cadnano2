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
virtualhelix.py
Created by Jonathan deWerd.

AFAICS, we have two reasonable approaches to change notification:
1) Qt Signals
    Good: seamlessly moves between C++ and Python code
    Bad: only works between QObject subclasses, QGraphicsObject isn't available
2) Observer pattern
    Good: works between any python classes
    Bad: doesn't move between python and C++
    Good: we could easily layer Qt Signals on top of the Observable mixin later
        Bad: that would be a total hack
            Good: but it would work
Option 2 is most expedient since the problem of migration to C++ is less pressing
for the forseeable future than the problem of not being able to use QGraphicsObject.
I therefore Arbitrarily Decide Unless Overridden that we're going with option 2.
- Jonathan
"""
import weakref

class Observable(object):
    def __init__(self):
        self._observers = []
        
    def notifyObservers(self, message, **kwargs):
        for o in self._observers:
            if o():
                o().observedObjectDidChange(self, message, **kwargs)
    
    def addObserver(self, obs):
        self._observers.append(weakref.ref(obs, lambda x: self._observers.remove(x)))
    