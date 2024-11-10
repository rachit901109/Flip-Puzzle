from kivy. app import App
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.properties import ObjectProperty, DictProperty, NumericProperty, StringProperty
from kivy.uix.button import Button
from kivy.core.window import Window
from kivy.uix.image import Image
from kivy.clock import Clock
from functools import partial
from flip_solver_utility import get_constant_matrix, get_transformation_matrix, solve
import numpy as np
import os
class NavWidget(BoxLayout):
    pass

class HomeScreen(Screen):
    pass

def get_neighbour_dir(connect):
    if connect == "4":
        return ([0, 1, 0, -1, 0], [0, 0, 1, 0, -1])
    elif connect == "8":
        return ([0, 1, 0, -1, 0, -1, -1, 1, 1], [0, 0, 1, 0, -1, -1, 1, -1, 1]) 
class ColoredButton(Button):
    def __init__(self, value, pos_x, pos_y, m, n, N, color_map, position, connect, **kwargs):
        super().__init__(**kwargs)
        
        # Store initial values
        self.value = value
        self.pos_x = pos_x
        self.pos_y = pos_y
        self.neighbours = []

        dirx, diry = get_neighbour_dir(connect)
            
        for i in range(len(dirx)):
            nx = self.pos_x + dirx[i]
            ny = self.pos_y + diry[i]
            if nx >= 0 and nx < m and ny >= 0 and ny < n:
                self.neighbours.append((nx*n)+ny)

        # Set button properties
        self.background_color = color_map[value]
        self.background_normal = ""
        
        # Adjust text color based on background brightness
        # brightness = sum(color_map[value][:3]) / 3
        # self.color = (0, 0, 0, 1) if brightness > 0.5 else (1, 1, 1, 1)
        
        # Based on connectivity of board pixel neighbouring button for intuition
        base_path = os.path.abspath("media")
        image_file = f"{position}_{connect}.png"
        image_path = os.path.join(base_path, image_file)
        
        if os.path.exists(image_path):
            self.image = Image(
                source=image_path,
                size_hint=(None, None),
                # allow_stretch=True,
                # keep_ratio=True,
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
        
        self.bind(on_release=partial(self._toggle, m,n,N,color_map))

    def _update_image(self, *args):
        """Update both image size and position"""
        if hasattr(self, 'image'):
            # Set image size to 40% of the button's smallest dimension
            # only usefull if i switch to different pixel art, currently only using 16x16 size as default.
            size = min(self.width, self.height)*0.4
            self.image.size = (size, size)
            
            # Calculate center position
            self.image.pos = (
                self.x + (self.width - self.image.width) / 2,  # Center horizontally
                self.y + (self.height - self.image.height) / 2  # Center vertically
            )
    
    def update_value(self, N, color_map):
        """Update the button's value and color"""
        self.value = (self.value+1) % N
        self.background_color = color_map[self.value]

    def _toggle(self, m,n,N,color_map, instance):
        """Handle the button press"""
        # Get reference to the game board grid
        board_grid = self.parent
        
        # Update neighbors
        for cell in self.neighbours:
            # Calculate the index in the grid's children
            # Note: Kivy's GridLayout stores children in reverse order
            index = ((m*n)-1)-cell
            # print(f"index: {index}")
            if 0 <= index < len(board_grid.children):
                neighbor_button = board_grid.children[index]
                if isinstance(neighbor_button, ColoredButton):
                    neighbor_button.update_value(N, color_map)
    
    #no need for specific event handler update image will do both
    # def on_size(self, *args):
    #     """Handle size changes"""
    #     Clock.schedule_once(lambda dt: self._update_image(), 0)

    # def on_pos(self, *args):
    #     """Handle position changes"""
    #     Clock.schedule_once(lambda dt: self._update_image(), 0)

class GameScreen(Screen):
    N = NumericProperty()
    m = NumericProperty()
    n = NumericProperty()
    connect = StringProperty()
    win_condition = NumericProperty()
    color_map = DictProperty({
        0: (0.1725, 0.6275, 0.9725, 1),  # Bright sky blue
        1: (1.0000, 0.8431, 0.0000, 1),  # Vibrant yellow
        2: (0.0000, 0.8078, 0.4196, 1),  # Emerald green
        3: (1.0000, 0.3412, 0.3333, 1),  # Vivid orange
        4: (0.5412, 0.1686, 0.8863, 1),  # Electric purple
        5: (0.722, 0.431, 0.225, 1),  # random
        6: (0.9569, 0.2627, 0.2118, 1)   # Bright red
    })
    
    def generate_board(self, N, m, n, connect, win_condition):
        if not m or not n:  # Check if dimensions are provided
            return
        try:
            self.N = int(N)
            self.m, self.n = int(m), int(n)
            self.win_condition = int(win_condition)
            self.connect = connect
            board = np.random.randint(self.N, size=(self.m*self.n, 1), dtype=np.int8)
            # Convert board to displayable format
            self.display_board(board.reshape(self.m, self.n), self.m, self.n, self.N, self.connect, self.win_condition)
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

    def display_board(self, board, m, n, N, connect, win_condition):
        # Clear previous board
        board_grid = self.ids.board_grid
        board_grid.clear_widgets()
        board_grid.rows = m
        board_grid.cols = n

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
                    pos_x=i,
                    pos_y=j,
                    m=m,
                    n=n,
                    N=N,
                    color_map=self.color_map,
                    position=position,
                    connect=connect,
                    # text=str(value),
                    size_hint=(1, 1)
                )
                board_grid.add_widget(btn)
        
        # fill current game settings and color map
        current_game_label = self.ids.current_game_settings
        current_game_label.text = f"{N} Colors\n{m} x {n} Board\n{connect} Connectivity\n{win_condition} Winning Color"

        color_map_box = self.ids.show_color_map
        color_map_box.clear_widgets()
        for i in range(N):
            btn = Button(
                text=str(i),
                size_hint=(1,1),
                background_normal="",
                background_color=self.color_map[i]
            )
            color_map_box.add_widget(btn)
        
        Clock.schedule_once(update_buttons, 0)

    def update_win_condition_values(self, N):
        values = [str(i) for i in range(N)]
        self.ids.win_condition.values = values
    
    def solve_board(self):
        # Get the current board from the gridlayout
        board_grid = self.ids.board_grid
        ini_board = np.zeros(shape=(self.m*self.n, 1), dtype=np.int8)
        final_board = np.array([self.win_condition for _ in range(self.m*self.n)]).reshape(-1,1)
        dirx, diry = get_neighbour_dir(self.connect)

        for cell in board_grid.children:
            if isinstance(cell, ColoredButton):
                pos = (cell.pos_x*self.n)+cell.pos_y
                ini_board[pos] = cell.value

        a = get_transformation_matrix(self.m, self.n, dirx, diry)
        b = get_constant_matrix(final_board, ini_board, self.N)

        solution = solve(a, b, self.m, self.n, self.N)
        if solution is not None:
            for i in range(self.m*self.n):
                if solution[i][0]>0:
                    row,col = divmod(i, self.n)
                    print(f"Press {i}th cell at coordinate ({row}, {col}) {solution[i][0]} times.")
        else:
            print("Board not solvalbe")

        
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
        win_condition = game_screen.ids.win_condition.text

        game_screen.generate_board(N, m, n, connect, win_condition)

    def close_app(self):
        app = App.get_running_app()
        app.stop()
        # Window.close()

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