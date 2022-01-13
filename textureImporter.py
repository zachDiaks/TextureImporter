from kivy.app import App
from kivy.core.text import Label
from kivy.lang import Builder
from kivy.uix.popup import Popup
from kivy.uix.button import Button
from kivy.uix.tabbedpanel import TabbedPanel
from kivy.uix.tabbedpanel import TabbedPanelItem
from kivy.uix.floatlayout import FloatLayout
from kivy.properties import StringProperty
from kivy.uix.dropdown import DropDown
from kivy.uix.popup import Popup
import tkinter as tk
from tkinter.filedialog import askopenfilename
from tkinter.filedialog import askopenfilenames
from zipfile import ZipFile as zipper, is_zipfile
import subprocess
import shutil
import os
import datetime

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
        self.resolveTab = self.makeResolveTab()

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
    Create a new tab where a user can resolve incorrect file names. This function is used to set the 
    resolveTab property so that we can use it downstream when checking file names.
    '''
    def makeResolveTab(self):
        # Create the panel
        tp = TabbedPanelItem()
        tp.text = "Resolve Names"
        self.add_widget(tp)

        # Float layout
        fl = FloatLayout()
        tp.add_widget(fl)

        filenameDropdown = DropDown()
        variantDropdown = DropDown()
        
        # Set up main button
        charButton = Button(text="Choose Character",size_hint =(None, None), pos =(150, 350))
        charButton.bind(on_release = filenameDropdown.open)
        
        variantButton = Button(text="Choose Variant",size_hint=(None,None),pos = (500,350))
        variantButton.bind(on_release=variantDropdown.open)
        
        variantDropdown.bind(on_select = lambda instance, x: setattr(variantButton, 'text', x)) # Set button to whatever is selected
        filenameDropdown.bind(on_select = lambda instance, x: setattr(charButton, 'text', x)) # Set button to whatever is selected
        
        fl.add_widget(charButton)
        fl.add_widget(variantButton)

        # Read file contents and grab names of characters
        with open("validFileNames.txt","r") as f:
            lines = f.readlines()
        names = [x[2:] for x in lines if "##" in x]

        # Populate the filename dropdown with character names
        for i in range(1,len(names)):
            btn = Button(text=names[i],size_hint=(None,None), height = 40)
            btn.bind(on_release=lambda btn: filenameDropdown.select(btn.text))
            filenameDropdown.add_widget(btn)

        # Populate the variant dropdown with color options
        colors = ["normal","red","orange","blue","lavender","green","black"]
        for i in range(1,len(colors)):
            btn = Button(text=colors[i],size_hint=(None,None), height = 40)
            btn.bind(on_release=lambda btn: variantDropdown.select(btn.text))
            variantDropdown.add_widget(btn)

        # Action button to perform the resolution
        resolveButton = Button(text="Resolve files",size_hint=(None,None),pos=(200,200),height=40)
        fl.add_widget(resolveButton)

        # Return
        return tp

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
            self.status += "making temp folder \n"
            os.mkdir("temp")
        
        # Create a backup folder for the textures you're replacing
        if not os.path.isdir("backup"):
            os.mkdir("backup")

        with zipper(fName,'r') as f:
            self.status += "Extracting files\n"
            f.extractall("temp")
        
        # Parse through the extracted files and try importing into Melee ISO
        # Back up the old files into a backup folder
        textures = os.listdir("temp")
        for texture in textures:
            # Validate the texture extension
            if texture[-3:] != "dat":
                self.status += "File doesn't have .dat extension. Skipping this file.\n"
            if not self.isValidDatFile(texture):
                self.createPopup(texture)
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

                # Remove any newline chars
                backupFix = backupCallStr.split("\n") 
                backupCallStr = "".join(backupFix)
                importFix = importCallStr.split("\n")  
                importCallStr = "".join(importFix)

                try:
                    self.status += "Trying to import texture... \n"
                    subprocess.call(backupCallStr,shell=False)
                    subprocess.call(importCallStr,shell=False)
                    self.status += "Import success! \n"
                    self.status += "Backing up old textures to ZIP file...\n"
                    self.zipBackupFiles()
                    self.status += "Backup success!\n"
                except Exception as e:
                    self.status += e.__str__() + "\n"
                    self.status += "Unknown import error.\n"
                    returnVal = -1
        # Remove temporary folder to avoid unnecessary imports
        shutil.rmtree("temp")
        return returnVal

    '''
    Helper function to throw all of the backed up files into a ZIP folder that can be re-imported at a later date. 
    Essentially, just find any file that's not a ZIP and ZIP them using the current date and time.
    '''
    def zipBackupFiles(self):
        allFiles = os.listdir("backup")
        exportedFiles = [file for file in allFiles if file[-4:] != ".zip"]
        thisTime = datetime.datetime.now()
        fileName = "backup/backup_" +  str(thisTime.year) + str(thisTime.month) + str(thisTime.day) + "_" + str(thisTime.hour) + str(thisTime.minute) + str(thisTime.second) + ".zip"
        zipObj = zipper(fileName,'w')
        for file in exportedFiles:
            zipObj.write("backup/" + file)
            os.remove("backup/" + file)            
        zipObj.close()

    '''
    Helper function to allow the user to re-name their texture so that it has the name corresponding to the texture they're trying to import. 
    GCR requires the texture name to match the default name in the Melee ISO. 
    Example:
        - User downloads textures.ZIP which contains:
            - PlFxNr.dat --> This is the expected name for the default Fox texture. 
            - MySickRedFox.dat --> This name doesn't match the corresponding Melee ISO name for Red Fox. It needs to br 
                                   re-named to PlFxOr.dat 
    Implementation:
        - Open a new UI that's layed out as:
            Prompt to explain what's going on with the original file name
            Drop-down to identify what texture type they're trying to change...
                - Stage?
                - Character? 
                - Something else? Not sure what other textures there are...
            Drop-down for the character/stage
            Drop-down for the variant (red,blue,normal,etc.)
        - Look up the                                  
    '''
    def createPopup(self,textureName):
        # Update the log
        self.status += "This file " + textureName + " has a different name than is required by the Melee ISO. Popup deployed for file name resolution.\n"

        # Create a notification popup 
        popup = Popup(title="Resolve file name",size=(400,400))
        dismissButton = Button(text="Press to dismiss message")
        popup.add_widget(dismissButton)
        dismissButton.bind(on_press=popup.dismiss)
        popup.open()


    def isValidDatFile(self,textureName):
        return False # Setting to false for now to test popup behavior.
        
class TextureImporter(App):
    def build(self):
        return Tab()

if __name__ == "__main__":
    TextureImporter().run()