from kivy. app import App
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.screenmanager import NoTransition

class NavWidget(BoxLayout):
    pass

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
    def build(self):
        return WindowManager()

    def navigate_to(self, screen_name, transition=None):
        """Handle screen navigation with optional transition"""
        if transition:
            self.root.transition = transition
        self.root.current = screen_name

if __name__=="__main__":
    FlipApp().run()