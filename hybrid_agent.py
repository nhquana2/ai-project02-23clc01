from environment import Environment, Action, Percept, AgentState, Direction
from agent_knowledge import MapKnowledge, CellStatus
from inference_engine import InferenceEngine
from planning import Planner
from typing import List, Optional
import time

class HybridAgent:
    def __init__(self, environment: Environment):
        self.environment = environment
        self.knowledge = MapKnowledge(environment.size, environment.num_wumpus)
        self.inference_engine = InferenceEngine(self.knowledge)
        self.planner = Planner(environment.size, self.knowledge)
        self.state = AgentState()
        self.action_plan: List[Action] = []

    def run(self):
        percepts = self.environment.get_percept()

        while self.state.alive:
            self.think(percepts)

            self.knowledge.display_agent_view(agent_pos=(self.state.x, self.state.y), agent_dir=self.state.direction)
            self.environment.display()

            if not self.action_plan:
                print("\nAgent is stuck and has no plan. Ending simulation.")
                break

            action = self.action_plan.pop(0)
            print(f"\nAction: {action.name}")

            percepts = self.environment.execute_action(action)
            self._update_state(action, percepts)
            
            if action == Action.CLIMB:
                break
        
        print(f"\nGame Over. Final Score: {self.environment.agent_state.score}")

    def think(self, percepts: Percept):
        self.knowledge.update_after_visit(self.state.x, self.state.y, percepts)

        inference_start_time = time.time()
        self.inference_engine.run_inference(
            (self.state.x, self.state.y),
            self.environment.agent_action_count,
            self.environment.moving_wumpus_mode
        )
        inference_end_time = time.time()

        if percepts.glitter:
            self.action_plan = [Action.GRAB]
            self.state.has_gold = True
            return

        if self.state.has_gold and (self.state.x, self.state.y) == (0, 0):
            self.action_plan = [Action.CLIMB]
            return

        if self.action_plan:
            return

        planning_start_time = time.time()
        if self.state.has_gold:
            self.action_plan = self.planner.find_path(self.state, (0, 0))
        else:
            self.action_plan = self._plan_exploration()

    def _plan_exploration(self) -> Optional[List[Action]]:
        unvisited_safe_cells = []
        known_wumpus_cells = []
        for (x, y), cell in self.knowledge.grid.items():
            if cell.status == CellStatus.SAFE and not cell.visited:
                unvisited_safe_cells.append((x, y))
            if cell.status == CellStatus.WUMPUS and not cell.visited:
                known_wumpus_cells.append((x, y))
                
                
        if (known_wumpus_cells or not unvisited_safe_cells) and self.state.has_arrow:
            if known_wumpus_cells:
                target = known_wumpus_cells[0]
                print(f"Known Wumpus at {target}, planning to shoot.")
                return self._plan_shoot_wumpus(target)
            else:
                print("No safe cells left, gambling with arrow.")
                return [Action.SHOOT]        
            
            
        if unvisited_safe_cells:
            unvisited_safe_cells.sort(key=lambda pos: abs(pos[0] - self.state.x) + abs(pos[1] - self.state.y))
            target_pos = unvisited_safe_cells[0]
            print(f"New exploration target: {target_pos}")
            return self.planner.find_path(self.state, target_pos)

        #risk if no safe cells
        risky_target = self.planner.find_least_risky_unknown(self.state.x, self.state.y)
        if risky_target:
            print(f"Gambling: least risky unknown target: {risky_target}")
            return self.planner.find_path(self.state, risky_target)
        return None
    
    
    def _plan_shoot_wumpus(self, wumpus_pos) -> Optional[List[Action]]:
        agent_x, agent_y = self.state.x, self.state.y
        wumpus_x, wumpus_y = wumpus_pos

        actions = []

        if agent_x == wumpus_x or agent_y == wumpus_y:
            # determine direction 
            if agent_x == wumpus_x:
                if agent_y < wumpus_y:
                    desired_dir = Direction.NORTH
                else:
                    desired_dir = Direction.SOUTH
            else:
                if agent_x < wumpus_x:
                    desired_dir = Direction.EAST
                else:
                    desired_dir = Direction.WEST

            # turn
            current_dir = self.state.direction
            while current_dir != desired_dir:
                actions.append(Action.TURN_RIGHT)
                current_dir = current_dir.turn_right()

            actions.append(Action.SHOOT)
            return actions

        # find closet same row/col if the curr cell does not on the same row/col
        candidates = []
        for i in range(self.knowledge.size):
            if i != agent_x:
                candidates.append((i, wumpus_y))
            if i != agent_y:
                candidates.append((wumpus_x, i))

        safe_candidates = [pos for pos in candidates if self.knowledge.get_cell(pos[0], pos[1]).status == CellStatus.SAFE]
        if safe_candidates:
            safe_candidates.sort(key=lambda pos: abs(pos[0] - agent_x) + abs(pos[1] - agent_y))
            target = safe_candidates[0]
            path = self.planner.find_path(self.state, target)
            if path is None:
                return None

            if target[0] == wumpus_x:
                if target[1] < wumpus_y:
                    desired_dir = Direction.NORTH
                else:
                    desired_dir = Direction.SOUTH
            else:
                if target[0] < wumpus_x:
                    desired_dir = Direction.EAST
                else:
                    desired_dir = Direction.WEST

            current_dir = self.state.direction
            turns = []
            while current_dir != desired_dir:
                turns.append(Action.TURN_RIGHT)
                current_dir = current_dir.turn_right()
            return path + turns + [Action.SHOOT]

        return [Action.SHOOT]
    
    
    def _update_state(self, action: Action, percept: Percept):
        if action == Action.TURN_LEFT:
            self.state.direction = self.state.direction.turn_left()
        elif action == Action.TURN_RIGHT:
            self.state.direction = self.state.direction.turn_right()
        elif action == Action.FORWARD and not percept.bump:
            dx, dy = self.state.direction.value
            self.state.x += dx
            self.state.y += dy
        elif action == Action.SHOOT:
            self.state.has_arrow = False
            if percept.scream:
                self.knowledge.wumpus_is_dead()
        
        self.state.alive = self.environment.agent_state.alive