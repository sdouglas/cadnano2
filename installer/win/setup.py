from distutils.core import setup  
import py2exe  
import sys

# go one directory above the cadnano2 directory to get it on the path
sys.path.insert(0, '../../../')
  
setup(name="cadnano2",  
      version="1.5",  
      author="Nick Conway",  
      author_email="nick.conway@wyss.harvard.edu",  
      #url="",  
      license="MIT License",  
      packages=['cadnano2'],  
      package_data={"cadnano2": ["ui/mainwindow/images/*"]},
      windows=['main.py'],  
      options={"py2exe": {"skip_archive": True, "includes": ["sip"]}})