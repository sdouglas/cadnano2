The MIT License

Copyright (c) 2011 Wyss Institute at Harvard University

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.

http://www.opensource.org/licenses/mit-license.php

# CADnano DNA Origami Software

## Overview

CADnano is DNA origami design software, check out the [wiki](http://en.wikipedia.org/wiki/DNA_origami)

## Installation

For now just run from the terminal with python main.py
We're still working out the bugs

### Required Dependencies

* [Qt 4.7](http://qt.nokia.com/products/)
* [PyQt](http://www.riverbankcomputing.co.uk/software/pyqt/intro) or [PySide](http://www.pyside.org/)

### Optional Dependencies
* Maya 2012 ([Free to students](http://students.autodesk.com/))

## Links
* [CADnano.org](http://cadnano.org/)
* [Maya 2012](http://usa.autodesk.com/maya/)

## Configuration
Configuration of tools (in terms of capabilities) is implemented
using class members. Some are listed below:
### VirtualHelix.prohibitSingleBaseCrossovers
If True, every time a modification is made to a VirtualHelix, it will check to
see if it has any single base crossovers and will fix them by connecting
them to the next base on the strand.
### SelectTool.limitEndptDragging
If True, dragging endpoints will be constrained so that it never
merges segments, creates segments, or destroys crossovers.
### SelectTool.disallowClickBreaksStrand
If True, prohibits the user from clicking in the middle of a segment to
break it.
### SelectTool.drawActionPreview
If True, the select tool will draw red and green lines on the perimeter
of the base the tool is hovering over to indicate what API operation will
be performed by dragging in a certain direction.
### SelectTool.colorPreview
If True, the select tool will draw a dot on the base being hovered over
that is the color of the underlying base (useful when you need to know
the color of a base that doesn't have any strand to exhibit its color with)