from kivy.app import App
from kivy.uix.label import Label
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
        self.badFileDropdown = None
        self.BadLabel = None
        self.bSize = (200,100)
        self.files = []
        self.status += "- Logs:\n"
        self.getCachedPaths()
        self.instructionsText = "Instructions coming!"
        self.isValidISO = False
        self.isValidgcr = False
        self.firstTime = True
        self.thisPath = os.getcwd()
        self.validNames = self.getValidNames()
        self.resolveTab = self.makeResolveTab()
        self.problemFiles = []
        

    '''
    Find the cached paths, and create paths.txt if it doesn't exist
    '''
    def getCachedPaths(self):
        if os.path.isfile("paths.txt"):
            self.validatePathsText()
            with open("paths.txt","r") as f:
                for line in f:
                    if line.startswith("Melee"):
                        self.status += "- Getting cached Melee ISO... "
                        self.isoPath = line.split(" ")[1]
                        self.status += "- Success!\n"
                    elif line.startswith("gcr"):
                        self.status += "- Getting cached gcr.exe..."
                        self.gcrPath = line.split(" ")[1]
                        self.status += "- Success!\n"
                    else:
                        pass
    '''
    Grab all valid texture names
    '''                
    def getValidNames(self):
        with open("validFileNames.txt","r") as f:
            lines = f.readlines()
        return [line[:-1] for line in lines] # Remove escape chars
        
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
        badFileDropdown = DropDown()

        # Set up main buttons
        badFileButton = Button(text="Choose File to Resolve",size_hint =(None, None), pos =(275,325),size=self.bSize)
        badFileButton.bind(on_release = badFileDropdown.open)
        
        charButton = Button(text="Choose Character",size_hint =(None, None), pos =(100,200),size=self.bSize)
        charButton.bind(on_release = filenameDropdown.open)
        
        variantButton = Button(text="Choose Variant",size_hint=(None,None),pos = (450,200),size=self.bSize)
        variantButton.bind(on_release=variantDropdown.open)
        
        variantDropdown.bind(on_select = lambda instance, x: setattr(variantButton, 'text', x)) # Set button to whatever is selected
        filenameDropdown.bind(on_select = lambda instance, x: setattr(charButton, 'text', x)) # Set button to whatever is selected
        badFileDropdown.bind(on_select = lambda instance, x: setattr(badFileButton, 'text', x)) # Same as above
        self.badFileDropdown = badFileDropdown # TODO: cleaner way to wire this up?
        
        fl.add_widget(charButton)
        fl.add_widget(variantButton)
        fl.add_widget(badFileButton)

        # Create a mapping from character/stage to variant
        mapping = {}
        variants = []
        cItem = []
        for line in self.validNames:
            if "##" in line:
                if variants:
                    mapping[cItem] = variants
                cItem = line[2:]
                variants = []
            else:
                variants.append(line)
        mapping[cItem] = variants

        # Populate the filename dropdown with the mapping
        for key in mapping:
            itemButton = Button(text=key,size_hint=(None,None),size=self.bSize)
            itemButton.bind(on_release=lambda itemButton: self.handleItemSelect(itemButton,filenameDropdown,variantDropdown,mapping))
            filenameDropdown.add_widget(itemButton)
                
        # Action button to perform the resolution
        resolveButton = Button(text="Resolve files",size_hint=(None,None),pos=(300,100),size=(150,70))
        resolveButton.bind(on_release=lambda resolveButton: self.handleResolveFiles(variantButton,badFileButton))
        fl.add_widget(resolveButton)

        # Create label for file that needs changing
        problematicLabel = Label(text="Problematic files: \n",pos=(-25,200))
        fl.add_widget(problematicLabel)

        # Return
        return tp

    '''
    This function is the callback for when an item (character, stage, etc) is selected from the dropdown list
    when resolving file names. On selection, we need to do a few things:
        1) Update the item dropdown (left) with the item that was chosen
        2) Remove any buttons that might exist from the dropdown. Also, reset the text on the main button
        3) Based on what was chosen, fill the variantDropdown with the possible variants. 
    '''
    def handleItemSelect(self,itemButton,filenameDropdown,variantDropdown,mapping):
        # Setup
        selectedText = itemButton.text
        # Step 1
        filenameDropdown.select(selectedText)
        # Step 2
        variantDropdown.clear_widgets()
        variantDropdown.select("Choose variant")
        # Step 3
        variants = mapping[selectedText]
        for variant in variants:
            btn = Button(text=variant,size_hint=(None,None), size=self.bSize)
            btn.bind(on_release=lambda btn: variantDropdown.select(btn.text))
            variantDropdown.add_widget(btn)

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
            self.status += "- There was an issue fetching the cached files. Clearing the cache now (paths.txt should be empty)\n"
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
            self.status += "- Caching " + fileType + " to paths.txt\n"
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
            self.status += "- No file was selected\n"

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
            self.status += "- No files were selected for import\n"
        else:
            # Update status
            self.status += "- Files selected for import:\n"
            for f in self.files:                                              
                self.fileList += f + "\n"
                self.status += f + "\n"
    
    '''
    Main callback for importing the files into ISO
    '''
    def importFiles(self):
        if len(self.files) == 0:
            self.status += "- No files were selected for import. Ignoring button press.\n"
        
        # Only begin the import process if the user selected ZIP files
        for f in self.files:
            if not is_zipfile(f):
                self.status += f + " is not a ZIP file. Skipping this file.\n"
            else:
                # Import the textures from this ZIP file
                importStatus = self.fileImporter(f)
                if importStatus == 0:
                    self.status += "- Imported textures from " + f + "\n"
                else:
                    self.status += "- Import error. See above log.\n"
    
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
            self.status += "- making temp folder \n"
            os.mkdir("temp")
        
        # Create a backup folder for the textures you're replacing
        if not os.path.isdir("backup"):
            os.mkdir("backup")

        # Add logic to ONLY extract if the file name in question is a ZIP file this is needed
        # because we use this function for file name resolution
        if is_zipfile(fName):
            with zipper(fName,'r') as f:
                self.status += "- Extracting files\n"
                f.extractall("temp")
                # Parse through the extracted files and try importing into Melee ISO
                # Back up the old files into a backup folder
                textures = []
                for (textPath,tmp,filenames) in os.walk("temp"):
                    textures.append([os.path.join(textPath,file) for file in filenames])
                textures = [item for sublist in textures for item in sublist] # Flatten texture list and remove any empties
        # For resolve files
        else:
            textures = [fName]
        for texture in textures:
            # Validate the texture extension
            if texture[-3:] != "dat":
                self.status += "- File doesn't have .dat extension. Skipping this file.\n"
                continue
            if not self.isValidDatFile(texture):
                self.createPopup(texture)
                continue
            else:
                # This is where the magic happens!
                # Remove any backslashes to forward slashes
                texture = texture.replace("\\","/")
                # Get subdir under temp if ther is one
                textureSubdir = self.getSubDir(texture)
                # Rename the folder to remove spaces if needed
                textureSubdir = self.fixDirWithSpace(textureSubdir)
                # If there's pathing, get JUST the name of the texture file
                justName = texture.split("/")[-1]

                # Build call string and call gcr
                base = os.getcwd().replace("\\","/")
                nodePath = "root/" + justName
                textureImportPath = base + "/temp/" + textureSubdir + "/" + justName
                textureBackupPath = base + "/backup/" + justName
            
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
                    self.status += "- Trying to import texture... \n"
                    subprocess.call(backupCallStr,shell=False)
                    subprocess.call(importCallStr,shell=False)
                    self.status += "- Import success! \n"
                    self.status += "- Backing up old textures to ZIP file...\n"
                    self.zipBackupFiles()
                    self.status += "- Backup success!\n"
                except Exception as e:
                    self.status += e.__str__() + "\n"
                    self.status += "- Unknown import error.\n"
                    returnVal = -1
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
            - MySickRedFox.dat --> This name doesn't match the corresponding Melee ISO name for Red Fox. It needs to be 
                                   re-named to PlFxOr.dat                                  
    '''
    def createPopup(self,textureName):
        # Just get the name of the file
        justName = textureName.split("\\")[-1]
        # Update the log
        self.status += "- This file " + justName + " has a different name than is required by the Melee ISO. Popup deployed for file name resolution.\n"

        # Update the list of problem files to be resolved
        self.problemFiles.append(textureName)

        # Create a notification popup 
        popup = Popup(title="Resolve file name " + justName,size=(400,400))
        dismissButton = Button(text="Please go to the Resolve Tab to change the file names. Press to dismiss message")
        popup.add_widget(dismissButton)
        dismissButton.bind(on_press=popup.dismiss)
        popup.open()
    
        # Set the handle to the bad label
        if self.BadLabel is None:
            self.setBadLabel()

        # Update the label to display all bad files
        self.BadLabel.text += justName + "\n"

        # Add button
        btn = Button(text=justName,size_hint=(None,None),size=self.bSize)
        btn.bind(on_release=lambda btn: self.badFileDropdown.select(btn.text))
        self.badFileDropdown.add_widget(btn)

    '''
    Helper function: Grab a handle to the bad label
    '''
    def setBadLabel(self):
        # Update the resolve tab label with problematic file name
        children = self.resolveTab.content.children
        for child in children:
            if type(child) is Label:
                self.BadLabel = child
    '''
    Callback function to handle file name resolution in the Resolve Tab. 
    '''
    def handleResolveFiles(self,variantButton,badFileButton):
        # Create new full file name (including path) 
        justName = badFileButton.text
        oldFileName = [x for x in self.problemFiles if justName in x][0]
        newFileName = variantButton.text    
        fileparts = oldFileName.split("\\")
        fileparts[-1] = newFileName
        newFile = "\\".join(fileparts)

        # Rename the bad file
        os.rename(oldFileName,newFile)
        # Remove from problem files list
        self.problemFiles.remove(oldFileName)
        # Remove from BadLabel
        splitLines = self.BadLabel.text.splitlines()
        splitLines.remove(justName)
        self.BadLabel.text = "\n".join(splitLines)
        # Remove from dropdown
        btns = self.badFileDropdown.children[0].children
        btns = [x for x in btns if x.text not in justName]
        self.badFileDropdown.children[0].children = btns 
        self.badFileDropdown.select("Choose File to Resolve")
        # Call import
        self.fileImporter(newFile)

    def isValidDatFile(self,textureName):
        justName = textureName.split("\\")[-1]
        return justName in self.validNames
    
    '''Helper function to extract the subdirectory of a texture'''
    def getSubDir(self,texture):
        return "/".join(texture.split("/")[1:-1])

    '''Helper function to remove spaces from subdir'''
    def fixDirWithSpace(self,textureSubdir):
        withoutSpace = textureSubdir.replace(" ","")
        os.rename("temp/"+textureSubdir,"temp/"+withoutSpace)
        return withoutSpace
        
class TextureImporter(App):
    def build(self):
        return Tab()
    def on_stop(self):
        # Remove temporary folder on app exit
        shutil.rmtree("temp")

if __name__ == "__main__":
    TextureImporter().run()