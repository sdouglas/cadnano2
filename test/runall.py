"""
runtests.py
Helper file to run tests with 1 command and output the results to an XML file.
Usage: From the main cadnano folder: python -m test.runtests
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

def main():
    # load hard-coded tests
    unitsuite = unittest.makeSuite(UnitTests)
    modelsuite = unittest.makeSuite(ModelTests)
    funsuite = unittest.makeSuite(FunctionalTests)

    # load recorded tests
    os.chdir('test/recordedtests')
    tests = glob.glob("recordedtest_*.py")  # get all the recorded tests
    for test in tests:
        mod, ext = os.path.splitext(os.path.split(test)[-1])
        m = __import__(mod)  # dynamic import magic
        testname = "testMethod" + mod[-3:]  # recover test number
        setattr(RecordedTests, testname, m.testMethod)
    recsuite = unittest.makeSuite(RecordedTests)

    # combine and run tests
    alltests = unittest.TestSuite([unitsuite, modelsuite, funsuite, recsuite])
    stream = file("testresults.xml", "w")
    runner = XMLTestRunner(stream)
    result = runner.run(alltests)
    stream.close()
    return result


if __name__ == "__main__":
    main()
