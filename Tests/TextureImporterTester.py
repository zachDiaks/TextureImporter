'''
This file defines unit tests for the TextureImporter. This file is to be run by
runTestSuite.py in the TextureImporter top level package. Thus, the base path is this
directory. 

Anything related to UI behavior is manually tested. 
'''
import unittest
from textureImporter import Tab
import os

class TextureImporterTester(unittest.TestCase):
    # Run on class setup
    def setUp(self):
        # Add main folder to search path
        self.app = Tab()
    
    # Verify cached paths matches the file
    def testCaching(self):
        if os.path.exists("paths.txt"):
            paths = self.grabPaths("paths.txt")
            melee = paths(0)
            gcr = paths(1)
        else:
            melee = "empty"
            gcr = "empty"
        assert melee == self.app.isoPath,"ISO Path not being found correctly"
        assert gcr == self.app.gcrPath,"GCR Path not being found correctly"

    # Verify that a known file is a valid name and a made up file is not a valid name
    def testValidNames(self):
        testFile = "PlFxNr.dat"
        badFile = "SickFoxPlFxNr.dat"
        assert self.app.isValidDatFile(testFile),"%s should be counted as a valid texture file"%testFile
        assert not self.app.isValidDatFile(badFile),"%s should NOT be counted as a valid texture file"%badFile

    # Test call string creation with nested directories in ZIP file
    def testNestingNoSpaces(self):
        fName = "Tests/TestNesting_NoSpaces.zip"
        textures = self.app.extractTextures(fName)
        for texture in textures:
            callStrs = self.app.buildCallStrings(texture)
            backupCallStr = callStrs(0)
            importCallStr = callStrs(1)
            # Do some validation here
    
    # Test call string creation with nested directories in ZIP file containing spaces
    def testNestingWithSpaces(self):
        self.app.files = "Tests/TestNesting_Spaces.zip"

    '''
    --------------------------
     Helper functions 
     --------------------------
    '''
    def grabPaths(self,file):
        with open(file) as f:
            lines = f.readlines()
            melee = lines[0].split(" ")[-1]
            gcr = lines[1].split(" ")[-1]
        return (melee,gcr)
        