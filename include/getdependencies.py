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

from fetchfile import fetchFile
import shutil
from os.path import basename, dirname, splitext, exists, split, abspath
import os

# list of tuples of the url and the subdirectory to copy to the include directory
urls = [('http://pypi.python.org/packages/source/n/networkx/networkx-1.6.tar.gz', 'networkx')
        ]

# this is intended to be run in the include folder of cadnano2
if __name__ == '__main__':
    for urlBlock in urls:
        url, subfolder_name = urlBlock
        filename = basename(url)
        base_url = dirname(url)
        folder = fetchFile(filename, base_url)
        this_dirname, this_filename = split(abspath(__file__))
        os.chdir(this_dirname)
        if subfolder_name:
            subfolder_path = folder + '/' + subfolder_name
            # remove existing folder
            if os.path.exists(subfolder_name):
                print "file exists"
                shutil.rmtree(subfolder_name)
            else:
                print "file does not exist", subfolder_name
            shutil.move(subfolder_path, subfolder_name)
            shutil.rmtree(folder)
    # end for
