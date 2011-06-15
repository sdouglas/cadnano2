"""
runtests.py
Helper file to run tests with 1 command and output the results to an XML file.
Usage: From the main cadnano folder: python -m test.runtests
Created by Flo Mazzoldi on 2011-06-15.
"""

from xmlrunner import XMLTestRunner
from sampletest import SampleTests
import unittest

def runAll():
    suite = unittest.makeSuite(SampleTests)
    stream = file("testresults.xml", "w")
    runner = XMLTestRunner(stream)
    result = runner.run(suite)
    stream.close()
    return result

if __name__ == "__main__":
    runAll()