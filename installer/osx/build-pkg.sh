#!/bin/sh
if [ ! -f ./build-pkg.sh ]; then
	echo "This script was designed to be run from the current working directory."
	exit 1
fi

PYQT_DIR=`python <<END_PY
print 

tar vxf /Users/jon/Downloads/PyQt-mac-gpl-4.8.4.tar.gz 2>&1 | head -n 1