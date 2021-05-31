# Program to explain how to create tabbed panel App in kivy
	
# import kivy module	
import kivy
		
# base Class of your App inherits from the App class.	
# app:always refers to the instance of your application	
from kivy.app import App

from kivy.lang import Builder
# to use this must have to import it
from kivy.uix.tabbedpanel import TabbedPanel

# Floatlayout allows us to place the elements
# relatively based on the current window
# size and height especially in mobiles

Builder.load_file("Tab.kv")
# Create Tabbed class
class Tab(TabbedPanel):
	pass

# create App class
class TabbedPanelApp(App):
	def build(self):
		return Tab()

# run the App
if __name__ == '__main__':
	TabbedPanelApp().run()
