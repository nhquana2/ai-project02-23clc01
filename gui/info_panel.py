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
        
        # Load assets directly
        self.title_font = pygame.font.Font("assets/font/Grand9KPixel.ttf", font_size + 8)
        self.large_font = pygame.font.Font("assets/font/Grand9KPixel.ttf", font_size + 4)
        self.text_font = pygame.font.Font("assets/font/Grand9KPixel.ttf", font_size)
        self.pause_button_img = pygame.image.load("assets/buttons/gray_button.png")
        
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
    
    def _on_pause_clicked(self):
        if self.pause_callback:
            self.pause_callback()
    
    def set_pause_callback(self, callback):
        self.pause_callback = callback
    
    def draw(self, env: Environment, agent: HybridAgent, step_count: int, current_percepts):
        self.surface.fill(self.bg_color)
        pygame.draw.rect(self.surface, self.border_color, (0, 0, self.width, self.height), 3)
        
        y = 20
        # Title
        title = self.title_font.render("GAME INFO", True, self.title_color)
        self.surface.blit(title, (title.get_rect(centerx=self.width // 2).x, y))
        y += 50
        
        # Score
        score = self.large_font.render(f"SCORE: {env.agent_state.score}", True, self.highlight_color)
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
        """Handle events for the info panel (mainly pause button)"""
        if offset_x or offset_y:
            # Adjust event position for offset
            if hasattr(event, 'pos'):
                adjusted_event = type(event)(event.type, event.dict)
                adjusted_event.pos = (event.pos[0] - offset_x, event.pos[1] - offset_y)
                return self.pause_button.handle_event(adjusted_event)
        return self.pause_button.handle_event(event)
    
    def update(self):
        self.pause_button.update()
    
    def get_surface(self):
        return self.surface
