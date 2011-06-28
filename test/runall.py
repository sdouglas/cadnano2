"""
runtests.py
Helper file to run tests with 1 command and output the results to an XML file.
Usage: From the main cadnano folder: python -m test.runtests
Created by Flo Mazzoldi on 2011-06-15.
"""

import unittest
from xmlrunner import XMLTestRunner
from unittests import UnitTests
from modeltests import ModelTests
from functionaltests import FunctionalTests


def main():
    unitsuite = unittest.makeSuite(UnitTests)
    modelsuite = unittest.makeSuite(ModelTests)
    funsuite = unittest.makeSuite(FunctionalTests)
    alltests = unittest.TestSuite([unitsuite, modelsuite, funsuite])
    stream = file("testresults.xml", "w")
    runner = XMLTestRunner(stream)
    result = runner.run(alltests)
    stream.close()
    return result

if __name__ == "__main__":
    main()
