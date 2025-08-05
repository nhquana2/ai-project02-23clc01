import pygame
from environment import Environment
from agent_knowledge import MapKnowledge
from .image_manager import ImageManager
from .background_renderer import BackgroundRenderer
from .entity_renderer import EntityRenderer
from .knowledge_renderer import KnowledgeRenderer

class BoardCompositor:
    """Main board class that coordinates all rendering components"""
    
    def __init__(self, environment: Environment, cell_size: int = 32, agent_knowledge: MapKnowledge = None):
        self.environment = environment
        self.agent_knowledge = agent_knowledge
        self.cell_size = cell_size
        self.board_size = environment.size
        self.width = self.board_size * cell_size
        self.height = self.board_size * cell_size
        
        # Initialize rendering components
        self.image_manager = ImageManager(cell_size)
        self.background_renderer = BackgroundRenderer(environment, cell_size, self.image_manager)
        self.entity_renderer = EntityRenderer(cell_size, self.board_size, self.image_manager)
        self.knowledge_renderer = KnowledgeRenderer(cell_size, self.board_size)
        
        
        self.board_surface = pygame.Surface((self.width, self.height))
        self.background_renderer.build_background()
    
    def draw(self):
        if self.background_renderer.should_rebuild_background(self.environment):
            self.background_renderer.update_environment(self.environment)
            self.background_renderer.build_background()
            self.background_renderer.update_tracking_state(self.environment)
        
        self.board_surface.blit(self.background_renderer.get_surface(), (0, 0))
        
        self.entity_renderer.clear_surface()
        self.entity_renderer.draw_wumpuses(self.environment)
        self.entity_renderer.draw_agent(self.environment)
        
        self.knowledge_renderer.draw_knowledge(self.agent_knowledge)
        
        self.board_surface.blit(self.knowledge_renderer.get_surface(), (0, 0))
        self.board_surface.blit(self.entity_renderer.get_surface(), (0, 0))
    
    
    def get_surface(self):
        return self.board_surface
    
    def update(self, environment: Environment, agent_knowledge: MapKnowledge = None):
        self.environment = environment
        if agent_knowledge:
            self.agent_knowledge = agent_knowledge
        self.draw()
    
    def force_background_rebuild(self):
        self.background_renderer.force_rebuild()
    
    def on_wumpus_moved(self):
        self.background_renderer.force_rebuild()
