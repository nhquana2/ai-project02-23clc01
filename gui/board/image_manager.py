import pygame

class ImageManager:
    def __init__(self, cell_size: int):
        self.cell_size = cell_size
        self.images = {}
        self.scale_factors = {
            'tile': 1.0, 'pit': 1.0, 'gold': 0.6, 'breeze': 0.6, 
            'stench': 0.5, 'agent': 0.5, 'wumpus': 0.5, 'arrow': 0.5
            
        }
        self.load_images()
    
    def load_images(self):
        static_images = {
            'tile': "cell.png", 'pit': "pit.png", 'gold': "gold.png",
            'breeze': "breeze.png", 'stench': "stench.png"
        }
        
        for key, filename in static_images.items():
            self.images[key] = pygame.image.load(f'assets/images/{filename}')
        
        for direction in ['up', 'down', 'left', 'right']:
            self.images[f'agent_{direction}'] = pygame.image.load(f'assets/images/agent/agent_{direction}.png')
            self.images[f'wumpus_{direction}'] = pygame.image.load(f'assets/images/wumpus/wumpus_{direction}.png')
            self.images[f'arrow_{direction}'] = pygame.image.load(f'assets/images/arrow/arrow_{direction}.png')
        
        self._scale_images()

    
    def _scale_images(self):
        for key, image in self.images.items():
            scale_factor = self.scale_factors['agent'] if key.startswith(('agent_', 'wumpus_', 'arrow_')) else self.scale_factors.get(key, 1.0)
            scaled_size = int(self.cell_size * scale_factor)
            self.images[key] = pygame.transform.scale(image, (scaled_size, scaled_size))
    
    def get_image(self, key: str):
        return self.images.get(key)
    
    def get_centered_position(self, image_key: str, screen_x: int, screen_y: int):
        scale_factor = self.scale_factors['agent'] if image_key.startswith(('agent_', 'wumpus_', 'arrow_')) else self.scale_factors.get(image_key, 1.0)
        scaled_size = int(self.cell_size * scale_factor)
        offset = (self.cell_size - scaled_size) // 2
        return (screen_x + offset, screen_y + offset)
