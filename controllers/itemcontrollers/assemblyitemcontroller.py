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


class AssemblyItemController():
    def __init__(self, assemblyItem, modelAssembly):
        self._assemblyItem = assemblyItem
        self._modelAssembly = modelAssembly
        self.connectSignals()

    def connectSignals(self):
        self._modelAssembly.partAddedSignal.connect(_assemblyItem.partAddedSlot)
        self._modelAssembly.assemblyMovedSignal.connect(_assemblyItem.assemblyMovedSlot)
        self._modelAssembly.assemblyDestroyedSignal.connect(_assemblyItem.assemblyDestroyedSlot)

    def disconnectSignals(self):
        self._modelAssembly.partAddedSignal.disconnect(_assemblyItem.partAddedSlot)
        self._modelAssembly.assemblyMovedSignal.disconnect(_assemblyItem.assemblyMovedSlot)
        self._modelAssembly.assemblyDestroyedSignal.disconnect(_assemblyItem.assemblyDestroyedSlot)
