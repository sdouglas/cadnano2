"""
runtests.py
Helper file to run tests with 1 command and output the results to an XML file.
Usage: From the main cadnano folder: python -m tests.runtests
TextMate Usage: copypaste the following script into TextMate's
Bundles > Bundle Editor > Show Bundle Editor > Python > Run Project Unit Tests

cd "$TM_PROJECT_DIRECTORY"
CADNANO_RUN_PLAINTEXT_TESTS=YES python tests/runall.py | pre


Created by Flo Mazzoldi on 2011-06-15.
"""

import glob
import os
import unittest
from xmlrunner import XMLTestRunner
from unittests import UnitTests
from modeltests import ModelTests
from functionaltests import FunctionalTests
from recordedtests.template import RecordedTests

# load hard-coded tests
unitsuite = unittest.makeSuite(UnitTests)
modelsuite = unittest.makeSuite(ModelTests)
funsuite = unittest.makeSuite(FunctionalTests)

# load recorded tests
os.chdir('tests/recordedtests')
tests = glob.glob("recordedtest_*.py")  # get all the recorded tests
for test in tests:
    mod, ext = os.path.splitext(os.path.split(test)[-1])
    m = __import__(mod)  # dynamic import magic
    testname = "testMethod" + mod[-3:]  # recover test number
    setattr(RecordedTests, testname, m.testMethod)
os.chdir('../..')
recsuite = unittest.makeSuite(RecordedTests)

# One suite to run them all
suite = unittest.TestSuite([unitsuite, modelsuite, funsuite, recsuite])

def main(useXMLRunner=True):
    if useXMLRunner:
        stream = file("testresults.xml", "w")
        runner = XMLTestRunner(stream)
        result = runner.run(suite)
        stream.close()
    else:
        print "Plain Text!"
        runner = unittest.TextTestRunner(verbosity=2)
        result = runner.run(suite)
    return result


if __name__ == "__main__":
    useXMLRunner = 'CADNANO_RUN_PLAINTEXT_TESTS' not in os.environ
    print "Running all tests. Using XMLTestRunner: %s"%useXMLRunner
    main(useXMLRunner=useXMLRunner)
