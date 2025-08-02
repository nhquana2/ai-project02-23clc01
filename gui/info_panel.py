import pygame
import os
from environment import Environment
from hybrid_agent import HybridAgent

class InfoPanel:
    """Handles rendering of game information panel"""
    
    def __init__(self, width: int, height: int, font_size: int = 16):
        self.width = width
        self.height = height
        self.surface = pygame.Surface((width, height))
        
        # Load fonts with fallback
        font_path = self._get_font_path()
        try:
            if font_path and os.path.exists(font_path):
                self.title_font = pygame.font.Font(font_path, font_size + 8)
                self.large_font = pygame.font.Font(font_path, font_size + 4)
                self.text_font = pygame.font.Font(font_path, font_size)
            else:
                # Fallback to default fonts
                self.title_font = pygame.font.Font(None, font_size + 8)
                self.large_font = pygame.font.Font(None, font_size + 4)
                self.text_font = pygame.font.Font(None, font_size)
        except pygame.error:
            # Fallback to default fonts if custom font fails
            self.title_font = pygame.font.Font(None, font_size + 8)
            self.large_font = pygame.font.Font(None, font_size + 4)
            self.text_font = pygame.font.Font(None, font_size)
        
        # Colors
        self.bg_color = (45, 45, 45)
        self.border_color = (80, 80, 80)
        self.title_color = (100, 150, 255)
        self.text_color = (220, 220, 220)
        self.highlight_color = (255, 255, 100)
        self.good_color = (100, 255, 100)
        self.bad_color = (255, 100, 100)
    
    def _get_font_path(self):
        """Get path to custom font with proper error handling"""
        current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        font_path = os.path.join(current_dir, "assets", "font", "Grand9KPixel.ttf")
        return font_path if os.path.exists(font_path) else None
    
    def draw(self, env: Environment, agent: HybridAgent, step_count: int, current_percepts):
        """Draw the info panel with current percepts"""
        # Clear surface
        self.surface.fill(self.bg_color)
        
        # Draw border
        pygame.draw.rect(self.surface, self.border_color, (0, 0, self.width, self.height), 3)
        
        # Title
        y_pos = 20
        title_text = self.title_font.render("CURRENT PERCEPTS", True, self.title_color)
        title_rect = title_text.get_rect(centerx=self.width // 2)
        self.surface.blit(title_text, (title_rect.x, y_pos))
        
        # Current percepts display
        self._draw_large_percepts(current_percepts, y_pos + 60)
    
    def _draw_large_percepts(self, current_percepts, y_pos: int):
        """Draw current percepts in large format"""
        if not current_percepts:
            return
        
        percepts = [
            ("STENCH", current_percepts.stench, self.bad_color),
            ("BREEZE", current_percepts.breeze, self.bad_color),
            ("GLITTER", current_percepts.glitter, self.good_color),
            ("BUMP", current_percepts.bump, self.highlight_color),
            ("SCREAM", current_percepts.scream, self.good_color)
        ]
        
        # Calculate spacing
        percept_height = 80
        start_y = y_pos + (self.height - y_pos - len(percepts) * percept_height) // 2
        
        for i, (name, value, active_color) in enumerate(percepts):
            current_y = start_y + i * percept_height
            
            # Background for each percept
            percept_bg_color = (60, 60, 60) if value else (30, 30, 30)
            percept_rect = pygame.Rect(15, current_y, self.width - 30, percept_height - 10)
            pygame.draw.rect(self.surface, percept_bg_color, percept_rect, border_radius=5)
            
            if value:
                # Active percept - draw border
                pygame.draw.rect(self.surface, active_color, percept_rect, 3, border_radius=5)
            
            # Percept name and status
            text_color = active_color if value else self.text_color
            status_text = "true" if value else "false"
            
            # Large percept name
            name_text = self.large_font.render(name, True, text_color)
            name_x = 30
            name_y = current_y + 15
            self.surface.blit(name_text, (name_x, name_y))
            
            # Status text
            status_text_surface = self.text_font.render(status_text, True, text_color)
            status_x = 30
            status_y = current_y + 45
            self.surface.blit(status_text_surface, (status_x, status_y))
    
    def get_surface(self):
        """Get the info panel surface"""
        return self.surface
