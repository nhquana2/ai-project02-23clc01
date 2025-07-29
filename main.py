from inference import KnowledgeBase
from typing import List, Set, Tuple, FrozenSet
from environment import Environment, Action

if __name__ == "__main__":
    env = Environment(size=8, num_wumpus=10, pit_prob=0.05)
    env.display()
    print(env.execute_action(Action.TURN_LEFT))
    env.display()
    print(env.execute_action(Action.SHOOT))
    env.display()

    kb = KnowledgeBase()
    c1 = frozenset({("B_1_1", False), ("P_1_2", True), ("P_2_1", True)})
    kb.tell(c1)
    c2 = frozenset({("B_1_1", True), ("P_1_2", False)})
    kb.tell(c2)
    q = frozenset({("P_2_1", True)})
    print(kb.ask(q))  # Check entailment