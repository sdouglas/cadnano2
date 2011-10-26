#!/usr/bin/python
import os, shutil, glob, re, subprocess
import os.path as path
import shutil

if not path.exists('build_pkg.py'):
    print "This script was designed to be run from the same directory in which it resides (cadnano2/install/osx)."
    exit(1)

install_root = os.environ.get('INSTROOT', path.abspath('./install_root'))
build_root = os.environ.get('BUILDROOT', path.abspath('./build/packager'))
def mkdir(dirpath):
    if path.exists(dirpath):
        try:
            shutil.rmtree(dirpath)
        except OSError as e:
            print "Could not clear out the old %s: "%dirpath, str(e)
            exit(1)
    os.makedirs(dirpath)
mkdir(install_root)
mkdir(build_root)
print "Using install staging area INSTROOT=%s"%install_root
print "Putting logs, etc in BUILDROOT=%s"%build_root

print "Packaging Qt..."
qtdir = '/Library/Frameworks'  # Hardcoded, fsck yeah!
qtdir_glob = qtdir + '/Qt*.framework'
qtdir_results = glob.glob(qtdir_glob)
qt_modules_to_copy = set(('Core', 'Svg', 'Gui'))
if not qtdir_results:
    print "Didn't find any! Try the library-only binaries (Cocoa, no debug symbols) from http://qt.nokia.com/downloads/qt-for-open-source-cpp-development-on-mac-os-x"
    exit(1)
else:
    print "\tFound Qt frameworks, will proceed with copying..."
    print "\tSkipping copy of frameworks except for those in", str(qt_modules_to_copy)
for qt_fmwk_path in qtdir_results:
    cp_from = qt_fmwk_path
    cp_to = install_root + qt_fmwk_path
    fmwk_name = re.match('.+Qt(\w+)\.framework', qt_fmwk_path).groups()[0]
    skip = fmwk_name not in qt_modules_to_copy
    print "\t%scp %s $INSTROOT/%s"%("# " if skip else "", cp_from, qt_fmwk_path)
    if skip: continue
    try:
        shutil.copytree(cp_from, cp_to, symlinks=True)
    except OSError as e:
        print str(e)
        exit(1)

def repackage_riverbank(pkgname, tarball_re_str, folder_re_str, download_url):
    print "Packaging %s..."%pkgname
    def sort_by_version(compiled_re, names):
        """Return a sorted version of names (higher version numbers first)"""
        annotated_names = [([int(n) for n in compiled_re.match(name).groups()], name) for name in names]
        annotated_names.sort()
        return [annotated_name[1] for annotated_name in reversed(annotated_names)]
    folder_re = re.compile(folder_re_str)
    candidates = filter(path.isdir, filter(folder_re.match, os.listdir('.') ))
    candidates = sort_by_version(folder_re, candidates)
    print "\tLooking in . for a %s directory matching /%s/..."%(pkgname, folder_re_str)
    print "\tFound (best first):", candidates
    if not candidates:
        pkg_tar_re = re.compile(tarball_re_str)
        candidate_tarballs = filter(path.isfile, filter(pkg_tar_re.match, os.listdir('.') ))
        print "matched:",str(filter(pkg_tar_re.match, os.listdir('.') ))
        print "\tLooking in . for a %s tarball (or .tar.gz) matching /%s/..."%(pkgname, tarball_re_str)
        if not candidate_tarballs:
            print "\tERROR: No candidate tarballs found. Try getting one from\n\t%s\n\tand putting it in %s"%(download_url, os.getcwd())
            exit(1)
        candidate_tarballs = sort_by_version(pkg_tar_re, candidate_tarballs)
        print "\tFound (best first):", candidate_tarballs
        print "\ttar xf '%s' 2>&1 >$BUILDROOT/%s_untar.log"%(candidate_tarballs[0], pkgname)
        logfile = file('%s/%s_untar.log'%(build_root, pkgname), 'w')
        untar = subprocess.Popen(('tar', 'xf', candidate_tarballs[0]), stdout=logfile, stderr=logfile)
        retval = untar.wait()
        print "\ttar's exit code:", retval
        if retval != 0:
            print "\tERROR: tar had a nonzero exit code"
            exit(1)
        # Hopefully by untarring we've generated a new candidate SIP folder
        candidates = filter(path.isdir, filter(folder_re.match, os.listdir('.') ))
        candidates = sort_by_version(folder_re, candidates)
        if not candidates:
            print "ERROR: Still can't find a %s folder?!"%pkgname
            exit(1)
    pkg_folder = candidates[0]
    print "\tcd", pkg_folder
    print "\tpython configure.py 2>&1 1>$BUILDROOT/%s_config.log"%pkgname
    pkg_config_log = file('%s/%s_config.log'%(build_root, pkgname), 'w')
    old_cwd = os.getcwd()
    os.chdir(pkg_folder)
    pkg_conf = subprocess.Popen(('python', 'configure.py'), stdout=pkg_config_log, stderr=pkg_config_log, stdin=subprocess.PIPE)
    pkg_conf.stdin.write('yes\n')
    pkg_conf.stdin.flush()
    if pkg_conf.wait() != 0:
        print "\tERROR: %s's configure.py returned a nonzero status"%pkgname
        exit(1)
    print "\tmake 2>&1 >$BUILDROOT/%s_make.log"%pkgname
    pkg_make_log = file('%s/%s_make.log'%(build_root, pkgname), 'w')
    pkg_build = subprocess.Popen('make', stdout=pkg_make_log, stderr=pkg_make_log)
    if pkg_build.wait() != 0:
        print"\tERROR: %s's make returned a nonzero exit status"%pkgname
        exit(1)
    print "\tmake install DESTDIR=%s  2>&1 >$BUILDROOT/%s_make_install0.log"%(install_root, pkgname)
    pkg_make_install_log = file('%s/%s_make_install0.log'%(build_root, pkgname), 'w')
    pkg_build = subprocess.Popen(('make', 'install', 'DESTDIR=%s'%install_root), stdout=pkg_make_install_log, stderr=pkg_make_install_log)
    if pkg_build.wait() != 0:
        print"\tERROR: %s's make install returned a nonzero exit status"%pkgname
        exit(1)
    # blow away possibly old root install
    print "\tmake install DESTDIR=%s  2>&1 >$BUILDROOT/%s_make_install1.log"%('/', pkgname)
    pkg_make_install_log = file('%s/%s_make_install1.log'%(build_root, pkgname), 'w')
    pkg_build = subprocess.Popen(('make', 'install', 'DESTDIR=%s' % '/'), stdout=pkg_make_install_log, stderr=pkg_make_install_log)
    if pkg_build.wait() != 0:
        print"\tERROR: %s's make install returned a nonzero exit status"%pkgname
        exit(1)
    print "\tcd", old_cwd
    os.chdir(old_cwd)


