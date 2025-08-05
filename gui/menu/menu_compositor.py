from .menu_ui import MenuUI
from .menu_logic import MenuLogic, EnvironmentMode, AgentMode, GameSettings

class MainMenu:
    """Main menu for Wumpus World game - Facade for UI and Logic components"""
    
    # Export enums/classes as class attributes for easy access
    EnvironmentMode = EnvironmentMode
    AgentMode = AgentMode
    GameSettings = GameSettings
    
    def __init__(self, width: int, height: int, screen=None):
        # Create UI component
        self.ui = MenuUI(width, height, screen)
        
        # Create Logic component
        self.logic = MenuLogic(self.ui)
    
    # Delegate all methods to appropriate components
    def is_visible(self):
        return self.logic.is_visible
    
    def start_game(self):
        return self.logic.start_game
    
    def should_quit(self):
        return self.logic.should_quit()
    
    def reset_state(self):
        """Reset menu state when returning from game"""
        return self.logic.reset_state()
    
    def settings(self):
        return self.logic.settings
    
    def handle_event(self, event):
        """Handle user input events"""
        return self.logic.handle_event(event)
    
    def update(self):
        """Update menu state"""
        self.logic.update()
    
    def draw(self, surface=None):
        """Draw the menu"""
        self.logic.draw(surface)
    
    def get_settings(self):
        """Get game settings object"""
        return self.logic.get_settings()
