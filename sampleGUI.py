'''
This is a sample file for me to remember how to make a GUI using Tkinter

GENERAL FLOW:
    - Create a window with tk.Tk()
    - Add widgets
    - Execute using window.mainloop
'''
from tkinter.filedialog import askopenfilenames
import tkinter as tk
import sys
import os

def getFile():
    fileName = askopenfilenames()
    for file in fileName:
        print(file)

window = tk.Tk()
greeting = tk.Label(text="Sample GUI")
greeting.pack()
button = tk.Button(text="NewButton",command=getFile)
test = tk.StringVar()
button.pack()


window.mainloop()
