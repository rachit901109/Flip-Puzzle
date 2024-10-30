from kivy. app import App
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.properties import ObjectProperty, DictProperty
from kivy.uix.button import Button
import numpy as np
class NavWidget(BoxLayout):
    pass

class HomeScreen(Screen):
    pass

class ColoredButton(Button):
    def __init__(self, value, color_map, **kwargs):
        super().__init__(**kwargs)
        self.background_color = color_map[value]
        self.background_normal=""
        # Adjust text color based on background brightness for better visibility
        brightness = sum(color_map[value][:3]) / 3
        self.color = (0, 0, 0, 1) if brightness > 0.5 else (1, 1, 1, 1)
        self.color = (0,0,0,1)

class GameScreen(Screen):
    board = ObjectProperty(None)
    color_map = DictProperty({
        0: (0.1725, 0.6275, 0.9725, 1),  # Bright sky blue
        1: (1.0000, 0.8431, 0.0000, 1),  # Vibrant yellow
        2: (0.0000, 0.8078, 0.4196, 1),  # Emerald green
        3: (1.0000, 0.3412, 0.3333, 1),  # Vivid orange
        4: (0.5412, 0.1686, 0.8863, 1),  # Electric purple
        5: (0.722, 0.431, 0.225, 1),  # random
        6: (0.9569, 0.2627, 0.2118, 1)   # Bright red
    })
    
    def generate_board(self, N, m, n):
        if not m or not n:  # Check if dimensions are provided
            return
        try:
            N = int(N)
            m, n = int(m), int(n)
            board = np.random.randint(N, size=(m*n, 1), dtype=np.int8)
            # Convert board to displayable format
            self.display_board(board.reshape(m, n), m, n)
        except ValueError:
            print("Please enter valid numbers for N and dimensions of the board.")
    
    def display_board(self, board, m, n):
        # Clear previous board
        board_grid = self.ids.board_grid
        board_grid.clear_widgets()
        board_grid.rows = m
        board_grid.cols = n
        
        # Add buttons for each cell
        for i in range(m):
            for j in range(n):
                value = int(board[i][j])
                btn = ColoredButton(
                    value=value,
                    color_map=self.color_map,
                    text=str(value),
                    size_hint=(1, 1)
                )
                board_grid.add_widget(btn)

    def update_win_condition_values(self, N):
        values = [str(i) for i in range(N)]
        self.ids.win_condition.values = values
        if int(self.ids.win_condition.text) >= N:
            self.ids.win_condition.text = "0"
class InfoScreen(Screen):
    pass

class AboutScreen(Screen):
    pass

class WindowManager(ScreenManager):
    pass

class HomeWidget(AnchorLayout):
    def default_game(self):
        game_screen = self.parent.manager.get_screen("game_screen")
        N = int(game_screen.ids.mod_system.text)
        m = int(game_screen.ids.rows_input.text)
        n = int(game_screen.ids.cols_input.text)

        game_screen.generate_board(N, m, n)

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