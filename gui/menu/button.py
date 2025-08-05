import pygame
from typing import Callable, Optional

class Button:
    def __init__(self, x: int, y: int, width: int, height: int, 
                 image_source, text: str = "", font_size: int = 16,
                 text_color: tuple = (255, 255, 255), callback: Optional[Callable] = None):
        self.rect = pygame.Rect(x, y, width, height)
        self.original_rect = self.rect.copy()
        self.text = text
        self.callback = callback
        self.is_hovered = False
        self.is_pressed = False
        self.is_selected = False 
        self.text_color = text_color
        
        # Load image and font
        self.image = pygame.transform.scale(image_source.copy(), (width, height))
        self.font = pygame.font.Font("assets/font/Grand9KPixel.ttf", font_size)
        
        # Create text surfaces
        if self.text:
            self._create_text_surfaces()
    
    def _create_text_surfaces(self):
        self.text_surface = self.font.render(self.text, True, self.text_color)
        
        # Outlined text for selected state
        text_w, text_h = self.font.size(self.text)
        outlined_surface = pygame.Surface((text_w + 4, text_h + 4), pygame.SRCALPHA)
        
        # Draw outline
        outline_color = (50, 50, 50)
        selected_text_color = (20, 20, 20)
        outline_offsets = [(-1, -1), (-1, 1), (1, -1), (1, 1), (-1, 0), (1, 0), (0, -1), (0, 1)]
        
        for dx, dy in outline_offsets:
            outline_text = self.font.render(self.text, True, outline_color)
            outlined_surface.blit(outline_text, (dx + 2, dy + 2))
        
        main_text = self.font.render(self.text, True, selected_text_color)
        outlined_surface.blit(main_text, (2, 2))
        
        self.outlined_text_surface = outlined_surface
        self.text_rect = self.text_surface.get_rect(center=self.rect.center)
        outline_offsets = [(-1, -1), (-1, 1), (1, -1), (1, 1), (-1, 0), (1, 0), (0, -1), (0, 1)]
        for dx, dy in outline_offsets:
            outline_text = self.font.render(self.text, True, outline_color)
            outlined_surface.blit(outline_text, (dx + 2, dy + 2))
    def set_selected(self, selected: bool):
        self.is_selected = selected
    
    def reset_state(self):
        """Reset button interaction state"""
        self.is_hovered = False
        self.is_pressed = False
        # Note: is_selected is not reset as it represents logical state, not interaction state
    
    def set_text(self, text: str):
        self.text = text
        if self.text:
            self._create_text_surfaces()
            self.text_rect = self.text_surface.get_rect(center=self.rect.center)
    
    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1 and self.rect.collidepoint(event.pos):
                self.is_pressed = True
                return True
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1 and self.is_pressed:
                self.is_pressed = False
                if self.rect.collidepoint(event.pos) and self.callback:
                    self.callback()
                return True
        elif event.type == pygame.MOUSEMOTION:
            self.is_hovered = self.rect.collidepoint(event.pos)
        return False
    
    def update(self):
        scale = 0.95 if self.is_pressed else 1.05 if self.is_hovered else 1.0
        
        center = self.original_rect.center
        self.rect = pygame.Rect(0, 0, 
                               int(self.original_rect.width * scale),
                               int(self.original_rect.height * scale))
        self.rect.center = center
        
        if self.text:
            self.text_rect = self.text_surface.get_rect(center=self.rect.center)
    
    def draw(self, surface):
        # Draw button image
        if self.rect.size != self.image.get_size():
            scaled_image = pygame.transform.scale(self.image, self.rect.size)
            surface.blit(scaled_image, self.rect)
        else:
            surface.blit(self.image, self.rect)
        
        # Draw text
        if self.text:
            if self.is_selected:
                outlined_rect = self.outlined_text_surface.get_rect(center=self.rect.center)
                surface.blit(self.outlined_text_surface, outlined_rect)
            else:
                surface.blit(self.text_surface, self.text_rect)
