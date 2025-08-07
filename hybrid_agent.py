from environment import Environment, Action, Percept, AgentState
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
        self.turn_count = 0

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

        self.turn_count += 1

        if self.environment.moving_wumpus_mode and self.turn_count % 5 == 0:
            print("!!! Wumpus has moved! Resetting knowledge. !!!")
            self.knowledge.smart_reset()
            self.inference_engine.reset()

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
        for (x, y), cell in self.knowledge.grid.items():
            if cell.status == CellStatus.SAFE and not cell.visited:
                unvisited_safe_cells.append((x, y))

        if unvisited_safe_cells:
            unvisited_safe_cells.sort(key=lambda pos: abs(pos[0] - self.state.x) + abs(pos[1] - self.state.y))
            target_pos = unvisited_safe_cells[0]
            print(f"New exploration target: {target_pos}")
            return self.planner.find_path(self.state, target_pos)
        
        # ƯU TIÊN 2: TÁI KHẢO SÁT - Đi đến ô ĐÃ THĂM để thu thập thông tin mới
        # Mục tiêu tốt nhất là một ô ĐÃ THĂM, an toàn, và kề với nhiều ô UNKNOWN nhất.
        # Điều này tối đa hóa lượng thông tin mới (stench) có thể thu được.
        rescout_targets = []
        for (x, y), cell in self.knowledge.grid.items():
            if cell.visited: # Chỉ xem xét các ô đã thăm
                unknown_neighbors = 0
                for nx, ny in self.knowledge.get_neighbors(x, y):
                    if self.knowledge.get_cell(nx, ny).status == CellStatus.UNKNOWN:
                        unknown_neighbors += 1
                if unknown_neighbors > 0:
                    # (số ô UNKNOWN hàng xóm, tọa độ)
                    rescout_targets.append((-unknown_neighbors, (x, y))) # Dấu trừ để sort giảm dần

        if rescout_targets:
            rescout_targets.sort() # Sắp xếp để ưu tiên ô có nhiều hàng xóm UNKNOWN nhất
            target_pos = rescout_targets[0][1]
            print(f"Strategy: Re-scouting visited cell {target_pos} for new percepts.")
            return self.planner.find_path(self.state, target_pos)

        #risk if no safe cells
        risky_target = self.planner.find_least_risky_unknown(self.state.x, self.state.y)
        if risky_target:
            print(f"Gambling: least risky unknown target: {risky_target}")
            return self.planner.find_path(self.state, risky_target)
        return None

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