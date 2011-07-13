#!/usr/bin/env python

# run python setup.py bdist_rpm --requires="PyQt4" --group="Application/Engineering" --icon=
# install with yum install *.rpm

from distutils.core import setup
import sys
sys.prefix = '/usr/local/cadnano'

setup(name='CADnano',
      version='1.5',
      description='Python Distribution Utilities',
      author='Wyss Institute',
      author_email='wyss@wyss.harvard.edu',
      url='http://www.cadnano.org/',
      packages=['cadnano2'],
     )
