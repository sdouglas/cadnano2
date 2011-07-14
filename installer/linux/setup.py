#!/usr/bin/env python

# run python setup.py bdist_rpm --requires="PyQt4" --group="Application/Engineering" --icon=
# install with yum install *.rpm

from distutils.core import setup
import sys
import os
sys.prefix = '/usr/local/cadnano'

# get this file's directory
sourcepath = os.path.dirname( os.path.realpath( __file__ ) )
# go up one level
cadnano_dir = os.path.dirname(sourcepath)
# go up another level
cadnano_dir = os.path.dirname(cadnano_dir)

# get one directory above cadnano2
sys.path.insert(0, os.path.dirname(cadnano_dir))

setup(name='CADnano',
      version='1.5',
      description='DNA Origami Design Software',
      author='Wyss Institute',
      author_email='wyss@wyss.harvard.edu',
      url='http://www.cadnano.org/',
      packages=['cadnano2'],
      package_dir = {'' : ''}
     )
