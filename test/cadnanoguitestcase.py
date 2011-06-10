from PyQt4.QtCore import *
from PyQt4.QtGui import *
import test.guitestcase

from cadnano import app as getAppInstance

main = test.guitestcase.main

#SEE: http://docs.python.org/library/unittest.html
class CadnanoGuiTestCase(test.guitestcase.GUITestCase):
	def setUp(self):
	    """
	    The setUp method is called before running any test. It is used
	    to set the general conditions for the tests to run correctly.
	    For GUI Tests, you always have to call setWidget to tell the
	    framework what you will be testing.
	    """
	    self.app = getAppInstance()
	    self.mainWindow = list(self.app.documentControllers)[0].win
	    # By setting the widget to the main window we can traverse and
	    # interact with any part of it. Also, tearDown will close
	    # the application so we don't need to worry about that.
	    self.setWidget(self.mainWindow, False, None)

	def tearDown(self):
	    """
	    The tearDown method is called at the end of running each test,
	    generally used to clean up any objects created in setUp
	    """
	    test.guitestcase.GUITestCase.tearDown(self)
	    	    
if __name__ == '__main__':
	test.guitestcase.main()