import pygame
from .button import Button

class MenuUI:
    """Menu UI rendering and asset management"""
    
    SECTION_SPACING = 120
    BASE_Y = 150
    BUTTON_WIDTH = 200
    BUTTON_HEIGHT = 50
    
    def __init__(self, width: int, height: int, screen=None):
        self.width = width
        self.height = height
        self.screen = screen
        self.surface = pygame.Surface((width, height))
        
        # Colors
        self.bg_color = (30, 30, 40)
        self.title_color = (100, 150, 255)
        self.text_color = (220, 220, 220)
        self.highlight_color = (255, 255, 100)
        
        # Fonts
        self.title_font = pygame.font.Font("assets/font/Grand9KPixel.ttf", 32)
        self.subtitle_font = pygame.font.Font("assets/font/Grand9KPixel.ttf", 20)
        self.text_font = pygame.font.Font("assets/font/Grand9KPixel.ttf", 16)

        # Load assets
        self.bg_image = pygame.image.load("assets/bg_menu.png")
        
        button_names = ['yellow', 'gray', 'red', 'prev', 'next']
        self.button_images = {}
        for name in button_names:
            self.button_images[name] = pygame.image.load(f'assets/buttons/{name}_button.png')
    
    def create_button(self, x, y, width, height, image_key, text, callback=None):
        return Button(x, y, width, height, self.button_images[image_key], text, 
                     font_size=16, text_color=(255, 255, 255), callback=callback)
    
    def update_button_group(self, buttons, states):
        for btn, is_selected in zip(buttons, states):
            image_key = 'yellow' if is_selected else 'gray'
            btn.image = pygame.transform.scale(self.button_images[image_key].copy(), 
                                             (btn.original_rect.width, btn.original_rect.height))
            btn.set_selected(is_selected)
    
    def draw_background(self):
        """Draw background"""
        if self.bg_image:
            self.surface.blit(self.bg_image, (0, 0))
        else:
            self.surface.fill(self.bg_color)
    
    def draw_title(self):
        title = self.title_font.render("WUMPUS WORLD", True, self.title_color)
        self.surface.blit(title, title.get_rect(centerx=self.width // 2, y=50))
        
        #subtitle = self.subtitle_font.render("Game Configuration", True, self.text_color)
        #self.surface.blit(subtitle, subtitle.get_rect(centerx=self.width // 2, y=90))
    
    def draw_section_title(self, title, y_pos):
        title_surface = self.subtitle_font.render(title, True, self.highlight_color)
        self.surface.blit(title_surface, title_surface.get_rect(centerx=self.width // 2, y=y_pos))
    
    def draw_environment_section(self, base_y):
        self.draw_section_title("Environment Mode", base_y)
        desc = self.text_font.render("(Dynamic mode - Moving Wumpus)", True, (150, 150, 150))
        self.surface.blit(desc, desc.get_rect(centerx=self.width // 2, y=base_y + 20))
    
    def draw_agent_section(self, base_y):
        self.draw_section_title("Agent Mode", base_y - 10)
    
    def draw_config_section(self, base_y):
        self.draw_section_title("Game Configuration", base_y)
        
        labels = [("Board Size", self.width // 2 - 150),
                 ("Pit Probability", self.width // 2),
                 ("Wumpus Count", self.width // 2 + 150)]
        
        for text, x_pos in labels:
            label = self.text_font.render(text, True, self.text_color)
            self.surface.blit(label, label.get_rect(centerx=x_pos, y=base_y + 30))
    
    def draw_buttons(self, buttons):
        for button in buttons:
            button.draw(self.surface)
    
    def draw_complete_menu(self, buttons):
        self.draw_background()
        self.draw_title()
        
        self.draw_environment_section(self.BASE_Y)
        self.draw_agent_section(self.BASE_Y + self.SECTION_SPACING)
        self.draw_config_section(self.BASE_Y + 2 * self.SECTION_SPACING)
        
        self.draw_buttons(buttons)
    
    def blit_to_target(self, target_surface):
        if target_surface and target_surface != self.surface:
            target_surface.blit(self.surface, (0, 0))
