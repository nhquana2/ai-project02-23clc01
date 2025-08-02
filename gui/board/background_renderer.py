import pygame
from environment import Environment

class BackgroundRenderer:
    """Handles rendering of static background elements"""
    
    def __init__(self, environment: Environment, cell_size: int, image_manager):
        self.environment = environment
        self.cell_size = cell_size
        self.board_size = environment.size
        self.image_manager = image_manager
        
        # Create background surface
        self.background_surface = pygame.Surface((
            self.board_size * cell_size,
            self.board_size * cell_size
        ))
        
        # State tracking for optimized updates
        self.background_dirty = True
        self._last_wumpus_positions = set(environment.wumpus_positions)
        self._last_gold_state = False
    
    def build_background(self):
        """Build the static background with tiles, pits, effects, and gold"""
        self.background_surface.fill((201, 123, 198))
        
        for y in range(self.board_size):
            for x in range(self.board_size):
                pos = (x, y)
                screen_x, screen_y = self._get_screen_coords(x, y)
                
                # Draw base tile
                tile_image = self.image_manager.get_image('tile')
                self.background_surface.blit(tile_image, (screen_x, screen_y))
                
                # Skip other elements if this is a pit cell
                if pos in self.environment.pit_positions:
                    self._draw_image_at_position('pit', screen_x, screen_y)
                    continue
                
                # Draw environmental effects on empty cells
                self._draw_effects(pos, screen_x, screen_y)
                
                # Draw gold if present and not collected
                if pos == self.environment.gold_position and not self.environment.agent_state.has_gold:
                    self._draw_image_at_position('gold', screen_x, screen_y)
        
        self.background_dirty = False
    
    def _get_screen_coords(self, x: int, y: int):
        """Convert grid coordinates to screen coordinates"""
        screen_x = x * self.cell_size
        screen_y = (self.board_size - 1 - y) * self.cell_size
        return screen_x, screen_y
    
    def _draw_effects(self, pos, screen_x: int, screen_y: int):
        """Draw breeze and stench effects for a position"""
        if pos in self.environment.wumpus_positions:
            return  # No effects on wumpus cells
            
        # Draw breeze first (underneath stench)
        if self._has_adjacent_effect(pos, self.environment.pit_positions):
            self._draw_image_at_position('breeze', screen_x, screen_y)
        
        # Draw stench on top
        if self._has_adjacent_effect(pos, self.environment.wumpus_positions):
            self._draw_image_at_position('stench', screen_x, screen_y)
    
    def _has_adjacent_effect(self, pos, target_positions):
        """Check if position has effect from adjacent targets (Manhattan distance = 1)"""
        for target_pos in target_positions:
            if abs(pos[0] - target_pos[0]) + abs(pos[1] - target_pos[1]) == 1:
                return True
        return False
    
    def _draw_image_at_position(self, image_key: str, screen_x: int, screen_y: int):
        """Draw image centered at screen position"""
        img_x, img_y = self.image_manager.get_centered_position(image_key, screen_x, screen_y)
        image = self.image_manager.get_image(image_key)
        self.background_surface.blit(image, (img_x, img_y))
    
    def should_rebuild_background(self, environment: Environment):
        """Check if background needs rebuilding"""
        current_wumpus_positions = set(environment.wumpus_positions)
        wumpus_moved = current_wumpus_positions != self._last_wumpus_positions
        gold_state_changed = environment.agent_state.has_gold != self._last_gold_state
        
        return self.background_dirty or wumpus_moved or gold_state_changed
    
    def update_tracking_state(self, environment: Environment):
        """Update state tracking variables"""
        self._last_gold_state = environment.agent_state.has_gold
        self._last_wumpus_positions = set(environment.wumpus_positions)
    
    def update_environment(self, environment: Environment):
        """Update environment reference"""
        self.environment = environment
    
    def get_surface(self):
        """Get the background surface"""
        return self.background_surface
    
    def force_rebuild(self):
        """Force rebuild of background on next draw"""
        self.background_dirty = True
