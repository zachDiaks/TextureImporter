'''
Sample to see how to call gcr.exe from Python
To extract one file:
.\gcr.exe .\Melee.iso root\PlFxNr.dat e out.dat
'''
import os
import sys
import subprocess

gcrPath = "C:\\Users\\zachr\\OneDrive\\Desktop\\Dolphin\\Games\\gcr.exe"
meleePath = "C:\\Users\\zachr\\OneDrive\\Desktop\\Dolphin\\Games\\Melee.iso"
file = "root\\PlFxNr.dat"
outName = "Out.dat"
callStr = "%s %s %s e %s"%(gcrPath,meleePath,file,outName)
subprocess.call(callStr,shell=True)
