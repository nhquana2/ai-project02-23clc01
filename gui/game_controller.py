import pygame
import time
from gui.menu.button import Button
from environment import Environment, Action
from hybrid_agent import HybridAgent
from random_agent import RandomAgent
from gui.board import Board
from gui.info_panel import InfoPanel

class GameController:
    """Game state controller for pause/resume functionality"""

    def __init__(self, screen_width: int, screen_height: int):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.is_visible = False
        self.resume_game = False
        self.quit_to_menu = False
        
        # Create overlay
        self.overlay = pygame.Surface((screen_width, screen_height))
        self.overlay.set_alpha(128)
        self.overlay.fill((0, 0, 0))
        
        # Load assets and setup UI
        self._load_assets()
        self._setup_layout()
        self._create_buttons()

    def _load_assets(self):
        """Load fonts and button images"""
        font_path = "assets/font/Grand9KPixel.ttf"
        self.green_button_img = pygame.image.load("assets/buttons/yellow_button.png")
        self.red_button_img = pygame.image.load("assets/buttons/red_button.png")
        self.title_font = pygame.font.Font(font_path, 32)
        self.text_font = pygame.font.Font(font_path, 20)
        
        # Colors
        self.title_color = (255, 255, 255)
        self.bg_color = (45, 45, 45)
        self.border_color = (100, 150, 255)

    def _setup_layout(self):
        """Calculate menu layout dimensions"""
        self.menu_width = 450
        self.menu_height = 300
        self.menu_x = (self.screen_width - self.menu_width) // 2
        self.menu_y = (self.screen_height - self.menu_height) // 2

    def _create_buttons(self):
        """Create pause menu buttons"""
        btn_w, btn_h = 150, 50
        center_x = self.menu_x + self.menu_width // 2
        btn_y = self.menu_y + self.menu_height - 80
        start_x = center_x - (2 * btn_w + 20) // 2
        
        self.resume_button = Button(
            start_x, btn_y, btn_w, btn_h, self.green_button_img, 
            "RESUME", 18, (255, 255, 255), self._resume_game
        )
        
        self.menu_button = Button(
            start_x + btn_w + 20, btn_y, btn_w, btn_h, 
            self.red_button_img, "MENU", 18, (255, 255, 255), 
            self._return_to_menu
        )
    
    def _resume_game(self):
        self.resume_game = True
        self.is_visible = False
    
    def _return_to_menu(self):
        self.quit_to_menu = True
        self.is_visible = False
    
    def show(self):
        """Show pause menu and reset state flags"""
        self.is_visible = True
        self.resume_game = False
        self.quit_to_menu = False

    def reset_controller_state(self):
        """Reset controller state for new game or returning to menu"""
        self.is_visible = False
        self.resume_game = False
        self.quit_to_menu = False
        print("Controller state reset - all flags cleared")
    
    def handle_event(self, event):
        if not self.is_visible:
            return False
        
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self._resume_game()
            return True
        
        self.resume_button.handle_event(event)
        self.menu_button.handle_event(event)
        return True
    
    def update(self):
        if self.is_visible:
            self.resume_button.update()
            self.menu_button.update()
    
    def draw(self, screen):
        if not self.is_visible:
            return
        
        # Draw overlay and background
        screen.blit(self.overlay, (0, 0))
        menu_rect = pygame.Rect(self.menu_x, self.menu_y, self.menu_width, self.menu_height)
        pygame.draw.rect(screen, self.bg_color, menu_rect)
        pygame.draw.rect(screen, self.border_color, menu_rect, 3)
        
        # Draw centered text
        center_x = self.menu_x + self.menu_width // 2
        
        # Title
        title = self.title_font.render("GAME PAUSED", True, self.title_color)
        screen.blit(title, title.get_rect(centerx=center_x, y=self.menu_y + 30))
        
        # Instruction
        instruction = self.text_font.render("Press ESC or click RESUME to continue", True, (200, 200, 200))
        screen.blit(instruction, instruction.get_rect(centerx=center_x, y=self.menu_y + 100))
        
        # Buttons
        self.resume_button.draw(screen)
        self.menu_button.draw(screen)
    
    @property
    def should_resume_game(self):
        return self.resume_game
    
    @property 
    def should_return_to_menu(self):
        return self.quit_to_menu

    # Game management methods
    def create_agent(self, env, agent_mode):
        """Create agent based on selected mode"""
        # Import here to avoid circular imports
        from gui.menu import MainMenu
        if agent_mode == MainMenu.AgentMode.RANDOM:
            return RandomAgent(env)
        else:
            return HybridAgent(env)

    def setup_game_components(self, settings):
        """Initialize all game components and return them"""
        from gui.menu import MainMenu
        
        # Create environment
        moving_wumpus = (settings.environment_mode == MainMenu.EnvironmentMode.DYNAMIC)
        env = Environment(settings.board_size, settings.num_wumpus, settings.pit_probability, moving_wumpus)
        agent = self.create_agent(env, settings.agent_mode)
        
        # Calculate dimensions
        cell_size = 80
        board_size = settings.board_size * cell_size
        info_panel_width = 480
        screen_width = board_size + info_panel_width + 20
        info_panel_x = board_size + 10
        
        # Update screen and controller
        screen = pygame.display.set_mode((screen_width, board_size))
        self._update_for_new_screen_size(screen_width, board_size)
        
        # Create GUI components
        board = Board(env, cell_size=cell_size, agent_knowledge=agent.knowledge)
        info_panel = InfoPanel(info_panel_width, board_size, font_size=14)
        info_panel.set_pause_callback(lambda: self.show())
        
        return env, agent, screen, board, info_panel, info_panel_x

    def _update_for_new_screen_size(self, screen_width, screen_height):
        """Update controller layout for new screen size"""
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.overlay = pygame.Surface((screen_width, screen_height))
        self.overlay.set_alpha(128)
        self.overlay.fill((0, 0, 0))
        self._setup_layout()
        self._create_buttons()

    def handle_game_events(self, event, info_panel, info_panel_x):
        """Handle all game-related events and return action needed"""
        if event.type == pygame.QUIT:
            return "quit"
        
        # Handle pause menu events first
        if self.handle_event(event):
            return "continue"
        
        # Handle info panel events and ESC key
        info_panel.handle_event(event, info_panel_x, 0)
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.show()
        
        return "normal"

    def execute_agent_step(self, env, agent, step_count, current_time, last_step_time, step_delay):
        """Execute one step of agent thinking and action"""
        if current_time - last_step_time < step_delay:
            return step_count, last_step_time, True
        
        percepts = env.get_percept()
        
        # Print percept status
        percept_attrs = ['stench', 'breeze', 'glitter', 'bump', 'scream']
        percept_status = [f"{attr}: {str(getattr(percepts, attr)).lower()}" for attr in percept_attrs]
        print(f"Step {step_count + 1}: {{{'; '.join(percept_status)}}}")
        
        # Execute agent action
        agent.think(percepts)

        if not agent.action_plan:
            print("No more actions available")
            return step_count, last_step_time, False
        
        action = agent.action_plan.pop(0)
        new_percepts = env.execute_action(action)
        agent._update_state(action, new_percepts)
        
        # Reset KB
        if env.moving_wumpus_mode and env.agent_action_count > 0 and env.agent_action_count % 5 == 0:
            agent.inference_engine.reset_kb()
        
        step_count += 1
        last_step_time = current_time
        
        # Check end conditions
        if action == Action.CLIMB or not agent.state.alive:
            print(f"Agent {'climbed out' if action == Action.CLIMB else 'died'}! Final Score: {env.agent_state.score}")
            return step_count, last_step_time, False
        
        return step_count, last_step_time, True

    def render_game(self, screen, board, info_panel, env, agent, step_count, info_panel_x):
        """Render all game components"""
        screen.fill((40, 40, 40))
        
        # Draw board
        board.draw()
        screen.blit(board.get_surface(), (0, 0))
        
        # Draw info panel
        current_percepts = env.get_percept()
        info_panel.draw(env, agent, step_count, current_percepts)
        screen.blit(info_panel.get_surface(), (info_panel_x, 0))
        
        # Draw game controller overlay if visible
        self.draw(screen)
        
        pygame.display.flip()

    def run_game_with_settings(self, settings):
        """Run the game with given settings"""
        self.reset_controller_state()
        
        # Setup game components
        env, agent, screen, board, info_panel, info_panel_x = self.setup_game_components(settings)
        
        # Game state variables
        running = True
        step_delay = 0.5
        last_step_time = time.time()
        step_count = 0
        clock = pygame.time.Clock()
        
        while running and agent.state.alive:
            current_time = time.time()
            
            # Handle events
            for event in pygame.event.get():
                event_result = self.handle_game_events(event, info_panel, info_panel_x)
                if event_result == "quit":
                    return False
                elif event_result == "continue":
                    continue
            
            # Update components
            self.update()
            info_panel.update()
            
            # Check pause menu actions
            if self.should_return_to_menu:
                self.resume_game = False
                self.quit_to_menu = False
                self.is_visible = False
                return True

            # Execute game logic if not paused
            if not self.is_visible and agent.state.alive:
                step_count, last_step_time, should_continue = self.execute_agent_step(
                    env, agent, step_count, current_time, last_step_time, step_delay
                )
                # Always update board after an action is executed
                board.update(env, agent.knowledge)
                
                if not should_continue:
                    running = False
            
            # Render everything
            self.render_game(screen, board, info_panel, env, agent, step_count, info_panel_x)
            clock.tick(60)
        
        print(f"\nSimulation ended. Final Score: {env.agent_state.score}")
        return True
