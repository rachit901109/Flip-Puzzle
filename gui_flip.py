from kivy. app import App
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.properties import ObjectProperty, DictProperty
from kivy.uix.button import Button
from kivy.core.window import Window
from kivy.uix.image import Image
from kivy.core.image import Image as CoreImage
import numpy as np
import os
from kivy.clock import Clock
class NavWidget(BoxLayout):
    pass

class HomeScreen(Screen):
    pass

class ColoredButton(Button):
    def __init__(self, value, color_map, position, connect, **kwargs):
        super().__init__(**kwargs)
        
        # Set button properties
        self.background_color = color_map[value]
        self.background_normal = ""
        
        # Adjust text color based on background brightness
        brightness = sum(color_map[value][:3]) / 3
        self.color = (0, 0, 0, 1) if brightness > 0.5 else (1, 1, 1, 1)
        
        # Based on connectivity of board pixel neighbouring button for intuition
        base_path = os.path.abspath("media")
        image_file = "bottom_right_corner_4.png" 
        image_path = os.path.join(base_path, image_file)
        
        if os.path.exists(image_path):
            self.image = Image(
                source=image_path,
                size_hint=(None, None),
                size=(16, 16),
                pos_hint={'center_x': 0.5, 'center_y': 0.5}
            )
            self.add_widget(self.image)
            # create bindings to change image size and position, when change in button size and position
            self.bind(size=self._update_image)
            self.bind(pos=self._update_image)
            
            # We schedule the update function to run on the next frame so that we get the accurate positions of the pixels
            # after the widgets are fully rendered, not doing this will cause image centering issues. 
            Clock.schedule_once(lambda dt: self._update_image(), 0)

    def _update_image(self, *args):
        """Update both image size and position"""
        if hasattr(self, 'image'):
            # Set image size to 40% of the button's smallest dimension
            # only usefull if i switch to different pixel, currently only using 16x16 size as default.
            size = min(self.width, self.height)
            self.image.size = (size, size)
            
            # Calculate center position
            self.image.pos = (
                self.x + (self.width - self.image.width) / 2,  # Center horizontally
                self.y + (self.height - self.image.height) / 2  # Center vertically
            )
    
    #no need for specific event handler update image will do both
    # def on_size(self, *args):
    #     """Handle size changes"""
    #     Clock.schedule_once(lambda dt: self._update_image(), 0)

    # def on_pos(self, *args):
    #     """Handle position changes"""
    #     Clock.schedule_once(lambda dt: self._update_image(), 0)

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
    
    def generate_board(self, N, m, n, connect):
        if not m or not n:  # Check if dimensions are provided
            return
        try:
            N = int(N)
            m, n = int(m), int(n)
            board = np.random.randint(N, size=(m*n, 1), dtype=np.int8)
            # Convert board to displayable format
            self.display_board(board.reshape(m, n), m, n, connect)
        except ValueError:
            print("Please enter valid numbers for N and dimensions of the board.")
    
    def get_position_type(self, row, col, total_rows, total_cols):
        """Determine if a cell is a corner, edge, or center"""
        # corner cases
        if row==0 and col==0:
            return "top_left_corner"
        elif row==0 and col==total_cols-1:
            return "top_right_corner"
        elif row==total_rows-1 and col==0:
            return "bottom_left_corner"
        elif row==total_rows-1 and col==total_cols-1:
            return "bottom_right_corner"
        # edge case
        elif row==0:
            return "top_edge"
        elif row==total_rows-1:
            return "bottom_edge"
        elif col==0:
            return "left_edge"
        elif col==total_cols-1:
            return "right_edge"
        # center
        else:
            return "center"

    def display_board(self, board, m, n, connect):
        # Clear previous board
        board_grid = self.ids.board_grid
        board_grid.clear_widgets()
        board_grid.rows = m
        board_grid.cols = n

        # Calculate button size based on available space
        # We'll set a minimum size to ensure the pixel art is visible
        # min_size = 40  # minimum size in pixels
        # button_size = max(min_size, min(board_grid.width/n, board_grid.height/m))
        def update_buttons(*args):
            """Update all buttons after grid is laid out"""
            for child in board_grid.children:
                if isinstance(child, ColoredButton):
                    child._update_image()
        
        # Add buttons for each cell
        for i in range(m):
            for j in range(n):
                value = int(board[i][j])
                position = self.get_position_type(i,j,m,n)
                btn = ColoredButton(
                    value=value,
                    color_map=self.color_map,
                    position=position,
                    connect=connect,
                    # text=str(value),
                    size_hint=(1, 1)
                )
                board_grid.add_widget(btn)
        Clock.schedule_once(update_buttons, 0)

    def update_win_condition_values(self, N):
        values = [str(i) for i in range(N)]
        self.ids.win_condition.values = values
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
        connect = game_screen.ids.connectivity.text

        game_screen.generate_board(N, m, n, connect)

    def close_app(self):
        app = App.get_running_app()
        app.stop()
        Window.close()

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