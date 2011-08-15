
# Install instructions
    
    # If necessary create the project
    qmake -project -t lib -o testitem.pro
    # add CONFIG += x86_64 to testitem.pro
    qmake
    xcodebuild
    
    # ensure that the library built for the correct architecture with:
    lipo -info libtestitem.dylib
    # make sure the built library is on the linker PATH
    export DYLD_LIBRARY_PATH=`pwd`:$DYLD_LIBRARY_PATH
    python configure.py  # this configures the build
    make           # this builds the modules
    make install # this installs the modules to your current python install