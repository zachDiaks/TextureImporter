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
    - Cache gcr and melee in constructor
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
        self.gcrPath = ''
        self.meleePath = ''
        self.tempPath = os.getcwd() + "/tempDir"
        self.fileList = []
        self.window = tk.Tk()
        self.window.title("Texture Importer")
        self.window.geometry("500x500")

        self.status = tk.StringVar()
        self.staticStatus = tk.StringVar()
        self.staticStatus.set("Current Status:")
        self.staticStatusLabel = tk.Label(self.window,
            textvariable=self.staticStatus,justify="left")
        self.instructionLabel = tk.Label(self.window,
            textvariable=self.status,justify="left",wraplength=300)

        self.gcrButton = tk.Button(text="Select GCR",command=self.getGCR)
        self.gcrButton.grid(row=1,column=1,ipadx=10,ipady=10)

        self.isoButton = tk.Button(text="Select Melee ISO",command=self.getISO)
        self.isoButton.grid(row=1,column=2,ipadx=10,ipady=10)

        self.fileButton = tk.Button(text="Select files to import",
            command=self.getFiles)
        self.fileButton.grid(row=1,column=3,ipadx=10,ipady=10)

        self.importButton = tk.Button(text="Import files",
            command=self.importFiles)
        self.importButton.grid(row=2,column=2,ipadx=10,ipady=10)
        self.staticStatusLabel.grid(row=3,column=1,columnspan=3,pady=20)
        self.instructionLabel.grid(row=4,column=1,columnspan=3)


    # Get the GCR path
    def getGCR(self):
        self.gcrPath = askopenfilename()
        if (self.gcrPath.split("/")[-1] == "gcr.exe"):
            self.isValidGCR = True
        else:
            self.status.set("The file you selected is not named gcr.exe " +
                "be sure to select the right file!")

    # Get the ISO path
    def getISO(self):
        self.meleePath = askopenfilename()
        if (self.meleePath.split("/")[-1][-4:] == ".iso"):
            self.isValidISO = True
        else:
            self.status.set("The file you selected is not an ISO. Please select a " +
                "Melee ISO")

    # Get the files to add to
    def getFiles(self):
        self.fileList = askopenfilenames()

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
        backupPath = "/".join(self.meleePath.split("/")[:-1]) + "/TextureBackups"
        if not os.path.exists(backupPath):
            os.mkdir(backupPath)

        files = os.listdir(self.tempPath)
        for file in files:
            nodePath = "root/" + file
            textureImportPath = self.tempPath + "/" + file
            textureBackupPath = backupPath + "/" + file
            backupCallStr = "%s %s %s e %s"%(self.gcrPath,self.meleePath,nodePath,textureBackupPath)
            importCallStr = "%s %s %s i %s"%(self.gcrPath,self.meleePath,nodePath,textureImportPath)
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