# SIP
# repackage_riverbank('sip', 'sip-(\d+).(\d+).*', 'sip-(\d+).(\d+).*', 'http://www.riverbankcomputing.co.uk/software/sip/download')


# PyQt
# repackage_riverbank('PyQt', 'PyQt-mac-gpl-(\d+).(\d+).(\d+).*', 'PyQt-mac-gpl-(\d+).(\d+).(\d+).*', 'http://www.riverbankcomputing.co.uk/software/pyqt/download')




# cadnano2.app
print "Building cadnano2.app..."
print "\txcodebuild -configuration Release 2>&1 >$BUILDROOT/xcodebuild.log"
xcodebuild_out = file('%s/xcodebuild.log'%build_root, 'w')
xcodebuild = subprocess.Popen(('xcodebuild', '-configuration', 'Release'), stdout=xcodebuild_out, stderr=xcodebuild_out)
if xcodebuild.wait() != 0:
    print "\tERROR: xcodebuild returned a nonzero exit status"
    exit(1)
print "\tmkdir %s/Applications"%install_root
os.mkdir('%s/Applications'%install_root)
print "\tcp build/Release/cadnano2.app %s/Applications"%install_root
try:
    shutil.copytree('build/Release/cadnano2.app', '%s/Applications/cadnano2.app'%install_root, symlinks=True)
except OSError as e:
    print "\tERROR: failed to copy cadnano2.app:", str(e)
    exit(1)




# cadnano.pkg : cadnano2.app PyQt SIP
print "Building cadnano.pkg"
print "\tDetermining version from cadnano2-Info.plist(CFBundleVersion)..."
info_plist_path = path.abspath('./cadnano2-Info')
versionreporter = subprocess.Popen(('defaults', 'read', info_plist_path, 'CFBundleVersion'), stdout=subprocess.PIPE)
version_out, version_err = versionreporter.communicate()
if versionreporter.returncode != 0:
    print "\tERROR: defaults utility returned nonzero exit code."
    exit(1)
version = version_out.strip()
print "\tUsing version = '%s'."%version

pkgmaker_out = file('%s/packagemaker.log'%build_root, 'w')
pkgmaker_args = ('/Developer/usr/bin/packagemaker',\
                 '--install-to', '/',\
                 '--root', install_root,\
                 '--out', 'cadnano2.pkg',\
                 '--id', 'org.cadnano.allinone',\
                 '--title', 'CADnano2',\
                 '--resources', 'InstallerResources',\
                 '--version', version,\
                 '--no-relocate')
print "\t%s 2>&1 >$BUILDROOT/packagemaker.log"%(" ".join(pkgmaker_args))
pkgmaker = subprocess.Popen(pkgmaker_args, stdout=pkgmaker_out, stderr=pkgmaker_out)
if pkgmaker.wait() != 0:
    print "\tERROR: packagemaker had a nonzero exit status."
    exit(1)

exit(0)
