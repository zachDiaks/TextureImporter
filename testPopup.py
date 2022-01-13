# popup import
from kivy.uix.popup import Popup
	
# base Class of your App inherits from the App class.	
# app:always refers to the instance of your application
from kivy.app import App
	
# Importing Drop-down from the module to use in the program
from kivy.uix.dropdown import DropDown

# The Button is a Label with associated actions
# that are triggered when the button is pressed
# (or released after a click / touch)
from kivy.uix.button import Button

# another way used to run kivy app
from kivy.base import runTouchApp
'''
Issue: 
	- Popups aren't the solution here. They're mostly used for alerting the user of something and stopping their progress. 
	- We should instead either launch a new standard window or have a separate tab and direct the user to this tab using a popup
'''

# Create the popup and add dropdowns 
popup = Popup(title="Resolve file name",size=(400,400))
dropdown = DropDown()

# Read file contents and grab names of characters
with open("validFileNames.txt","r") as f:
	lines = f.readlines()
names = [x for x in lines if "##" in x]

# Populate the dropdown with character names
for i in range(1,len(names)):
	btn = Button(text=names[i],size_hint_y = None, height = 40)
	btn.bind(on_release=lambda btn: dropdown.select(btn.text))
	dropdown.add_widget(btn)

# Set up main button
mainbutton = Button(text="Choose Character",size_hint =(None, None), pos =(200, 200))
mainbutton.bind(on_release = dropdown.open)
dropdown.bind(on_select = lambda instance, x: setattr(mainbutton, 'text', x)) # Set main button to whatever is selected
button2 = Button(text="TestButton")
popup.add_widget(mainbutton)

# Add dropdown to the popup window
runTouchApp(popup)
