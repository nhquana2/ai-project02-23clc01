from environment import Environment, Direction, Action
from gui.board import Board
from gui.info_panel import InfoPanel
from hybrid_agent import HybridAgent
import pygame
import time

if __name__ == "__main__":
    print("Wumpus World Auto Solver with Visualization")
    
    # Create environment
    env = Environment(size=8, num_wumpus=1, pit_prob=0.1, moving_wumpus_mode=True)
    agent = HybridAgent(env)
    
    pygame.init()
    board = Board(env, cell_size=80, agent_knowledge=agent.knowledge)
    
    # Create info panel for the right side
    info_panel_width = 480
    info_panel = InfoPanel(info_panel_width, env.size * 80, font_size=14)
    
    screen_width = env.size * 80 + info_panel_width + 20  # Board + panel + padding
    screen_height = env.size * 80
    screen = pygame.display.set_mode((screen_width, screen_height))
    pygame.display.set_caption("Wumpus World")
    
    font = pygame.font.Font(None, 20)
    clock = pygame.time.Clock()
    running = True
    step_delay = 0.5  # Fast auto mode
    last_step_time = time.time()
    step_count = 0
    
    
    while running and agent.state.alive:
        current_time = time.time()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
        if agent.state.alive and current_time - last_step_time >= step_delay:
            
            percepts = env.get_percept()
            
            percept_status = []
            percept_status.append(f"stench: {str(percepts.stench).lower()}")
            percept_status.append(f"breeze: {str(percepts.breeze).lower()}")
            percept_status.append(f"glitter: {str(percepts.glitter).lower()}")
            percept_status.append(f"bump: {str(percepts.bump).lower()}")
            percept_status.append(f"scream: {str(percepts.scream).lower()}")
            
            print(f"Step {step_count + 1}: {{{'; '.join(percept_status)}}}")
            
            agent.think(percepts)
            if agent.action_plan:
                action = agent.action_plan.pop(0)
                new_percepts = env.execute_action(action)
                agent._update_state(action, new_percepts)
                
                step_count += 1
                board.update(env, agent.knowledge)
                last_step_time = current_time
                
                if action == Action.CLIMB:
                    print(f"Agent climbed out! Final Score: {env.agent_state.score}")
                    break
                elif not agent.state.alive:
                    print(f"Agent died! Final Score: {env.agent_state.score}")
                    break
            else:
                print("No more actions available")
                break
        
        
        screen.fill((40, 40, 40))
        
        board.draw()
        screen.blit(board.get_surface(), (0, 0))
        
        current_percepts = env.get_percept()
        info_panel.draw(env, agent, step_count, current_percepts)
        info_panel_x = env.size * 80 + 10  # Board width + padding
        screen.blit(info_panel.get_surface(), (info_panel_x, 0))
        
        pygame.display.flip()
        clock.tick(60)
    
    pygame.quit()
    print(f"\nSimulation ended. Final Score: {env.agent_state.score}")
