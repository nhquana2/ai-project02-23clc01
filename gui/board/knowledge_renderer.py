import pygame
from agent_knowledge import MapKnowledge, CellStatus

class KnowledgeRenderer:
    def __init__(self, cell_size: int, board_size: int):
        self.cell_size = cell_size
        self.board_size = board_size
        self.knowledge_surface = pygame.Surface((board_size * cell_size, board_size * cell_size), pygame.SRCALPHA)
    
    def clear_surface(self):
        self.knowledge_surface.fill((0, 0, 0, 0))
    
    def draw_knowledge(self, agent_knowledge: MapKnowledge):
        if not agent_knowledge:
            return
        
        self.clear_surface()
        
        for y in range(self.board_size):
            for x in range(self.board_size):
                cell = agent_knowledge.get_cell(x, y)
                if not cell:
                    continue
                
                screen_x, screen_y = self._get_screen_coords(x, y)
                self._draw_cell_knowledge(cell, screen_x, screen_y)
    
    
    def _get_screen_coords(self, x: int, y: int):
        return x * self.cell_size, (self.board_size - 1 - y) * self.cell_size
    
    def _draw_cell_knowledge(self, cell, screen_x: int, screen_y: int):
        cell_overlay = pygame.Surface((self.cell_size, self.cell_size), pygame.SRCALPHA)
        
        if cell.visited:
            cell_overlay.fill((0, 255, 0, 25))
        
        font_size = max(12, self.cell_size // 4)
        font = pygame.font.Font(None, font_size)
        
        self._draw_status_symbol(cell_overlay, cell.status, font)
        self._draw_percept_indicators(cell_overlay, cell, font, font_size)
        
        self.knowledge_surface.blit(cell_overlay, (screen_x, screen_y))
    
    def _draw_status_symbol(self, surface, status: CellStatus, font):
        status_colors = {
            CellStatus.SAFE: ((0, 255, 0), "OK"),
            CellStatus.PIT: ((255, 0, 0), "P"),
            CellStatus.WUMPUS: ((255, 100, 0), "W"),
            CellStatus.UNKNOWN: ((128, 128, 128), "?")
        }
        
        if status in status_colors:
            color, symbol = status_colors[status]
            text = font.render(symbol, True, color)
            surface.blit(text, (2, 2))
    
    
    def _draw_percept_indicators(self, surface, cell, font, font_size: int):
        if not cell.visited:
            return
            
        y_offset = font_size + 4
        
        if cell.breeze is not None:
            color = (0, 255, 255) if cell.breeze else (64, 64, 64)
            symbol = "B" if cell.breeze else "b"
            text = font.render(symbol, True, color)
            surface.blit(text, (2, y_offset))
            y_offset += font_size
        
        if cell.stench is not None:
            color = (255, 255, 0) if cell.stench else (64, 64, 64)
            symbol = "S" if cell.stench else "s"
            text = font.render(symbol, True, color)
            surface.blit(text, (2, y_offset))
    
    def get_surface(self):
        return self.knowledge_surface
