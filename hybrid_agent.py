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
        # Ensure KB is reset immediately after any wumpus movement
        # self.environment.reset_kb_callback = self.inference_engine.reset_kb

    def run(self):
        percepts = self.environment.get_percept()

        while self.state.alive:
            self.think(percepts)

            # self.knowledge.display_agent_view(agent_pos=(self.state.x, self.state.y), agent_dir=self.state.direction)
            # self.environment.display()

            if not self.action_plan:
                print("\nAgent is stuck and has no plan. Ending simulation.")
                break

            action = self.action_plan.pop(0)
            print(f"\nAction: {action.name}")

            percepts = self.environment.execute_action(action)
            self._update_state(action, percepts)

            if action == Action.SHOOT:
                # Reset KB after shooting
                self.inference_engine.reset_kb_after_shoot((self.state.x, self.state.y), self.state.direction)  

            # Reset KB
            if self.environment.moving_wumpus_mode and self.environment.agent_action_count > 0 and self.environment.agent_action_count % 5 == 0:
                self.inference_engine.reset_kb()
            
            if action == Action.CLIMB:
                break
        
        print(f"\nGame Over. Final Score: {self.environment.agent_state.score}, {self.environment.agent_action_count} actions taken, {self.environment.agent_state.has_gold} gold collected, {self.environment.agent_state.alive} alive")

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
        
        if not self._has_unvisited_safe():
            if self._plan_shoot():
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
        
        if unvisited_safe_cells:
            unvisited_safe_cells.sort(key=lambda pos: abs(pos[0] - self.state.x) + abs(pos[1] - self.state.y))
            target_pos = unvisited_safe_cells[0]
            print(f"New exploration target: {target_pos}")
            return self.planner.find_path(self.state, target_pos)

        if known_wumpus_cells and self.state.has_arrow:
            wpos = known_wumpus_cells[0]
            print(f"Known Wumpus at {wpos}, planning to move to its row/col.")
            return self._plan_align_wumpus(wpos)

        # 2) No unvisited SAFE cells left: consider between visited & UNKNOWN and unvisited & UNKNOWN
        visited_unknown = self.planner.find_least_risky_unknown(self.state.x, self.state.y, visited_filter=True)
        unvisited_unknown = self.planner.find_least_risky_unknown(self.state.x, self.state.y, visited_filter=False)

        # Choose the better between the two categories by risk, then distance
        best_unknown_target = None
        best_unknown_risk = float('inf')
        best_unknown_distance = float('inf')
        best_unknown_was_visited = False

        for candidate_pos in [visited_unknown, unvisited_unknown]:
            if candidate_pos is None:
                continue
            cx, cy = candidate_pos
            candidate_risk = self.planner._estimate_cell_risk(cx, cy)
            candidate_distance = abs(cx - self.state.x) + abs(cy - self.state.y)
            candidate_was_visited = self.knowledge.get_cell(cx, cy).visited
            if (
                candidate_risk < best_unknown_risk
                or (candidate_risk == best_unknown_risk and not candidate_was_visited and best_unknown_was_visited)
                or (candidate_risk == best_unknown_risk and candidate_was_visited == best_unknown_was_visited and candidate_distance < best_unknown_distance)
            ):
                best_unknown_risk = candidate_risk
                best_unknown_distance = candidate_distance
                best_unknown_target = candidate_pos
                best_unknown_was_visited = candidate_was_visited

        if best_unknown_target:
            print(f"Gambling: chosen UNKNOWN target {best_unknown_target} (risk={best_unknown_risk:.2f})")
            return self.planner.find_path(self.state, best_unknown_target)
        return None
    
    
    def _plan_align_wumpus(self, wumpus_pos) -> Optional[List[Action]]:
        agent_x, agent_y = self.state.x, self.state.y
        wumpus_x, wumpus_y = wumpus_pos

        if agent_x == wumpus_x or agent_y == wumpus_y:
            return []

        candidates = []
        for i in range(self.knowledge.size):
            if i != wumpus_y:
                pos = (wumpus_x, i)
                cell = self.knowledge.get_cell(pos[0], pos[1])
                if cell and cell.status == CellStatus.SAFE:
                    candidates.append(pos)
            if i != wumpus_x:
                pos2 = (i, wumpus_y)
                cell2 = self.knowledge.get_cell(pos2[0], pos2[1])
                if cell2 and cell2.status == CellStatus.SAFE:
                    candidates.append(pos2)

        if not candidates:
            return None

        candidates = list(set(candidates))  
        candidates.sort(key=lambda pos: abs(pos[0] - agent_x) + abs(pos[1] - agent_y))
        target = candidates[0]

        return self.planner.find_path(self.state, target)
    
    def _plan_shoot(self) -> bool:
        print("Planning to shoot Wumpus...")
        if not self.state.has_arrow:
            return False

        known_wumpus_cells = [
            pos for pos, c in self.knowledge.grid.items()
            if c.status == CellStatus.WUMPUS and not c.visited
        ]

        if not known_wumpus_cells:
            return False

        print(f"Known Wumpus cells: {known_wumpus_cells}")

        for wx, wy in known_wumpus_cells:
            print(f"Checking Wumpus at {(wx, wy)}")
            if self.state.x == wx or self.state.y == wy:
                if self.state.x == wx:
                    desired_dir = Direction.NORTH if wy > self.state.y else Direction.SOUTH
                else:
                    desired_dir = Direction.EAST if wx > self.state.x else Direction.WEST

                actions = []
                current_dir = self.state.direction
                while current_dir != desired_dir:
                    actions.append(Action.TURN_RIGHT)
                    current_dir = current_dir.turn_right()

                actions.append(Action.SHOOT)
                self.action_plan = actions
                print(f"Aligned with Wumpus at {(wx, wy)}: plan to {self.action_plan}")
                return True
        return False    
    
    def _has_unvisited_safe(self) -> bool:
        for (_, _), cell in self.knowledge.grid.items():
            if cell.status == CellStatus.SAFE and not cell.visited:
                return True
        return False
    
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