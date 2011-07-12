$(INSTALL_PROGRAM) foo $(bindir)/foo
$(INSTALL_DATA) libfoo.a $(libdir)/libfoo.a

# Copy cadnano source files into the app
import os, sys
from subprocess import Popen, PIPE

home_dir = os.environ['HOME']

def main(argv=None):
    if argv is None:
        argv = sys.argv
    # end if
    
    # get this file's directory
    sourcepath = os.path.dirname( os.path.realpath( __file__ ) )
    # go up one level
    cadnano_dir = os.path.dirname(sourcepath)
    # go up another level
    cadnano_dir = os.path.dirname(cadnano_dir)
    built_products_dir = installpath + '/'+ argv[1]

    exec_name = cadnano2
    exec_from_prod_dir = executable_path
    exec_folder = os.path.dirname(built_products_dir + '/' + exec_from_prod_dir)

    #Remove old files
    for f in os.listdir(exec_folder):
        if f == exec_name:
            continue
        retval = Popen(('rm', '-rf', exec_folder + '/' + f)).wait()

    os.chdir(cadnano_dir)
    pyfiles = Popen(('find', '.', '-name', '*.py', '-print0'), stdout=PIPE).communicate()[0].split("\0")
    dirs_containing_pyfiles = set(os.path.dirname(f) for f in pyfiles)

    #Create directory structure
    for d in dirs_containing_pyfiles:
        destination_d = exec_folder+'/'+d
        retval = Popen(('install', '-d', destination_d)).wait()
        if retval != 0:
            print "install -d %s => %i"%(destination_d, retval)

    #Fill it with the pyfiles
    for f in pyfiles:
        if not f.strip():
            continue
        destination_f = exec_folder + '/' + f
        retval = Popen(('install', '-p', f, destination_f)).wait()
        if retval != 0:
            print "install %s %s => %i"%(f, destination_f, retval)
# end main

if __name__ == "__main__":
    sys.exit(main())
