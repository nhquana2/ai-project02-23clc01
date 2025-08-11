import random
from environment import Environment, Action, Direction, Percept, AgentState
from agent_knowledge import MapKnowledge
from typing import List, Optional

class RandomAgent:
    """A simple random agent that chooses actions randomly with basic logic"""
    
    def __init__(self, environment: Environment):
        self.environment = environment
        self.knowledge = MapKnowledge(environment.size, environment.num_wumpus)
        self.state = AgentState()
        self.action_plan: List[Action] = []
        
        # Available actions for random selection (including CLIMB for completeness)
        self.available_actions = [
            Action.FORWARD,
            Action.TURN_LEFT,
            Action.TURN_RIGHT,
            Action.GRAB,
            Action.SHOOT,
            Action.CLIMB
        ]

    def think(self, percepts: Percept):
        """Main thinking method called each step"""
        # Update knowledge with current position and percepts
        self.knowledge.update_after_visit(self.state.x, self.state.y, percepts)
        
        # Only handle essential actions, everything else is random
        if percepts.glitter:
            self.action_plan = [Action.GRAB]
            self.state.has_gold = True
            return
        
        if self.state.has_gold and (self.state.x, self.state.y) == (0, 0):
            self.action_plan = [Action.CLIMB]
            return
        
        # Always choose a completely random action
        self.action_plan = [self._choose_random_action()]
    
    def run(self):
        """Main game loop for the random agent"""
        percepts = self.environment.get_percept()

        while self.state.alive:
            self.think(percepts)

            # self.knowledge.display_agent_view(agent_pos=(self.state.x, self.state.y), agent_dir=self.state.direction)
            # self.environment.display()

            if not self.action_plan:
                print("\nRandom agent has no action planned. Ending simulation.")
                break

            action = self.action_plan.pop(0)
            print(f"\nRandom Action: {action.name}")

            # Execute action and get new percepts
            percepts = self.environment.execute_action(action)
            self._update_state(action, percepts)

            # End game if agent climbs out
            if action == Action.CLIMB:
                break
        
        print(f"\nGame Over. Final Score: {self.environment.agent_state.score}")

    def _choose_random_action(self) -> Action:
        """Choose a completely random action from available actions"""
        valid_actions = []
        
        for action in self.available_actions:
            if action == Action.CLIMB:
                if (self.state.x, self.state.y) == (0, 0):
                    valid_actions.append(action)
            else:
                valid_actions.append(action)
        
        if not valid_actions:
            valid_actions = [Action.FORWARD, Action.TURN_LEFT, Action.TURN_RIGHT]
        
        return random.choice(valid_actions)

    def _update_state(self, action: Action, percept: Percept):
        """Update agent's internal state after taking an action"""
        if action == Action.TURN_LEFT:
            self.state.direction = self.state.direction.turn_left()
        elif action == Action.TURN_RIGHT:
            self.state.direction = self.state.direction.turn_right()
        elif action == Action.FORWARD and not percept.bump:
            dx, dy = self.state.direction.value
            self.state.x += dx
            self.state.y += dy
        elif action == Action.GRAB and percept.glitter:
            self.state.has_gold = True
        elif action == Action.SHOOT:
            self.state.has_arrow = False
            if percept.scream:
                self.knowledge.wumpus_is_dead()
        
        # Update alive status from environment
        self.state.alive = self.environment.agent_state.alive
        
    def get_strategy_info(self) -> str:
        """Return information about current strategy"""
        if self.state.has_gold:
            return "Random: Has gold, acting randomly"
        else:
            return "Random: Acting completely randomly"
