from enum import Enum
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
import random

class Direction(Enum):
    NORTH = (0, 1)
    EAST = (1, 0)
    SOUTH = (0, -1)
    WEST = (-1, 0)

    def turn_left(self):
        directions = list(Direction)
        index = (directions.index(self) - 1) % len(directions)
        return directions[index]

    def turn_right(self):
        directions = list(Direction)
        index = (directions.index(self) + 1) % len(directions)
        return directions[index]

class Action(Enum):
    FORWARD = "forward"
    TURN_LEFT = "turn_left"
    TURN_RIGHT = "turn_right"
    GRAB = "grab"
    SHOOT = "shoot"
    CLIMB = "climb"

@dataclass
class Percept:
    stench: bool = False
    breeze: bool = False
    glitter: bool = False
    bump: bool = False
    scream: bool = False

@dataclass
class AgentState:
    x: int = 0
    y: int = 0
    direction: Direction = Direction.EAST
    has_gold: bool = False
    has_arrow: bool = True
    alive: bool = True
    score: int = 0

class Environment:
    def __init__(self, size: int = 8, num_wumpus: int = 2, pit_prob: float = 0.2):
        self.size = size
        self.num_wumpus = num_wumpus
        self.pit_prob = pit_prob
        self.reset()

    def reset(self):
        self.wumpus_positions = set()
        self.pit_positions = set()
        self.gold_position = None
        self.agent_state = AgentState()
        self._generate_world()
    
    def _generate_world(self):
        # Generate wumpus
        while len(self.wumpus_positions) < self.num_wumpus:
            pos = (random.randint(0, self.size-1), random.randint(0, self.size-1))
            if pos != (0, 0):
                self.wumpus_positions.add(pos)
            
        # Generate pits
        for x in range(self.size):
            for y in range(self.size):
                if (x, y) not in self.wumpus_positions and (x, y) != (0, 0):
                    if random.random() < self.pit_prob:
                        self.pit_positions.add((x, y))
        
        # Generate ONE gold
        available_positions = [(x, y) for x in range(self.size) for y in range(self.size) 
        if (x, y) not in self.wumpus_positions and (x, y) not in self.pit_positions]
        self.gold_position = random.choice(available_positions)

    def get_percept(self) -> Percept:
        percept = Percept()
        x, y = self.agent_state.x, self.agent_state.y

        adjacent = [(x+1, y), (x-1, y), (x, y+1), (x, y-1)]

        for adj_x, adj_y in adjacent:
            if 0 <= adj_x < self.size and 0 <= adj_y < self.size:
                if (adj_x, adj_y) in self.wumpus_positions:
                    percept.stench = True
                if (adj_x, adj_y) in self.pit_positions:
                    percept.breeze = True

        if (x, y) == self.gold_position:
            percept.glitter = True

        return percept

    def execute_action(self, action: Action) -> Percept:
        if not self.agent_state.alive:
            return Percept()
        
        bump_occurred = False
        scream_occurred = False
        
        if action == Action.FORWARD:
            bump_occurred = self._move_forward()
            self.agent_state.score -= 1

        elif action == Action.TURN_LEFT:
            self.agent_state.direction = self.agent_state.direction.turn_left()
            self.agent_state.score -= 1

        elif action == Action.TURN_RIGHT:
            self.agent_state.direction = self.agent_state.direction.turn_right()
            self.agent_state.score -= 1

        elif action == Action.GRAB:
            if (self.agent_state.x, self.agent_state.y) == self.gold_position:
                self.agent_state.has_gold = True
                self.agent_state.score += 10

        elif action == Action.SHOOT:
            if self.agent_state.has_arrow:
                self.agent_state.has_arrow = False
                self.agent_state.score -= 10
                scream_occurred = self._shoot_arrow()

        elif action == Action.CLIMB:
            if (self.agent_state.x, self.agent_state.y) == (0, 0):
                if self.agent_state.has_gold:
                    self.agent_state.score += 1000
                self.agent_state.alive = False  # Game ends
        
        # Check dead 
        pos = (self.agent_state.x, self.agent_state.y)
        if pos in self.wumpus_positions or pos in self.pit_positions:
            self.agent_state.alive = False
            self.agent_state.score -= 1000
        
        percept = self.get_percept()
        percept.bump = bump_occurred
        percept.scream = scream_occurred
        return percept
    
    def _move_forward(self) -> bool:
        dx, dy = self.agent_state.direction.value
        new_x = self.agent_state.x + dx
        new_y = self.agent_state.y + dy
        
        if 0 <= new_x < self.size and 0 <= new_y < self.size:
            self.agent_state.x = new_x
            self.agent_state.y = new_y
            return False  

        return True 
    
    def _shoot_arrow(self) -> bool:
        dx, dy = self.agent_state.direction.value
        x, y = self.agent_state.x, self.agent_state.y
        
        while True:
            x += dx
            y += dy
            if not (0 <= x < self.size and 0 <= y < self.size):
                break
            if (x, y) in self.wumpus_positions:
                self.wumpus_positions.remove((x, y))
                return True 
        
        return False
    
    def display(self):
        print("\n" + "="*40)
        for y in range(self.size-1, -1, -1):
            row = []
            for x in range(self.size):
                if (x, y) == (self.agent_state.x, self.agent_state.y):
                    if self.agent_state.direction == Direction.NORTH:
                        cell = "^"
                    elif self.agent_state.direction == Direction.EAST:
                        cell = ">"
                    elif self.agent_state.direction == Direction.SOUTH:
                        cell = "v"
                    else:
                        cell = "<"
                elif (x, y) in self.wumpus_positions:
                    cell = "W"
                elif (x, y) in self.pit_positions:
                    cell = "P"
                elif (x, y) == self.gold_position:
                    cell = "G"
                else:
                    cell = "."
                row.append(cell.center(3))
            print(" ".join(row))
        print(f"Score: {self.agent_state.score}, Arrow: {self.agent_state.has_arrow}, Gold: {self.agent_state.has_gold}")