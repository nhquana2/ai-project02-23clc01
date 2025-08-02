import pygame
import os

class ImageManager:
    """Handles loading and scaling of all game images"""
    
    def __init__(self, cell_size: int):
        self.cell_size = cell_size
        self.images = {}
        
        # Image scale factors for visual balance
        self.scale_factors = {
            'tile': 1.0,
            'pit': 1.0,
            'gold': 0.6,
            'breeze': 0.6,
            'stench': 0.5,
            'agent': 0.5,
            'wumpus': 0.5
        }
        
        self.load_images()
    
    def load_images(self):
        """Load and scale all game images"""
        current_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        base_path = os.path.join(current_dir, "assets", "images")

        # Static images
        static_images = {
            'tile': "cell.png",
            'pit': "pit.png",
            'gold': "gold.png",
            'breeze': "breeze.png",
            'stench': "stench.png"
        }
        
        # Directional images
        directions = ['up', 'down', 'left', 'right']
        
        try:
            # Load static images
            for key, filename in static_images.items():
                self.images[key] = pygame.image.load(os.path.join(base_path, filename))

            # Load directional images
            for direction in directions:
                wumpus_path = os.path.join(base_path, "wumpus", f'wumpus_{direction}.png')
                agent_path = os.path.join(base_path, "agent", f'agent_{direction}.png')
                self.images[f'wumpus_{direction}'] = pygame.image.load(wumpus_path)
                self.images[f'agent_{direction}'] = pygame.image.load(agent_path)
            
            # Scale all images
            self._scale_images()
                
        except pygame.error as e:
            print(f"Could not load image: {e}")

    def _scale_images(self):
        """Scale all loaded images according to scale factors"""
        for key, image in self.images.items():
            if key.startswith(('agent_', 'wumpus_')):
                scale_factor = self.scale_factors['agent']
            else:
                scale_factor = self.scale_factors.get(key, 1.0)
                
            scaled_size = int(self.cell_size * scale_factor)
            self.images[key] = pygame.transform.scale(image, (scaled_size, scaled_size))
    
    def get_image(self, key: str):
        """Get scaled image by key"""
        return self.images.get(key)
    
    def get_centered_position(self, image_key: str, screen_x: int, screen_y: int):
        """Calculate centered position for image placement"""
        if image_key.startswith(('agent_', 'wumpus_')):
            scale_factor = self.scale_factors['agent']
        else:
            scale_factor = self.scale_factors.get(image_key, 1.0)
            
        scaled_size = int(self.cell_size * scale_factor)
        offset = (self.cell_size - scaled_size) // 2
        return (screen_x + offset, screen_y + offset)
