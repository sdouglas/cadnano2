from PyQt4.QtCore import *
from PyQt4.QtGui import *
from test.cadnanoguitestcase import CadnanoGuiTestCase
import time

from cadnano import app as getAppInstance

#SEE: http://docs.python.org/library/unittest.html
class SampleTests(CadnanoGuiTestCase):
	def setUp(self):
	    """
	    The setUp method is called before running any test. It is used
	    to set the general conditions for the tests to run correctly.
	    """
	    CadnanoGuiTestCase.setUp(self)
	    # Add your initialization here
	    # self.app gives you a pointer to the application object
	    pass

	def tearDown(self):
	    """
	    The tearDown method is called at the end of running each test,
	    generally used to clean up any objects created in setUp
	    """
	    CadnanoGuiTestCase.tearDown(self)
	    # Add your clean up here
	    pass
	    
	
	def testFirst(self):
	    """
	    This is a sample test. It uses the CADnano application, clicks on a button
	    and ensures that the slice view changes appropriately.
	    """
	    # You need to traverse the UI looking for the widgets you want to
	    # interact with
	    myWidget = self.mainWindow.topToolBar.widgetForAction(self.mainWindow.actionNewHoneycombPart)
	    # See the GUITestCase for all the operations you can do to
	    # widgets
	    self.click(myWidget)
	    
	    # Do this if you want the simulation to wait for 1 second
	    #time.sleep(1)
	    
	    # Do this if you want the simulation to stop and give control to the
	    # user
	    # self.debugHere()
	    
	    # Do this for assertions. You can use any assertion in the python
	    # unit test framework, and use self.app as the starting point to check the
	    # state of the application
	    self.assertEqual(2,2)

	def testSecond(self):
	    # Another test in this class. Note that the tests'
	    # names must start with "test"
	    self.assertEqual(1,1)

import test.cadnanoguitestcase	    
if __name__ == '__main__':
	test.cadnanoguitestcase.main()