import pygame
from environment import Environment, Direction

class EntityRenderer:
    """Handles rendering of dynamic entities (agent, wumpus)"""
    
    def __init__(self, cell_size: int, board_size: int, image_manager):
        self.cell_size = cell_size
        self.board_size = board_size
        self.image_manager = image_manager
        
        # Create entity surface with transparency
        self.entity_surface = pygame.Surface((
            board_size * cell_size,
            board_size * cell_size
        ), pygame.SRCALPHA)
    
    def clear_surface(self):
        """Clear the entity surface for redrawing"""
        self.entity_surface.fill((0, 0, 0, 0))
    
    def draw_agent(self, environment: Environment):
        """Draw agent on the entity surface"""
        agent_pos = (environment.agent_state.x, environment.agent_state.y)
        screen_x, screen_y = self._get_screen_coords(agent_pos[0], agent_pos[1])
        
        direction = environment.agent_state.direction
        agent_img_name = self._get_direction_image_name('agent', direction)
        self._draw_image_at_position(agent_img_name, screen_x, screen_y)
    
    def draw_wumpuses(self, environment: Environment):
        """Draw all wumpuses on the entity surface"""
        for pos in environment.wumpus_positions:
            screen_x, screen_y = self._get_screen_coords(pos[0], pos[1])
            
            # Get wumpus direction (default to south if not available)
            wumpus_direction = self._get_wumpus_direction(environment, pos)
            wumpus_img_name = self._get_direction_image_name('wumpus', wumpus_direction)
            self._draw_image_at_position(wumpus_img_name, screen_x, screen_y)
    
    def _get_screen_coords(self, x: int, y: int):
        """Convert grid coordinates to screen coordinates"""
        screen_x = x * self.cell_size
        screen_y = (self.board_size - 1 - y) * self.cell_size
        return screen_x, screen_y
    
    def _get_direction_image_name(self, entity_type: str, direction: Direction):
        """Get image name based on entity type and direction"""
        direction_map = {
            Direction.NORTH: f'{entity_type}_up',
            Direction.SOUTH: f'{entity_type}_down',
            Direction.WEST: f'{entity_type}_left',
            Direction.EAST: f'{entity_type}_right'
        }
        return direction_map.get(direction, f'{entity_type}_down')
    
    def _get_wumpus_direction(self, environment: Environment, pos):
        """Get direction for wumpus at given position"""
        if not hasattr(environment, 'wumpus_directions'):
            return Direction.SOUTH
            
        wumpus_list = list(environment.wumpus_positions)
        if pos in wumpus_list:
            index = wumpus_list.index(pos)
            if index < len(environment.wumpus_directions):
                return environment.wumpus_directions[index]
        return Direction.SOUTH
    
    def _draw_image_at_position(self, image_key: str, screen_x: int, screen_y: int):
        """Draw image centered at screen position"""
        img_x, img_y = self.image_manager.get_centered_position(image_key, screen_x, screen_y)
        image = self.image_manager.get_image(image_key)
        self.entity_surface.blit(image, (img_x, img_y))
    
    def get_surface(self):
        """Get the entity surface"""
        return self.entity_surface
