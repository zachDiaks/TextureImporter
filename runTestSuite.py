import unittest

from Tests.TextureImporterTester import TextureImporterTester

def makeTestSuite():
    suite = unittest.TestSuite()
    suite.addTest(TextureImporterTester("testCaching"))
    suite.addTest(TextureImporterTester("testValidNames"))
    return suite

if __name__ == "__main__":
    suite = makeTestSuite()
    runner = unittest.TextTestRunner()
    runner.run(suite)