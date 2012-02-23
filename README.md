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

# cadnano DNA Origami Software

## Overview
[cadnano](http://cadnano.org/) is software for design of 
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

## Environment options
Some environment variables convenient for debugging (or customizing to personal taste).
### CADNANO_IGNORE_ENV_VARS_EXCEPT_FOR_ME
Turns off other cadnano environment variables.
### CADNANO_DISCARD_UNSAVED
Don't prompt the user to save unsaved changes; just exit.
### CADNANO_DEFAULT_DOCUMENT
On creation of the default document, open the named file (put a path to the file
in the value of the environment variable) instead of a blank document.