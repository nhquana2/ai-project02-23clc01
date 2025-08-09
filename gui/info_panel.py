import pygame
from environment import Environment
from hybrid_agent import HybridAgent
from gui.menu.button import Button

class InfoPanel:
    """Game information panel with pause functionality"""
    
    def __init__(self, width: int, height: int, font_size: int = 16):
        self.width = width
        self.height = height
        self.surface = pygame.Surface((width, height))
        self.pause_callback = None
        self.menu_callback = None
        self.game_over = False
        self.game_over_message = ""
        self.final_score = 0
        
        # Load assets directly
        self.title_font = pygame.font.Font("assets/font/Grand9KPixel.ttf", font_size + 8)
        self.large_font = pygame.font.Font("assets/font/Grand9KPixel.ttf", font_size + 4)
        self.text_font = pygame.font.Font("assets/font/Grand9KPixel.ttf", font_size)
        self.pause_button_img = pygame.image.load("assets/buttons/gray_button.png")
        self.menu_button_img = pygame.image.load("assets/buttons/red_button.png")
        
        # Colors
        self.bg_color = (45, 45, 45)
        self.border_color = (80, 80, 80)
        self.title_color = (100, 150, 255)
        self.text_color = (220, 220, 220)
        self.highlight_color = (255, 255, 100)
        self.good_color = (100, 255, 100)
        self.bad_color = (255, 100, 100)
        
        # Create pause button
        button_width, button_height = 120, 40
        self.pause_button = Button(
            (width - button_width) // 2, height - 60,
            button_width, button_height, self.pause_button_img,
            "PAUSE", 16, (255, 255, 255), self._on_pause_clicked
        )
        
        # Create menu button for game over (initially hidden)
        self.menu_button = Button(
            (width - button_width) // 2, height - 60,
            button_width, button_height, self.menu_button_img,
            "MENU", 16, (255, 255, 255), self._on_menu_clicked
        )
    
    def _on_pause_clicked(self):
        if self.pause_callback:
            self.pause_callback()
    
    def _on_menu_clicked(self):
        if self.menu_callback:
            self.menu_callback()
    
    def set_pause_callback(self, callback):
        self.pause_callback = callback
    
    def set_menu_callback(self, callback):
        self.menu_callback = callback
    
    def set_game_over(self, message: str, final_score: int):
        """Set game over state with message and final score"""
        self.game_over = True
        self.game_over_message = message
        self.final_score = final_score
    
    def draw(self, env: Environment, agent: HybridAgent, step_count: int, current_percepts):
        # Force refresh surface every time for accurate score display
        self.surface.fill(self.bg_color)
        pygame.draw.rect(self.surface, self.border_color, (0, 0, self.width, self.height), 3)
        
        if self.game_over:
            self._draw_game_over()
        else:
            self._draw_normal_game_info(env, agent, step_count, current_percepts)
    
    def _draw_normal_game_info(self, env: Environment, agent: HybridAgent, step_count: int, current_percepts):
        """Draw normal game information"""
        y = 20
        # Title
        title = self.title_font.render("GAME INFO", True, self.title_color)
        self.surface.blit(title, (title.get_rect(centerx=self.width // 2).x, y))
        y += 50
        
        # Score
        current_score = env.agent_state.score
        score = self.large_font.render(f"SCORE: {current_score}", True, self.highlight_color)
        self.surface.blit(score, (score.get_rect(centerx=self.width // 2).x, y))
        y += 40
        
        # Step
        step = self.text_font.render(f"STEP: {step_count}", True, self.text_color)
        self.surface.blit(step, (step.get_rect(centerx=self.width // 2).x, y))
        y += 30
        
        # Mode
        if hasattr(env, 'moving_wumpus_mode'):
            mode_text = "MODE: DYNAMIC" if env.moving_wumpus_mode else "MODE: STATIC"
            mode_color = self.good_color if env.moving_wumpus_mode else self.text_color
            mode = self.text_font.render(mode_text, True, mode_color)
            self.surface.blit(mode, (mode.get_rect(centerx=self.width // 2).x, y))
        y += 30
        
        # Agent type
        agent_type = "RANDOM" if 'Random' in str(type(agent).__name__) else "HYBRID"
        agent_color = self.highlight_color if agent_type == "RANDOM" else self.good_color
        agent_text = self.text_font.render(f"AGENT: {agent_type}", True, agent_color)
        self.surface.blit(agent_text, (agent_text.get_rect(centerx=self.width // 2).x, y))
        y += 40
        
        # Percepts title
        percepts_title = self.title_font.render("CURRENT PERCEPTS", True, self.title_color)
        self.surface.blit(percepts_title, (percepts_title.get_rect(centerx=self.width // 2).x, y))
        y += 50
        
        # Draw percepts
        self._draw_percepts(current_percepts, y)
        
        # Draw pause button
        self.pause_button.draw(self.surface)
    
    def _draw_game_over(self):
        """Draw game over screen"""
        y = 50
        
        # Game Over title
        title = self.title_font.render("GAME OVER", True, self.bad_color)
        self.surface.blit(title, (title.get_rect(centerx=self.width // 2).x, y))
        y += 80
        
        # Game result message
        message_color = self.good_color if "climbed" in self.game_over_message.lower() else self.bad_color
        message = self.large_font.render(self.game_over_message, True, message_color)
        self.surface.blit(message, (message.get_rect(centerx=self.width // 2).x, y))
        y += 60
        
        # Final score
        score_text = self.large_font.render(f"FINAL SCORE: {self.final_score}", True, self.highlight_color)
        self.surface.blit(score_text, (score_text.get_rect(centerx=self.width // 2).x, y))
        y += 80
        
        # Instructions
        instruction1 = self.text_font.render("Game has ended!", True, self.text_color)
        self.surface.blit(instruction1, (instruction1.get_rect(centerx=self.width // 2).x, y))
        y += 30
        
        instruction2 = self.text_font.render("Click the button below to", True, self.text_color)
        self.surface.blit(instruction2, (instruction2.get_rect(centerx=self.width // 2).x, y))
        y += 25
        
        instruction3 = self.text_font.render("return to main menu", True, self.text_color)
        self.surface.blit(instruction3, (instruction3.get_rect(centerx=self.width // 2).x, y))
        
        # Draw menu button
        self.menu_button.draw(self.surface)
    
    def _draw_percepts(self, percepts, y_pos):
        if not percepts:
            return
        
        percept_data = [
            ("STENCH", percepts.stench, self.bad_color),
            ("BREEZE", percepts.breeze, self.bad_color),
            ("GLITTER", percepts.glitter, self.good_color),
            ("BUMP", percepts.bump, self.highlight_color),
            ("SCREAM", percepts.scream, self.good_color)
        ]
        
        for i, (name, value, color) in enumerate(percept_data):
            y = y_pos + i * 60
            if y + 50 > self.height - 80:  # Leave space for pause button
                break
                
            # Background
            bg_color = (60, 60, 60) if value else (30, 30, 30)
            rect = pygame.Rect(15, y, self.width - 30, 50)
            pygame.draw.rect(self.surface, bg_color, rect, border_radius=5)
            
            if value:
                pygame.draw.rect(self.surface, color, rect, 3, border_radius=5)
            
            # Text
            text_color = color if value else self.text_color
            name_text = self.text_font.render(name, True, text_color)
            status_text = self.text_font.render("true" if value else "false", True, text_color)
            
            self.surface.blit(name_text, (30, y + 10))
            self.surface.blit(status_text, (30, y + 30))
    
    def handle_event(self, event, offset_x=0, offset_y=0):
        """Handle events for the info panel (pause button or menu button)"""
        if offset_x or offset_y:
            # Adjust event position for offset
            if hasattr(event, 'pos'):
                adjusted_event = type(event)(event.type, event.dict)
                adjusted_event.pos = (event.pos[0] - offset_x, event.pos[1] - offset_y)
                if self.game_over:
                    return self.menu_button.handle_event(adjusted_event)
                else:
                    return self.pause_button.handle_event(adjusted_event)
        
        if self.game_over:
            return self.menu_button.handle_event(event)
        else:
            return self.pause_button.handle_event(event)
    
    def update(self):
        if self.game_over:
            self.menu_button.update()
        else:
            self.pause_button.update()
    
    def get_surface(self):
        return self.surface
