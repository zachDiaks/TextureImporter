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
'''
from tkinter.filedialog import askopenfilename
from tkinter.filedialog import askopenfilenames
import tkinter as tk
import os
import sys
import subprocess

class textureImporter:

    # Constructor
    def __init__(self):
        self.gcrPath = ''
        self.meleePath = ''
        self.fileList = []
        self.window = tk.Tk()
        self.window.geometry("500x500")

        self.instructions = tk.StringVar()
        self.instructions.set("Instructions")
        self.instructionLabel = tk.Label(self.window,
            textvariable=self.instructions)

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
        self.instructionLabel.grid(row=3,column=2)


    # Get the GCR path
    def getGCR(self):
        self.gcrPath = askopenfilename()

    # Get the ISO path
    def getISO(self):
        self.meleePath = askopenfilename()

    # Get the files to add to
    def getFiles(self):
        self.fileList = askopenfilenames()

    # Import the selected files into the ISO
    def importFiles(self):
        for file in self.fileList:
            print(file)

if __name__ == "__main__":
    doit = textureImporter()
    doit.window.mainloop()
