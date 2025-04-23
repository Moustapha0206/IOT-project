
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.core.window import Window
from kivy.lang import Builder

Window.size = (450, 550)

Builder.load_file("gui.kv")

class CoolerMonitorScreen(BoxLayout):
    pass

class CoolerApp(App):
    def build(self):
        return CoolerMonitorScreen()

if __name__ == '__main__':
    CoolerApp().run()
