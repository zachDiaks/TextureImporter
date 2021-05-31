from kivy.app import App
from kivy.lang import Builder
from kivy.uix.tabbedpanel import TabbedPanel

Builder.load_file("Tab.kv")

class Tab(TabbedPanel):
    pass

class kivyTestApp(App):
    def build(self):
        return Tab()

if __name__ == "__main__":
    kivyTestApp().run()