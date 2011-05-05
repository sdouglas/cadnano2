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

class LatticeType:
    Honeycomb = 0
    Square = 1


class EndType:
    FivePrime = 0
    ThreePrime = 1


class StrandType:
    Scaffold = 0
    Staple = 1


class Parity:
    Even = 0
    Odd = 1


class BreakType:
    Left5Prime = 0
    Left3Prime = 1
    Right5Prime = 2
    Right3Prime = 3


class Crossovers:
    honeycombScafLeft = [[1, 11], [8, 18], [4, 15]]
    honeycombScafRight = [[2, 12], [9, 19], [5, 16]]
    honeycombStapLeft = [[6], [13], [20]]
    honeycombStapRight = [[7], [14], [0]]
    squareScafLeft = [[4, 26, 15], [18, 28, 7], [10, 20, 31], [2, 12, 23]]
    squareScafRight = [[5, 27, 16], [19, 29, 8], [11, 21, 0], [3, 13, 24]]
    squareStapLeft = [[31], [23], [15], [7]]
    squareStapRight = [[0], [24], [16], [8]]


class HandleOrient:
    LeftUp = 0
    RightUp = 1
    LeftDown = 2
    RightDown = 3
