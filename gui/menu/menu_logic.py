from enum import Enum
from .menu_ui import MenuUI

class EnvironmentMode(Enum):
    STATIC = "static"
    DYNAMIC = "dynamic"

class AgentMode(Enum):
    DEFAULT = "default"
    RANDOM = "random"

class GameSettings:
    def __init__(self):
        self.environment_mode = EnvironmentMode.STATIC
        self.agent_mode = AgentMode.DEFAULT
        self.board_size = 8  
        self.pit_probability = 0.2  
        self.num_wumpus = 2 

class MenuLogic:
    def __init__(self, ui: MenuUI):
        self.ui = ui
        self.settings = GameSettings()
        self.is_visible = True
        self.start_game = False
        self.quit_game = False
        
        self.buttons = []
        self.env_buttons = []
        self.agent_buttons = []
        self.config_buttons = []
        
        self._create_all_buttons()
    
    def _create_all_buttons(self):
        center_x = self.ui.width // 2
        
        env_y = self.ui.BASE_Y + 50
        agent_y = self.ui.BASE_Y + self.ui.SECTION_SPACING + 30
        config_y = self.ui.BASE_Y + 2 * self.ui.SECTION_SPACING + 60
        start_y = self.ui.BASE_Y + 2 * self.ui.SECTION_SPACING + 120
        self.env_buttons = [
            self.ui.create_button(center_x - 220, env_y, self.ui.BUTTON_WIDTH, self.ui.BUTTON_HEIGHT,
                                'yellow', "STATIC", lambda: self._set_environment_mode(EnvironmentMode.STATIC)),
            self.ui.create_button(center_x + 20, env_y, self.ui.BUTTON_WIDTH, self.ui.BUTTON_HEIGHT,
                                'gray', "DYNAMIC", lambda: self._set_environment_mode(EnvironmentMode.DYNAMIC))
        ]
        
        # Create Agent buttons (Default/Random)
        self.agent_buttons = [
            self.ui.create_button(center_x - 220, agent_y, self.ui.BUTTON_WIDTH, self.ui.BUTTON_HEIGHT,
                                'yellow', "DEFAULT", lambda: self._set_agent_mode(AgentMode.DEFAULT)),
            self.ui.create_button(center_x + 20, agent_y, self.ui.BUTTON_WIDTH, self.ui.BUTTON_HEIGHT,
                                'gray', "RANDOM", lambda: self._set_agent_mode(AgentMode.RANDOM))
        ]
        
        # Create Configuration buttons
        config_buttons = self._create_config_buttons(center_x, config_y)
        
        # Create Start button (centered)
        start_button = self.ui.create_button(center_x - 100, start_y, 200, 60,
                                           'red', "START GAME", self._start_game)
        
        # Create Quit button (top-right corner, smaller)
        quit_button = self.ui.create_button(self.ui.width - 120, 20, 100, 40,
                                          'gray', "QUIT", self._quit_game)
        
        # Combine all buttons
        self.buttons = (self.env_buttons + self.agent_buttons + config_buttons + 
                       [start_button, quit_button])
        self.config_buttons = [config_buttons[1], config_buttons[4], config_buttons[7]]  # Value buttons only
        
        # Update initial button states
        self._update_button_states()
    
    def _create_config_buttons(self, center_x, config_y):
        """Create configuration control buttons (prev/value/next for each setting)"""
        config_buttons = []
        
        # Helper function to create proper closures for callbacks
        def make_callback(cb, delta_val):
            return lambda: cb(delta_val)
        
        # Configuration data: positions, callbacks, and current texts
        positions = [center_x - 150, center_x, center_x + 150]  # Board, Pit, Wumpus
        callbacks = [self._change_board_size, self._change_pit_probability, self._change_wumpus_count]
        texts = [
            f"{self.settings.board_size}x{self.settings.board_size}", 
            f"{int(self.settings.pit_probability * 100)}%", 
            f"{self.settings.num_wumpus}"
        ]
        
        for i, (pos, callback, text) in enumerate(zip(positions, callbacks, texts)):
            # Determine delta values based on callback type
            if callback == self._change_pit_probability:
                delta_prev, delta_next = -0.05, 0.05
            else:
                delta_prev, delta_next = -1, 1
            
            # Create button group: [prev] [value] [next]
            config_buttons.extend([
                self.ui.create_button(pos - 70, config_y + 6, 25, 25, 'prev', "", 
                                    make_callback(callback, delta_prev)),
                self.ui.create_button(pos - 40, config_y, 80, 40, 'gray', text),
                self.ui.create_button(pos + 45, config_y + 6, 25, 25, 'next', "", 
                                    make_callback(callback, delta_next))
            ])
        
        return config_buttons
    
    # Settings management methods
    def _set_environment_mode(self, mode: EnvironmentMode):
        """Set environment mode and update UI"""
        self.settings.environment_mode = mode
        self._update_button_states()
    
    def _set_agent_mode(self, mode: AgentMode):
        """Set agent mode and update UI"""
        self.settings.agent_mode = mode
        self._update_button_states()
    
    def _change_board_size(self, delta: int):
        """Change board size within valid range"""
        new_size = self.settings.board_size + delta
        if new_size >= 8:
            self.settings.board_size = new_size
            self._update_config_buttons()
    
    def _change_pit_probability(self, delta: float):
        """Change pit probability within valid range"""
        new_prob = round(self.settings.pit_probability + delta, 2)
        if 0.2 <= new_prob <= 1.0:
            self.settings.pit_probability = new_prob
            self._update_config_buttons()
    
    def _change_wumpus_count(self, delta: int):
        """Change wumpus count within valid range"""
        new_count = self.settings.num_wumpus + delta
        if new_count >= 2:
            self.settings.num_wumpus = new_count
            self._update_config_buttons()
    
    def _start_game(self):
        """Start the game"""
        self.start_game = True
        self.is_visible = False
        return self.settings
    
    def _quit_game(self):
        """Quit the application"""
        self.quit_game = True
        self.is_visible = False
    
    def reset_state(self):
        """Reset menu state when returning from game"""
        self.start_game = False
        self.quit_game = False
        self.is_visible = True
        
        # Reset all button interaction states
        for button in self.buttons:
            if hasattr(button, 'reset_state'):
                button.reset_state()
        
        # Also reset button states to ensure proper display
        self._update_button_states()
        self._update_config_buttons()
    
    def force_refresh(self):
        """Force refresh all UI elements - useful when returning from game"""
        if self.is_visible:
            self._update_button_states()
            self._update_config_buttons()
    
    def _update_button_states(self):
        """Update button appearance based on current settings"""
        # Environment buttons
        env_states = [
            self.settings.environment_mode == EnvironmentMode.STATIC,
            self.settings.environment_mode == EnvironmentMode.DYNAMIC
        ]
        self.ui.update_button_group(self.env_buttons, env_states)
        
        # Agent buttons  
        agent_states = [
            self.settings.agent_mode == AgentMode.DEFAULT,
            self.settings.agent_mode == AgentMode.RANDOM
        ]
        self.ui.update_button_group(self.agent_buttons, agent_states)
    
    def _update_config_buttons(self):
        """Update configuration buttons text"""
        texts = [
            f"{self.settings.board_size}x{self.settings.board_size}",
            f"{int(self.settings.pit_probability * 100)}%",
            f"{self.settings.num_wumpus}"
        ]
        for i, text in enumerate(texts):
            self.config_buttons[i].set_text(text)
    
    # Public interface methods
    def handle_event(self, event):
        """Handle user input events"""
        if not self.is_visible:
            return None
        
        for button in self.buttons:
            try:
                if button.handle_event(event):
                    # Check if this is the start game button
                    if hasattr(button, 'callback') and button.callback == self._start_game:
                        return self._start_game()
                    # For other buttons, the callback is already executed by handle_event
                    break
            except Exception as e:
                print(f"Error handling button event: {e}")
                continue
        return None
    
    def update(self):
        """Update menu state"""
        if self.is_visible:
            for button in self.buttons:
                button.update()
    
    def get_settings(self):
        """Get game settings object"""
        return self.settings
    
    def should_quit(self):
        """Check if user wants to quit the application"""
        return self.quit_game

    def draw(self, surface=None):
        """Draw the menu"""
        if not self.is_visible:
            return
        
        self.ui.draw_complete_menu(self.buttons)
        
        target_surface = surface or self.ui.screen
        self.ui.blit_to_target(target_surface)
