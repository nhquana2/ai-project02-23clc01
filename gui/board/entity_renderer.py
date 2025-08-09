import pygame
from environment import Environment, Direction

class EntityRenderer:
    def __init__(self, cell_size: int, board_size: int, image_manager):
        self.cell_size = cell_size
        self.board_size = board_size
        self.image_manager = image_manager
        self.entity_surface = pygame.Surface((board_size * cell_size, board_size * cell_size), pygame.SRCALPHA)
    
    def clear_surface(self):
        self.entity_surface.fill((0, 0, 0, 0))
    
    def draw_agent(self, environment: Environment):
        agent_pos = (environment.agent_state.x, environment.agent_state.y)
        screen_x, screen_y = self._get_screen_coords(agent_pos[0], agent_pos[1])
        direction = environment.agent_state.direction
        agent_img_name = self._get_direction_image_name('agent', direction)
        self._draw_image_at_position(agent_img_name, screen_x, screen_y)
    
    def draw_wumpuses(self, environment: Environment):
        for pos in environment.wumpus_positions:
            screen_x, screen_y = self._get_screen_coords(pos[0], pos[1])
            wumpus_direction = self._get_wumpus_direction(environment, pos)
            wumpus_img_name = self._get_direction_image_name('wumpus', wumpus_direction)
            self._draw_image_at_position(wumpus_img_name, screen_x, screen_y)
    
    def draw_arrows(self, arrow_path=None):
        """Draw arrows along the arrow path when agent shoots"""
        if not arrow_path:
            return
        x, y, direction = arrow_path[-1]

        screen_x, screen_y = self._get_screen_coords(x, y)
        arrow_img_name = self._get_direction_image_name('arrow', direction)
        self._draw_image_at_position(arrow_img_name, screen_x, screen_y)
    
    
    def _get_screen_coords(self, x: int, y: int):
        return x * self.cell_size, (self.board_size - 1 - y) * self.cell_size
    
    def _get_direction_image_name(self, entity_type: str, direction: Direction):
        direction_map = {
            Direction.NORTH: f'{entity_type}_up',
            Direction.SOUTH: f'{entity_type}_down',
            Direction.WEST: f'{entity_type}_left',
            Direction.EAST: f'{entity_type}_right'
        }
        return direction_map.get(direction, f'{entity_type}_down')
    
    def _get_wumpus_direction(self, environment: Environment, pos):
        return environment.wumpus_directions.get(pos, Direction.SOUTH)
    
    def _draw_image_at_position(self, image_key: str, screen_x: int, screen_y: int):
        img_x, img_y = self.image_manager.get_centered_position(image_key, screen_x, screen_y)
        image = self.image_manager.get_image(image_key)
        self.entity_surface.blit(image, (img_x, img_y))
    
    def get_surface(self):
        return self.entity_surface
