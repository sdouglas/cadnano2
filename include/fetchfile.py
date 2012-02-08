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

from urllib2 import Request, urlopen, URLError, HTTPError
import sys
from os.path import basename, dirname, splitext, exists
import os
import shutil
import tarfile

def fetchFile(filename, baseurl, filemode='b', filetype='gz', filepath=None):
    """
    
    filepath - is optional file path location to store the fetched file
    """
    # create the url and the request
    url = baseurl + '/' + filename
    request = Request(url)

    # Open the url
    try:
        f_url = urlopen(request)
        print "downloading " + url

        # Open our local file for writing
        f_dest = open(filename, "w" + filemode)
        
        # Write to our local file
        f_dest.write(f_url.read())
        f_dest.close()
        
    # handle errors
    except HTTPError, e:
        print "HTTP Error:", e.code , url
    except URLError, e:
        print "URL Error:", e.reason , url
    
    filename_out = filename
    # unzip if possible
    if filetype == 'gz':
        
        # get the extracted folder name
        filename_out = splitext(filename)[0]
        temp = splitext(filename_out)
        if temp[1] == '.tar':
            filename_out = temp[0]
        
        # open the archive
        try:
            f_zip= tarfile.open(filename, mode='r')
        except tarfile.ReadError, e:
            print "unable to read archive", e.code
        print "extracting " + filename_out
        try:
            if filepath:
                # remove existing folder
                if os.path.exists(filepath + '/' + filename_out):
                    print "file exists"
                    shutil.rmtree(filepath + '/' + filename_out)
                else:
                    print "file does not exist", filename_out
                f_zip.extractall(path=filepath)
            else:
                # remove existing folder
                if os.path.exists(filename_out):
                    print "file exists"
                    shutil.rmtree(filename_out)
                else:
                    print "file does not exist", filename_out
                f_zip.extractall()
        except tarfile.ExtractError, e:
            print "unable to extract archive", e.code
        f_zip.close()
        # remove the archive
        print "removing the downloaded archive", filename
        os.remove(filename)
        print "done"
    return filename_out
# end def

if __name__ == '__main__':
    argv = sys.argv
    url = argv[1]
    filename = basename(url)
    base_url = dirname(url)
    fetchFile(filename, base_url)

