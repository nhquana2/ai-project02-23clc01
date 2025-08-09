import heapq
from typing import List, Optional, Tuple, Dict
from environment import Action, AgentState, Direction
from agent_knowledge import MapKnowledge, CellStatus

SearchState = Tuple[int, int, Direction]  # (x, y, direction)

class Planner:
    RISK_PENALTY = 100

    def __init__(self, grid_size: int, knowledge: MapKnowledge):
        self.grid_size = grid_size
        self.map_knowledge = knowledge

    def _heuristic(self, pos: Tuple[int, int], goal: Tuple[int, int]) -> int:
        """Manhattan distance heuristic"""
        return abs(pos[0] - goal[0]) + abs(pos[1] - goal[1])
    
    def _get_action_cost(self, action: Action, next_pos: Tuple[int, int]) -> float:
        """Cost of moving to the next position, factoring risk for unknown cells."""
        cost = 1.0
        if action == Action.FORWARD:
            cell = self.map_knowledge.get_cell(next_pos[0], next_pos[1])
            if cell.status == CellStatus.WUMPUS or cell.status == CellStatus.PIT:
                return float('inf')
            if cell.status == CellStatus.UNKNOWN:
                risk = self._estimate_cell_risk(next_pos[0], next_pos[1])
                # Risk penalty scales with estimated risk
                return cost + self.RISK_PENALTY * risk
        return cost
    def _estimate_cell_risk(self, x: int, y: int) -> float:
        cell = self.map_knowledge.get_cell(x, y)
        if cell.status != CellStatus.UNKNOWN:
            return 0.0
        neighbors = self.map_knowledge.get_neighbors(x, y)
        risk = 0.0
        for nx, ny in neighbors:
            neighbor_cell = self.map_knowledge.get_cell(nx, ny)
            if neighbor_cell.stench:
                risk += 0.5
            if neighbor_cell.breeze:
                risk += 0.5
        # normalize
        risk = min(risk / max(1, len(neighbors)), 1.0)
        return risk
    
    def find_least_risky_unknown(self, agent_x: int, agent_y: int, visited_filter: Optional[bool] = None) -> Optional[Tuple[int, int]]:
        min_risk = float('inf')
        best_cell = None
        for (x, y), cell in self.map_knowledge.grid.items():
            if cell.status != CellStatus.UNKNOWN:
                continue
            if visited_filter is True and not cell.visited:
                continue
            if visited_filter is False and cell.visited:
                continue
            
            risk = self._estimate_cell_risk(x, y)
            # prefer closer cells if risk is equal
            dist = abs(x - agent_x) + abs(y - agent_y)  
            if risk < min_risk or (risk == min_risk and (best_cell is None or dist < abs(best_cell[0] - agent_x) + abs(best_cell[1] - agent_y))):
                min_risk = risk
                best_cell = (x, y)

        return best_cell
    
    def _reconstruct_path(self, came_from: Dict, current: SearchState) -> List[Action]:
        """Reconstruct the path from start to goal"""
        path = []

        while current in came_from:
            prev, action = came_from[current]
            path.append(action)
            current = prev
        
        return path[::-1]
    
    def find_path(self, start_state: AgentState, goal_pos: Tuple[int, int]) -> Optional[List[Action]]:
        """A* search algorithm to find the path to the goal position"""
        start_node: SearchState = (start_state.x, start_state.y, start_state.direction)
        self.counter = 0
        open_set = [(self._heuristic((start_state.x, start_state.y), goal_pos), self.counter, start_node)]
        came_from: Dict[SearchState, Tuple[SearchState, Action]] = {}

        g_score = {
            (x, y, d): float('inf') for x in range(self.grid_size) for y in range(self.grid_size) for d in Direction
        }
        g_score[start_node] = 0

        while open_set:
            _, _, current_node = heapq.heappop(open_set)

            if (current_node[0], current_node[1]) == goal_pos:
                return self._reconstruct_path(came_from, current_node)

            for action in [Action.FORWARD, Action.TURN_LEFT, Action.TURN_RIGHT]:
                x, y, direction = current_node

                if action == Action.TURN_LEFT:
                    next_node = (x, y, direction.turn_left())
                elif action == Action.TURN_RIGHT:
                    next_node = (x, y, direction.turn_right())
                else: # Action.FORWARD
                    dx, dy = direction.value
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < self.grid_size and 0 <= ny < self.grid_size:
                        next_node = (nx, ny, direction)
                    else: continue

                cost = self._get_action_cost(action, (next_node[0], next_node[1]))
                tentative_g_score = g_score[current_node] + cost

                if tentative_g_score < g_score[next_node]:
                    came_from[next_node] = (current_node, action)
                    g_score[next_node] = tentative_g_score
                    f_score = tentative_g_score + self._heuristic((next_node[0], next_node[1]), goal_pos)
                    self.counter += 1
                    heapq.heappush(open_set, (f_score, self.counter, next_node))

        return None # No path found