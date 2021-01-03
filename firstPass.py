'''
This is the first pass at making the main script.
Uses:
    - Try to flesh out the design of the UI
    - Ensure functionality
    - Doesn't need to be pretty for this iteration

NOTES:
    - Need interactions for:
        a) Select gcr
        b) Select melee iso
        c) Select files/folders to import from

TODO:
    - Figure out how to make certain things bold
    - Add instructions tab (will require a restructuring)
    - Backup button and implementation
    - Stages
    - No ZIP file implementation?
    - Compile into executable! Then, the testing begins...
'''
from tkinter.filedialog import askopenfilename
from tkinter.filedialog import askopenfilenames
from zipfile import ZipFile as unzipper
import tkinter as tk
import os
import sys
import subprocess
import shutil


class textureImporter:

    # Constructor
    def __init__(self):
        self.isValidISO = False
        self.isValidGCR = False
        self.noDuplicates = True
        self.firstTime = True
        self.gcrPath = ''
        self.meleePath = ''
        self.tempPath = os.getcwd() + "/tempDir"
        self.fileList = []
        self.window = tk.Tk()
        self.window.title("Texture Importer")
        self.window.geometry("450x500")

        self.meleePathVar = tk.StringVar()
        self.gcrPathVar = tk.StringVar()
        self.status = tk.StringVar()
        self.staticStatus = tk.StringVar()
        self.meleePathVar.set("Melee Path: ")
        self.gcrPathVar.set("GCR Path: ")
        self.staticStatus.set("Current Status:")
        self.staticStatusLabel = tk.Label(self.window,
            textvariable=self.staticStatus,justify="left",
            font = ('bold'))
        self.statusLabel = tk.Label(self.window,
            textvariable=self.status,justify="left",wraplength=300)
        self.meleePathLabel = tk.Label(self.window,
            textvariable=self.meleePathVar,justify="left")
        self.GCRPathLabel = tk.Label(self.window,
            textvariable=self.gcrPathVar,justify="left")

        self.gcrButton = tk.Button(text="Select GCR",command=self.getGCR)
        self.gcrButton.grid(row=1,column=1,ipadx=10,ipady=10)

        self.isoButton = tk.Button(text="Select Melee ISO",command=self.getISO)
        self.isoButton.grid(row=1,column=2,ipadx=10,ipady=10)

        self.fileButton = tk.Button(text="Select files to import",
            command=self.getFiles)
        self.fileButton.grid(row=1,column=3,ipadx=10,ipady=10)

        self.importButton = tk.Button(text="Import files",
            command=self.importFiles)
        self.importButton.grid(row=2,column=2,ipadx=10,ipady=10,pady=10)
        self.meleePathLabel.grid(row=3,column=1,columnspan=3,pady=10)
        self.GCRPathLabel.grid(row=4,column=1,columnspan=3)
        self.staticStatusLabel.grid(row=5,column=1,columnspan=3)
        self.statusLabel.grid(row=6,column=1,columnspan=3)

        # Check if GCR and Melee paths have already been set
        self.thisPath = os.getcwd()
        if os.path.exists(self.thisPath + '/paths.txt'):
            self.firstTime = False
            self.specifyPaths()

    # Specify the melee and GCR paths if they've already been specified
    def specifyPaths(self):
        with open(self.thisPath + '/paths.txt','r') as f:
            lines = f.readlines()
            for line in lines:
                tmp = line.split(" ")
                if tmp[0] == "GCR":
                    self.gcrPath = tmp[1]
                    self.gcrPathVar.set(self.gcrPathVar.get() + tmp[1])
                elif tmp[0] == "Melee":
                    self.meleePath = tmp[1]
                    self.meleePathVar.set(self.meleePathVar.get() + tmp[1])
                else:
                    self.status.set("Unknown GCR or Melee Path. Please reset this")
    # Get the GCR path
    def getGCR(self):
        self.gcrPath = askopenfilename()
        if (self.gcrPath.split("/")[-1] == "gcr.exe"):
            self.isValidGCR = True
            self.gcrPathVar.set(self.gcrPathVar.get() + self.gcrPath)
            if self.firstTime:
                with open(self.thisPath + '/paths.txt','a') as f:
                    f.write("GCR " + self.gcrPath + "\n")
        elif self.gcrPath == "":
            # Do nothing, gcr has not been set
            self.status.set("")
        else:
            self.status.set("The file you selected is not named gcr.exe " +
                "be sure to select the right file!")

    # Get the ISO path
    def getISO(self):
        self.meleePath = askopenfilename()
        if (self.meleePath.split("/")[-1][-4:] == ".iso"):
            self.isValidISO = True
            self.meleePathVar.set(self.meleePathVar.get() + self.meleePath)
            if self.firstTime:
                with open(self.thisPath + '/paths.txt','a') as f:
                    f.write("Melee " + self.meleePath + "\n")
        elif self.meleePath == "":
            # Do nothing because file was not actually selected
            self.status.set("")
        else:
            self.status.set("The file you selected is not an ISO. Please select a " +
                "Melee ISO")

    # Get the files to add to
    def getFiles(self):
        self.fileList = askopenfilenames()
        if len(self.fileList) == 0:
            self.status.set("No files selected for import")

    # Determine if this is a zip file
    def isZIP(self,fName):
        return fName[-4:] == '.zip'

    # Determine if a user is trying to import multiple textures with the same name
    def hasDuplicateFile(self,fileList):
        dups = [item for item in os.listdir(self.tempPath) if item in fileList]
        if len(dups) > 0:
            self.status.set("Found duplicate file(s):")
            self.status.set(dups)
        return len(dups) > 0

    # Extract the files
    def extractFiles(self,file):
        with unzipper(file,'r') as f:
            if not self.hasDuplicateFile(f.namelist()):
                self.status.set("Extracting " + file)
                f.extractall(self.tempPath)
            else:
                self.status.set(file + " contains a texture file that exists in another zip file that you've chosen. " +
                    "please choose only the file that you want to import.")
                self.noDuplicates = False
        f.close()

    # Import the files in this
    def importToISO(self):
        if not (self.isValidGCR and self.isValidISO and self.noDuplicates):
            self.status.set("Cannot import textures because either the GCR path, ISO path, or the files selected are invalid" +
            " or haven't been set yet or there are duplicate files that you're trying to import")
            return
        self.backupPath = "/".join(self.meleePath.split("/")[:-1]) + "/TextureBackups"
        if not os.path.exists(self.backupPath):
            os.mkdir(self.backupPath)

        files = os.listdir(self.tempPath)
        for file in files:
            nodePath = "root/" + file
            textureImportPath = self.tempPath + "/" + file
            textureBackupPath = self.backupPath + "/" + file
            backupCallStr = "%s %s %s e %s"%(self.gcrPath,self.meleePath,
                nodePath,textureBackupPath)
            importCallStr = "%s %s %s i %s"%(self.gcrPath,self.meleePath,
                nodePath,textureImportPath)
            subprocess.call(backupCallStr,shell=True)
            subprocess.call(importCallStr,shell=True)

    # Import the selected files into the ISO
    def importFiles(self):
        if not os.path.exists(self.tempPath):
            os.mkdir(self.tempPath)
        for file in self.fileList:
            if self.isZIP(file):
                self.extractFiles(file)
            else:
                return
        self.importToISO()
        shutil.rmtree(self.tempPath)

if __name__ == "__main__":
    doit = textureImporter()
    doit.window.mainloop()
