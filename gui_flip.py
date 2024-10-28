from kivy. app import App
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.screenmanager import ScreenManager, Screen

class HomeScreen(Screen):
    pass

class GameScreen(Screen):
    pass

class InfoScreen(Screen):
    pass

class AboutScreen(Screen):
    pass

class WindowManager(ScreenManager):
    pass

class HomeWidget(AnchorLayout):
    pass

class FlipApp(App):
    pass

if __name__=="__main__":
    FlipApp().run()