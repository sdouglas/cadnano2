#!/usr/bin/python
import os
import os.path as path
import shutil

if not path.exists('build_dist.py'):
    print "The current working directory should be the folder this script resides in."
    exit(1)
if path.exists('cadnano2'):
    shutil.rmtree('cadnano2')
os.mkdir('cadnano2')
def process_dir(self, dirname, files):
    print "cb %s %s"%(dirname, files)
    if dirname == path.pardir:
        loc_in_proj = path.curdir
    else:
        loc_in_proj = dirname[len(path.pardir):]
    base = path.curdir + loc_in_proj + path.sep
    
    # Make sure the current directory exists
    print "mkdir -p %s"%base
    try:
        os.makedirs(base)
    except OSError:
        pass

    # Prevent infinite recursion
    try:
        files.remove('installer')
    except ValueError:
        pass

    # Copy .py files
    contains_a_py_file = False
    for f in files:
        if not path.isfile(path.join(dirname, f)):
            continue
        _, ext = path.splitext(f)
        if ext == '.py':
            oldloc = path.join(dirname, f)
            newloc = path.join(base, f)
            print "\tcp %s %s"%(oldloc, newloc)
            shutil.copy(oldloc, newloc)
            contains_a_py_file = True
    if not contains_a_py_file:
        # Kill recursion
        del files[:]
path.walk(path.pardir, process_dir, None)
