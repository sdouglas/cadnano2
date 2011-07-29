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
    if dirname == path.pardir:
        base = 'cadnano2' + path.sep
    else:
        base = 'cadnano2' + dirname[len(path.pardir):]
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
            try:
                shutil.copy(oldloc, newloc)
                errstr = ""
            except shutil.Error as e:
                errstr = " ERROR: " + str(e)
            print "\tcp %s %s"%(oldloc, newloc) + errstr
            contains_a_py_file = True
    if not contains_a_py_file:
        # Kill recursion
        del files[:]
path.walk(path.pardir, process_dir, None)
