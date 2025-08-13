from gui.menu import MainMenu
from gui.game_controller import GameController
import pygame

HEIGHT = 640
WIDTH = 1200

def run_menu_loop():
    """Run the main menu and return game settings when ready"""
    menu_width, menu_height = WIDTH, HEIGHT
    screen = pygame.display.set_mode((menu_width, menu_height))
    menu = MainMenu(menu_width, menu_height)
    
    # Reset and refresh menu state
    menu.reset_state()
    menu.force_refresh()
    
    clock = pygame.time.Clock()
    
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return None, True  # settings=None, should_quit=True
            menu.handle_event(event)
        
        menu.update()
        
        # Check if game should start
        if menu.start_game():
            return menu.get_settings(), False
        
        # Check if user wants to quit
        if menu.should_quit():
            return None, True
        
        screen.fill((30, 30, 40))
        menu.draw(screen)
        pygame.display.flip()
        clock.tick(60)

def initialize_pygame():
    """Initialize pygame and set up the display"""
    print("Wumpus World Auto Solver with Visualization")
    pygame.init()
    initial_width, initial_height = WIDTH, HEIGHT


    screen = pygame.display.set_mode((initial_width, initial_height))
    pygame.display.set_caption("Wumpus World")
    return screen

def main():
    """Main game function"""
    initialize_pygame()
    game_controller = GameController(WIDTH, HEIGHT)  # Initial size, will be updated

    while True:
        # Reset game controller state before showing menu
        game_controller.reset_controller_state()
        
        # Run menu and get settings
        settings, should_quit = run_menu_loop()
        
        if should_quit:
            break
        
        return_to_menu = game_controller.run_game_with_settings(settings)
        
        if not return_to_menu:
            break
    
    pygame.quit()

if __name__ == "__main__":
    main()
