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
[CADnano](http://cadnano.org/) is software for design of 
[DNA origami](http://en.wikipedia.org/wiki/DNA_origami) nanostructures. 
It was written with the goal of providing a simple and user-friendly interface 
to facilitate a process that can be complex and error-prone.

## Installation
* Download a [package installer](http://cadnano.org/beta.html)

### Required Dependencies
* [Qt 4.7](http://qt.nokia.com/products/)
* [PyQt](http://www.riverbankcomputing.co.uk/software/pyqt/intro) or [PySide](http://www.pyside.org/)
* [python-cjson](http://pypi.python.org/pypi/python-cjson)

### Optional Dependencies
* [Maya 2012](http://usa.autodesk.com/maya/) ([free to academics](http://students.autodesk.com/))

## Under the hood
Configuration of tools (in terms of capabilities) is implemented using class members. Some are listed below:
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

## Environment options
Some environment variables convenient for debugging (or customizing to personal taste).
### CADNANO_IGNORE_ENV_VARS_EXCEPT_FOR_ME
Turns off other cadnano environment variables.
### CADNANO_PENCIL_FIRST
Activates the pencil tool on document open instead of the select tool.
### CADNANO_DISCARD_UNSAVED
Don't prompt the user to save unsaved changes; just exit.
### CADNANO_DEFAULT_DOCUMENT
On creation of the default document, open the named file (put a path to the file
in the value of the environment variable) instead of a blank document.
### CADNANO_NO_THOUGHTPOLICE
Allow single base crossovers (and whatever other things the thoughtPolice() method
of VirtualHelix disallows)
### CADNANO_FSCK_AFTER_SELECT_TOOL_USE
Every time the mouse is released while in Select or Pencil mode and over a PathHelix
, fsck() is called on the frontmost part.