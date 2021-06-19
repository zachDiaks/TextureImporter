from kivy.app import App
from kivy.lang import Builder
from kivy.uix.tabbedpanel import TabbedPanel
from kivy.properties import StringProperty
import tkinter as tk
from tkinter.filedialog import askopenfilename
from tkinter.filedialog import askopenfilenames
from zipfile import ZipFile as unzipper, is_zipfile
import subprocess
import shutil
import os

Builder.load_file("tabImpl.kv")

class Tab(TabbedPanel):
    # Declare properties for the tab group
    isoPath = StringProperty()
    gcrPath = StringProperty()
    filePath = StringProperty()
    instructionsText = StringProperty()
    status = StringProperty()
    fileList = StringProperty()
    
    def __init__(self, **kwargs):
        super(Tab, self).__init__(**kwargs)
        self.isoPath = "empty"
        self.gcrPath = "empty"
        self.filePath = "empty"
        self.files = []
        self.status += "Logs:\n"
        self.getCachedPaths()
        self.instructionsText = "Instructions coming!"
        self.isValidISO = False
        self.isValidgcr = False
        self.firstTime = True
        self.thisPath = os.getcwd()

    '''
    Find the cached paths, and create paths.txt if it doesn't exist
    '''
    def getCachedPaths(self):
        if os.path.isfile("paths.txt"):
            self.validatePathsText()
            with open("paths.txt","r") as f:
                for line in f:
                    if line.startswith("Melee"):
                        self.status += "Getting cached Melee ISO... "
                        self.isoPath = line.split(" ")[1]
                        self.status += "Success!\n"
                    elif line.startswith("gcr"):
                        self.status += "Getting cached gcr.exe..."
                        self.gcrPath = line.split(" ")[1]
                        self.status += "Success!\n"
                    else:
                        pass
    '''
    This function is used to ensure that the paths.txt file is in a 'good' state such that:
        - Each line has two parts: The identifier (e.g. 'Melee') and the path
    If the file is not in a good state, empty the file and notify the user. 
    '''
    def validatePathsText(self):
        with open("paths.txt","r") as f:
            lines = f.readlines()
        clearFile = False
        if len(lines) == 2:
            # Validate each line
            clearFile = not(self.isValidLine(lines[0]) and self.isValidLine(lines[1]))
        elif len(lines) == 1:
            # Validate the line that's there.
            clearFile = not self.isValidLine(lines[0])
        else:
            # It's okay if there's no lines in the file. The user will have to specify the paths again. Do nothing here.
            pass
        if clearFile:
            self.status += "There was an issue fetching the cached files. Clearing the cache now (paths.txt should be empty)\n"
            with open("paths.txt","w") as f:
                f.writelines([])
    '''
    Helper function to ensure that each line has:
        - fileID in position 1
        - Some sort of path in position 2
    '''
    def isValidLine(self,line):
        temp = line.split(" ")
        return len(temp) == 2 and temp.count("") < 1
            
            
    '''
    Callback for both ISO and gcr selection
    '''
    def setPaths(self,fileType,extension):
        # Open file dialogue, but not Tk window
        tk.Tk().withdraw()
        potentialPath = askopenfilename()
        # Validate the file extension
        if (potentialPath.split("/")[-1][-4:] == "." + extension):

            # Cache file location
            self.status += "Caching " + fileType + " to paths.txt\n"
            newLines = []

            # I started a comment but forgot what this is supposed to be
            if fileType == "Melee":
                if self.isoPath == "empty":
                    with open(self.thisPath + '/paths.txt','a+') as f:
                        f.write(fileType + " " + potentialPath + "\n")
                # Update the correct line in the file
                else:
                    with open(self.thisPath + '/paths.txt','r') as f:
                        for line in f:
                            self.status += line + "\n"
                            if line.startswith(fileType):
                                line = fileType + " " + potentialPath + "\n"
                            newLines.append(line)
            
                self.isoPath = potentialPath
                self.status += fileType + " cached\n"
            else:
                if self.gcrPath == "empty":
                    with open(self.thisPath + '/paths.txt','a+') as f:
                        f.write(fileType + " " + potentialPath + "\n")
                # Update the correct line in the file
                else:
                    with open(self.thisPath + '/paths.txt','r') as f:
                        for line in f:
                            if line.startswith(fileType):
                                line = fileType + " " + potentialPath + "\n"
                            newLines.append(line)
            
                self.gcrPath = potentialPath
                self.status += fileType + " cached\n"

            if len(newLines) > 0:
                with open("paths.txt",'w') as f:
                    # Re-write the new file if we need to update a path
                    f.writelines(newLines)

        # Handle no file chosen                    
        elif potentialPath == "":
            # Do nothing because file was not actually selected
            self.status += "No file was selected\n"

        # Tell the user no file has been chosen
        else:
            self.status = self.status + "The selected file isn't an ISO. Please select a Melee iso\n"
    
    '''
    Callback for file selection
    '''
    def getFiles(self):
        # Reset the selected files
        self.files = []
        self.fileList = ""
        # Ask user to select files
        tk.Tk().withdraw()
        self.files = askopenfilenames(filetypes=[("ZIP Files", ".zip")])
        
        # Let the user know that no files were chosen
        if len(self.files) == 0:
            self.status += "No files were selected for import\n"
        else:
            # Update status
            self.status += "Files selected for import:\n"
            for f in self.files:
                self.fileList += f + "\n"
                self.status += f + "\n"
    
    '''
    Main callback for importing the files into ISO
    '''
    def importFiles(self):
        if len(self.files) == 0:
            self.status += "No files were selected for import. Ignoring button press.\n"
        
        # Only begin the import process if the user selected ZIP files
        for f in self.files:
            if not is_zipfile(f):
                self.status += f + " is not a ZIP file. Skipping this file.\n"
            else:
                # Import the textures from this ZIP file
                importStatus = self.fileImporter(f)
                if importStatus == 0:
                    self.status += "Imported textures from " + f + "\n"
                else:
                    self.status += "Import error. See above log.\n"
    
    '''
    Helper function for importFiles. This does most of the work.
    '''
    def fileImporter(self,fName):
        # This variable will broadcast the result of import attempt
        # 0 = success
        # -1 = failure (along with updating status string for failure reason)
        returnVal = 0
        # Create a temporary folder to extract files
        if not os.path.isdir("temp"):
            os.mkdir("temp")
        
        # Create a backup folder for the textures you're replacing
        if not os.path.isdir("backup"):
            os.mkdir("backup")

        with unzipper(fName,'r') as f:
            self.status += "Extracting files\n"
            f.extractall("temp")
        
        # Parse through the extracted files and try importing into Melee ISO
        # Back up the old files into a backup folder
        textures = os.listdir("temp")
        for texture in textures:
            # Validate the texture extension
            if texture[-3:] != "dat":
                self.status += "File doesn't have .dat extension. Skipping this file.\n"
            else:
                # This is where the magic happens!
                # Build call string and call gcr
                nodePath = "root/" + texture
                textureImportPath = "temp/" + texture
                textureBackupPath = "backup/" + texture
                backupCallStr = "%s %s %s e %s"%(self.gcrPath,self.isoPath,
                    nodePath,textureBackupPath)
                importCallStr = "%s %s %s i %s"%(self.gcrPath,self.isoPath,
                    nodePath,textureImportPath)
                try:
                    self.status += "Trying to import texture... \n"
                    subprocess.call(backupCallStr,shell=False)
                    subprocess.call(importCallStr,shell=False)
                    self.status += "Import success! \n"
                except Exception as e:
                    self.status += e + "\n"
                    self.status += "Unknown import error.\n"
                    returnVal = -1
        # Remove temporary folder to avoid unnecessary imports
        shutil.rmtree("temp")
        return returnVal
        
class TextureImporter(App):
    def build(self):
        return Tab()

if __name__ == "__main__":
    TextureImporter().run()